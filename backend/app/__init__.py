"""
Flask应用初始化文件
"""

import os
import sys
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# 确保路径正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载.env文件中的环境变量
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(dotenv_path)

# 创建数据库对象
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """创建并配置Flask应用"""
    app = Flask(__name__)
    
    # 配置跨域资源共享
    CORS(app)
    
    # 配置数据库连接 - 从.env加载配置
    app.logger.info("配置数据库连接")
    
    # 从环境变量获取数据库配置
    db_host = os.getenv('DB_HOST', '47.118.250.53')
    db_port = os.getenv('DB_PORT', '3306')
    db_user = os.getenv('DB_USER', 'mcp')
    db_pass = os.getenv('DB_PASS', 'admin123456!')
    db_name = os.getenv('DB_NAME', 'wenshu_mcp')
    
    # 构建数据库URI
    mysql_uri = f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    app.logger.info(f"数据库连接URI: {mysql_uri}")
    
    # 设置SQLAlchemy配置
    app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.logger.info(f"最终使用的URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # JWT配置
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 1天
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']  # 允许从头部或cookie获取token
    app.config['JWT_HEADER_NAME'] = 'Authorization'  # 头部名称
    app.config['JWT_HEADER_TYPE'] = 'Bearer'  # 头部类型
    
    # 开发环境中允许使用demo-token (仅开发环境使用)
    app.config['JWT_IDENTITY_CLAIM'] = 'sub'
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # JWT错误处理
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        from flask import request
        app.logger.error(f"无效的令牌: {error_string}")
        # 检查是否使用了demo-token
        auth_header = request.headers.get('Authorization', '')
        if auth_header == 'Bearer demo-token':
            # 开发环境中允许使用demo-token
            return jsonify({"id": 1, "username": "admin"}), 200
        return jsonify({"msg": "Invalid token"}), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        from flask import request
        app.logger.error(f"未授权请求: {error_string}")
        # 检查是否使用了demo-token
        auth_header = request.headers.get('Authorization', '')
        if auth_header == 'Bearer demo-token':
            # 开发环境中允许使用demo-token
            return jsonify({"id": 1, "username": "admin"}), 200
        return jsonify({"msg": "Missing or invalid token"}), 401
    
    # 注册认证蓝图
    from .api.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # 注册蓝图
    from .api import datasources_bp
    app.register_blueprint(datasources_bp)
    
    # 注册兼容性蓝图 (处理旧路径请求)
    from .api import datasource_compat_bp
    app.register_blueprint(datasource_compat_bp)
    
    # 注册模型API蓝图
    from .api import model_bp
    app.register_blueprint(model_bp, url_prefix='/api/models')
    
    # 注册聊天API蓝图 - 从app.api导入
    from .api import chat_bp
    app.register_blueprint(chat_bp)
    
    # 创建所有表 - 添加错误处理
    try:
        with app.app_context():
            app.logger.info("尝试创建数据库表...")
            db.create_all()
            app.logger.info("数据库表创建成功！")
    except Exception as e:
        app.logger.error(f"创建数据库表失败: {str(e)}")
        app.logger.error("请确保数据库连接配置正确，并且数据库已创建")
    
    return app 