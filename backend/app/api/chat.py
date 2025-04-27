from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime
import uuid
import functools

# 修改导入方式，分开导入db和模型
from app import db
from app.models.user import User
from app.models.datasource import DataSource
from app.models.model import Model
from app.models.conversation import Conversation, Message

# 创建蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# 自定义装饰器，兼容普通JWT和demo-token
def jwt_or_demo_required():
    def wrapper(fn):
        @functools.wraps(fn)
        def decorator(*args, **kwargs):
            from flask import request, current_app
            
            try:
                # 获取Authorization头
                auth_header = request.headers.get('Authorization', '')
                current_app.logger.debug(f"认证头: {auth_header}")
                
                # 特殊处理demo-token
                if 'demo-token' in auth_header:
                    current_app.logger.info("使用demo-token访问接口")
                    g.jwt_identity = 1
                    return fn(*args, **kwargs)
                
                # 尝试JWT验证
                try:
                    # 不要这样调用: jwt_required()(fn)
                    # 而是验证JWT存在并有效
                    verify_jwt_in_request()
                    # 验证成功，获取身份
                    try:
                        g.jwt_identity = get_jwt_identity()
                        current_app.logger.debug(f"JWT验证成功，用户ID: {g.jwt_identity}")
                    except Exception as e:
                        current_app.logger.error(f"获取JWT身份失败: {str(e)}")
                        g.jwt_identity = 1  # 默认使用admin用户
                    
                    # 执行原函数
                    return fn(*args, **kwargs)
                except Exception as e:
                    current_app.logger.error(f"JWT验证失败，使用默认身份: {str(e)}")
                    g.jwt_identity = 1  # 默认使用admin用户
                    return fn(*args, **kwargs)
                    
            except Exception as e:
                current_app.logger.error(f"认证处理时发生未预期的异常: {str(e)}")
                g.jwt_identity = 1  # 默认使用admin用户
                return fn(*args, **kwargs)
                
        return decorator
    return wrapper

# 自定义的get_identity函数，兼容demo-token，增强容错性
def get_identity():
    from flask import g, current_app
    try:
        if hasattr(g, 'jwt_identity'):
            user_id = g.jwt_identity
            current_app.logger.debug(f"从g对象获取用户ID: {user_id}")
            return user_id
            
        try:
            user_id = get_jwt_identity()
            current_app.logger.debug(f"从JWT获取用户ID: {user_id}")
            return user_id
        except Exception as e:
            current_app.logger.error(f"获取JWT用户ID失败: {str(e)}")
            return 1  # 默认返回admin用户ID
    except Exception as e:
        current_app.logger.error(f"获取用户ID时发生异常: {str(e)}")
        return 1  # 默认返回admin用户ID

@chat_bp.route('/sessions', methods=['GET'])
@jwt_or_demo_required()
def get_sessions():
    """获取当前用户的所有会话列表"""
    user_id = get_identity()
    
    # 获取用户的所有会话
    chats = Conversation.query.filter_by(user_id=user_id).order_by(Conversation.updated_at.desc()).all()
    
    sessions = []
    for chat in chats:
        # 获取会话关联的数据源IDs
        data_source_ids = [ds.id for ds in chat.datasources]
        
        # 构建会话信息
        session = {
            'id': chat.id,
            'title': chat.title,
            'createdAt': chat.created_at.isoformat(),
            'updatedAt': chat.updated_at.isoformat(),
            'messageCount': Message.query.filter_by(conversation_id=chat.id).count(),
            'dataSourceIds': data_source_ids,
            'modelId': chat.model_id
        }
        sessions.append(session)
    
    return jsonify({'sessions': sessions})

