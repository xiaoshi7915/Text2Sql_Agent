"""
时间服务MCP工具模块
提供获取当前时间和时区功能
"""

from flask import jsonify, request
from . import mcp_bp
import pytz
from datetime import datetime

@mcp_bp.route('/time_server/get_current_time', methods=['POST'])
def get_current_time():
    """
    获取指定时区的当前时间
    
    参数:
        timezone: 时区名称，默认为UTC，例如：Asia/Shanghai, America/New_York
                 完整的时区列表可在pytz.all_timezones中查看
    
    返回:
        包含当前时间信息的字符串
    """
    try:
        # 获取请求数据
        data = request.json
        timezone = data.get('timezone', 'UTC')
        
        # 验证时区是否有效
        if timezone not in pytz.all_timezones:
            return jsonify({
                'error': f'无效的时区: {timezone}',
                'suggestion': '请使用list_available_timezones获取有效时区列表'
            }), 400
        
        # 获取指定时区的当前时间
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        # 格式化时间
        formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S %Z%z')
        
        # 构建响应
        response = {
            'current_time': formatted_time,
            'timezone': timezone,
            'year': current_time.year,
            'month': current_time.month,
            'day': current_time.day,
            'hour': current_time.hour,
            'minute': current_time.minute,
            'second': current_time.second,
            'weekday': current_time.strftime('%A'),
            'iso_format': current_time.isoformat(),
            'unix_timestamp': int(current_time.timestamp())
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mcp_bp.route('/time_server/list_available_timezones', methods=['POST'])
def list_available_timezones():
    """
    列出可用的时区
    
    参数:
        region: 可选，筛选特定区域的时区，例如：Asia, America, Europe
    
    返回:
        可用时区列表
    """
    try:
        # 获取请求数据
        data = request.json
        region = data.get('region')
        
        # 获取所有时区
        all_timezones = pytz.all_timezones
        
        # 如果指定了区域，筛选该区域的时区
        if region:
            filtered_timezones = [tz for tz in all_timezones if tz.startswith(region)]
            if not filtered_timezones:
                return jsonify({
                    'error': f'未找到区域: {region}的时区',
                    'available_regions': sorted(set(tz.split('/')[0] for tz in all_timezones if '/' in tz))
                }), 400
            return jsonify(filtered_timezones)
        
        # 按地区组织时区
        timezones_by_region = {}
        for tz in all_timezones:
            if '/' in tz:
                region, city = tz.split('/', 1)
                if region not in timezones_by_region:
                    timezones_by_region[region] = []
                timezones_by_region[region].append(tz)
            else:
                if 'Other' not in timezones_by_region:
                    timezones_by_region['Other'] = []
                timezones_by_region['Other'].append(tz)
        
        return jsonify({
            'regions': sorted(timezones_by_region.keys()),
            'timezones_by_region': timezones_by_region,
            'all_timezones': all_timezones
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 