#!/bin/bash

echo "开始修复前端问题..."

# 进入前端目录
cd frontend

# 安装依赖确保完整
echo "重新安装前端依赖..."
npm install

# 清除缓存
echo "清除缓存..."
npm cache clean --force
rm -rf node_modules/.cache

# 重新构建
echo "重新构建前端..."
npm run build

echo "重启前端服务"
cd ..
docker-compose restart frontend

echo "前端修复完成！"
echo "访问 http://localhost 检查问题是否解决" 