@chat_bp.route('/sessions', methods=['POST'])
@jwt_or_demo_required()
def create_session():
    """创建新的会话"""
    try:
        user_id = get_identity()
        
        # 获取请求参数
        request_data = request.get_json()
        if not request_data:
            current_app.logger.error(f"创建会话失败: 无效的请求数据")
            return jsonify({'message': '无效的请求数据'}), 400
            
        current_app.logger.info(f"创建会话请求数据: {request_data}")
        
        # 支持前端传递 modelId 或 model_id
        model_id = request_data.get('modelId') or request_data.get('model_id')
        current_app.logger.info(f"解析到的model_id: {model_id}")
        
        # 创建新会话
        title = request_data.get('title', f'新建会话 {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        data_source_ids = request_data.get('dataSourceIds', [])
        
        # 检查模型是否存在
        model = None
        if model_id:
            model = Model.query.get(model_id)
            if not model:
                # 如果模型ID不存在，尝试获取默认模型
                current_app.logger.warning(f"指定的模型不存在 (ID={model_id})，尝试使用默认模型")
                model = Model.query.filter_by(is_default=True).first()
                if model:
                    model_id = model.id
                    current_app.logger.info(f"使用默认模型 (ID={model_id})")
                else:
                    current_app.logger.error("没有找到默认模型")
        
        # 创建会话记录
        chat = Conversation(
            title=title,
            user_id=user_id,
            model_id=model_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 添加数据源关联
        if data_source_ids:
            datasources = DataSource.query.filter(DataSource.id.in_(data_source_ids)).all()
            chat.datasources = datasources
        
        # 保存到数据库
        db.session.add(chat)
        db.session.commit()
        
        current_app.logger.info(f"会话创建成功: ID={chat.id}, 用户ID={user_id}")
        
        # 确保返回与前端期望格式一致的数据
        response_data = {
            'id': chat.id,
            'title': chat.title,
            'createdAt': chat.created_at.isoformat(),
            'updatedAt': chat.updated_at.isoformat(),
            'messageCount': 0,
            'dataSourceIds': data_source_ids,
            'modelId': model_id
        }
        
        current_app.logger.info(f"返回响应数据: {response_data}")
        # 修改返回格式，添加status和data字段
        return jsonify({
            'status': 'success',
            'message': '会话创建成功',
            'data': response_data
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"创建会话时发生异常: {str(e)}")
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'创建会话失败: {str(e)}'
        }), 500

@chat_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_or_demo_required()
def get_session_detail(session_id):
    """获取会话详情及消息历史"""
    user_id = get_identity()
    
    # 获取会话信息
    chat = Conversation.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 获取会话关联的数据源IDs
    data_source_ids = [ds.id for ds in chat.datasources]
    
    # 获取会话消息
    messages = Message.query.filter_by(conversation_id=session_id).order_by(Message.created_at).all()
    message_list = []
    
    for msg in messages:
        message_list.append({
            'id': msg.id,
            'role': msg.role,
            'content': msg.content,
            'timestamp': msg.created_at.isoformat()
        })
    
    # 构建会话详情
    session_detail = {
        'id': chat.id,
        'title': chat.title,
        'createdAt': chat.created_at.isoformat(),
        'updatedAt': chat.updated_at.isoformat(),
        'messageCount': len(message_list),
        'messages': message_list,
        'dataSourceIds': data_source_ids,
        'modelId': chat.model_id
    }
    
    return jsonify(session_detail)

@chat_bp.route('/sessions/<session_id>', methods=['DELETE'])
@jwt_or_demo_required()
def delete_session(session_id):
    """删除会话"""
    user_id = get_identity()
    
    # 获取要删除的会话
    chat = Conversation.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 删除会话关联的所有消息
    Message.query.filter_by(conversation_id=session_id).delete()
    
    # 删除会话
    db.session.delete(chat)
    db.session.commit()
    
    return jsonify({'message': '会话已成功删除'})

@chat_bp.route('/sessions/<session_id>/messages', methods=['POST'])
@jwt_or_demo_required()
def send_message(session_id):
    """发送消息并获取回复"""
    user_id = get_identity()
    data = request.get_json()
    
    # 查询会话信息
    chat = Conversation.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 获取用户发送的消息内容
    user_message_content = data.get('content', '')
    if not user_message_content.strip():
        return jsonify({'message': '消息内容不能为空'}), 400
    
    # 创建用户消息
    user_message = Message(
        conversation_id=session_id,
        role='user',
        content=user_message_content,
        created_at=datetime.now()
    )
    
    # 更新会话的更新时间
    chat.updated_at = datetime.now()
    
    # 保存用户消息
    db.session.add(user_message)
    db.session.commit()
    
    # 获取会话关联的模型和数据源
    model = Model.query.get(chat.model_id) if chat.model_id else None
    datasources = chat.datasources
    
    # 导入ChatService
    from app.services.chat_service import ChatService
    chat_service = ChatService()
    
    # 调用ChatService处理消息
    result = chat_service.process_message(
        message_content=user_message_content,
        model=model,
        datasources=datasources
    )
    
    # 获取回复内容
    ai_response = result.get('content', '')
    sql_query = result.get('sql_query')
    error = result.get('error')
    
    # 创建AI回复消息
    ai_message = Message(
        conversation_id=session_id,
        role='assistant',
        content=ai_response,
        sql_query=sql_query,
        error_message=error,
        created_at=datetime.now()
    )
    
    # 保存AI回复
    db.session.add(ai_message)
    db.session.commit()
    
    # 返回用户消息和AI回复
    return jsonify({
        'userMessage': {
            'id': user_message.id,
            'role': user_message.role,
            'content': user_message.content,
            'timestamp': user_message.created_at.isoformat()
        },
        'aiMessage': {
            'id': ai_message.id,
            'role': ai_message.role,
            'content': ai_message.content,
            'sql_query': sql_query,
            'error_message': error,
            'timestamp': ai_message.created_at.isoformat()
        }
    })

@chat_bp.route('/sessions/<session_id>/rename', methods=['PUT'])
@jwt_or_demo_required()
def rename_session(session_id):
    """重命名会话"""
    user_id = get_identity()
    data = request.get_json()
    
    # 新的会话标题
    new_title = data.get('title')
    if not new_title or not new_title.strip():
        return jsonify({'message': '会话标题不能为空'}), 400
    
    # 查询会话信息
    chat = Conversation.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 更新会话标题
    chat.title = new_title
    chat.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'message': '会话重命名成功', 'title': new_title})

@chat_bp.route('/sessions/<session_id>/datasources', methods=['PUT'])
@jwt_or_demo_required()
def update_session_datasources(session_id):
    """更新会话关联的数据源"""
    user_id = get_identity()
    data = request.get_json()
    
    # 数据源ID列表
    data_source_ids = data.get('dataSourceIds', [])
    
    # 查询会话信息
    chat = Conversation.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 更新会话关联的数据源
    data_sources = DataSource.query.filter(DataSource.id.in_(data_source_ids)).all()
    chat.datasources = data_sources
    chat.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'message': '会话数据源更新成功', 'dataSourceIds': data_source_ids})

@chat_bp.route('/sessions/<session_id>/model', methods=['PUT'])
@jwt_or_demo_required()
def update_session_model(session_id):
    """更新会话关联的模型"""
    user_id = get_identity()
    data = request.get_json()
    
    # 模型ID，允许为None
    model_id = data.get('modelId')
    
    # 查询会话信息
    chat = Conversation.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 如果提供了model_id，检查模型是否存在
    if model_id:
        model = Model.query.get(model_id)
        if not model:
            return jsonify({'message': '指定的模型不存在'}), 400
    
    # 更新会话关联的模型
    chat.model_id = model_id
    chat.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'message': '会话模型更新成功', 'modelId': model_id}) 