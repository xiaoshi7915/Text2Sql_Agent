# 问数智能体项目

## 项目介绍

问数智能体是一个基于大语言模型的智能对话系统，专注于数据库查询和分析。通过自然语言交互，用户可以查询数据库、生成SQL、可视化数据和获取分析报告，无需编写复杂的SQL语句。

## 功能特点

- 自然语言转SQL查询
- 多种数据库支持（MySQL、PostgreSQL、Oracle、SQL Server）
- 数据可视化（图表展示）
- 会话管理与历史记录
- 多种AI模型支持

## 项目架构

- 前端：Vue 3 + Element Plus + ECharts
- 后端：Flask + SQLAlchemy
- 数据库：MySQL
- 部署：Docker + Docker Compose（直接服务，不使用Nginx）

## Docker部署指南

### 前提条件

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)

### 快速部署

1. 克隆项目
```bash
git clone https://github.com/xiaoshi7915/Text2Sql_Agent
cd wenshu-mcp
```

2. 使用一键部署脚本
```bash
./startup.sh
```

系统将自动构建并启动所有服务，包括前端、后端和数据库。启动完成后，可通过以下地址访问：
- 前端界面：http://localhost
- 后端API：http://localhost:5000/api
- 默认管理员账号：admin 密码：admin123

### 手动部署

如果需要手动部署，可以按照以下步骤操作：

1. 构建并启动所有服务
```bash
docker-compose up -d --build
```

2. 初始化数据库
```bash
docker-compose exec backend python init_default_datasource.py
docker-compose exec backend python init_default_model_direct.py
docker-compose exec backend python create_admin.py
```

### 环境配置

可以通过修改 `docker-compose.yml` 文件来调整环境配置，主要包括：

- 数据库连接信息
- 端口映射
- 存储卷配置

### 常用命令

- 启动服务：`docker-compose up -d`
- 停止服务：`docker-compose down`
- 查看日志：`docker-compose logs -f [服务名]`
- 重启服务：`docker-compose restart [服务名]`

## 本地开发

### 前端开发
```bash
cd frontend
npm install
npm run serve
```

### 后端开发
```bash
cd backend
pip install -r requirements.txt
python run.py
```

## 贡献指南

欢迎贡献代码或提交问题报告，请参考以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 许可证

[MIT License](LICENSE) 