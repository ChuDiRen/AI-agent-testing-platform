import request from '~/axios'

export default {
    login(data) {
        return request.post('/login', data)
    },

    getUserInfo() {
        return request.get('/permission/userinfo')
    },

    getUserMenu() {
        return request.get('/permission/usermenu')
    },

    getUserApi() {
        return request.get('/permission/userapi')
    },

    checkPermission(permission) {
        return request.post('/permission/check', { permission })
    },

    changePassword(data) {
        return request.post('/permission/change-password', data)
    }
}
