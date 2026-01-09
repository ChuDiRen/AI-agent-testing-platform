import axios from "~/axios"

const module_name = "menus" // 模块名

// 获取菜单树
export function getMenuTree() {
    return axios.get(`/${module_name}/tree?_alias=menu-tree`)
}

// 根据ID查询菜单
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=menu-detail`)
}

// 新增菜单
export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=menu-insert`, data)
}

// 更新菜单
export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=menu-update`, data)
}

// 删除菜单
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=menu-delete`)
}

// 获取用户的菜单权限（用于动态路由）
export function getUserMenus(userId) {
    return axios.get(`/${module_name}/user/${userId}?_alias=user-menus`)
}

