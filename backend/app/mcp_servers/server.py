"""
MCP服务器主入口
提供数据库连接和查询服务以及其他辅助功能
"""

import json
import logging
import sys
import os
from typing import Dict, Any, Optional, List, Union

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 导入MySQL MCP服务
from backend.app.mcp_servers.mysql.mcp_server import (
    get_database_metadata as mysql_get_database_metadata,
    get_sample_data as mysql_get_sample_data,
    execute_readonly_query as mysql_execute_readonly_query
)

# 导入时间MCP服务
from backend.app.mcp_servers.time.mcp_server import (
    mcp_time_server_get_current_time,
    mcp_time_server_list_available_timezones
)

# TODO: 导入其他数据库类型的MCP服务

class MCPServer:
    """MCP服务器入口，路由不同数据源的请求到对应的处理器"""
    
    # 支持的数据源类型
    SUPPORTED_DATASOURCES = {
        'mysql': {
            'get_database_metadata': mysql_get_database_metadata,
            'get_sample_data': mysql_get_sample_data,
            'execute_readonly_query': mysql_execute_readonly_query
        },
        # TODO: 添加其他数据库类型支持
    }
    
    @staticmethod
    def get_database_metadata(host: str, user: str, password: str, database: str, port: int, ds_type: str) -> Dict[str, Any]:
        """
        获取数据库元数据
        
        Args:
            host: 数据库主机地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
            port: 数据库端口
            ds_type: 数据源类型
            
        Returns:
            数据库元数据信息
        """
        ds_type = ds_type.lower()
        if ds_type not in MCPServer.SUPPORTED_DATASOURCES:
            raise ValueError(f"不支持的数据源类型: {ds_type}")
        
        # 调用对应数据源类型的处理函数
        handler = MCPServer.SUPPORTED_DATASOURCES[ds_type]['get_database_metadata']
        return handler(host, user, password, database, port)
    
    @staticmethod
    def get_sample_data(host: str, user: str, password: str, database: str, port: int, ds_type: str, limit: int = 3) -> Dict[str, Any]:
        """
        获取数据库表样例数据
        
        Args:
            host: 数据库主机地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
            port: 数据库端口
            ds_type: 数据源类型
            limit: 每个表返回的最大行数
            
        Returns:
            表样例数据
        """
        ds_type = ds_type.lower()
        if ds_type not in MCPServer.SUPPORTED_DATASOURCES:
            raise ValueError(f"不支持的数据源类型: {ds_type}")
        
        # 调用对应数据源类型的处理函数
        handler = MCPServer.SUPPORTED_DATASOURCES[ds_type]['get_sample_data']
        return handler(host, user, password, database, port, limit)
    
    @staticmethod
    def execute_readonly_query(host: str, user: str, password: str, database: str, port: int, ds_type: str, query: str, max_rows: int = 100) -> Dict[str, Any]:
        """
        执行只读SQL查询
        
        Args:
            host: 数据库主机地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
            port: 数据库端口
            ds_type: 数据源类型
            query: SQL查询语句
            max_rows: 返回的最大行数
            
        Returns:
            查询结果
        """
        ds_type = ds_type.lower()
        if ds_type not in MCPServer.SUPPORTED_DATASOURCES:
            raise ValueError(f"不支持的数据源类型: {ds_type}")
        
        # 调用对应数据源类型的处理函数
        handler = MCPServer.SUPPORTED_DATASOURCES[ds_type]['execute_readonly_query']
        return handler(host, user, password, database, port, query, max_rows)


# MCP工具接口定义 - MySQL数据库查询工具
def mcp_mysql_query_get_database_metadata(host: str, user: str, password: str, database: str, port: int) -> str:
    """
    获取所有数据库的元数据信息，包括表名、字段名、字段注释、字段类型、字段长度、是否为空、是否主键、外键、索引
    
    参数:
        host: 数据库主机地址
        user: 数据库用户名
        password: 数据库密码
        database: 要连接的特定数据库名称
        port: 数据库端口
        
    返回:
        包含所有数据库元数据信息的字符串，格式化为便于阅读的结构
    """
    try:
        result = MCPServer.get_database_metadata(host, user, password, database, port, 'mysql')
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"获取数据库元数据失败: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def mcp_mysql_query_get_sample_data(host: str, user: str, password: str, database: str, port: int, limit: int = 3) -> str:
    """
    获取所有数据库每个表的样例数据（默认最多3条）
    
    参数:
        host: 数据库主机地址
        user: 数据库用户名
        password: 数据库密码
        database: 要连接的特定数据库名称
        port: 数据库端口
        limit: 每个表获取的最大样例数据条数，默认为3
        
    返回:
        包含所有表样例数据的字符串，格式化为便于阅读的结构
    """
    try:
        result = MCPServer.get_sample_data(host, user, password, database, port, 'mysql', limit)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"获取样例数据失败: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def mcp_mysql_query_execute_readonly_query(host: str, user: str, password: str, database: str, port: int, query: str, max_rows: int = 100) -> str:
    """
    在只读事务中执行自定义SQL查询，确保查询不会修改数据库
    
    参数:
        host: 数据库主机地址
        user: 数据库用户名
        password: 数据库密码
        database: 要连接的特定数据库名称
        port: 数据库端口
        query: 要执行的SQL查询语句
        max_rows: 返回的最大行数，默认为100
        
    返回:
        查询结果的字符串表示，格式化为便于阅读的结构
    """
    try:
        result = MCPServer.execute_readonly_query(host, user, password, database, port, 'mysql', query, max_rows)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"执行查询失败: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False) 

# 导出时间服务API
# 这两个函数已经在time/mcp_server.py中定义，这里直接从那里导入使用 