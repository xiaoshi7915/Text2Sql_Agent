#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检查模型配置情况
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置必要的环境变量以支持解密
os.environ['ENCRYPTION_KEY'] = "uLYJeqGYsRcD8Qh8-N-m3ZbqJAaJDDiSN2UYkFcVBYA="
os.environ['SECRET_KEY'] = "hard-to-guess-string"

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入必要的模块
from app import create_app, db
from app.models.model import Model
from app.api.models import decrypt_api_key

def check_models():
    """检查模型配置情况"""
    try:
        # 创建Flask应用
        app = create_app()
        
        with app.app_context():
            # 获取所有模型
            models = Model.query.all()
            
            print(f"共找到 {len(models)} 个模型配置")
            
            for model in models:
                print(f"\n模型 #{model.id}:")
                print(f"  名称: {model.name}")
                print(f"  提供商: {model.provider}")
                print(f"  模型类型: {model.model_type}")
                print(f"  API基础URL: {model.api_base}")
                print(f"  API密钥长度: {len(model.api_key) if model.api_key else 0}")
                print(f"  是否默认: {'是' if model.is_default else '否'}")
                print(f"  是否激活: {'是' if model.is_active else '否'}")
                
                # 尝试解密API密钥
                if model.api_key:
                    try:
                        decrypted_key = decrypt_api_key(model.api_key)
                        print(f"  API密钥解密: {'成功' if decrypted_key else '失败'}")
                        print(f"  解密后API密钥长度: {len(decrypted_key) if decrypted_key else 0}")
                        print(f"  API密钥前10个字符: {decrypted_key[:10] if decrypted_key and len(decrypted_key) > 10 else decrypted_key}")
                    except Exception as e:
                        print(f"  API密钥解密出错: {str(e)}")
                        import traceback
                        print(f"  错误详情:\n{traceback.format_exc()}")
                else:
                    print("  API密钥未设置")
    
    except Exception as e:
        logger.error(f"检查模型配置失败: {str(e)}")

if __name__ == "__main__":
    check_models() 