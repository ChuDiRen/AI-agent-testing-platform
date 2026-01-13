<template>
 <div class="f-menu">
    <el-menu default-active="2" class="border-0" @select="handleSelect">
      <template v-for="(item,index) in asideMenus" :key="index">
        <el-sub-menu
          v-if="item.child && item.child.length > 0" :index="item.name">
          <template #title>
            <el-icon>
              <component :is="item.icon"></component>
            </el-icon>
            <span>{{ item.name }}</span>
          </template>
          
          <el-menu-item v-for="(item2, index2) in item.child" 
                        :key="index2" 
                        :index="item2.frontpath">
            <el-icon>
              <component :is="item2.icon"></component>
            </el-icon>
            <span>{{ item2.name }}</span>
        </el-menu-item>
        </el-sub-menu>
        <el-menu-item v-else :index="item.frontpath">
          <component :is="item.icon"></component>
          <span>{{ item.name }}</span>
        </el-menu-item>
      </template>
    </el-menu>
  </div>
</template>

<script setup>
   import { useRouter } from 'vue-router';
   const router = useRouter()

    //02 添加事件
    const handleSelect =(e)=>{
    //可以看看这里点击后事什么?
    console.log(e)
    router.push(e)
    }

const asideMenus = [{
    "name":"系统管理",
    "icon":"Tools",
    "child":[
        {
          "name":"用户管理",
          "icon":"User",
          "frontpath":"/userList" // 需要改成真实的路径
        }
    ]
 },{
     "name":"API自动化",
     "icon":"Promotion",
     "child":[
     {
        "name": "项目管理",
        "icon": "Tickets",
        "frontpath": "/ApiProjectList",
      },{
        "name": "关键字方法管理",
        "icon":"Key",
        "frontpath": "/ApiKeyWordList",
      },{
        "name": "素材维护管理",
        "icon":"Document",
        "frontpath": "/ApiMateManageList",
      },{
        "name": "接口信息维护",
        "icon": "Link",
        "frontpath": "/ApiInfoList",
      },{
        "name": "API用例信息管理",
        "icon": "Reading",
        "frontpath": "/ApiInfoCaseList",
      },{
        "name": "API测试计划管理",
        "icon": "Collection",
        "frontpath": "/ApiCollectionInfoList",
      },
      ]
  },{
    "name":"消息通知管理", 
    "icon":"Comment",
    "child":[
      {
        "name": "微信配置",
        "icon": "ChatSquare",
        "frontpath": "/WeChartMsgManageList",
      },{
        "name": "钉钉配置",
        "icon": "Coordinate",
        "frontpath": "/DingDingMsgManageList",
       },{
        "name": "飞书配置",
        "icon": "Position",
        "frontpath": "/FeiShuMsgManageList",
      }
  ]
}]
</script>

<!--01 bottom 表示到底部的距离，其他同理，shadow表示阴影 ，fixed表示滚动时自己不动 overflow: auto;长度问题可以自动滚动-->
<style>
.f-menu {
  width: 250px;
  top: 64px;
  bottom: 0;
  left: 0;
  overflow: auto;
  overflow-x: hidden;
  @apply shadow-md fixed bg-light-50;
}
</style>