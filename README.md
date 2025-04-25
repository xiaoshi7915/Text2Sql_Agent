# 问数智能体系统

## 项目概述

问数智能体系统是一个基于Flask和Vue.js的全栈应用程序，旨在提供数据源管理和智能交互功能。

## 系统架构

### 后端（Flask）

后端采用模块化设计，主要分为以下几层：

1. **API层**：处理HTTP请求和响应
   - `/backend/api/` - 外部API接口
   - `/backend/app/api/` - 内部API实现

2. **服务层**：实现业务逻辑
   - `/backend/app/services/` - 封装核心业务逻辑

3. **模型层**：定义数据模型
   - `/backend/app/models/` - 数据库模型定义

4. **工具层**：提供通用功能
   - `/backend/app/utils/` - 工具类和辅助函数

### 前端（Vue.js）

前端使用Vue.js框架，采用组件化设计：

1. **视图**：用户界面
   - `/frontend/src/views/` - 页面视图组件

2. **组件**：可复用UI元素
   - `/frontend/src/components/` - 组件定义

3. **状态管理**：
   - `/frontend/src/store/` - Pinia状态管理

4. **API调用**：
   - `/frontend/src/api/` - 后端API调用

## 数据源管理模块

### 模块功能

数据源管理模块允许用户：
- 创建、编辑、删除和查看数据源
- 测试数据源连接
- 查看数据源中的表数量和连接状态

### 技术亮点

1. **模块化设计**：
   - 使用策略模式处理不同类型的数据库连接
   - 服务层封装业务逻辑，与API层分离

2. **数据库支持**：
   - MySQL
   - PostgreSQL
   - SQL Server
   - Oracle
   - KingbaseES (PostgreSQL兼容)

3. **安全特性**：
   - 密码加密存储
   - 敏感信息保护

## 模型管理模块

### 模块功能

模型管理模块允许用户：
- 创建、编辑、删除和查看LLM模型配置
- 测试模型API连接
- 设置默认模型
- 调整模型参数

### 技术亮点

1. **多种LLM支持**：
   - OpenAI API
   - DeepSeek API
   - 智谱AI API
   - 易于扩展其他LLM提供商

2. **安全特性**：
   - API密钥加密存储
   - 敏感信息保护

3. **连接测试**：
   - 实时测试API连接
   - 友好的错误信息和解决方案
   - 支持自定义API端点

## 启动项目

### 后端

```bash
cd backend
python run.py
```

### 前端

```bash
cd frontend
npm run serve
```

## 项目结构

```
wenshu-mcp/
├── backend/                   # 后端代码
│   ├── api/                   # 外部API定义
│   ├── app/                   # 应用核心代码
│   │   ├── api/               # 内部API实现
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务服务
│   │   └── utils/             # 工具函数
│   ├── migrations/            # 数据库迁移
│   ├── app.py                 # 应用入口
│   ├── config.py              # 配置文件
│   └── run.py                 # 运行脚本
├── frontend/                  # 前端代码
│   ├── public/                # 静态资源
│   ├── src/                   # 源代码
│   │   ├── api/               # API调用
│   │   ├── assets/            # 资源文件
│   │   ├── components/        # 组件
│   │   ├── router/            # 路由
│   │   ├── store/             # 状态管理
│   │   ├── views/             # 视图
│   │   ├── App.vue            # 主组件
│   │   └── main.js            # 入口文件
│   ├── package.json           # 依赖配置
│   └── vue.config.js          # Vue配置
└── README.md                  # 项目文档
```

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
- 前端界面：http://localhost:8087
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