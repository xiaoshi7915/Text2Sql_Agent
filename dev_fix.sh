#!/bin/bash

echo "开始修复前端开发环境问题..."

# 进入前端目录
cd frontend

# 备份原路由文件
echo "备份原路由文件..."
cp src/router/index.js src/router/index.js.bak

# 将新路由文件复制到位
echo "应用新路由配置..."
cp src/router/index-fixed.js src/router/index.js

# 修改Vue配置增加静态构建而不是代码分割
echo "更新Vue配置..."
cat > vue.config.dev.js << 'EOF'
const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: 'warning',
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws',
    },
    allowedHosts: 'all',
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_DEVTOOLS__: true,
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: true
      })
    ],
    // 禁用代码分割和懒加载以解决开发环境中的问题
    optimization: {
      splitChunks: false
    }
  }
})
EOF

# 使用新的配置
cp vue.config.dev.js vue.config.js

# 清除缓存
echo "清除缓存..."
npm cache clean --force
rm -rf node_modules/.cache

# 重启开发服务器
echo "重启开发服务器..."
npx kill-port 8080
npm run serve &

echo "前端开发环境修复完成！"
echo "等待几秒钟后，访问 http://localhost:8080 检查问题是否解决" 