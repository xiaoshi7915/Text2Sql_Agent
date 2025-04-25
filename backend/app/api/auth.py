from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from app.models import User, db
from datetime import datetime, timedelta

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
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
    
    # 验证用户状态
    if not user.is_active:
        return jsonify({
            'status': 'error',
            'message': '账户已被禁用，请联系管理员'
        }), 403
    
    # 生成访问令牌和刷新令牌
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '登录成功',
        'token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/refresh-token', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """刷新访问令牌"""
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'status': 'success',
        'token': new_access_token
    }), 200

@auth_bp.route('/user-info', methods=['GET'])
@jwt_required()
def get_user_info():
    """获取当前登录用户信息"""
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
    }), 200

@auth_bp.route('/logout', methods=['POST'])
# 移除JWT验证，允许任何请求都能登出
# @jwt_required()
def logout():
    """
    用户登出，前端负责清除token
    
    无需JWT验证，允许任何请求都能登出成功
    即使未登录或token已失效的用户也可以调用此接口
    """
    return jsonify({
        'status': 'success',
        'message': '登出成功'
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """修改密码"""
    data = request.json
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')
    confirm_password = data.get('confirmPassword')
    
    if not old_password or not new_password or not confirm_password:
        return jsonify({
            'status': 'error',
            'message': '所有密码字段都不能为空'
        }), 400
    
    if new_password != confirm_password:
        return jsonify({
            'status': 'error',
            'message': '新密码和确认密码不匹配'
        }), 400
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            'status': 'error',
            'message': '用户不存在'
        }), 404
    
    if not user.check_password(old_password):
        return jsonify({
            'status': 'error',
            'message': '原密码错误'
        }), 401
    
    user.set_password(new_password)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': '密码修改成功'
    }), 200 