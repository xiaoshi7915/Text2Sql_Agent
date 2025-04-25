"""
API蓝图模块
包含所有API路由和视图函数
"""

from flask import Blueprint, jsonify

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 添加一个简单的测试路由
@api_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({"message": "pong", "status": "success"}), 200

# 在最后导入视图模块，避免循环导入问题
# 从app.api中导入认证模块，不再从当前目录导入
# from . import auth  # 移除这个导入，避免冲突
from . import datasources, chat  # 导入其他模块
# 其他视图模块按需导入
# from . import datasources, models, conversations, users 