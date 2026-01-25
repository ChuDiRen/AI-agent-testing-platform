import request from '@/axios'

export default {
    queryByPage(data) {
        return request.post('/api/v1/user/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/api/v1/user/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/api/v1/user/insert', data)
    },

    updateData(data) {
        return request.put('/api/v1/user/update', data)
    },

    deleteData(id) {
        return request.delete(`/api/v1/user/delete?id=${id}`)
    },

    resetPassword(data) {
        return request.post('/api/v1/user/resetPassword', data)
    }
}
