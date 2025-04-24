import { createPinia } from 'pinia'
import { defineStore } from 'pinia'

// 创建会话相关的状态管理
export const useSessionStore = defineStore('session', {
  state: () => ({
    // 当前所有会话
    sessions: [],
    // 当前活跃会话ID
    activeSessionId: null,
    // 每个会话关联的数据源
    sessionDataSources: {},
    // 每个会话关联的模型
    sessionModels: {},
  }),
  
  getters: {
    // 获取当前活跃会话
    currentSession: (state) => {
      return state.sessions.find(session => session.id === state.activeSessionId) || null
    },
    
    // 获取会话关联的数据源
    getSessionDataSources: (state) => (sessionId) => {
      return state.sessionDataSources[sessionId] || []
    },
    
    // 获取会话关联的模型
    getSessionModel: (state) => (sessionId) => {
      return state.sessionModels[sessionId] || null
    }
  },
  
  actions: {
    // 添加新会话
    addSession(session) {
      this.sessions.unshift(session)
      this.activeSessionId = session.id
      // 初始化会话的数据源和模型关联
      this.sessionDataSources[session.id] = session.dataSourceIds || []
      this.sessionModels[session.id] = session.modelId || null
    },
    
    // 设置活跃会话
    setActiveSession(sessionId) {
      this.activeSessionId = sessionId
    },
    
    // 更新会话关联的数据源
    updateSessionDataSources(sessionId, dataSourceIds) {
      this.sessionDataSources[sessionId] = dataSourceIds
    },
    
    // 更新会话关联的模型
    updateSessionModel(sessionId, modelId) {
      this.sessionModels[sessionId] = modelId
    },
    
    // 删除会话
    removeSession(sessionId) {
      const index = this.sessions.findIndex(session => session.id === sessionId)
      if (index !== -1) {
        this.sessions.splice(index, 1)
        // 如果删除的是当前活跃会话，则切换到第一个会话
        if (this.activeSessionId === sessionId) {
          this.activeSessionId = this.sessions.length > 0 ? this.sessions[0].id : null
        }
        // 清理该会话的关联数据
        delete this.sessionDataSources[sessionId]
        delete this.sessionModels[sessionId]
      }
    },
    
    // 添加消息到会话
    addMessageToSession(sessionId, message) {
      const session = this.sessions.find(s => s.id === sessionId)
      if (session) {
        if (!session.messages) {
          session.messages = []
        }
        session.messages.push(message)
        session.updatedAt = new Date().toISOString()
        session.messageCount = session.messages.length
      }
    }
  }
})

// 创建Pinia实例
const pinia = createPinia()

export default pinia 