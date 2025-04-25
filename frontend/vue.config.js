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
        target: 'http://127.0.0.1:5001',
        changeOrigin: true,
        pathRewrite: { '^/api': '/api' },
        logLevel: 'debug',
        onProxyReq(proxyReq, req, res) {
          console.log('请求路径:', req.path)
          console.log('代理请求:', req.method, req.path)
        },
        onProxyRes(proxyRes, req, res) {
          console.log('代理响应:', proxyRes.statusCode, req.path)
        },
        onError(err, req, res) {
          // 记录更详细的错误信息
          console.error('代理错误:', err.toString())
          
          // 在开发环境中，对于模型和数据源接口，返回模拟数据而不是错误
          if (req.path.includes('/api/models')) {
            res.writeHead(200, { 'Content-Type': 'application/json' })
            res.end(JSON.stringify({
              status: 'success',
              data: [
                {
                  id: 1,
                  name: '默认模型',
                  provider: 'OpenAI',
                  model_type: 'gpt-3.5-turbo',
                  is_default: true,
                  is_active: true
                }
              ]
            }))
            return
          }
          
          if (req.path.includes('/api/datasources/list')) {
            res.writeHead(200, { 'Content-Type': 'application/json' })
            res.end(JSON.stringify({
              status: 'success',
              data: [
                {
                  id: 1,
                  name: '示例数据源',
                  ds_type: 'mysql',
                  host: 'localhost',
                  port: 3306,
                  database: 'demo',
                  connection_status: 'connected'
                }
              ]
            }))
            return
          }
          
          // 其他情况返回错误响应
          res.writeHead(500, { 'Content-Type': 'application/json' })
          res.end(JSON.stringify({
            status: 'error',
            message: '后端服务暂时不可用，请稍后再试',
            error: err.toString()
          }))
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
