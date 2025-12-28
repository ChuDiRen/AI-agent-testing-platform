
<template>
    <!-- 面包屑导航 -->
    <Breadcrumb />
    <!-- 搜索表单 -->
    <el-form :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="用户名">
            <el-input v-model="searchForm.username" placeholder="根据用户名筛选" />
        </el-form-item>
        <el-row class="mb-4" type="flex" justify="end"> <!-- 居右 type="flex" justify="end" -->
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
    </el-form>
    <!-- END 搜索表单 -->

      <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <!-- 数据列 -->
        <!-- 默认情况下，如果单元格内容过长，会占用多行显示。 若需要单行显示可以使用 show-overflow-tooltip -->
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
            show-overflow-tooltip="true" />
        <!-- 操作 -->
        <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button link type="primary" size="small" @click.prevent="onDataForm(scope.$index)">
                    编辑
                </el-button>
                <el-button link type="primary" size="small" @click.prevent="onDelete(scope.$index)">
                    删除
                </el-button>
            </template>
        </el-table-column>
    </el-table>
    <!--END  数据表格 -->

    <!-- 分页 -->
    <div class="demo-pagination-block">
        <el-pagination 
        v-model:current-page="currentPage" 
        v-model:page-size="pageSize" 
        :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total" @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>
    <!-- END 分页 -->

</template>


<script lang="ts" setup>
import { ref, reactive } from "vue"
import { useRouter } from "vue-router";
import { queryByPage, deleteData } from './user' // 不同页面不同的接口
import Breadcrumb from "../Breadcrumb.vue"; // 面包屑导航，导入

const router = useRouter()

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索功能 - 筛选表单
const searchForm = reactive({"username":""})

// --------------功能1 ：扩展查询--------------
// 表格数据
const tableData = ref([])

// 加载页面数据
const loadData = () => {
    let searchData = searchForm
    searchData["page"] = currentPage.value
    searchData["pageSize"] = pageSize.value

    queryByPage(searchData).then((res: { data: { data: never[]; total: number; msg: string }; }) => {
        tableData.value = res.data.data
        // 分页用到该数据
        total.value = res.data.total  

        console.log("当前查询出来的数据")
        console.log(res.data.data)
    })


}
loadData()
// --------------END 功能1 ：扩展查询--------------


// --------------功能2 ：数据回显--------------
// 表格列 - 不同页面不同的列,注意要和对应的返回数据key一致
const columnList = ref([
    { prop: "id", label: '用户ID' },
    { prop: "username", label: '用户名' },
    // { prop: "password", label: '密码' },
    { prop: "create_time", label: '创建时间' }
])
// --------------END 功能2 ：数据回显--------------


// --------------功能3 ：删除数据--------------
const onDelete = (index: number) => {
    deleteData(tableData.value[index]["id"]).then((res: {}) => {
        loadData()
    })
}
// --------------END 功能3 ：删除数据--------------


// --------------功能4 ：页码功能--------------
// 变更 页大小
const handleSizeChange = (val: number) => {
    console.log("页大小变化:" + val)
    pageSize.value = val
    loadData()
}
// 变更 页码
const handleCurrentChange = (val: number) => {
    console.log("页码变化:" + val)
    currentPage.value = val
    loadData()
}
// --------------END 功能4 ：页码功能--------------


// --------------功能5 ：打开表单 （编辑/新增）--------------
const onDataForm = (index: number) => {
    let params_data = {}
    if (index >= 0) {
        params_data = {
            id: tableData.value[index]["id"]
        }
    }
    router.push({
        path: 'userForm', // 不同页面不同的表单路径
        query: params_data
    });
}
// --------------END 功能5 ：打开表单 （编辑/新增）--------------
</script>

<style scoped>
.demo-pagination-block{
    margin-top: 20px;
}
</style>