"""
应用启动脚本
"""

import os
import sys
import os.path

# 确保当前目录在路径中
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from app import create_app

app = create_app()

if __name__ == '__main__':
    # 修改默认端口为5001，避免与其他服务冲突
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port) 