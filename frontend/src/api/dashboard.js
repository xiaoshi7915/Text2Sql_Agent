import { get } from './request'

// 获取仪表盘数据统计信息
export function getDashboardStats() {
  return get('/dashboard/stats')
}

// 获取最近7天会话统计数据
export function getSessionStats() {
  return get('/dashboard/sessions')
}

// 获取系统响应时间
export function getResponseTime() {
  return get('/dashboard/response-time')
}

// 获取系统状态
export function getSystemStatus() {
  return get('/dashboard/status')
} 