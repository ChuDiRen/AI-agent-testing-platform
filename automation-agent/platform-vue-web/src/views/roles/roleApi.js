import request from '~/axios'

export default {
    queryByPage(data) {
        return request.post('/role/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/role/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/role/insert', data)
    },

    updateData(data) {
        return request.put('/role/update', data)
    },

    deleteData(id) {
        return request.delete(`/role/delete?id=${id}`)
    },

    queryMenus(id) {
        return request.get(`/role/queryMenus?id=${id}`)
    },

    updateMenus(data) {
        return request.put('/role/updateMenus', data)
    },

    queryApis(id) {
        return request.get(`/role/queryApis?id=${id}`)
    },

    updateApis(data) {
        return request.put('/role/updateApis', data)
    },

    getRoleAuthorized(params) {
        return request.get('/role/authorized', { params })
    },

    updateRoleAuthorized(data) {
        return request.post('/role/updateAuthorized', data)
    }
}
