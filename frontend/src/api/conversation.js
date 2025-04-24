import { get, post, put, del } from './request'

// 获取所有会话列表
export function getConversations() {
  return get('/conversations/')
}

// 获取单个会话详情
export function getConversation(id) {
  return get(`/conversations/${id}`)
}

// 创建新的会话
export function createConversation(data) {
  return post('/conversations/', data)
}

// 更新会话信息
export function updateConversation(id, data) {
  return put(`/conversations/${id}`, data)
}

// 删除会话
export function deleteConversation(id) {
  return del(`/conversations/${id}`)
}

// 获取会话消息列表
export function getMessages(conversationId) {
  return get(`/conversations/${conversationId}/messages`)
}

// 发送消息
export function sendMessage(conversationId, data) {
  return post(`/conversations/${conversationId}/messages`, data)
}

// 修正查询
export function correctQuery(conversationId, messageId, correction) {
  return post(`/conversations/${conversationId}/messages/${messageId}/correct`, { correction })
}

// 获取会话数据源
export function getConversationDatasources(conversationId) {
  return get(`/conversations/${conversationId}/datasources`)
}

// 更新会话数据源
export function updateConversationDatasources(conversationId, datasourceIds) {
  return put(`/conversations/${conversationId}/datasources`, { datasource_ids: datasourceIds })
} 