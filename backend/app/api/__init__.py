# API 模块初始化文件 
from flask import Blueprint, redirect, url_for

# 创建数据源蓝图 (新路径)
datasources_bp = Blueprint('datasources', __name__, url_prefix='/api/datasources')

# 注册蓝图内的路由
from . import datasources

# 创建兼容性蓝图 (旧路径)
datasource_compat_bp = Blueprint('datasource_compat', __name__, url_prefix='/api/datasource')

# 为旧路径添加重定向
@datasource_compat_bp.route('/list', methods=['GET'])
def redirect_list():
    """将旧路径重定向到新路径"""
    return redirect('/api/datasources/list', code=302)

@datasource_compat_bp.route('/<int:datasource_id>', methods=['GET'])
def redirect_get(datasource_id):
    """将旧路径重定向到新路径"""
    return redirect(f'/api/datasources/{datasource_id}', code=302)

@datasource_compat_bp.route('/', methods=['POST'])
def redirect_create():
    """将旧路径重定向到新路径"""
    return redirect('/api/datasources/', code=307)  # 307保留POST请求

@datasource_compat_bp.route('/<int:datasource_id>', methods=['PUT'])
def redirect_update(datasource_id):
    """将旧路径重定向到新路径"""
    return redirect(f'/api/datasources/{datasource_id}', code=307)  # 307保留PUT请求

@datasource_compat_bp.route('/<int:datasource_id>', methods=['DELETE'])
def redirect_delete(datasource_id):
    """将旧路径重定向到新路径"""
    return redirect(f'/api/datasources/{datasource_id}', code=307)  # 307保留DELETE请求

@datasource_compat_bp.route('/test-connection', methods=['POST'])
def redirect_test_connection():
    """将旧路径重定向到新路径"""
    return redirect('/api/datasources/test-connection', code=307)  # 307保留POST请求

# 创建模型蓝图
from .models import model_bp

# 不要重复导入同样的功能
# 移除冗余文件引用
# 注释掉重复的导入，解决表重复定义问题
# from . import datasource 