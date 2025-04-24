"""
数据源管理相关的API视图
"""

from flask import request, jsonify
from . import api_bp
# 直接从app导入db实例
from app import db
from app.models.datasource import DataSource

@api_bp.route('/datasource/list', methods=['GET'])
def get_datasources():
    """
    获取数据源列表API
    """
    # 获取所有数据源
    datasources = DataSource.query.all()
    return jsonify({
        'status': 'success',
        'data': [ds.to_dict() for ds in datasources]
    }) 