import request from '~/axios'

export default {
    queryByPage(data) {
        return request.post('/menu/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/menu/queryById?id=${id}`)
    },

    insertData(data) {
        return request.post('/menu/insert', data)
    },

    updateData(data) {
        return request.put('/menu/update', data)
    },

    deleteData(id) {
        return request.delete(`/menu/delete?id=${id}`)
    },

    queryTree() {
        return request.get('/menu/queryTree')
    }
}
