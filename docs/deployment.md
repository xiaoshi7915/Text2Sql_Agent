# 问数智能体部署指南

本文档提供了问数智能体系统的部署说明，包括传统部署和Docker部署两种方式。

## 系统要求

### 硬件要求
- CPU: 4核或更高
- 内存: 最小8GB，推荐16GB以上
- 存储: 最小20GB可用空间

### 软件要求
- 操作系统: Linux (推荐Ubuntu 20.04+或CentOS 7+)，也支持Windows Server 2019+
- 数据库: MySQL 8.0+ 或 MariaDB 10.5+
- Python: 3.10+
- Node.js: 16.0+
- Nginx: 用于反向代理(可选)

## 传统部署

### 1. 后端部署

#### 准备环境
```bash
# 更新包管理器
sudo apt update  # Ubuntu
# 或
sudo yum update  # CentOS

# 安装依赖
sudo apt install python3 python3-pip python3-venv  # Ubuntu
# 或
sudo yum install python3 python3-pip  # CentOS

# 安装数据库客户端库
sudo apt install libmysqlclient-dev libpq-dev unixodbc-dev  # Ubuntu
# 或
sudo yum install mysql-devel postgresql-devel unixODBC-devel  # CentOS
```

#### 部署应用
```bash
# 克隆代码(如果使用Git)
git clone https://your-repository-url/wenshu-mcp.git
cd wenshu-mcp

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件配置数据库和API密钥

# 初始化数据库
flask db upgrade

# 创建管理员账户
python create_admin.py

# 启动服务(开发环境)
python run.py

# 使用Gunicorn启动(生产环境)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

#### 使用Systemd管理服务
```bash
# 创建服务文件
sudo nano /etc/systemd/system/wenshu-mcp.service
```

服务文件内容:
```
[Unit]
Description=Wenshu MCP Backend Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/wenshu-mcp/backend
Environment="PATH=/path/to/wenshu-mcp/backend/venv/bin"
ExecStart=/path/to/wenshu-mcp/backend/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 run:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动服务
sudo systemctl daemon-reload
sudo systemctl start wenshu-mcp
sudo systemctl enable wenshu-mcp
```

### 2. 前端部署

#### 准备环境
```bash
# 安装Node.js和npm
curl -sL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs  # Ubuntu
# 或
sudo yum install -y nodejs  # CentOS
```

#### 构建前端
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.production.local
# 编辑.env.production.local文件

# 构建生产版本
npm run build
```

#### 使用Nginx部署
```bash
# 安装Nginx
sudo apt install nginx  # Ubuntu
# 或
sudo yum install nginx  # CentOS

# 配置Nginx
sudo nano /etc/nginx/sites-available/wenshu-mcp
```

Nginx配置文件内容:
```
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/wenshu-mcp/frontend/dist;
    index index.html;

    # 前端文件缓存设置
    location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
        expires 1y;
        add_header Cache-Control "public, max-age=31536000";
    }

    # 前端路由处理
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 创建符号链接并启用站点(Ubuntu)
sudo ln -s /etc/nginx/sites-available/wenshu-mcp /etc/nginx/sites-enabled/
# CentOS通常在/etc/nginx/conf.d/目录下直接创建配置文件

# 检查Nginx配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

## Docker部署

### 1. 安装Docker和Docker Compose
```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 创建Docker Compose配置
在项目根目录创建`docker-compose.yml`文件:

```yaml
version: '3'

services:
  db:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: your_mysql_root_password
      MYSQL_DATABASE: wenshu_mcp
      MYSQL_USER: wenshu
      MYSQL_PASSWORD: your_mysql_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  backend:
    build: ./backend
    restart: always
    depends_on:
      - db
    environment:
      - DB_HOST=db
      - DB_PORT=3306
      - DB_USER=wenshu
      - DB_PASSWORD=your_mysql_password
      - DB_NAME=wenshu_mcp
      - SECRET_KEY=your_secret_key
      - JWT_SECRET_KEY=your_jwt_secret_key
      - DEFAULT_LLM_MODEL=deepseek-chat
      - LLM_API_KEY=your_llm_api_key
      - LLM_API_BASE=https://api.deepseek.com/v1/chat/completions
    volumes:
      - ./backend:/app
    ports:
      - "5000:5000"

  frontend:
    build: ./frontend
    restart: always
    depends_on:
      - backend
    ports:
      - "80:80"
    volumes:
      - ./frontend/nginx.conf:/etc/nginx/conf.d/default.conf

volumes:
  mysql_data:
```

### 3. 创建Dockerfile

在backend目录下创建`Dockerfile`:
```Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

在frontend目录下创建`Dockerfile`:
```Dockerfile
FROM node:16 as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:stable-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

在frontend目录下创建`nginx.conf`:
```
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. 启动服务
```bash
# 构建并启动容器
docker-compose up -d

# 初始化数据库(仅首次运行)
docker-compose exec backend flask db upgrade
docker-compose exec backend python create_admin.py
```

## 维护与故障排除

### 日志查看
```bash
# 传统部署
sudo journalctl -u wenshu-mcp.service  # 后端系统服务日志
sudo tail -f /var/log/nginx/access.log  # Nginx访问日志
sudo tail -f /var/log/nginx/error.log  # Nginx错误日志

# Docker部署
docker-compose logs -f backend  # 后端容器日志
docker-compose logs -f frontend  # 前端容器日志
```

### 常见问题

1. **数据库连接失败**
   - 检查数据库凭据是否正确
   - 确认数据库服务器防火墙设置
   - 验证数据库是否正常运行

2. **API密钥问题**
   - 确认大语言模型API密钥是否有效
   - 检查API请求限制是否达到上限

3. **性能优化**
   - 配置数据库连接池大小
   - 调整Gunicorn工作进程数量
   - 为Nginx静态文件添加适当的缓存策略

## 安全建议

1. 使用HTTPS加密传输，可以使用Let's Encrypt获取免费SSL证书
2. 定期更新系统和依赖包
3. 实施适当的防火墙规则
4. 使用强密码和密钥
5. 定期备份数据库

## 备份与恢复

### 数据库备份
```bash
# MySQL备份
mysqldump -u username -p wenshu_mcp > backup.sql

# 恢复
mysql -u username -p wenshu_mcp < backup.sql
```

### Docker卷备份
```bash
# 备份
docker run --rm -v wenshu-mcp_mysql_data:/volume -v $(pwd):/backup alpine tar -czvf /backup/mysql_data.tar.gz /volume

# 恢复
docker run --rm -v wenshu-mcp_mysql_data:/volume -v $(pwd):/backup alpine sh -c "cd /volume && tar -xzvf /backup/mysql_data.tar.gz --strip 1"
``` 