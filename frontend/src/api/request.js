import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const service = axios.create({
  baseURL: '/api', // 直接使用相对路径，不再依赖环境变量
  timeout: 30000, // 请求超时时间（毫秒）
  withCredentials: true, // 跨域请求时发送cookies
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求前的处理
    console.log('请求URL:', config.baseURL + config.url)
    
    // 添加token到请求头（如果存在）
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    
    return config
  },
  error => {
    // 请求错误的处理
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据的处理
    const res = response.data
    
    // 根据后端API的响应结构判断请求是否成功
    if (res.status === 'success') {
      return res
    }
    
    // 处理特定的错误码
    if (res.status === 'error') {
      ElMessage({
        message: res.message || '请求失败',
        type: 'error',
        duration: 5 * 1000
      })
      
      // 处理401未授权错误
      if (response.status === 401) {
        // 可以在这里处理登出逻辑，清除token等
        localStorage.removeItem('token')
        // 跳转到登录页
        window.location.href = '/login'
      }
      
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  error => {
    // 响应错误的处理
    console.error('响应错误:', error)
    
    // 处理HTTP状态码的错误
    if (error.response) {
      const status = error.response.status
      let message = ''
      
      switch (status) {
        case 400:
          message = '请求错误'
          break
        case 401:
          message = '未授权，请登录'
          // 清除token并跳转到登录页
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求地址不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = `连接错误 ${status}`
      }
      
      ElMessage({
        message: message,
        type: 'error',
        duration: 5 * 1000
      })
    } else {
      // 处理网络错误或请求被取消
      ElMessage({
        message: error.message || '网络异常，请稍后重试',
        type: 'error',
        duration: 5 * 1000
      })
    }
    
    return Promise.reject(error)
  }
)

// 封装GET请求
export function get(url, params) {
  return service({
    url,
    method: 'get',
    params
  })
}

// 封装POST请求
export function post(url, data) {
  return service({
    url,
    method: 'post',
    data
  })
}

// 封装PUT请求
export function put(url, data) {
  return service({
    url,
    method: 'put',
    data
  })
}

// 封装DELETE请求
export function del(url, params) {
  return service({
    url,
    method: 'delete',
    params
  })
}

export default service 