"""
MySQL查询MCP工具模块
提供连接MySQL数据库并执行查询的功能
"""

from flask import jsonify, request
from . import mcp_bp
import mysql.connector
import json

@mcp_bp.route('/mysql_query/get_database_metadata', methods=['POST'])
def get_database_metadata():
    """
    获取所有数据库的元数据信息，包括表名、字段名、字段注释、字段类型、字段长度、是否为空、是否主键、外键、索引
    """
    try:
        # 获取请求数据
        data = request.json
        host = data.get('host')
        user = data.get('user')
        password = data.get('password')
        database = data.get('database')
        port = data.get('port', 3306)
        
        # 验证必要参数
        if not all([host, user, password, database]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 连接数据库
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # 查询所有表
        cursor.execute("""
            SELECT 
                TABLE_NAME 
            FROM 
                information_schema.TABLES 
            WHERE 
                TABLE_SCHEMA = %s
        """, (database,))
        
        tables = cursor.fetchall()
        
        metadata = {}
        
        # 获取每个表的字段信息
        for table in tables:
            table_name = table['TABLE_NAME']
            
            # 获取表的字段信息
            cursor.execute("""
                SELECT 
                    COLUMN_NAME, 
                    COLUMN_TYPE, 
                    IS_NULLABLE, 
                    COLUMN_KEY, 
                    COLUMN_COMMENT,
                    CHARACTER_MAXIMUM_LENGTH
                FROM 
                    information_schema.COLUMNS 
                WHERE 
                    TABLE_SCHEMA = %s AND 
                    TABLE_NAME = %s
                ORDER BY 
                    ORDINAL_POSITION
            """, (database, table_name))
            
            columns = cursor.fetchall()
            
            # 获取表索引信息
            cursor.execute("""
                SELECT 
                    INDEX_NAME,
                    COLUMN_NAME,
                    NON_UNIQUE
                FROM 
                    information_schema.STATISTICS
                WHERE 
                    TABLE_SCHEMA = %s AND 
                    TABLE_NAME = %s
            """, (database, table_name))
            
            indexes = cursor.fetchall()
            
            # 获取外键信息
            cursor.execute("""
                SELECT 
                    CONSTRAINT_NAME,
                    COLUMN_NAME,
                    REFERENCED_TABLE_NAME,
                    REFERENCED_COLUMN_NAME
                FROM 
                    information_schema.KEY_COLUMN_USAGE
                WHERE 
                    TABLE_SCHEMA = %s AND 
                    TABLE_NAME = %s AND
                    REFERENCED_TABLE_NAME IS NOT NULL
            """, (database, table_name))
            
            foreign_keys = cursor.fetchall()
            
            # 组织元数据
            metadata[table_name] = {
                'columns': columns,
                'indexes': indexes,
                'foreign_keys': foreign_keys
            }
        
        cursor.close()
        connection.close()
        
        return jsonify(metadata)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mcp_bp.route('/mysql_query/get_sample_data', methods=['POST'])
def get_sample_data():
    """
    获取所有数据库每个表的样例数据（默认最多3条）
    """
    try:
        # 获取请求数据
        data = request.json
        host = data.get('host')
        user = data.get('user')
        password = data.get('password')
        database = data.get('database')
        port = data.get('port', 3306)
        limit = data.get('limit', 3)
        
        # 验证必要参数
        if not all([host, user, password, database]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 连接数据库
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # 查询所有表
        cursor.execute("""
            SELECT 
                TABLE_NAME 
            FROM 
                information_schema.TABLES 
            WHERE 
                TABLE_SCHEMA = %s
        """, (database,))
        
        tables = cursor.fetchall()
        
        sample_data = {}
        
        # 获取每个表的样例数据
        for table in tables:
            table_name = table['TABLE_NAME']
            
            try:
                # 获取表的样例数据
                cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit}")
                rows = cursor.fetchall()
                
                # 转换datetime等对象为字符串以便JSON序列化
                for row in rows:
                    for key, value in row.items():
                        if isinstance(value, (bytes, bytearray)):
                            row[key] = value.hex()
                
                sample_data[table_name] = rows
            except Exception as e:
                sample_data[table_name] = {"error": str(e)}
        
        cursor.close()
        connection.close()
        
        return jsonify(sample_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mcp_bp.route('/mysql_query/execute_readonly_query', methods=['POST'])
def execute_readonly_query():
    """
    在只读事务中执行自定义SQL查询，确保查询不会修改数据库
    """
    try:
        # 获取请求数据
        data = request.json
        host = data.get('host')
        user = data.get('user')
        password = data.get('password')
        database = data.get('database')
        port = data.get('port', 3306)
        query = data.get('query')
        max_rows = data.get('max_rows', 100)
        
        # 验证必要参数
        if not all([host, user, password, database, query]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 检查查询是否是只读查询
        query_lower = query.lower().strip()
        if not query_lower.startswith('select') and not query_lower.startswith('show') and not query_lower.startswith('desc'):
            return jsonify({'error': '只允许执行SELECT、SHOW或DESC查询'}), 400
        
        # 连接数据库
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        
        cursor = connection.cursor(dictionary=True)
        
        # 开始只读事务
        cursor.execute("SET TRANSACTION READ ONLY")
        cursor.execute("START TRANSACTION")
        
        # 执行查询
        cursor.execute(query)
        
        # 获取结果
        results = cursor.fetchmany(max_rows)
        
        # 获取列信息
        columns = [column[0] for column in cursor.description]
        
        # 转换datetime等对象为字符串以便JSON序列化
        for row in results:
            for key, value in row.items():
                if isinstance(value, (bytes, bytearray)):
                    row[key] = value.hex()
        
        # 回滚事务（只读事务无需提交）
        connection.rollback()
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'columns': columns,
            'rows': results,
            'rowCount': len(results),
            'truncated': cursor.rowcount > len(results) if cursor.rowcount >= 0 else False
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 