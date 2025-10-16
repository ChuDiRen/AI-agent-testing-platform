import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "login"

/**
 * 用户登录
 * @param {String} username - 用户名
 * @param {String} password - 密码
 */
export function login(username, password) {
    return axios.post(`/${module_name}`, {
        username,
        password
    })
}