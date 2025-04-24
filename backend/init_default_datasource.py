#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化默认数据源脚本
在数据库中创建一个默认的数据源配置
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 将当前目录添加到系统路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 从环境变量获取数据库配置
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'wenshu_mcp')

try:
    from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    
    # 创建数据库连接
    def get_connection_url():
        """获取数据库连接URL"""
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    Base = declarative_base()
    
    class DataSource(Base):
        """数据源模型，用于存储连接各类数据库的配置信息"""
        
        __tablename__ = 'datasources'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(100), nullable=False)
        description = Column(Text, nullable=True)
        ds_type = Column(String(50), nullable=False)
        host = Column(String(255), nullable=False)
        port = Column(Integer, nullable=False)
        database = Column(String(100), nullable=False)
        username = Column(String(100), nullable=False)
        password = Column(String(255), nullable=False)
        options = Column(JSON, nullable=True)
        include_views = Column(Boolean, default=False)
        format = Column(String(50), default='public')
        selected_fields = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.now)
        updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def init_default_datasource():
        """创建默认数据源配置"""
        connection_url = get_connection_url()
        print(f"尝试连接数据库: {connection_url.replace(DB_PASSWORD, '******')}")
        
        try:
            engine = create_engine(connection_url)
            Base.metadata.create_all(engine)  # 确保表存在
            Session = sessionmaker(bind=engine)
            session = Session()
            print("数据库连接成功")
        except Exception as e:
            print(f"连接数据库失败: {str(e)}")
            return False
        
        try:
            # 检查是否已有默认数据源
            existing_datasource = session.query(DataSource).filter_by(name="示例MySQL数据源").first()
            if existing_datasource:
                print(f"已存在数据源: {existing_datasource.name}")
                session.close()
                return False
            
            # 创建默认数据源
            default_datasource = DataSource(
                name="示例MySQL数据源",
                description="这是一个示例MySQL数据源，用于系统测试",
                ds_type="mysql",
                host=DB_HOST,
                port=int(DB_PORT),
                database=DB_NAME,
                username=DB_USER,
                password=DB_PASSWORD,
                include_views=True,
                format="public",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 添加到数据库并提交
            session.add(default_datasource)
            session.commit()
            print(f"默认数据源 {default_datasource.name} 创建成功!")
            
            session.close()
            return True
            
        except Exception as e:
            session.rollback()
            session.close()
            print(f"创建默认数据源失败: {str(e)}")
            return False
    
    if __name__ == "__main__":
        init_default_datasource()
        
except ImportError as e:
    print(f"导入错误: {str(e)}")
    sys.exit(1) 