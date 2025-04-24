// API配置文件
const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000';

// 导出API基础URL
export const baseURL = API_URL;

// 创建axios请求实例的配置
export const apiConfig = {
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
};

// API端点列表
export const API_ENDPOINTS = {
  LOGIN: '/api/auth/login',
  REGISTER: '/api/auth/register',
  CHAT: '/api/chat',
  DATASOURCES: '/api/datasources',
  MODELS: '/api/models',
  // 其他API端点...
};

export default {
  baseURL,
  apiConfig,
  API_ENDPOINTS
}; 