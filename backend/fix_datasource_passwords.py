#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据源密码修复脚本
重新加密所有数据源的密码，解决密钥不匹配问题
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 确保路径正确
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app, db
from app.models.datasource import DataSource
from app.utils.encryption import encrypt_password

def fix_datasource_passwords():
    """修复所有数据源的密码加密"""
    app = create_app()
    
    with app.app_context():
        print("开始修复数据源密码...")
        
        try:
            # 获取所有数据源
            datasources = DataSource.query.all()
            print(f"找到 {len(datasources)} 个数据源")
            
            # 统一密码，这里可以根据实际情况设置
            default_password = os.getenv('DB_PASSWORD', 'admin123456!')
            
            # 更新所有数据源密码
            updated_count = 0
            for ds in datasources:
                print(f"正在处理数据源: {ds.name} (ID: {ds.id})")
                
                # 重新加密密码
                encrypted_password = encrypt_password(default_password)
                if encrypted_password:
                    ds.password = encrypted_password
                    updated_count += 1
                    print(f"  - 已更新密码加密")
                else:
                    print(f"  - 密码加密失败，跳过")
            
            # 提交更改
            if updated_count > 0:
                db.session.commit()
                print(f"成功修复 {updated_count} 个数据源的密码")
            else:
                print("没有数据源需要修复")
                
        except Exception as e:
            print(f"修复过程中出错: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    fix_datasource_passwords() 