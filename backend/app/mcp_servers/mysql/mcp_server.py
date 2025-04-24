import json
import logging
import pymysql
import sqlalchemy
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from typing import Dict, List, Optional, Any, Union

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MySQLMCPServer:
    """MySQL数据库MCP服务器，提供元数据管理和查询功能"""
    
    def __init__(self, connection_params: Dict[str, Any]):
        """
        初始化MySQL MCP服务
        
        Args:
            connection_params: 数据库连接参数，包含host, port, user, password, database等
        """
        self.connection_params = connection_params
        self.engine = None
        self.inspector = None
        self.connect()
    
    def connect(self) -> None:
        """建立数据库连接"""
        try:
            host = self.connection_params.get('host', 'localhost')
            port = self.connection_params.get('port', 3306)
            user = self.connection_params.get('user')
            password = self.connection_params.get('password')
            database = self.connection_params.get('database')
            
            if not all([user, password, database]):
                raise ValueError("缺少必要的连接参数: 用户名、密码或数据库名")
            
            # 构建连接URL
            connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
            self.engine = create_engine(connection_url)
            self.inspector = inspect(self.engine)
            
            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                
            logger.info(f"成功连接到MySQL数据库: {host}:{port}/{database}")
            
        except SQLAlchemyError as e:
            logger.error(f"连接MySQL数据库失败: {str(e)}")
            raise
    
    def get_database_metadata(self) -> Dict[str, Any]:
        """
        获取数据库元数据信息，包括表名、字段信息等
        
        Returns:
            数据库元数据信息的字典
        """
        try:
            if not self.engine or not self.inspector:
                self.connect()
            
            schema = self.connection_params.get('database')
            
            # 获取所有表名
            tables = self.inspector.get_table_names(schema=schema)
            
            # 如果指定了包含视图，也获取视图
            include_views = self.connection_params.get('include_views', False)
            views = []
            if include_views:
                try:
                    views = self.inspector.get_view_names(schema=schema)
                except:
                    logger.warning("获取视图失败，可能数据库不支持")
            
            result = {
                "tables": {},
                "views": {},
                "database": schema
            }
            
            # 获取表结构
            for table in tables:
                columns = self.inspector.get_columns(table, schema=schema)
                primary_keys = self.inspector.get_pk_constraint(table, schema=schema).get('constrained_columns', [])
                
                # 获取外键
                foreign_keys = []
                try:
                    fks = self.inspector.get_foreign_keys(table, schema=schema)
                    for fk in fks:
                        foreign_keys.append({
                            'constrained_columns': fk.get('constrained_columns', []),
                            'referred_table': fk.get('referred_table', ''),
                            'referred_columns': fk.get('referred_columns', [])
                        })
                except:
                    logger.warning(f"获取表 {table} 的外键信息失败")
                
                # 获取索引
                indices = []
                try:
                    for index in self.inspector.get_indexes(table, schema=schema):
                        indices.append({
                            'name': index.get('name', ''),
                            'columns': index.get('column_names', []),
                            'unique': index.get('unique', False)
                        })
                except:
                    logger.warning(f"获取表 {table} 的索引信息失败")
                
                # 构建列信息
                columns_info = []
                for column in columns:
                    column_info = {
                        'name': column['name'],
                        'type': str(column['type']),
                        'nullable': column.get('nullable', True),
                        'default': column.get('default', None),
                        'primary_key': column['name'] in primary_keys,
                        'comment': column.get('comment', '')
                    }
                    columns_info.append(column_info)
                
                result['tables'][table] = {
                    'columns': columns_info,
                    'primary_keys': primary_keys,
                    'foreign_keys': foreign_keys,
                    'indices': indices
                }
            
            # 获取视图结构
            for view in views:
                columns = self.inspector.get_columns(view, schema=schema)
                
                # 构建视图列信息
                columns_info = []
                for column in columns:
                    column_info = {
                        'name': column['name'],
                        'type': str(column['type']),
                        'nullable': column.get('nullable', True),
                        'comment': column.get('comment', '')
                    }
                    columns_info.append(column_info)
                
                result['views'][view] = {
                    'columns': columns_info
                }
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"获取数据库元数据失败: {str(e)}")
            raise
    
    def get_sample_data(self, limit: int = 3) -> Dict[str, Any]:
        """
        获取数据库所有表的样例数据
        
        Args:
            limit: 每个表返回的最大行数
            
        Returns:
            包含所有表样例数据的字典
        """
        try:
            if not self.engine:
                self.connect()
            
            schema = self.connection_params.get('database')
            
            # 获取所有表名
            tables = self.inspector.get_table_names(schema=schema)
            
            result = {}
            
            # 对每个表查询样例数据
            for table in tables:
                try:
                    query = f"SELECT * FROM `{table}` LIMIT {limit}"
                    df = pd.read_sql(query, self.engine)
                    
                    # 将DataFrame转换为字典列表
                    result[table] = json.loads(df.to_json(orient='records', date_format='iso'))
                except Exception as e:
                    logger.warning(f"获取表 {table} 的样例数据失败: {str(e)}")
                    result[table] = []
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"获取样例数据失败: {str(e)}")
            raise
    
    def execute_readonly_query(self, query: str, max_rows: int = 100) -> Dict[str, Any]:
        """
        执行只读SQL查询
        
        Args:
            query: SQL查询语句
            max_rows: 返回的最大行数
            
        Returns:
            查询结果的字典
        """
        try:
            if not self.engine:
                self.connect()
            
            # 验证查询是否为只读查询
            if not self._is_readonly_query(query):
                raise ValueError("只允许执行SELECT查询")
            
            # 执行查询
            df = pd.read_sql(query, self.engine)
            
            # 限制返回行数
            if len(df) > max_rows:
                df = df.head(max_rows)
                truncated = True
            else:
                truncated = False
            
            # 构建结果
            result = {
                "columns": df.columns.tolist(),
                "rows": json.loads(df.to_json(orient='records', date_format='iso')),
                "truncated": truncated,
                "total_rows": len(df)
            }
            
            return result
            
        except SQLAlchemyError as e:
            logger.error(f"执行查询失败: {str(e)}")
            raise
    
    def _is_readonly_query(self, query: str) -> bool:
        """
        检查查询是否为只读查询
        
        Args:
            query: SQL查询语句
            
        Returns:
            如果是只读查询则返回True，否则返回False
        """
        # 简化的检查，实际应用中可能需要更复杂的解析
        query = query.strip().lower()
        
        # 检查是否以SELECT开头
        if query.startswith('select'):
            # 检查是否包含数据修改关键字
            danger_keywords = ['insert', 'update', 'delete', 'drop', 'alter', 'truncate', 'create', 'replace']
            for keyword in danger_keywords:
                if f' {keyword} ' in f' {query} ':
                    return False
            return True
        
        return False
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
            logger.info("数据库连接已关闭")
            
    def __del__(self):
        """析构函数，确保连接被关闭"""
        self.close()


