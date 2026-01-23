import axios from "~/axios"

// 模块名 - 和后台对应
const module_name = "ApiInfoCase"

// 标准 - 增删改查接口调用
export function queryByPage(data) {
    return axios.post(`/${module_name}/queryByPage`, data)
}

export function queryById(id) {
    return axios.get(`/${module_name}/queryById?id=${id}`)
}

export function insertData(data) {
    return axios.post(`/${module_name}/insert`, data)
}

export function updateData(data) {
    return axios.put(`/${module_name}/update`, data)
}

export function deleteData(id){
    return axios.delete(`/${module_name}/delete?id=${id}`)
}

// 拓展其他方法
// 扩展-调试方法
export function excuteTest(data){
    return axios.post(`/${module_name}/debugTest`, data)
}


//文件上传处理
export function uploadXmindFile(data) {
    return axios.post(`/${module_name}/uploadFile`, data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }

// 下载模板
export function downloadTemplate() {
    return axios.get(`/${module_name}/downloadTemplate`, {
      responseType: 'blob'
    });
  }