from flask import Blueprint, request, jsonify, current_app, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid
# 修改导入方式，分开导入db和模型
from app import db
from app.models import User, DataSource, Model, Conversation as Chat, Message

# 创建蓝图
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """获取当前用户的所有会话列表"""
    user_id = get_jwt_identity()
    
    # 获取用户的所有会话
    chats = Chat.query.filter_by(user_id=user_id).order_by(Chat.updated_at.desc()).all()
    
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
@jwt_required()
def create_session():
    """创建新会话"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 创建新会话
    title = data.get('title', f'新建会话 {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    model_id = data.get('modelId')
    data_source_ids = data.get('dataSourceIds', [])
    
    # 检查模型是否存在
    if model_id:
        model = Model.query.get(model_id)
        if not model:
            return jsonify({'message': '指定的模型不存在'}), 400
    
    # 创建会话记录
    chat = Chat(
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
    
    return jsonify({
        'id': chat.id,
        'title': chat.title,
        'createdAt': chat.created_at.isoformat(),
        'updatedAt': chat.updated_at.isoformat(),
        'messageCount': 0,
        'dataSourceIds': data_source_ids,
        'modelId': model_id
    }), 201

@chat_bp.route('/sessions/<session_id>', methods=['GET'])
@jwt_required()
def get_session_detail(session_id):
    """获取会话详情及消息"""
    user_id = get_jwt_identity()
    
    # 查询会话信息
    chat = Chat.query.filter_by(id=session_id, user_id=user_id).first()
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
@jwt_required()
def delete_session(session_id):
    """删除会话"""
    user_id = get_jwt_identity()
    
    # 查询会话信息
    chat = Chat.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 删除会话关联的所有消息
    Message.query.filter_by(conversation_id=session_id).delete()
    
    # 删除会话
    db.session.delete(chat)
    db.session.commit()
    
    return jsonify({'message': '会话已成功删除'})

@chat_bp.route('/sessions/<session_id>/messages', methods=['POST'])
@jwt_required()
def send_message(session_id):
    """发送消息并获取回复"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 查询会话信息
    chat = Chat.query.filter_by(id=session_id, user_id=user_id).first()
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
    data_sources = chat.datasources
    
    # 处理消息并生成回复
    # 此处实际项目中应调用相应的服务来处理用户消息并生成回复
    # 这里简单模拟一个回复
    ai_response = "我已收到您的消息：" + user_message_content
    
    # 创建AI回复消息
    ai_message = Message(
        conversation_id=session_id,
        role='assistant',
        content=ai_response,
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
            'timestamp': ai_message.created_at.isoformat()
        }
    })

@chat_bp.route('/sessions/<session_id>/rename', methods=['PUT'])
@jwt_required()
def rename_session(session_id):
    """重命名会话"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 新的会话标题
    new_title = data.get('title')
    if not new_title or not new_title.strip():
        return jsonify({'message': '会话标题不能为空'}), 400
    
    # 查询会话信息
    chat = Chat.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 更新会话标题
    chat.title = new_title
    chat.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'message': '会话重命名成功', 'title': new_title})

@chat_bp.route('/sessions/<session_id>/datasources', methods=['PUT'])
@jwt_required()
def update_session_datasources(session_id):
    """更新会话关联的数据源"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 数据源ID列表
    data_source_ids = data.get('dataSourceIds', [])
    
    # 查询会话信息
    chat = Chat.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 更新会话关联的数据源
    data_sources = DataSource.query.filter(DataSource.id.in_(data_source_ids)).all()
    chat.datasources = data_sources
    chat.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'message': '会话数据源更新成功', 'dataSourceIds': data_source_ids})

@chat_bp.route('/sessions/<session_id>/model', methods=['PUT'])
@jwt_required()
def update_session_model(session_id):
    """更新会话关联的模型"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # 模型ID
    model_id = data.get('modelId')
    if not model_id:
        return jsonify({'message': '模型ID不能为空'}), 400
    
    # 检查模型是否存在
    model = Model.query.get(model_id)
    if not model:
        return jsonify({'message': '指定的模型不存在'}), 400
    
    # 查询会话信息
    chat = Chat.query.filter_by(id=session_id, user_id=user_id).first()
    if not chat:
        return jsonify({'message': '会话不存在或无权访问'}), 404
    
    # 更新会话关联的模型
    chat.model_id = model_id
    chat.updated_at = datetime.now()
    db.session.commit()
    
    return jsonify({'message': '会话模型更新成功', 'modelId': model_id}) 