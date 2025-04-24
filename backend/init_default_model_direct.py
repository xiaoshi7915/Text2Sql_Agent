#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化默认模型脚本
使用直接的数据库连接方法
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# 从环境变量获取数据库配置
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'wenshu_mcp')

try:
    from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    
    # 创建数据库连接
    def get_connection_url():
        """获取数据库连接URL"""
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    Base = declarative_base()
    
    class Model(Base):
        """大语言模型配置模型"""
        
        __tablename__ = 'models'
        
        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String(100), nullable=False)
        provider = Column(String(50), nullable=False)
        model_type = Column(String(50), nullable=False)
        api_base = Column(String(255), nullable=True)
        api_key = Column(String(255), nullable=True)
        api_version = Column(String(50), nullable=True)
        temperature = Column(Float, default=0.7)
        max_tokens = Column(Integer, default=4096)
        is_default = Column(Boolean, default=False)
        is_active = Column(Boolean, default=True)
        parameters = Column(JSON, nullable=True)
        created_at = Column(DateTime, default=datetime.now)
        updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def init_default_model():
        """创建默认模型配置"""
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
            # 检查是否已有默认模型
            existing_default = session.query(Model).filter_by(is_default=True).first()
            if existing_default:
                print(f"已存在默认模型: {existing_default.name}")
                session.close()
                return False
            
            # 创建默认模型
            default_model = Model(
                name="DeepSeek Chat",
                provider="DeepSeek",
                model_type="chat",
                api_base=os.getenv('LLM_API_BASE', 'https://api.deepseek.com'),
                api_key=os.getenv('LLM_API_KEY', ''),
                api_version="v1",
                temperature=0.7,
                max_tokens=4096,
                is_default=True,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # 添加到数据库并提交
            session.add(default_model)
            session.commit()
            print(f"默认模型 {default_model.name} 创建成功!")
            
            session.close()
            return True
            
        except Exception as e:
            session.rollback()
            session.close()
            print(f"创建默认模型失败: {str(e)}")
            return False
    
    if __name__ == "__main__":
        init_default_model()
        
except ImportError as e:
    print(f"导入错误: {str(e)}")
    sys.exit(1) 