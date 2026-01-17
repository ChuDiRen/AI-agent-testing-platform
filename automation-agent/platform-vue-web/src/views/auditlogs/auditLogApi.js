import request from '~/axios'

export default {
    queryByPage(data) {
        return request.post('/auditlog/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/auditlog/queryById?id=${id}`)
    },

    deleteData(id) {
        return request.delete(`/auditlog/delete?id=${id}`)
    },

    clearData() {
        return request.post('/auditlog/clear')
    }
}
