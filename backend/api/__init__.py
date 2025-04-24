"""
API蓝图模块
包含所有API路由和视图函数
"""

from flask import Blueprint

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# 在最后导入视图模块，避免循环导入问题
from . import auth  # 先导入auth模块
from . import datasources, chat  # 导入其他模块
# 其他视图模块按需导入
# from . import datasources, models, conversations, users 