# MCP工具函数定义
def get_database_metadata(host: str, user: str, password: str, database: str, port: int) -> Dict[str, Any]:
    """
    MCP工具：获取数据库元数据
    
    Args:
        host: 数据库主机地址
        user: 数据库用户名
        password: 数据库密码
        database: 数据库名称
        port: 数据库端口
        
    Returns:
        数据库元数据信息
    """
    connection_params = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }
    
    server = MySQLMCPServer(connection_params)
    result = server.get_database_metadata()
    server.close()
    
    return result

def get_sample_data(host: str, user: str, password: str, database: str, port: int, limit: int = 3) -> Dict[str, Any]:
    """
    MCP工具：获取数据库表样例数据
    
    Args:
        host: 数据库主机地址
        user: 数据库用户名
        password: 数据库密码
        database: 数据库名称
        port: 数据库端口
        limit: 每个表返回的最大行数
        
    Returns:
        表样例数据
    """
    connection_params = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }
    
    server = MySQLMCPServer(connection_params)
    result = server.get_sample_data(limit)
    server.close()
    
    return result

def execute_readonly_query(host: str, user: str, password: str, database: str, port: int, query: str, max_rows: int = 100) -> Dict[str, Any]:
    """
    MCP工具：执行只读SQL查询
    
    Args:
        host: 数据库主机地址
        user: 数据库用户名
        password: 数据库密码
        database: 数据库名称
        port: 数据库端口
        query: SQL查询语句
        max_rows: 返回的最大行数
        
    Returns:
        查询结果
    """
    connection_params = {
        'host': host,
        'port': port,
        'user': user,
        'password': password,
        'database': database
    }
    
    server = MySQLMCPServer(connection_params)
    result = server.execute_readonly_query(query, max_rows)
    server.close()
    
    return result 