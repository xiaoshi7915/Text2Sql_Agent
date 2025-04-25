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