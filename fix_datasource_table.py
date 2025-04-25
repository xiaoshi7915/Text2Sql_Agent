#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复数据源表结构脚本
添加缺失的table_count字段
"""

import sys
import os
from sqlalchemy import text

# 将当前目录添加到系统路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 调整导入路径
from backend.app import create_app
from backend.app.models import db

def fix_datasource_table():
    """添加缺失的table_count字段"""
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 使用原生SQL添加字段
            with db.engine.connect() as conn:
                # 检查字段是否存在
                result = conn.execute(text("PRAGMA table_info(datasources)")).fetchall()
                
                # 检查是否有table_count字段
                has_table_count = any(col[1] == 'table_count' for col in result)
                
                if not has_table_count:
                    # 添加字段
                    conn.execute(text("ALTER TABLE datasources ADD COLUMN table_count INTEGER DEFAULT 0"))
                    conn.commit()
                    print("成功添加table_count字段")
                else:
                    print("table_count字段已存在，无需添加")
                
                print("数据源表结构修复完成")
                return True
        except Exception as e:
            print(f"修复数据源表结构时发生错误: {str(e)}")
            return False

if __name__ == "__main__":
    fix_datasource_table() 