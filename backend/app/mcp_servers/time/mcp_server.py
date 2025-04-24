import datetime
import pytz
import json
from typing import Optional, List, Dict, Any

def mcp_time_server_get_current_time(timezone: str = "UTC") -> str:
    """
    获取指定时区的当前时间
    
    参数:
        timezone: 时区名称，默认为 UTC，例如：Asia/Shanghai, America/New_York
                 完整的时区列表可在 pytz.all_timezones 中查看
    
    返回:
        包含当前时间信息的字符串
    """
    try:
        # 验证时区是否有效
        if timezone not in pytz.all_timezones:
            return json.dumps({
                "error": f"无效的时区: {timezone}",
                "available_timezones": "使用 list_available_timezones 获取可用时区列表"
            }, ensure_ascii=False)
        
        # 获取指定时区的当前时间
        tz = pytz.timezone(timezone)
        current_time = datetime.datetime.now(tz)
        
        # 格式化时间信息
        result = {
            "timezone": timezone,
            "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": current_time.timestamp(),
            "iso_format": current_time.isoformat(),
            "weekday": current_time.strftime("%A"),
            "date": current_time.strftime("%Y-%m-%d"),
            "time": current_time.strftime("%H:%M:%S")
        }
        
        return json.dumps(result, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)

def mcp_time_server_list_available_timezones(region: Optional[str] = None) -> str:
    """
    列出可用的时区
    
    参数:
        region: 可选，筛选特定区域的时区，例如：Asia, America, Europe
    
    返回:
        可用时区列表
    """
    try:
        all_timezones = pytz.all_timezones
        
        # 如果指定了区域，筛选该区域的时区
        if region:
            filtered_timezones = [tz for tz in all_timezones if tz.startswith(region)]
            
            if not filtered_timezones:
                return json.dumps({
                    "error": f"找不到区域: {region}",
                    "available_regions": list(set(tz.split('/')[0] for tz in all_timezones if '/' in tz))
                }, ensure_ascii=False)
            
            result = {
                "region": region,
                "timezones": filtered_timezones,
                "count": len(filtered_timezones)
            }
        else:
            # 按区域分组时区
            grouped_timezones = {}
            for tz in all_timezones:
                if '/' in tz:
                    region_name = tz.split('/')[0]
                    if region_name not in grouped_timezones:
                        grouped_timezones[region_name] = []
                    grouped_timezones[region_name].append(tz)
                else:
                    if "Other" not in grouped_timezones:
                        grouped_timezones["Other"] = []
                    grouped_timezones["Other"].append(tz)
            
            result = {
                "regions": list(grouped_timezones.keys()),
                "total_count": len(all_timezones),
                "grouped_timezones": grouped_timezones
            }
        
        return json.dumps(result, ensure_ascii=False)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False) 