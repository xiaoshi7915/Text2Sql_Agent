"""
MCP API路由配置
用于注册MCP服务的API端点
"""

import json
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

# 导入MCP服务
from backend.app.mcp_servers.server import (
    mcp_mysql_query_get_database_metadata,
    mcp_mysql_query_get_sample_data,
    mcp_mysql_query_execute_readonly_query,
    mcp_time_server_get_current_time,
    mcp_time_server_list_available_timezones
)

# 创建蓝图
mcp_bp = Blueprint('mcp', __name__, url_prefix='/api/mcp')

# ---------------------- MySQL服务接口 ----------------------

@mcp_bp.route('/mysql/metadata', methods=['POST'])
@cross_origin()
def mysql_metadata():
    """获取MySQL数据库元数据"""
    try:
        data = request.get_json()
        # 验证必要参数
        required_params = ['host', 'user', 'password', 'database', 'port']
        for param in required_params:
            if param not in data:
                return jsonify({"error": f"缺少必要参数: {param}"}), 400
        
        # 调用MCP服务
        result = mcp_mysql_query_get_database_metadata(
            host=data['host'],
            user=data['user'],
            password=data['password'],
            database=data['database'],
            port=data['port']
        )
        
        # 解析JSON字符串为对象
        return jsonify(json.loads(result)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/mysql/sample', methods=['POST'])
@cross_origin()
def mysql_sample():
    """获取MySQL数据库表样例数据"""
    try:
        data = request.get_json()
        # 验证必要参数
        required_params = ['host', 'user', 'password', 'database', 'port']
        for param in required_params:
            if param not in data:
                return jsonify({"error": f"缺少必要参数: {param}"}), 400
        
        # 获取可选参数
        limit = data.get('limit', 3)
        
        # 调用MCP服务
        result = mcp_mysql_query_get_sample_data(
            host=data['host'],
            user=data['user'],
            password=data['password'],
            database=data['database'],
            port=data['port'],
            limit=limit
        )
        
        # 解析JSON字符串为对象
        return jsonify(json.loads(result)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/mysql/query', methods=['POST'])
@cross_origin()
def mysql_query():
    """执行MySQL只读查询"""
    try:
        data = request.get_json()
        # 验证必要参数
        required_params = ['host', 'user', 'password', 'database', 'port', 'query']
        for param in required_params:
            if param not in data:
                return jsonify({"error": f"缺少必要参数: {param}"}), 400
        
        # 获取可选参数
        max_rows = data.get('max_rows', 100)
        
        # 调用MCP服务
        result = mcp_mysql_query_execute_readonly_query(
            host=data['host'],
            user=data['user'],
            password=data['password'],
            database=data['database'],
            port=data['port'],
            query=data['query'],
            max_rows=max_rows
        )
        
        # 解析JSON字符串为对象
        return jsonify(json.loads(result)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------- 时间服务接口 ----------------------

@mcp_bp.route('/time/current', methods=['GET', 'POST'])
@cross_origin()
def time_current():
    """获取当前时间"""
    try:
        # 获取时区参数，支持GET和POST请求
        if request.method == 'GET':
            timezone = request.args.get('timezone', 'UTC')
        else:
            data = request.get_json() or {}
            timezone = data.get('timezone', 'UTC')
        
        # 调用MCP服务
        result = mcp_time_server_get_current_time(timezone=timezone)
        
        # 解析JSON字符串为对象
        return jsonify(json.loads(result)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mcp_bp.route('/time/timezones', methods=['GET', 'POST'])
@cross_origin()
def time_timezones():
    """获取可用时区列表"""
    try:
        # 获取区域参数，支持GET和POST请求
        if request.method == 'GET':
            region = request.args.get('region')
        else:
            data = request.get_json() or {}
            region = data.get('region')
        
        # 调用MCP服务
        result = mcp_time_server_list_available_timezones(region=region)
        
        # 解析JSON字符串为对象
        return jsonify(json.loads(result)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 注册其他MCP服务的API端点
# TODO: 添加更多数据库类型的API端点 