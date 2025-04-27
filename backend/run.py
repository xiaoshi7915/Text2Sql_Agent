"""
应用启动脚本
"""

import sys
import os
import os.path

# 确保路径正确
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# 导入Flask应用
from app import create_app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 运行Flask应用
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    ) 