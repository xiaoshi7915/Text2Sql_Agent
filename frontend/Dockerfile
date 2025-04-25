# 构建阶段
FROM node:16-alpine

# 设置npm使用淘宝镜像源
RUN npm config set registry https://registry.npmmirror.com

WORKDIR /app

# 复制依赖文件
COPY package*.json ./

# 安装依赖
RUN npm install
RUN npm install -g serve

# 复制项目文件
COPY . .

# 设置环境变量
ENV NODE_ENV=production

# 构建生产版本
RUN npm run build

# 暴露端口
EXPOSE 80

# 使用serve提供静态文件
CMD ["serve", "-s", "dist", "-l", "80"] 