import request from '~/axios'

export default {
    queryByPage(data) {
        return request.post('/dept/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/dept/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/dept/insert', data)
    },

    updateData(data) {
        return request.put('/dept/update', data)
    },

    deleteData(id) {
        return request.delete(`/dept/delete?id=${id}`)
    },

    queryTree(params) {
        return request.get('/dept/queryTree', { params })
    }
}
