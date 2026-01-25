import request from '@/axios'

export default {
    queryByPage(data) {
        return request.post('/api/v1/api/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/api/v1/api/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/api/v1/api/insert', data)
    },

    updateData(data) {
        return request.put('/api/v1/api/update', data)
    },

    deleteData(id) {
        return request.delete(`/api/v1/api/delete?id=${id}`)
    },

    refreshApi(data) {
        return request.post('/api/v1/api/refresh', data)
    }
}
