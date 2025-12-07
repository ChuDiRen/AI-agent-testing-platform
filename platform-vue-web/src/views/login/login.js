import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "login"

/**
 * 用户登录 - 只返回 access_token
 * @param {String} username - 用户名
 * @param {String} password - 密码
 */
export function login(username, password) {
    return axios.post(`/${module_name}?_alias=user-login`, {
        username,
        password
    })
}

/**
 * 获取当前用户信息 - 通过 token 获取
 */
export function getUserInfo() {
    return axios.get('/userinfo')
}