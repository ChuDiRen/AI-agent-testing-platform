import request from '~/axios'

export default {
    queryByPage(data) {
        return request.post('/api/v1/dept/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/api/v1/dept/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/api/v1/dept/insert', data)
    },

    updateData(data) {
        return request.put('/api/v1/dept/update', data)
    },

    deleteData(id) {
        return request.delete(`/api/v1/dept/delete?id=${id}`)
    },

    queryTree(params) {
        return request.get('/api/v1/dept/queryTree', { params })
    }
}
