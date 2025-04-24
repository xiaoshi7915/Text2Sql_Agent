"""
MCP蓝图模块
包含所有Model Context Protocol相关服务和工具
"""

from flask import Blueprint

mcp_bp = Blueprint('mcp', __name__)

# 导入蓝图内的视图和服务
from . import mysql_query, time_server 