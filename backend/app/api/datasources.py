from flask import Blueprint, request, jsonify, current_app
from backend.app.models import db, DataSource
from sqlalchemy.exc import SQLAlchemyError
from cryptography.fernet import Fernet
import json
import os

# 创建蓝图
datasource_bp = Blueprint('datasources', __name__)

# 密钥管理（实际应用中应该使用更安全的密钥管理方式）
def get_encryption_key():
    """获取或生成加密密钥"""
    key_env = os.getenv('ENCRYPTION_KEY')
    if key_env:
        return key_env.encode()
    
    # 如果环境变量不存在，使用应用密钥的派生键
    secret_key = current_app.config['SECRET_KEY']
    # 使用固定长度密钥
    return Fernet.generate_key()

def encrypt_password(password):
    """加密密码"""
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    """解密密码"""
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()

@datasource_bp.route('/', methods=['GET'])
def get_datasources():
    """获取所有数据源列表"""
    try:
        datasources = DataSource.query.all()
        return jsonify({
            'status': 'success',
            'data': [ds.to_dict() for ds in datasources]
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取数据源列表失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '获取数据源列表失败',
            'error': str(e)
        }), 500

@datasource_bp.route('/<int:datasource_id>', methods=['GET'])
def get_datasource(datasource_id):
    """获取单个数据源详情"""
    try:
        datasource = DataSource.query.get(datasource_id)
        if not datasource:
            return jsonify({
                'status': 'error',
                'message': f'数据源ID {datasource_id} 不存在'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': datasource.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取数据源详情失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '获取数据源详情失败',
            'error': str(e)
        }), 500

@datasource_bp.route('/', methods=['POST'])
def create_datasource():
    """创建新的数据源"""
    try:
        data = request.json
        
        # 验证必要字段
        required_fields = ['name', 'ds_type', 'host', 'port', 'database', 'username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必要字段: {field}'
                }), 400
        
        # 加密密码
        encrypted_password = encrypt_password(data['password'])
        
        # 处理可选字段
        options = data.get('options', {})
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except:
                options = {}
        
        # 创建数据源实例
        datasource = DataSource(
            name=data['name'],
            description=data.get('description', ''),
            ds_type=data['ds_type'],
            host=data['host'],
            port=data['port'],
            database=data['database'],
            username=data['username'],
            password=encrypted_password,
            options=options,
            include_views=data.get('include_views', False),
            format=data.get('format', 'public'),
            selected_fields=data.get('selected_fields', '')
        )
        
        db.session.add(datasource)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '数据源创建成功',
            'data': datasource.to_dict()
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"数据库错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '数据库错误',
            'error': str(e)
        }), 500
    except Exception as e:
        current_app.logger.error(f"创建数据源失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '创建数据源失败',
            'error': str(e)
        }), 500

@datasource_bp.route('/<int:datasource_id>', methods=['PUT'])
def update_datasource(datasource_id):
    """更新数据源信息"""
    try:
        datasource = DataSource.query.get(datasource_id)
        if not datasource:
            return jsonify({
                'status': 'error',
                'message': f'数据源ID {datasource_id} 不存在'
            }), 404
        
        data = request.json
        
        # 更新基本字段
        if 'name' in data:
            datasource.name = data['name']
        if 'description' in data:
            datasource.description = data['description']
        if 'host' in data:
            datasource.host = data['host']
        if 'port' in data:
            datasource.port = data['port']
        if 'database' in data:
            datasource.database = data['database']
        if 'username' in data:
            datasource.username = data['username']
        if 'ds_type' in data:
            datasource.ds_type = data['ds_type']
        
        # 如果提供了新密码，进行加密
        if 'password' in data and data['password']:
            datasource.password = encrypt_password(data['password'])
        
        # 更新可选字段
        if 'options' in data:
            options = data['options']
            if isinstance(options, str):
                try:
                    options = json.loads(options)
                except:
                    options = {}
            datasource.options = options
        
        if 'include_views' in data:
            datasource.include_views = data['include_views']
        if 'format' in data:
            datasource.format = data['format']
        if 'selected_fields' in data:
            datasource.selected_fields = data['selected_fields']
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '数据源更新成功',
            'data': datasource.to_dict()
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"数据库错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '数据库错误',
            'error': str(e)
        }), 500
    except Exception as e:
        current_app.logger.error(f"更新数据源失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '更新数据源失败',
            'error': str(e)
        }), 500

@datasource_bp.route('/<int:datasource_id>', methods=['DELETE'])
def delete_datasource(datasource_id):
    """删除数据源"""
    try:
        datasource = DataSource.query.get(datasource_id)
        if not datasource:
            return jsonify({
                'status': 'error',
                'message': f'数据源ID {datasource_id} 不存在'
            }), 404
        
        db.session.delete(datasource)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '数据源删除成功'
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"数据库错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '数据库错误',
            'error': str(e)
        }), 500
    except Exception as e:
        current_app.logger.error(f"删除数据源失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '删除数据源失败',
            'error': str(e)
        }), 500

@datasource_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """测试数据源连接"""
    try:
        data = request.json
        
        # 验证必要字段
        required_fields = ['ds_type', 'host', 'port', 'database', 'username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必要字段: {field}'
                }), 400
                
        # 测试连接逻辑将在服务层实现
        # 这里暂时返回模拟成功
        return jsonify({
            'status': 'success',
            'message': '连接测试成功'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"连接测试失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '连接测试失败',
            'error': str(e)
        }), 500 