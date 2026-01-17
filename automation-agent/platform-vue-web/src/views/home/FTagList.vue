<template>
    <div class="f-tag-list" :style="{ left: asideWidth }">
        <!-- 使用<v-model>绑定对应的对象-->
        <el-tabs v-model="activeTab" type="card" class="flex-1"  @tab-remove="removeTab" style="min-width:100px;" @tab-change="changeTab">
            <!-- v-for 表示循环，自动生成对应的面板，:closable表示为/的路径不允许屏蔽-->
            <el-tab-pane v-for="item in tabList"   :closable="item.path!='/'"   :key="item.path" :label="item.title" :name="item.path"></el-tab-pane>
        </el-tabs>
        <!-- 在模板中的适当位置添加 -->
        <span class="tag-btn">
            <el-dropdown>
                <span class="el-dropdown-link">
                    <el-icon>
                        <arrow-down />
                    </el-icon>
                </span>
                <template #dropdown>
                    <el-dropdown-menu>
                            <el-dropdown-item @click="clearAll">关闭所有</el-dropdown-item>
                        <el-dropdown-item @click="clearOther">关闭其他</el-dropdown-item>
                        <!-- 可以添加全部关闭功能 -->
                    </el-dropdown-menu>
                </template>
            </el-dropdown>
        </span>
    </div>
    <div style="height: 44px;"></div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, onBeforeRouteUpdate, useRouter } from 'vue-router';
import { useCookies } from '@vueuse/integrations/useCookies';
import { useStore } from 'vuex';

const route = useRoute()
const cookies = useCookies()
const router = useRouter()
const store = useStore()

// 计算侧边栏宽度
const asideWidth = computed(() => store.state.asideWidth || '250px')

// 定义好当前绑定的数据就是route中的path
const activeTab = ref(route.path)

//  修改js逻辑处理流程 --让它与PATH挂钩
const tabList = ref([
    {
        title: '主页信息',
        path:"/Statistics"
    }
])

// 添加标签页 (addTab)
function addTab(tab){
   // 不添加以"Form"结尾的路径
   if(!tab.path.endsWith("Form")){
     // 检查是否已存在相同路径的标签
     let noTab = tabList.value.findIndex(t=>t.path==tab.path) == -1
     if(noTab){
       tabList.value.push(tab) // 添加新标签
     }
     cookies.set("tabList",tabList.value) // 保存到cookie
   }
}

// 路由更新监听
onBeforeRouteUpdate((to)=>{
    // 路由变化时更新当前标签和添加新标签
    if(!to.path.endsWith("Form")){
      activeTab.value = to.path
      addTab({
        title:to.meta.title,
        path:to.path
      })
    }
})

// 切换标签页
const changeTab = (t)=>{
    if(!t.endsWith("Form")){
      activeTab.value = t
      try{
        router.push(t) // 路由跳转
      }catch(error){
        console.log("发生异常:",error)
      }
    }
}

// 初始化标签导航列表
function initTabList(){
    // 从cookie读取标签列表
    let tbs = cookies.get("tabList")
    if(tbs){
        tabList.value = tbs
    } else { 
        // 初次打开，默认进入第一个tab
        changeTab(tabList.value[0].path)
    }
}
initTabList()

// 删除标签页 (removeTab)
const removeTab = (t) => {
    let tabs = tabList.value
    if(t == tabs[0].path) return // 禁止删除第一个标签
    
    let a = activeTab.value
    if(a == t){
        // 如果删除的是当前标签，切换到相邻标签
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
    cookies.set("tabList",tabList.value) // 更新cookie
}

// cookies全部清除但是要保留【主页信息】
function clearAll(){
    cookies.remove("tabList")
    tabList.value = [
        {
            title: '主页信息',
            path:"/Statistics"
        }
    ]
    changeTab("/Statistics")
}
// cookies全部清除但是要保留【主页信息 和 当前路径】
function clearOther() {
    // 保留主页标签和当前激活的标签
    const homeTab = tabList.value[0]; // 主页信息标签
    const currentTab = tabList.value.find(tab => tab.path === activeTab.value); // 当前路径标签
    
    // 如果当前标签不是主页标签，则保留这两个标签
    if (currentTab && currentTab.path !== homeTab.path) {
        tabList.value = [homeTab, currentTab];
    } else {
        // 如果当前就是主页，只保留主页标签
        tabList.value = [homeTab];
    }
    
    // 更新cookie
    cookies.set("tabList", tabList.value);
}

</script>

<style scoped>
/* 使用 Tailwind CSS 和深度选择器自定义标签页样式：

- 固定定位在顶部导航下方
- 自定义标签页外观（圆角、间距等）
- 设置合适的高度和层级
 */
.f-tag-list{
    @apply fixed bg-gray-100 flex items-center px-2;
    top: 65px;
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