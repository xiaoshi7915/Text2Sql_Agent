import sys
import os.path

# 确保路径正确
models_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(models_dir)
backend_dir = os.path.dirname(app_dir)
sys.path.insert(0, backend_dir)

# 导入应用模块中的数据库实例，而不是创建新的
from app import db

# 导入所有模型，确保它们被注册到SQLAlchemy
from .datasource import DataSource, conversation_datasources
from .model import Model
from .conversation import Conversation, Message
from .user import User

# 为了兼容现有代码，创建别名
Chat = Conversation
chat_datasource = conversation_datasources

# 导出所有模型，让它们可以直接从app.models导入
__all__ = ['db', 'User', 'DataSource', 'Model', 'Conversation', 'Message', 'Chat', 'chat_datasource', 'conversation_datasources'] 