import apiClient from './index'

export const villageApi = {
  // 获取村庄列表
  getList() {
    return apiClient.get('/villages')
  },

  // 新增村庄
  create(data) {
    return apiClient.post('/villages', data)
  },

  // 更新村庄
  update(id, data) {
    return apiClient.put(`/villages/${id}`, data)
  },

  // 删除村庄
  delete(id) {
    return apiClient.delete(`/villages/${id}`)
  }
}