import axios from "~/axios"

const module_name = "role" // 模块名

// 分页查询角色
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage?_alias=role-page`, data)
}

// 根据ID查询角色
export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}&_alias=role-detail`)
}

// 新增角色
export function insertData(data) {
    return axios.post(`/${module_name}/insert?_alias=role-insert`, data)
}

// 更新角色
export function updateData(data) {
    return axios.put(`/${module_name}/update?_alias=role-update`, data)
}

// 删除角色
export function deleteData(id) {
    return axios.delete(`/${module_name}/delete?id=${id}&_alias=role-delete`)
}

// 为角色分配菜单权限
export function assignMenus(data) {
    return axios.post(`/${module_name}/assignMenus?_alias=role-assign-menus`, data)
}

// 获取角色的菜单权限
export function getRoleMenus(roleId) {
    return axios.get(`/${module_name}/menus/${roleId}?_alias=role-menus`)
}

