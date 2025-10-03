<template>
  <div class="f-menu" :style="{width:$store.state.asideWidth}">

    <!--01 添加事件监听 @select="handleSelect-->
    <el-menu unique-opened :collapse="isCollapse"  default-active="2" class="border-0" @select="handleSelect" :collapse-transition="false">
      <template v-for="(item,index) in asideMenus" :key="index">
        <el-sub-menu
          v-if="item.child && item.child.length > 0" :index="item.name">
          <template #title>
            <el-icon>
              <component :is="item.icon"></component>
            </el-icon>
            <span>{{ item.name }}</span>
          </template>
          <el-menu-item v-for="(item2, index2) in item.child" :key="index2" :index="item2.frontpath">
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
//03 为了跳转，要引入useRouter 
// 收起折叠功能 
import { computed } from 'vue'
import { useRouter } from 'vue-router';
import {useStore} from 'vuex'
// import store from '../../store';
const router = useRouter()
const store = useStore()

//是否折叠
const isCollapse = computed(()=>!(store.state.asideWidth== '250px'))

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
        "name": "用户管理",
        "icon": "User",
        "frontpath": "/userList",
      },]
  },
  {
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
},
      ]
  }
];
</script>

<!--01 bottom 表示到底部的距离，其他同理，shadow表示阴影 ，fixed表示滚动时自己不动 overflow: auto;长度问题可以自动滚动-->
<style>
.f-menu {
  transition: all 0.2s; 
  top: 64px;
  bottom: 0;
  left: 0;
  overflow-y: auto;
  overflow-x: hidden;
  @apply shadow-md fixed bg-light-50;
}
</style>

