"""
数据源管理相关的API视图
"""

from flask import request, jsonify, current_app
import logging
from . import datasources_bp
from ..services.datasource_service import DataSourceService
from ..services import datasource_service
from ..models.datasource import DataSource
from ..utils.encryption import decrypt_password
from ..services.db_connector import ConnectorFactory

@datasources_bp.route('/list', methods=['GET'])
def get_datasources():
    """获取所有数据源列表"""
    try:
        # 获取所有数据源
        success, datasources, error = DataSourceService.get_all_datasources()
        
        if not success:
            return jsonify({
                'success': False,
                'error': error
            }), 500
        
        # 直接返回数据源列表，to_dict方法已经添加了status信息
        return jsonify(datasources), 200
    
    except Exception as e:
        logging.error(f"获取数据源列表时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"服务器错误: {str(e)}"
        }), 500

@datasources_bp.route('/<int:datasource_id>', methods=['GET'])
def get_datasource(datasource_id):
    """获取单个数据源详情"""
    success, datasource, error = DataSourceService.get_datasource_by_id(datasource_id)
    if success:
        # 直接返回数据源，to_dict方法已经添加了status信息
        return jsonify({
            'status': 'success',
            'data': datasource
        }), 200
    else:
        status_code = 404 if "不存在" in error else 500
        return jsonify({
            'status': 'error',
            'message': error
        }), status_code

@datasources_bp.route('/', methods=['POST'])
def create_datasource():
    """创建新的数据源"""
    data = request.json
    success, datasource, error = DataSourceService.create_datasource(data)
    if success:
        return jsonify({
            'status': 'success',
            'message': '数据源创建成功',
            'data': datasource
        }), 201
    else:
        return jsonify({
            'status': 'error',
            'message': error
        }), 400 if "缺少必要字段" in error else 500

@datasources_bp.route('/<int:datasource_id>', methods=['PUT'])
def update_datasource(datasource_id):
    """更新数据源信息"""
    data = request.json
    success, datasource, error = DataSourceService.update_datasource(datasource_id, data)
    if success:
        return jsonify({
            'status': 'success',
            'message': '数据源更新成功',
            'data': datasource
        }), 200
    else:
        status_code = 404 if "不存在" in error else 500
        return jsonify({
            'status': 'error',
            'message': error
        }), status_code

@datasources_bp.route('/<int:datasource_id>', methods=['DELETE'])
def delete_datasource(datasource_id):
    """删除数据源"""
    success, error = DataSourceService.delete_datasource(datasource_id)
    if success:
        return jsonify({
            'status': 'success',
            'message': '数据源删除成功'
        }), 200
    else:
        status_code = 404 if "不存在" in error else 500
        return jsonify({
            'status': 'error',
            'message': error
        }), status_code

@datasources_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """测试数据源连接"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': '未提供数据源信息'
            }), 400
        
        # 调用服务层测试连接
        result = DataSourceService.test_connection(data)
        
        # 返回结果，无论成功或失败
        return jsonify(result), 200
    
    except Exception as e:
        logging.error(f"测试连接时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"服务器错误: {str(e)}",
            'details': {
                'original_error': str(e),
                'error_type': 'server_error'
            }
        }), 500

@datasources_bp.route('/<int:datasource_id>/tables', methods=['GET'])
def get_tables(datasource_id):
    """获取数据源中的所有表"""
    try:
        # 获取数据源信息
        datasource = DataSource.query.get(datasource_id)
        if not datasource:
            return jsonify({
                'success': False,
                'error': f'数据源ID {datasource_id} 不存在'
            }), 404
        
        # 获取数据库连接信息
        try:
            password = decrypt_password(datasource.password)
        except Exception as e:
            logging.error(f"密码解密失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"密码解密失败，无法连接到数据源"
            }), 500
        
        # 创建连接器
        connector = ConnectorFactory.create_connector(
            datasource.ds_type,
            datasource.host,
            datasource.port,
            datasource.database,
            datasource.username,
            password
        )
        
        # 获取所有表
        tables = connector.get_tables()
        
        # 返回表列表
        return jsonify({
            'success': True,
            'data': tables
        }), 200
    
    except Exception as e:
        logging.error(f"获取表列表时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"服务器错误: {str(e)}"
        }), 500

@datasources_bp.route('/<int:datasource_id>/schema', methods=['GET'])
def get_table_schema(datasource_id):
    """获取数据源中指定表的结构"""
    try:
        # 获取表名参数
        table_name = request.args.get('table')
        if not table_name:
            return jsonify({
                'success': False,
                'error': '未提供表名'
            }), 400
        
        # 获取数据源信息
        datasource = DataSource.query.get(datasource_id)
        if not datasource:
            return jsonify({
                'success': False,
                'error': f'数据源ID {datasource_id} 不存在'
            }), 404
        
        # 获取数据库连接信息
        try:
            password = decrypt_password(datasource.password)
        except Exception as e:
            logging.error(f"密码解密失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"密码解密失败，无法连接到数据源"
            }), 500
        
        # 创建连接器
        connector = ConnectorFactory.create_connector(
            datasource.ds_type,
            datasource.host,
            datasource.port,
            datasource.database,
            datasource.username,
            password
        )
        
        # 获取表结构
        schema = connector.get_table_schema(table_name)
        
        # 返回表结构
        return jsonify({
            'success': True,
            'data': schema
        }), 200
    
    except Exception as e:
        logging.error(f"获取表结构时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"服务器错误: {str(e)}"
        }), 500

@datasources_bp.route('/<int:datasource_id>/sample', methods=['GET'])
def get_sample_data(datasource_id):
    """获取数据源中指定表的样例数据"""
    try:
        # 获取表名和限制行数参数
        table_name = request.args.get('table')
        limit = request.args.get('limit', default=10, type=int)
        
        if not table_name:
            return jsonify({
                'success': False,
                'error': '未提供表名'
            }), 400
        
        # 获取数据源信息
        datasource = DataSource.query.get(datasource_id)
        if not datasource:
            return jsonify({
                'success': False,
                'error': f'数据源ID {datasource_id} 不存在'
            }), 404
        
        # 获取数据库连接信息
        try:
            password = decrypt_password(datasource.password)
        except Exception as e:
            logging.error(f"密码解密失败: {str(e)}")
            return jsonify({
                'success': False,
                'error': f"密码解密失败，无法连接到数据源"
            }), 500
        
        # 创建连接器
        connector = ConnectorFactory.create_connector(
            datasource.ds_type,
            datasource.host,
            datasource.port,
            datasource.database,
            datasource.username,
            password
        )
        
        # 获取样例数据
        sample_data = connector.get_sample_data(table_name, limit)
        
        # 返回样例数据
        return jsonify({
            'success': True,
            'data': sample_data
        }), 200
    
    except Exception as e:
        logging.error(f"获取样例数据时发生错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"服务器错误: {str(e)}"
        }), 500 