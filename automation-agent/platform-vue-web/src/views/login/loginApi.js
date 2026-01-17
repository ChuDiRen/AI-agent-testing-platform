import request from '~/axios'

export default {
    login(data) {
        return request.post('/login', data)
    },

    getUserInfo() {
        return request.get('/userinfo')
    },

    getUserMenu() {
        return request.get('/usermenu')
    },

    getUserApi() {
        return request.get('/userapi')
    },

    updatePassword(data) {
        return request.post('/updatePassword', data)
    }
}
