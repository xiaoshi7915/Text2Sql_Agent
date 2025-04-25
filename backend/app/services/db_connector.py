#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库连接服务
负责处理不同类型数据库的连接及表数量查询
"""

import logging
logger = logging.getLogger(__name__)

class BaseConnector:
    """数据库连接基类"""
    
    def __init__(self, host, port, database, username, password):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        
    def connect(self):
        """建立连接"""
        raise NotImplementedError("子类必须实现此方法")
        
    def get_table_count(self):
        """获取数据库中的表数量"""
        raise NotImplementedError("子类必须实现此方法")

    def get_tables(self):
        """获取数据库中的所有表"""
        raise NotImplementedError("子类必须实现此方法")
        
    def get_table_schema(self, table_name):
        """获取指定表的结构"""
        raise NotImplementedError("子类必须实现此方法")
        
    def get_sample_data(self, table_name, limit=10):
        """获取指定表的样例数据"""
        raise NotImplementedError("子类必须实现此方法")
        
    def test_connection(self):
        """测试连接并返回表数量"""
        try:
            logger.info(f"尝试连接到{self.__class__.__name__}: {self.host}:{self.port}")
            # 建立连接
            self.connect()
            logger.info(f"连接成功，正在获取表数量")
            # 获取表数量
            table_count = self.get_table_count()
            logger.info(f"获取表数量成功: {table_count}")
            return True, table_count, None
        except Exception as e:
            import traceback
            logger.error(f"数据库连接失败: {self.__class__.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return False, 0, str(e)


class MySQLConnector(BaseConnector):
    """MySQL数据库连接器"""
    
    def connect(self):
        """建立MySQL连接"""
        import mysql.connector
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            database=self.database,
            port=self.port,
            use_pure=True,  # 使用纯Python实现，避免c扩展问题
            auth_plugin='mysql_native_password',  # 使用旧版认证插件
            ssl_disabled=True  # 禁用SSL
        )
        self.cursor = self.connection.cursor()
        
    def get_table_count(self):
        """获取MySQL数据库中的表数量"""
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (self.database,))
        
        result = self.cursor.fetchone()
        table_count = result[0] if result else 0
        
        self.cursor.close()
        self.connection.close()
        return table_count
    
    def get_tables(self):
        """获取MySQL数据库中的所有表"""
        try:
            self.connect()
            self.cursor.execute("""
                SELECT 
                    TABLE_NAME as name, 
                    TABLE_COMMENT as description,
                    TABLE_ROWS as row_count,
                    CREATE_TIME as create_time,
                    UPDATE_TIME as update_time
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME
            """, (self.database,))
            
            columns = [col[0] for col in self.cursor.description]
            tables = []
            
            for row in self.cursor.fetchall():
                table_data = dict(zip(columns, row))
                # 处理None值和日期时间
                for key, value in table_data.items():
                    if isinstance(value, (bytes, bytearray)):
                        table_data[key] = value.decode('utf-8')
                    elif hasattr(value, 'isoformat'):  # 如果是日期时间类型
                        table_data[key] = value.isoformat()
                tables.append(table_data)
            
            return tables
            
        except Exception as e:
            logger.error(f"获取表列表失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
    
    def get_table_schema(self, table_name):
        """获取MySQL表的结构"""
        try:
            self.connect()
            
            # 获取表的列信息
            self.cursor.execute("""
                SELECT 
                    COLUMN_NAME as column_name,
                    DATA_TYPE as data_type,
                    COLUMN_TYPE as column_type,
                    IS_NULLABLE = 'YES' as is_nullable,
                    COLUMN_KEY = 'PRI' as is_primary_key,
                    COLUMN_DEFAULT as default_value,
                    COLUMN_COMMENT as description
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (self.database, table_name))
            
            columns = [col[0] for col in self.cursor.description]
            schema = []
            
            for row in self.cursor.fetchall():
                column_data = dict(zip(columns, row))
                # 处理None值和特殊类型
                for key, value in column_data.items():
                    if isinstance(value, (bytes, bytearray)):
                        column_data[key] = value.decode('utf-8')
                schema.append(column_data)
            
            return schema
            
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
    
    def get_sample_data(self, table_name, limit=10):
        """获取MySQL表的样例数据"""
        try:
            self.connect()
            
            # 安全地构造表名（防止SQL注入）
            safe_table_name = self.connection.converter.escape(table_name)
            # 移除引号
            if safe_table_name.startswith('`') and safe_table_name.endswith('`'):
                safe_table_name = safe_table_name[1:-1]
                
            # 获取样例数据
            query = f"SELECT * FROM `{safe_table_name}` LIMIT {int(limit)}"
            self.cursor.execute(query)
            
            # 获取列名
            columns = [col[0] for col in self.cursor.description]
            
            # 构造结果
            result = []
            for row in self.cursor.fetchall():
                row_dict = {}
                for i, value in enumerate(row):
                    # 处理特殊类型
                    if isinstance(value, (bytes, bytearray)):
                        row_dict[columns[i]] = value.decode('utf-8', errors='replace')
                    elif hasattr(value, 'isoformat'):  # 日期时间类型
                        row_dict[columns[i]] = value.isoformat()
                    else:
                        row_dict[columns[i]] = value
                result.append(row_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"获取样例数据失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()


class PostgreSQLConnector(BaseConnector):
    """PostgreSQL数据库连接器"""
    
    def connect(self):
        """建立PostgreSQL连接"""
        import psycopg2
        self.connection = psycopg2.connect(
            host=self.host,
            user=self.username,
            password=self.password,
            dbname=self.database,
            port=self.port
        )
        self.cursor = self.connection.cursor()
        
    def get_table_count(self):
        """获取PostgreSQL数据库中的表数量"""
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """)
        
        result = self.cursor.fetchone()
        table_count = result[0] if result else 0
        
        self.cursor.close()
        self.connection.close()
        return table_count
    
    def get_tables(self):
        """获取PostgreSQL数据库中的所有表"""
        try:
            self.connect()
            self.cursor.execute("""
                SELECT 
                    table_name as name, 
                    obj_description((quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass::oid, 'pg_class') as description,
                    NULL as row_count
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                ORDER BY table_name
            """)
            
            columns = [col[0] for col in self.cursor.description]
            tables = []
            
            for row in self.cursor.fetchall():
                table_data = dict(zip(columns, row))
                
                # 获取表的估计行数
                table_name = table_data['name']
                
                try:
                    self.cursor.execute(f"""
                        SELECT reltuples::bigint as row_count
                        FROM pg_class 
                        WHERE relname = %s
                    """, (table_name,))
                    
                    row_count = self.cursor.fetchone()
                    if row_count:
                        table_data['row_count'] = int(row_count[0])
                except:
                    # 如果获取行数失败，保持为NULL
                    pass
                
                tables.append(table_data)
            
            return tables
            
        except Exception as e:
            logger.error(f"获取表列表失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
    
    def get_table_schema(self, table_name):
        """获取PostgreSQL表的结构"""
        try:
            self.connect()
            
            # 获取表的列信息
            self.cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable = 'YES' as is_nullable,
                    column_default as default_value,
                    FALSE as is_primary_key,
                    '' as description
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = [col[0] for col in self.cursor.description]
            schema = []
            
            for row in self.cursor.fetchall():
                column_data = dict(zip(columns, row))
                schema.append(column_data)
            
            # 获取主键信息
            self.cursor.execute("""
                SELECT a.attname as column_name
                FROM   pg_index i
                JOIN   pg_attribute a ON a.attrelid = i.indrelid
                                     AND a.attnum = ANY(i.indkey)
                WHERE  i.indrelid = %s::regclass
                AND    i.indisprimary
            """, (table_name,))
            
            primary_keys = [row[0] for row in self.cursor.fetchall()]
            
            # 更新主键标记
            for col in schema:
                if col['column_name'] in primary_keys:
                    col['is_primary_key'] = True
            
            return schema
            
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
    
    def get_sample_data(self, table_name, limit=10):
        """获取PostgreSQL表的样例数据"""
        try:
            self.connect()
            
            # 安全地引用表名
            self.cursor.execute(f"SELECT * FROM \"{table_name}\" LIMIT {int(limit)}")
            
            # 获取列名
            columns = [col[0] for col in self.cursor.description]
            
            # 构造结果
            result = []
            for row in self.cursor.fetchall():
                row_dict = {}
                for i, value in enumerate(row):
                    # 处理特殊类型
                    if hasattr(value, 'isoformat'):  # 日期时间类型
                        row_dict[columns[i]] = value.isoformat()
                    else:
                        row_dict[columns[i]] = value
                result.append(row_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"获取样例数据失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()


class SQLServerConnector(BaseConnector):
    """SQL Server数据库连接器"""
    
    def connect(self):
        """建立SQL Server连接"""
        import pyodbc
        connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.host},{self.port};DATABASE={self.database};UID={self.username};PWD={self.password}"
        self.connection = pyodbc.connect(connection_string)
        self.cursor = self.connection.cursor()
        
    def get_table_count(self):
        """获取SQL Server数据库中的表数量"""
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_type = 'BASE TABLE'
        """)
        
        result = self.cursor.fetchone()
        table_count = result[0] if result else 0
        
        self.cursor.close()
        self.connection.close()
        return table_count
    
    def get_tables(self):
        """获取SQL Server数据库中的所有表"""
        try:
            self.connect()
            self.cursor.execute("""
                SELECT 
                    t.TABLE_NAME as name,
                    ep.value as description,
                    p.rows as row_count,
                    t.TABLE_SCHEMA as schema_name
                FROM information_schema.tables t
                LEFT JOIN sys.tables st ON st.name = t.TABLE_NAME
                LEFT JOIN sys.extended_properties ep ON ep.major_id = st.object_id AND ep.minor_id = 0 AND ep.name = 'MS_Description'
                LEFT JOIN sys.indexes i ON i.object_id = st.object_id AND i.index_id < 2
                LEFT JOIN sys.partitions p ON p.object_id = st.object_id AND p.index_id = i.index_id
                WHERE t.TABLE_TYPE = 'BASE TABLE'
                ORDER BY t.TABLE_NAME
            """)
            
            columns = [col[0] for col in self.cursor.description]
            tables = []
            
            for row in self.cursor.fetchall():
                table_data = dict(zip(columns, row))
                # 如果没有描述，使用空字符串
                if table_data.get('description') is None:
                    table_data['description'] = ''
                tables.append(table_data)
            
            return tables
            
        except Exception as e:
            logger.error(f"获取表列表失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
    
    def get_table_schema(self, table_name):
        """获取SQL Server表的结构"""
        try:
            self.connect()
            
            # 获取表的列信息
            self.cursor.execute("""
                SELECT 
                    c.COLUMN_NAME as column_name,
                    c.DATA_TYPE as data_type,
                    c.IS_NULLABLE = 'YES' as is_nullable,
                    CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 1 ELSE 0 END as is_primary_key,
                    c.COLUMN_DEFAULT as default_value,
                    ISNULL(ep.value, '') as description
                FROM information_schema.columns c
                LEFT JOIN (
                    SELECT ku.TABLE_CATALOG, ku.TABLE_SCHEMA, ku.TABLE_NAME, ku.COLUMN_NAME
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage ku
                        ON tc.CONSTRAINT_TYPE = 'PRIMARY KEY' 
                        AND tc.CONSTRAINT_NAME = ku.CONSTRAINT_NAME
                ) pk 
                    ON c.TABLE_CATALOG = pk.TABLE_CATALOG 
                    AND c.TABLE_SCHEMA = pk.TABLE_SCHEMA 
                    AND c.TABLE_NAME = pk.TABLE_NAME 
                    AND c.COLUMN_NAME = pk.COLUMN_NAME
                LEFT JOIN sys.columns sc ON sc.name = c.COLUMN_NAME
                LEFT JOIN sys.tables st ON st.name = c.TABLE_NAME
                LEFT JOIN sys.extended_properties ep ON ep.major_id = st.object_id AND ep.minor_id = sc.column_id AND ep.name = 'MS_Description'
                WHERE c.TABLE_NAME = ?
                ORDER BY c.ORDINAL_POSITION
            """, (table_name,))
            
            columns = [col[0] for col in self.cursor.description]
            schema = []
            
            for row in self.cursor.fetchall():
                column_data = dict(zip(columns, row))
                # 转换布尔值
                column_data['is_nullable'] = bool(column_data['is_nullable'])
                column_data['is_primary_key'] = bool(column_data['is_primary_key'])
                schema.append(column_data)
            
            return schema
            
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
    
    def get_sample_data(self, table_name, limit=10):
        """获取SQL Server表的样例数据"""
        try:
            self.connect()
            
            # 获取表的架构
            schema_query = f"SELECT TABLE_SCHEMA FROM information_schema.tables WHERE TABLE_NAME = ?"
            self.cursor.execute(schema_query, (table_name,))
            schema_result = self.cursor.fetchone()
            schema_name = schema_result[0] if schema_result else 'dbo'
            
            # 查询样例数据
            self.cursor.execute(f"SELECT TOP {int(limit)} * FROM [{schema_name}].[{table_name}]")
            
            # 获取列名
            columns = [col[0] for col in self.cursor.description]
            
            # 构造结果
            result = []
            for row in self.cursor.fetchall():
                row_dict = {}
                for i, value in enumerate(row):
                    # 处理特殊类型
                    if hasattr(value, 'isoformat'):  # 日期时间类型
                        row_dict[columns[i]] = value.isoformat()
                    else:
                        row_dict[columns[i]] = value
                result.append(row_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"获取样例数据失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()


class OracleConnector(BaseConnector):
    """Oracle数据库连接器"""
    
    def connect(self):
        """建立Oracle连接"""
        import cx_Oracle
        dsn = cx_Oracle.makedsn(self.host, self.port, service_name=self.database)
        self.connection = cx_Oracle.connect(self.username, self.password, dsn)
        self.cursor = self.connection.cursor()
        
    def get_table_count(self):
        """获取Oracle数据库中的表数量"""
        self.cursor.execute("""
            SELECT COUNT(*) 
            FROM all_tables 
            WHERE owner = :owner
        """, owner=self.username.upper())
        
        result = self.cursor.fetchone()
        table_count = result[0] if result else 0
        
        self.cursor.close()
        self.connection.close()
        return table_count
    
    def get_tables(self):
        """获取Oracle数据库中的所有表"""
        try:
            self.connect()
            self.cursor.execute("""
                SELECT 
                    TABLE_NAME as name,
                    COMMENTS as description,
                    NUM_ROWS as row_count
                FROM all_tables t
                LEFT JOIN all_tab_comments c ON t.TABLE_NAME = c.TABLE_NAME AND t.OWNER = c.OWNER
                WHERE t.OWNER = :owner
                ORDER BY TABLE_NAME
            """, owner=self.username.upper())
            
            columns = [col[0] for col in self.cursor.description]
            tables = []
            
            for row in self.cursor.fetchall():
                table_data = dict(zip(columns, row))
                # 如果没有描述，使用空字符串
                if table_data.get('description') is None:
                    table_data['description'] = ''
                tables.append(table_data)
            
            return tables
            
        except Exception as e:
            logger.error(f"获取表列表失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
    
    def get_table_schema(self, table_name):
        """获取Oracle表的结构"""
        try:
            self.connect()
            
            # 获取表的列信息
            self.cursor.execute("""
                SELECT 
                    c.COLUMN_NAME as column_name,
                    c.DATA_TYPE as data_type,
                    DECODE(c.NULLABLE, 'Y', 1, 0) as is_nullable,
                    DECODE(pk.COLUMN_NAME, NULL, 0, 1) as is_primary_key,
                    c.DATA_DEFAULT as default_value,
                    cc.COMMENTS as description
                FROM all_tab_columns c
                LEFT JOIN (
                    SELECT col.TABLE_NAME, col.COLUMN_NAME
                    FROM all_constraints cons, all_cons_columns col
                    WHERE cons.CONSTRAINT_TYPE = 'P'
                    AND cons.CONSTRAINT_NAME = col.CONSTRAINT_NAME
                    AND cons.OWNER = col.OWNER
                    AND cons.OWNER = :owner
                ) pk ON c.TABLE_NAME = pk.TABLE_NAME AND c.COLUMN_NAME = pk.COLUMN_NAME
                LEFT JOIN all_col_comments cc ON c.TABLE_NAME = cc.TABLE_NAME AND c.COLUMN_NAME = cc.COLUMN_NAME AND c.OWNER = cc.OWNER
                WHERE c.TABLE_NAME = :table_name
                AND c.OWNER = :owner
                ORDER BY c.COLUMN_ID
            """, owner=self.username.upper(), table_name=table_name.upper())
            
            columns = [col[0] for col in self.cursor.description]
            schema = []
            
            for row in self.cursor.fetchall():
                column_data = dict(zip(columns, row))
                # 转换布尔值
                column_data['is_nullable'] = bool(column_data['is_nullable'])
                column_data['is_primary_key'] = bool(column_data['is_primary_key'])
                # 如果没有描述，使用空字符串
                if column_data.get('description') is None:
                    column_data['description'] = ''
                schema.append(column_data)
            
            return schema
            
        except Exception as e:
            logger.error(f"获取表结构失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()
    
    def get_sample_data(self, table_name, limit=10):
        """获取Oracle表的样例数据"""
        try:
            self.connect()
            
            # 查询样例数据
            self.cursor.execute(f"SELECT * FROM \"{self.username.upper()}\".\"{table_name.upper()}\" WHERE ROWNUM <= {int(limit)}")
            
            # 获取列名
            columns = [col[0] for col in self.cursor.description]
            
            # 构造结果
            result = []
            for row in self.cursor.fetchall():
                row_dict = {}
                for i, value in enumerate(row):
                    # 处理特殊类型
                    if hasattr(value, 'isoformat'):  # 日期时间类型
                        row_dict[columns[i]] = value.isoformat()
                    elif isinstance(value, (bytes, bytearray)):
                        row_dict[columns[i]] = value.decode('utf-8', errors='replace')
                    else:
                        row_dict[columns[i]] = value
                result.append(row_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"获取样例数据失败: {str(e)}")
            raise
        finally:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
            if hasattr(self, 'connection') and self.connection:
                self.connection.close()


# 数据库连接器工厂类
class ConnectorFactory:
    """数据库连接器工厂，根据数据库类型创建对应的连接器"""
    
    @staticmethod
    def create_connector(db_type, host, port, database, username, password):
        """
        创建数据库连接器
        
        Args:
            db_type: 数据库类型，如mysql, postgresql, sqlserver, oracle
            host: 数据库主机地址
            port: 数据库端口
            database: 数据库名称
            username: 用户名
            password: 密码
            
        Returns:
            数据库连接器实例
        """
        db_type = db_type.lower()
        
        if db_type == 'mysql':
            return MySQLConnector(host, port, database, username, password)
        elif db_type == 'postgresql' or db_type == 'kingbase':
            return PostgreSQLConnector(host, port, database, username, password)
        elif db_type == 'sqlserver':
            return SQLServerConnector(host, port, database, username, password)
        elif db_type == 'oracle':
            return OracleConnector(host, port, database, username, password)
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}") 