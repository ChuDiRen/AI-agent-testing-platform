<template>
  <!-- 面包屑导航 -->
  <Breadcrumb />
    <!-- 搜索表单 -->
    <el-form ref="searchFormRef" :inline="true" :model="searchForm" class="demo-form-inline">
        <el-form-item label="集合名称：">
            <el-input v-model="searchForm.collection_name" placeholder="根据集合名称筛选" />
        </el-form-item>
        <el-form-item label="所属项目：">
            <el-select v-model="searchForm.project_id" placeholder="选择所属项目" clearable>
                <el-option v-for="project in projectList" :key="project.id" :label="project.project_name"
                    :value="project.id" />
            </el-select>
        </el-form-item>
        <!-- 这里可以根据需要添加其他搜索条件 -->
        <el-row class="mb-4" type="flex" justify="end">
            <el-button type="primary" @click="loadData()">查询</el-button>
            <el-button type="warning" @click="onDataForm(-1)">新增数据</el-button>
        </el-row>
    </el-form>
    <!-- END 搜索表单 -->

    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%;" max-height="500">
        <!-- 数据列 -->
        <!-- 默认情况下，如果单元格内容过长，会占用多行显示。 若需要单行显示可以使用 :show-overflow-tooltip -->
        <el-table-column v-for="col in columnList" :prop="col.prop" :label="col.label" :key="col.prop"
            :show-overflow-tooltip="true" />

        <!-- 操作 -->
        <el-table-column fixed="right" label="操作">
            <template #default="scope">
                <el-button link type="primary" size="small" @click="showWebPlanChart(scope.$index)">
                <el-icon><PieChart /></el-icon>
                </el-button>

                <el-button link type="primary" size="small" @click="okExecuteTest(scope.$index)">
                    执行测试计划
                </el-button>
                <el-button link type="primary" size="small" @click="showApiHistorysDialog(scope.$index)">
                    执行记录
                </el-button>
                <el-button link type="primary" size="small" @click="onDataForm(scope.$index)">
                    编辑
                </el-button>



                <el-button link type="primary" size="small" @click="copyCollection(scope.$index)">
                复制计划
                 </el-button>
                <el-button link type="primary" size="small" @click="onDelete(scope.$index)">
                    删除
                </el-button>
            </template>
        </el-table-column>
    </el-table>
    <!-- END 数据表格 -->

    <!-- 分页 -->
    <div class="demo-pagination-block">
        <div class="demonstration"></div>
        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 20, 30, 50]"
            layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
            @current-change="handleCurrentChange" />
    </div>
    <!-- END 分页 -->

        <!-- 弹窗 - 弹窗加载执行记录 -->
    <el-dialog v-model="apiHistoryDialogFormVisible" title="执行记录">
        <el-form-item>
            <el-table :data="apiHistoryList" style="width: 100%">
                <el-table-column prop="id" label="用例编号" style="width: 5%" />
                <el-table-column prop="create_time" label="执行时间" style="width: 30%" show-overflow-tooltip="true" />
                <el-table-column prop="history_desc" label="执行情况简述" style="width: 60%" show-overflow-tooltip="true" />
                <el-table-column fixed="right" label="操作" style="width: 5%">
                    <template #default="scope">
                        <el-button type="primary" size="small" @click.prevent="showApiHistory(scope.$index)">
                            查看测试报告
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </el-form-item>

        <el-form-item>
            <el-pagination 
                           :current-page="currentApiHistoryPage" 
                           :page-size="apiHistoryPageSize" 
                           :total="apiHistoryTotal"
                           @current-change="handleApiHistoryCurrentChange">
            </el-pagination>
        </el-form-item>
    </el-dialog>

</template>

<script lang="ts" setup>
import { ref, reactive } from "vue"
import { queryByPage, deleteData} from './ApiCollectionInfo.js' // 不同页面不同的接口
import { useRouter } from "vue-router";
import Breadcrumb from "../../Breadcrumb.vue";
const router = useRouter()

// 分页参数
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 搜索功能 - 筛选表单
const searchForm = reactive({ "collection_name": "", "project_id": "" })

// 表格列 - 不同页面不同的列
const columnList = ref([
    { prop: "id", label: '集合编号' },
    { prop: "collection_name", label: '集合名称' },
    // 其他列
])

// 表格数据
const tableData = ref([])

// 加载页面数据
const loadData = () => {
    let searchData = searchForm
    searchData["page"] = currentPage.value
    searchData["pageSize"] = pageSize.value

    queryByPage(searchData).then((res: { data: { data: never[]; total: number; msg: string }; }) => {
        tableData.value = res.data.data
        total.value = res.data.total
    })
}
loadData()

// 变更页大小
const handleSizeChange = (val: number) => {
    console.log("页大小变化:" + val)
    pageSize.value = val
    loadData()
}

// 变更页码
const handleCurrentChange = (val: number) => {
    console.log("页码变化:" + val)
    currentPage.value = val
    loadData()
}


