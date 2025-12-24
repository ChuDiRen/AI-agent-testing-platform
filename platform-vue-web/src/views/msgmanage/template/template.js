import axios from "~/axios"

// 消息模板管理 API
const base_path = "/msgmanage/template"

// 分页查询模板
export function queryByPage(data) {
    return axios.post(`${base_path}/queryByPage?_alias=msg-template-page`, data)
}

// 根据ID查询
export function queryById(id) {
    return axios.get(`${base_path}/queryById?id=${id}&_alias=msg-template-detail`)
}

// 根据编码查询
export function queryByCode(templateCode) {
    return axios.get(`${base_path}/queryByCode?template_code=${templateCode}&_alias=msg-template-code`)
}

// 新增模板
export function insertData(data) {
    return axios.post(`${base_path}/insert?_alias=msg-template-insert`, data)
}

// 更新模板
export function updateData(data) {
    return axios.put(`${base_path}/update?_alias=msg-template-update`, data)
}

// 删除模板
export function deleteData(id) {
    return axios.delete(`${base_path}/delete?id=${id}&_alias=msg-template-delete`)
}

// 预览模板
export function previewTemplate(data) {
    return axios.post(`${base_path}/preview?_alias=msg-template-preview`, data)
}

// 渲染模板
export function renderTemplate(data) {
    return axios.post(`${base_path}/render?_alias=msg-template-render`, data)
}

// 获取模板类型列表
export function getTemplateTypes() {
    return axios.get(`${base_path}/types?_alias=msg-template-types`)
}

// 获取渠道类型列表
export function getChannelTypes() {
    return axios.get(`${base_path}/channels?_alias=msg-template-channels`)
}
