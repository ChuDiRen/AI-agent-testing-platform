import request from '~/axios'

export default {
    queryByPage(data) {
        return request.post('/user/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/user/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/user/insert', data)
    },

    updateData(data) {
        return request.put('/user/update', data)
    },

    deleteData(id) {
        return request.delete(`/user/delete?id=${id}`)
    },

    resetPassword(data) {
        return request.post('/user/resetPassword', data)
    }
}
