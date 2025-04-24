#!/bin/bash

echo "启动问数智能体项目..."

# 确保 Docker 和 Docker Compose 已安装
if ! command -v docker &> /dev/null
then
    echo "Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null
then
    echo "Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 停止并删除旧容器（如果存在）
echo "清理旧环境..."
docker-compose down

# 构建并启动容器
echo "构建并启动服务..."
docker-compose up -d --build

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 初始化数据库（如果需要）
echo "初始化数据库..."
docker-compose exec backend python init_default_datasource.py
docker-compose exec backend python init_default_model_direct.py
docker-compose exec backend python create_admin.py

echo "问数智能体项目已成功启动！"
echo "前端地址: http://localhost"
echo "后端API: http://localhost:5000/api"
echo "管理员账号: admin 密码: admin123" 