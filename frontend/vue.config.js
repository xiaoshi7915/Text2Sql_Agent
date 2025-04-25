const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: 'warning',
  devServer: {
    host: '0.0.0.0',
    port: 8082,
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws',
    },
    allowedHosts: 'all',
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        pathRewrite: { '^/api': '/api' },
        logLevel: 'debug',
        onProxyReq(proxyReq, req, res) {
          console.log('代理请求:', req.method, req.path)
        },
        onProxyRes(proxyRes, req, res) {
          console.log('代理响应:', proxyRes.statusCode, req.path)
        },
        onError(err, req, res) {
          console.error('代理错误:', err)
        }
      }
    },
    setupMiddlewares: (middlewares, devServer) => {
      // 添加中间件，捕获404错误
      devServer.app.use((req, res, next) => {
        console.log('请求路径:', req.path)
        next()
      })
      
      return middlewares
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
