<template>
  <div class="button-container">
    <!--返回按钮 不写一个button 而是一个超链接-->
    <el-link type="primary" icon="el-icon-arrow-right" @click="goBack" :underline="false"><<返回主页面</el-link>
  </div>

  <div class="web-plan-chart">
    <!-- 统计信息  -->
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <p>测试计划执行次数</p>
            <h3>{{ executionCount }}</h3>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <p>最近一次计划测试用例总数</p>
            <h3>{{ testCaseCount }}</h3>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <div class="stat-item">
            <p>测试计划通过率</p>
            <h3>{{ passRate }}%</h3>
          </div>
        </el-card>
      </el-col>
    </el-row>


  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter  } from "vue-router";


const router = useRouter();

 function goBack() {
      // 实现返回功能
     router.push("/ApiCollectionInfoList");
  }



//定义执行次数数据
const executionCount = ref(0)
//定义最近一次执行用例总数
const testCaseCount = ref(0)
//定义通过率数据
const passRate = ref(0)

//  报表1： 加载【测试计划执行次数】
import { queryPlanCount } from "./ApiPlanChart";
let coll_id = router.currentRoute.value.query.id;
function queryPlanCounts() {
  queryPlanCount(coll_id).then(response => {
    console.log(response.data.data);
    executionCount.value = response.data.data;
  });
}

//定义最近一次执行用例总数
import { queryCaseCount } from "./ApiPlanChart";
function queryCaseCounts() {
  queryCaseCount(coll_id).then(response => {
    testCaseCount.value = response.data.data;
  });
}

//定义通过率数据
import { queryPassRate } from "./ApiPlanChart";
function queryPassRates() {
  queryPassRate(coll_id).then(response => {
    passRate.value = response.data.data;
  });
}


function loadData(){
  queryPlanCounts()
  queryCaseCounts()
  queryPassRates()
}

loadData()


</script>

<style scoped>
.button-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
}
.stat-item p {
  margin-bottom: 10px;
}
</style>