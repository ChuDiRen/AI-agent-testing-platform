import request from '~/axios'

export default {
    queryByPage(data) {
        return request.post('/api/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/api/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/api/insert', data)
    },

    updateData(data) {
        return request.put('/api/update', data)
    },

    deleteData(id) {
        return request.delete(`/api/delete?id=${id}`)
    },

    refreshApi(data) {
        return request.post('/api/refresh', data)
    }
}
