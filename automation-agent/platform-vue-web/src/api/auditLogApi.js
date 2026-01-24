import request from '~/axios'

export default {
    queryByPage(data) {
        return request.post('/api/v1/auditlog/queryByPage', data)
    },

    queryById(id) {
        return request.get(`/api/v1/auditlog/queryById?id=${id}`)
    },

    deleteData(id) {
        return request.delete(`/api/v1/auditlog/delete?id=${id}`)
    },

    clearData() {
        return request.post('/api/v1/auditlog/clear')
    }
}
