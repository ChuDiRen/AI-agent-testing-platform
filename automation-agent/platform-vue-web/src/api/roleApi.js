import request from '@/axios'

export default {
    queryByPage(data) {
        return request.post('/api/v1/role/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/api/v1/role/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/api/v1/role/insert', data)
    },

    updateData(data) {
        return request.put('/api/v1/role/update', data)
    },

    deleteData(id) {
        return request.delete(`/api/v1/role/delete?id=${id}`)
    },

    queryMenus(id) {
        return request.get(`/api/v1/role/queryMenus?id=${id}`)
    },

    updateMenus(data) {
        return request.put('/api/v1/role/updateMenus', data)
    },

    queryApis(id) {
        return request.get(`/api/v1/role/queryApis?id=${id}`)
    },

    updateApis(data) {
        return request.put('/api/v1/role/updateApis', data)
    },

    getRoleAuthorized(params) {
        return request.get('/api/v1/role/authorized', { params })
    },

    updateRoleAuthorized(data) {
        return request.post('/api/v1/role/updateAuthorized', data)
    },

    queryAll() {
        return request.get('/api/v1/role/queryAll')
    }
}
