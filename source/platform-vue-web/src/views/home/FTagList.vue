<template>
    <div class="f-tag-list" :style="{ left:$store.state.asideWidth }">
        
        <!-- 使用<v-model>绑定对应的对象-->
        <el-tabs v-model="activeTab" type="card" class="flex-1"  @tab-remove="removeTab" style="min-width:100px;" @tab-change="changeTab">

            <!-- v-for 表示循环，自动生成对应的面板，:closable表示为/的路径不允许屏蔽-->
            <el-tab-pane v-for="item in tabList"   :closable="item.path!='/'"   :key="item.path" :label="item.title" :name="item.path"></el-tab-pane>
        </el-tabs>
        <!--这里是下拉选项的标准写法-->
        <!-- <span class="tag-btn">
            <el-dropdown>
                <span class="el-dropdown-link">
                    <el-icon>
                        <arrow-down />
                    </el-icon>
                </span>
                <template #dropdown>
                    <el-dropdown-menu>
                        <el-dropdown-item>关闭其他 </el-dropdown-item>
                        <el-dropdown-item>全部关闭 </el-dropdown-item>
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </span> -->

    </div>
    <div style="height: 44px;"></div>
</template>

<script setup>
import { ref } from 'vue'
//这里要后期绑定对应的跳转流程，所以这里需要写下来
import { useRoute,onBeforeRouteUpdate,useRouter } from 'vue-router';
//引入cookie用来保存已经打开的页签
import { useCookies } from '@vueuse/integrations/useCookies';
// import * as router  from '../../router/index.js'

const route = useRoute()
const cookies = useCookies()
const router = useRouter()


// 定义好当前绑定的数据就是route中的path
const activeTab = ref(route.path)
//  修改js逻辑处理流程 --让它与path挂钩
const tabList = ref([
    {
        title: '主页信息',
        path:"/Statistics"
    }
])

function addTab(tab){

   if(!tab.path.endsWith("Form")){
   let noTab =  tabList.value.findIndex(t=>t.path==tab.path) == -1 //判断是不是有这个tab了
   if(noTab){
     //如果noTab为True就表示没有Tab
     tabList.value.push(tab)
   }
   cookies.set("tabList",tabList.value)
    }
}

onBeforeRouteUpdate((to)=>{
    if(!to.path.endsWith("Form")){
    activeTab.value = to.path
  addTab({
    title:to.meta.title,
    path:to.path
  })
}
})

const changeTab = (t)=>{
    if(!t.endsWith("Form")){
      activeTab.value = t
      try{
        if(t !== route.path){
          router.replace(t) // 避免重复导航与历史堆叠
        }
      }catch(error){
        console.log("发生异常:",error)
      }
    }
}

// 初始化标签导航列表
function initTabList(){
    const tbs = cookies.get("tabList")
    if(tbs){
        tabList.value = tbs
    } else {
        // 首次打开不主动导航，避免与路由重定向/其它导航冲突
        activeTab.value = route.path || tabList.value[0].path
    }
}

initTabList()

const removeTab = (t) => {
    let tabs = tabList.value
    if(t == tabs[0].path) return // 第一个tab不允许删除
    let a = activeTab.value
    if(a == t){
        tabs.forEach((tab,index)=>{
            if(tab.path == t){
                const nextTab = tabs[index+1] || tabs[index-1]
                if(nextTab){
                    a = nextTab.path
                }
            }
        })
    }

    changeTab(a)
    tabList.value = tabList.value.filter(tab=>tab.path != t)

    cookies.set("tabList",tabList.value)
}
</script>
<style scoped>
.f-tag-list{
    @apply fixed bg-gray-100 flex items-center px-2;
    top: 64px;
    right: 0;
    height: 44px;
    left:260px;
    z-index: 100;
}
.tag-btn{
    @apply bg-white rounded ml-auto flex items-center justify-center px-2;
    height: 32px;
}
:deep(.el-tabs__header){
    @apply mb-0;
}
:deep(.el-tabs__nav){
    border: 0!important;
}
:deep(.el-tabs__item){
    border: 0!important;
    height: 32px;
    line-height: 32px;
    @apply bg-white mx-1 rounded;
}
:deep(.el-tabs__nav-next),:deep(.el-tabs__nav-prev){
    line-height: 32px;
    height: 32px;
}
:deep(.is-disabled){
    cursor: not-allowed;
    @apply text-gray-300;
}
</style>