import request from '~/axios'

export default {
    queryByPage(data) {
        return request.post('/api/v1/menu/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/api/v1/menu/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/api/v1/menu/insert', data)
    },

    updateData(data) {
        return request.put('/api/v1/menu/update', data)
    },

    deleteData(id) {
        return request.delete(`/api/v1/menu/delete?id=${id}`)
    },

    queryTree() {
        return request.get('/api/v1/menu/queryTree')
    }
}