// 打开表单 （编辑/新增）
const onDataForm = (index: number) => {
    let params_data = {}
    if (index >= 0) {
        params_data = {
            id: tableData.value[index]["id"]
        }
    }
    router.push({
        path: '/ApiCollectionInfoForm', // 不同页面不同的表单路径
        query: params_data
    });
}

// 删除数据
const onDelete = (index: number) => {
    deleteData(tableData.value[index]["id"]).then((res: {}) => {
        loadData()
    })
}

// 其他功能拓展
// 1. 加载项目
import { queryAllProject } from "../project/ApiProject.js"; // 不同页面不同的接口
const projectList = ref([{
    id: 0,
    project_name: '',
    project_desc: ''
}]);
function getProjectList() {
    queryAllProject().then((res) => {
        projectList.value = res.data.data;
    });
}
getProjectList();


// -----------------------------扩展功能1-执行测试用例 --------------------------------
import { ElMessage, ElMessageBox } from 'element-plus';
import { excuteTest } from "./ApiCollectionInfo.js"; // 不同页面不同的接口
const okExecuteTest = (value: number) => {
    // 开始执行测试计划
    ElMessage.success('开始执行：'+tableData.value[value].collection_name);
   // 确定当前执行的ID
   let searchData = reactive({}); 
   searchData["id"] =  tableData.value[value].id;
   // 调用执行的接口，并且把需要执行的ID传递过去
   excuteTest(searchData).then((res: {}) => {
   console.log(res);
  });
};



// 执行记录加载
import { queryByPage as queryApiHistoryByPage } from "./ApiHistory.js"; // 不同页面不同的接口
const apiHistoryList = ref([] as any[]); // 关联的接口
const currentApiHistoryPage = ref(1) // 页码
const apiHistoryPageSize = ref(5) // 每页大小
const apiHistoryTotal = ref(0)
const apiHistoryDialogFormVisible = ref(false) // 是否展示弹窗
const currentCollectionId = ref(0) // 当前展示的执行记录关联的 collectionId
const showApiHistorysDialog = (index: number) => {
    apiHistoryDialogFormVisible.value = true
    apiHistoryTotal.value = 0
    apiHistoryPageSize.value = 5
    currentApiHistoryPage.value = 1
    apiHistoryList.value = []
    currentCollectionId.value = tableData.value[index]["id"]
    loadApiHistorys()
}

// 根据分页参数 加载数据
function loadApiHistorys() {
    let searchData = {}
    searchData["collection_info_id"] = currentCollectionId.value
    searchData["page"] = currentApiHistoryPage.value
    searchData["pageSize"] = apiHistoryPageSize.value
    queryApiHistoryByPage(searchData).then((res: { data: { data: never[]; total: number; msg: string } }) => {
        console.log(res.data.data)
        apiHistoryList.value = res.data.data
        apiHistoryTotal.value = res.data.total
    })
}

// 翻页
const handleApiHistoryCurrentChange = (val: number) => {
    console.log("页码变化:" + val)
    currentApiHistoryPage.value = val
    loadApiHistorys()
}

// 展示具体测试报告
const showApiHistory = (index: number) => {
    // 注意： 这个地方的测试报告服务器地址，是需要根据后端服务器修改的，这里写死了，后面要改成配置文件
    var report_id = apiHistoryList.value[index]["history_detail"]
    window.open(import.meta.env.VITE_APP_API_URL+"/ApiReportViewer/"+report_id+"/index.html", '_blank');
}


// -----------------------------扩展功能3-复制测试集合 --------------------------------
// 复制测试集合
import { copyCollectionData} from './ApiCollectionInfo.js' // 不同页面不同的接口

const copyCollection = (value: number) => {
    console.log("当前的复制的集合计划ID：",tableData.value[value].id);
    // 传查询的参数参数
    let searchData = reactive({}); 
    searchData["id"] =  tableData.value[value].id;
    // 调用复制的接口
    copyCollectionData(searchData).then((res: {}) => {
        console.log(res.data.code);
        if (res.data.code == 200) {
            // 重新拉取对应的数据列表
            loadData()
          }
       });
}
// -----------------------------END 扩展功能3-复制测试集合 --------------------------------


// -----扩展：跳转到报告页面
const showWebPlanChart = (index : number) => {
    let params_data = {}
    if (index >= 0) {
        params_data = {
            id: tableData.value[index]["id"]
        }
    }
    // 点击按钮后，跳转到对应的图表页面
    router.push({
        path: '/ApiPlanChartForm',
        query: params_data
    });
}
</script>

<style>
.demo-pagination-block+.demo-pagination-block {
    margin-top: 10px;
}

.demo-pagination-block .demonstration {
    margin-bottom: 16px;
}

/* 更改 el-select 的宽度 */  
.el-select {  
  width: 200px; /* 设置你想要的宽度 */  
} 

</style>
