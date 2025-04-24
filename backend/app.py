"""
应用工厂模块
用于创建Flask应用实例
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from config import Config
# 从app模块直接导入db
from app import db
# 改为导入单一的API蓝图
from api import api_bp

# 改为使用绝对导入
import config as app_config
import os
import sys

# 确保当前目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 创建扩展实例，但不初始化它们
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    """
    应用工厂函数
    
    参数:
        config_class: 配置类，默认为Config
    
    返回:
        app: Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_class)
    
    # 初始化CORS
    CORS(app)
    
    # 初始化数据库
    db.init_app(app)
    
    # 初始化其他扩展
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    # 全局错误处理
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"message": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"message": "Internal server error"}), 500
    
    # 创建上传目录
    if not os.path.exists(app.config.get('UPLOAD_FOLDER', 'uploads')):
        os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'))
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 