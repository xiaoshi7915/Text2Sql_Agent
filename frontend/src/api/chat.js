import request from './request'

// 获取用户所有会话
export function getSessions() {
  return request({
    url: '/api/chat/sessions',
    method: 'get'
  })
}

// 创建新会话
export function createSession(data) {
  return request({
    url: '/api/chat/sessions',
    method: 'post',
    data
  })
}

// 获取会话详情
export function getSessionDetail(sessionId) {
  return request({
    url: `/api/chat/sessions/${sessionId}`,
    method: 'get'
  })
}

// 删除会话
export function deleteSession(sessionId) {
  return request({
    url: `/api/chat/sessions/${sessionId}`,
    method: 'delete'
  })
}

// 发送消息并获取回复
export function sendMessage(sessionId, content) {
  return request({
    url: `/api/chat/sessions/${sessionId}/messages`,
    method: 'post',
    data: { content }
  })
}

// 重命名会话
export function renameSession(sessionId, title) {
  return request({
    url: `/api/chat/sessions/${sessionId}/rename`,
    method: 'put',
    data: { title }
  })
}

// 更新会话关联的数据源
export function updateSessionDataSources(sessionId, dataSourceIds) {
  return request({
    url: `/api/chat/sessions/${sessionId}/datasources`,
    method: 'put',
    data: { dataSourceIds }
  })
}

// 更新会话关联的模型
export function updateSessionModel(sessionId, modelId) {
  return request({
    url: `/api/chat/sessions/${sessionId}/model`,
    method: 'put',
    data: { modelId }
  })
} 