import { post, get } from './request'

/**
 * 用户登录
 * @param {Object} data - 登录信息
 * @param {string} data.username - 用户名
 * @param {string} data.password - 密码
 * @param {boolean} data.remember - 是否记住我
 * @returns {Promise} - 登录请求的Promise
 */
export function login(data) {
  return post('/auth/login', data)
}

/**
 * 用户登出
 * @returns {Promise} - 登出请求的Promise
 */
export function logout() {
  return post('/auth/logout')
}

/**
 * 获取当前登录用户信息
 * @returns {Promise} - 获取用户信息的Promise
 */
export function getUserInfo() {
  return get('/auth/user-info')
}

/**
 * 刷新Token
 * @returns {Promise} - 刷新Token的Promise
 */
export function refreshToken() {
  return post('/auth/refresh-token')
}

/**
 * 修改密码
 * @param {Object} data - 密码信息
 * @param {string} data.oldPassword - 旧密码
 * @param {string} data.newPassword - 新密码
 * @param {string} data.confirmPassword - 确认新密码
 * @returns {Promise} - 修改密码请求的Promise
 */
export function changePassword(data) {
  return post('/auth/change-password', data)
} 