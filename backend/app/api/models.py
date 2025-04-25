from flask import Blueprint, request, jsonify, current_app
from app.models.model import Model
from app.models import db
from sqlalchemy.exc import SQLAlchemyError
from cryptography.fernet import Fernet
import os

# 创建蓝图
model_bp = Blueprint('models', __name__)

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

def encrypt_api_key(api_key):
    """加密API密钥"""
    key = get_encryption_key()
    f = Fernet(key)
    return f.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key):
    """解密API密钥"""
    key = get_encryption_key()
    f = Fernet(key)
    return f.decrypt(encrypted_api_key.encode()).decode()

@model_bp.route('/', methods=['GET'])
def get_models():
    """获取所有模型列表"""
    try:
        models = Model.query.all()
        return jsonify({
            'status': 'success',
            'data': [model.to_dict() for model in models]
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取模型列表失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '获取模型列表失败',
            'error': str(e)
        }), 500

@model_bp.route('/<int:model_id>', methods=['GET'])
def get_model(model_id):
    """获取单个模型详情"""
    try:
        model = Model.query.get(model_id)
        if not model:
            return jsonify({
                'status': 'error',
                'message': f'模型ID {model_id} 不存在'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': model.to_dict()
        }), 200
    except Exception as e:
        current_app.logger.error(f"获取模型详情失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '获取模型详情失败',
            'error': str(e)
        }), 500

@model_bp.route('/', methods=['POST'])
def create_model():
    """创建新的模型"""
    try:
        data = request.json
        
        # 验证必要字段
        required_fields = ['name', 'provider', 'model_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必要字段: {field}'
                }), 400
        
        # 如果是默认模型，先取消其他默认模型
        if data.get('is_default', False):
            default_models = Model.query.filter_by(is_default=True).all()
            for default_model in default_models:
                default_model.is_default = False
        
        # 加密API密钥
        api_key = data.get('api_key', '')
        encrypted_api_key = encrypt_api_key(api_key) if api_key else ''
        
        # 创建模型实例
        model = Model(
            name=data['name'],
            provider=data['provider'],
            model_type=data['model_type'],
            api_base=data.get('api_base', ''),
            api_key=encrypted_api_key,
            api_version=data.get('api_version', ''),
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', 4096),
            is_default=data.get('is_default', False),
            is_active=data.get('is_active', True),
            parameters=data.get('parameters', {})
        )
        
        db.session.add(model)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '模型创建成功',
            'data': model.to_dict()
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
        current_app.logger.error(f"创建模型失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '创建模型失败',
            'error': str(e)
        }), 500

@model_bp.route('/<int:model_id>', methods=['PUT'])
def update_model(model_id):
    """更新模型信息"""
    try:
        model = Model.query.get(model_id)
        if not model:
            return jsonify({
                'status': 'error',
                'message': f'模型ID {model_id} 不存在'
            }), 404
        
        data = request.json
        
        # 如果设置为默认模型，先取消其他默认模型
        if 'is_default' in data and data['is_default'] and not model.is_default:
            default_models = Model.query.filter_by(is_default=True).all()
            for default_model in default_models:
                default_model.is_default = False
        
        # 更新基本字段
        if 'name' in data:
            model.name = data['name']
        if 'provider' in data:
            model.provider = data['provider']
        if 'model_type' in data:
            model.model_type = data['model_type']
        if 'api_base' in data:
            model.api_base = data['api_base']
        if 'api_version' in data:
            model.api_version = data['api_version']
        if 'temperature' in data:
            model.temperature = data['temperature']
        if 'max_tokens' in data:
            model.max_tokens = data['max_tokens']
        if 'is_default' in data:
            model.is_default = data['is_default']
        if 'is_active' in data:
            model.is_active = data['is_active']
        if 'parameters' in data:
            model.parameters = data['parameters']
        
        # 如果提供了新API密钥，进行加密
        if 'api_key' in data and data['api_key']:
            model.api_key = encrypt_api_key(data['api_key'])
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '模型更新成功',
            'data': model.to_dict()
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
        current_app.logger.error(f"更新模型失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '更新模型失败',
            'error': str(e)
        }), 500

@model_bp.route('/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    """删除模型"""
    try:
        model = Model.query.get(model_id)
        if not model:
            return jsonify({
                'status': 'error',
                'message': f'模型ID {model_id} 不存在'
            }), 404
        
        # 检查是否有会话使用此模型
        if model.conversations:
            return jsonify({
                'status': 'error',
                'message': '无法删除已被会话使用的模型，请先删除相关会话'
            }), 400
        
        db.session.delete(model)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': '模型删除成功'
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
        current_app.logger.error(f"删除模型失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '删除模型失败',
            'error': str(e)
        }), 500

@model_bp.route('/default', methods=['GET'])
def get_default_model():
    """获取默认模型"""
    try:
        model = Model.query.filter_by(is_default=True).first()
        if not model:
            # 如果没有默认模型，返回第一个激活的模型
            model = Model.query.filter_by(is_active=True).first()
            
        if not model:
            return jsonify({
                'status': 'error',
                'message': '没有可用模型'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': model.to_dict()
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取默认模型失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '获取默认模型失败',
            'error': str(e)
        }), 500

@model_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """测试模型连接"""
    try:
        data = request.json
        
        # 验证必要字段
        required_fields = ['provider', 'model_type', 'api_key']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'缺少必要字段: {field}'
                }), 400
                
        # 调用LLM服务层实现的测试连接功能
        from app.services.llm_service import LLMService
        result = LLMService.test_connection(data)
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
        
    except Exception as e:
        current_app.logger.error(f"模型连接测试失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '模型连接测试失败',
            'error': str(e)
        }), 500 