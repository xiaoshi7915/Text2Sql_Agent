#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建管理员账号脚本
用于初始化系统管理员账号
"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 将当前目录添加到系统路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import db
from app.models.user import User

def create_admin_user(username, password, email=None):
    """创建管理员用户"""
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"用户 {username} 已存在!")
            return False
        
        # 创建新管理员用户
        admin_user = User(
            username=username,
            email=email,
            is_active=True,
            is_admin=True
        )
        admin_user.set_password(password)
        
        # 添加到数据库会话并提交
        try:
            db.session.add(admin_user)
            db.session.commit()
            print(f"管理员用户 {username} 创建成功!")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"创建用户失败: {str(e)}")
            return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法: python create_admin.py <用户名> <密码> [电子邮件]")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    email = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_admin_user(username, password, email) 