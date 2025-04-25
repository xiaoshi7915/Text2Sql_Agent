import { get, post, put, del } from './request'

// 获取所有数据源列表
export function getDatasources() {
  return get('/datasources/list')
}

// 获取单个数据源详情
export function getDatasource(id) {
  return get(`/datasources/${id}`)
}

// 创建新的数据源
export function createDatasource(data) {
  return post('/datasources/', data)
}

// 更新数据源信息
export function updateDatasource(id, data) {
  return put(`/datasources/${id}`, data)
}

// 删除数据源
export function deleteDatasource(id) {
  return del(`/datasources/${id}`)
}

// 测试数据源连接
export function testDatasourceConnection(data) {
  return post('/datasources/test-connection', data)
}

// 获取表结构
export function getTableSchema(datasourceId, table) {
  return get(`/datasources/${datasourceId}/schema`, { table })
}

// 获取数据源所有表
export function getTables(datasourceId) {
  return get(`/datasources/${datasourceId}/tables`)
}

// 查询数据样例
export function querySampleData(datasourceId, table, limit = 10) {
  return get(`/datasources/${datasourceId}/sample`, { table, limit })
} 