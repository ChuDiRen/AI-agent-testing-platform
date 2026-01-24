import request from '~/axios'

export default {
    login(data) {
        return request.post('/api/v1/login', data)
    },

    getUserInfo() {
        return request.get('/api/v1/user/userinfo')
    },

    getUserMenu() {
        return request.get('/api/v1/user/usermenu')
    },

    getUserApi() {
        return request.get('/api/v1/user/userapi')
    },

    checkPermission(permission) {
        return request.post('/api/v1/check', { permission })
    },

    changePassword(data) {
        return request.post('/api/v1/change-password', data)
    }
}
