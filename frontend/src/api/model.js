import { get, post, put, del } from './request'

// 获取所有模型列表
export function getModels() {
  return get('/models/')
}

// 获取单个模型详情
export function getModel(id) {
  return get(`/models/${id}`)
}

// 创建新的模型
export function createModel(data) {
  return post('/models/', data)
}

// 更新模型信息
export function updateModel(id, data) {
  return put(`/models/${id}`, data)
}

// 删除模型
export function deleteModel(id) {
  return del(`/models/${id}`)
}

// 获取默认模型
export function getDefaultModel() {
  return get('/models/default')
}

// 测试模型连接
export function testModelConnection(data) {
  return post('/models/test-connection', data)
} 