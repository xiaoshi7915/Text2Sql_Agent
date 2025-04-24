"""
认证相关的API视图
处理用户登录、登出、获取用户信息等功能
"""

import sys
import os
import os.path

# 确保路径正确
api_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(api_dir)
sys.path.insert(0, backend_dir)

from flask import request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash

# 使用绝对导入避免冲突
from app.models.user import User
# 从app模块导入db实例
from app import db
from . import api_bp


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """
    用户登录API
    
    请求体：
    {
        "username": "用户名",
        "password": "密码",
        "remember": true/false
    }
    
    返回：
    {
        "status": "success",
        "token": "JWT访问令牌",
        "refresh_token": "JWT刷新令牌（可选）",
        "user": {
            "id": 用户ID,
            "username": "用户名",
            "email": "邮箱",
            "is_admin": true/false,
            ...
        }
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': '无效的请求数据'
        }), 400
    
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember', False)
    
    if not username or not password:
        return jsonify({
            'status': 'error',
            'message': '用户名和密码不能为空'
        }), 400
    
    # 查找用户
    user = User.query.filter_by(username=username).first()
    
    # 验证用户和密码
    if not user or not user.check_password(password):
        return jsonify({
            'status': 'error',
            'message': '用户名或密码错误'
        }), 401
    
    # 检查用户是否激活
    if not user.is_active:
        return jsonify({
            'status': 'error',
            'message': '账户已被禁用，请联系管理员'
        }), 403
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.session.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(days=30 if remember else 1)
    access_token = create_access_token(
        identity=user.id,
        expires_delta=access_token_expires,
        additional_claims={
            'username': user.username,
            'is_admin': user.is_admin
        }
    )
    
    # 创建刷新令牌（如果需要）
    refresh_token = None
    if remember:
        refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'status': 'success',
        'token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    })


@api_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    用户登出API
    
    需要JWT认证
    
    返回：
    {
        "status": "success",
        "message": "成功登出"
    }
    """
    # 实际的JWT登出需要在客户端移除令牌
    # 这里可以实现将令牌加入黑名单的逻辑（需要Redis支持）
    
    return jsonify({
        'status': 'success',
        'message': '成功登出'
    })


@api_bp.route('/auth/user-info', methods=['GET'])
@jwt_required()
def get_user_info():
    """
    获取当前登录用户信息API
    
    需要JWT认证
    
    返回：
    {
        "status": "success",
        "user": {
            "id": 用户ID,
            "username": "用户名",
            "email": "邮箱",
            "is_admin": true/false,
            ...
        }
    }
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    return jsonify({
        'status': 'success',
        'user': user.to_dict()
    })


@api_bp.route('/auth/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    刷新JWT令牌API
    
    需要JWT刷新令牌认证
    
    返回：
    {
        "status": "success",
        "token": "新的JWT访问令牌"
    }
    """
    # 获取当前用户ID
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    # 创建新的访问令牌
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'is_admin': user.is_admin
        }
    )
    
    return jsonify({
        'status': 'success',
        'token': access_token
    })


@api_bp.route('/auth/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    修改密码API
    
    需要JWT认证
    
    请求体：
    {
        "oldPassword": "旧密码",
        "newPassword": "新密码",
        "confirmPassword": "确认新密码"
    }
    
    返回：
    {
        "status": "success",
        "message": "密码修改成功"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': '无效的请求数据'
        }), 400
    
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    confirm_password = data.get('confirmPassword')
    
    if not old_password or not new_password or not confirm_password:
        return jsonify({
            'status': 'error',
            'message': '所有密码字段均不能为空'
        }), 400
    
    if new_password != confirm_password:
        return jsonify({
            'status': 'error',
            'message': '新密码和确认密码不匹配'
        }), 400
    
    # 获取当前用户
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    # 验证旧密码
    if not user.check_password(old_password):
        return jsonify({
            'status': 'error',
            'message': '旧密码不正确'
        }), 401
    
    # 设置新密码
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '密码修改成功'
    }) 