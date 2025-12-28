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

    <!-- 实现一个柱状图，用来显示测试计划每次执行的结果，比如： 2022-01-01 测试计划执行了20个用例，测试计划通过率是50%，
     通过的2次，失败2次 -->

    <!-- 添加柱状图 -->
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <div ref="barChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <div ref="lineChart" style="width: 100%; height: 400px;"></div>
        </el-card>
      </el-col>
    </el-row>
  <!-- END 添加柱状图 -->

      <!-- 失败率最高的5个用例-->
    <el-card style="margin-top: 20px;">
      <div slot="header" class="clearfix">
        <span>失败率最高的5个用例</span>
      </div>
      <el-table :data="failedCases" style="width: 100% ;margin-top: 10px;">
        <el-table-column prop="name" label="用例名称"></el-table-column>
        <el-table-column prop="fail_count" label="失败次数"></el-table-column>
      </el-table>
    </el-card>
    <!-- END 失败率最高的5个用例 -->



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


// --------------------扩展： 添加图标--------------------
import { onMounted } from "vue";
import { queryPlanTrend } from "./ApiPlanChart";  // 引入查询计划趋势接口
import * as echarts from 'echarts';
// 柱状图
const barChart = ref([]); // 引用的数据
const chartInstance = ref(null); // ECharts 实例
// 折线图
const lineChart = ref([]);
const lineChartInstance = ref(null); // ECharts 实例


// 通知加载Echart插件
// 生命周期钩子
// 当组件被挂载到 DOM 后自动执行其中的代码
// 确保在操作 DOM 元素前，它们已经被渲染完成
onMounted(() => {
  // 用来存放柱状图数据
  chartInstance.value = echarts.init(barChart.value);
  // 用来存放折线图数据
  lineChartInstance.value = echarts.init(lineChart.value);
  // 立即加载数据并渲染图表
  loadData()
});

// 加载柱状图
function queryPlanTrends() {
  queryPlanTrend(coll_id).then(response => {
    //返回柱状图数据,将返回数据绑定到 barChart变量中
    console.log(response.data.data);
    const data = response.data.data;
   
    const planNames = data.map(item => `${item.name}\n${item.date}`);
    const passedData = data.map(item => item.passed || 0);
    const failedData = data.map(item => item.failed || 0);
    const brokenData = data.map(item => item.broken || 0);
    const skippedData = data.map(item => item.skipped || 0);
    const unknownData = data.map(item => item.unknown || 0);

    // 定义每种状态的颜色
    const colors = {
      passed: '#91cc75',
      failed: '#ee6666',
      broken: '#fac858',  
      skipped: '#5470c6',
      unknown: '#73c0de'
    };

    // 设置 ECharts 选项
    const option = {
      title: {
        text: '最近5次计划执行结果趋势'
      },
      tooltip: {
        trigger: 'axis'
      },
      legend: {
        data: ['通过', '失败', '中断', '跳过', '未知'],
        bottom: 0,
      },
      xAxis: {
        type: 'category',
        data: planNames
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          name: '通过',
          type: 'bar',
          data: passedData,
          itemStyle: {
            color: colors.passed
          }
        },
        {
          name: '失败',
          type: 'bar',
          data: failedData,
          itemStyle: {
            color: colors.failed
          }
        },
        {
          name: '中断',
          type: 'bar',
          data: brokenData,
          itemStyle: {
            color: colors.broken
          }
        },
        {
          name: '跳过',
          type: 'bar',
          data: skippedData,
          itemStyle: {
            color: colors.skipped
          }
        },
        {
          name: '未知',
          type: 'bar',
          data: unknownData,
          itemStyle: {
            color: colors.unknown
          }
        }
      ]
    };

    // 设置 ECharts 选项并渲染图表
    if (chartInstance.value) {
      chartInstance.value.setOption(option);
    }
  })
}

// 加载折线图
//生成线图，x轴为时间 Y轴为执行时间
import { queryPlanTime } from "./ApiPlanChart";  // 引入查询计划趋势接口
function queryPlanTimes() {
  queryPlanTime(coll_id).then(response => {
    const data = response.data.data;
    // 获取对应的数据
    const dates = data.map(item => item.date);
    const durations = data.map(item => item.duration);
    
    // 设置 ECharts 选项
    const option = {
      title: {
        text: '最近10次计划执行时间趋势'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value',
        name: '执行时间 (ms)'
      },
      series: [
        {
          name: '执行时间',
          type: 'line',
          data: durations,
          itemStyle: {
            color: '#5470c6'
          },
          smooth: true // 平滑曲线
        }
      ]
    };
      // 设置 ECharts 选项并渲染图表
    if (lineChartInstance.value) {
      lineChartInstance.value.setOption(option);
    }
  });
}


function loadData(){
  queryPlanCounts()
  queryCaseCounts()
  queryPassRates()
  queryPlanTrends()
  queryPlanTimes()
  queryFailTop5s()
}

// loadData()

// --------------------END 扩展： 添加图标--------------------


// --------------------扩展： 添加显示失败的前五个用例--------------------
import { queryFailTop5 } from "./ApiPlanChart";
const failedCases = ref([]);
// 完成失败率5个
function queryFailTop5s() {
  queryFailTop5(coll_id).then(response => {
    failedCases.value = response.data.data;
  });
}
// --------------------END 扩展： 添加显示失败的前五个用例--------------------

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