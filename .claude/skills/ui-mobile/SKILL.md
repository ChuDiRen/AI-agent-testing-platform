# 移动端 UI 开发技能

## 触发条件
- 关键词：移动端、WD UI 组件、移动端页面、H5、小程序、Vant
- 场景：当用户需要开发移动端界面时

## 核心规范

### 规范1：必须使用 WD UI 组件库

```vue
<template>
  <view class="page">
    <!-- 表单组件 -->
    <wd-form ref="formRef" :model="formData">
      <wd-cell-group>
        <wd-input
          label="用户名"
          v-model="formData.username"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请输入用户名' }]"
        />
        <wd-input
          label="手机号"
          v-model="formData.phone"
          placeholder="请输入手机号"
          :rules="[{ required: true, pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }]"
        />
      </wd-cell-group>
    </wd-form>
    
    <!-- 按钮 -->
    <wd-button type="primary" block @click="handleSubmit">提交</wd-button>
  </view>
</template>
```

### 规范2：样式单位使用 rpx

```css
/* ✅ 正确：使用 rpx */
.container {
  width: 750rpx;
  padding: 24rpx 32rpx;
  margin-bottom: 20rpx;
}

.title {
  font-size: 32rpx;
  line-height: 44rpx;
}

.btn {
  height: 88rpx;
  border-radius: 44rpx;
}

/* ❌ 错误：使用 px */
.container {
  width: 375px;
  padding: 12px 16px;
}
```

### 规范3：列表页面模板

```vue
<template>
  <view class="list-page">
    <!-- 搜索栏 -->
    <wd-search
      v-model="searchValue"
      placeholder="搜索"
      @search="handleSearch"
    />
    
    <!-- 列表 -->
    <scroll-view
      scroll-y
      class="list-scroll"
      @scrolltolower="loadMore"
    >
      <view
        v-for="item in list"
        :key="item.id"
        class="list-item"
        @click="handleItemClick(item)"
      >
        <view class="item-title">{{ item.title }}</view>
        <view class="item-desc">{{ item.description }}</view>
        <view class="item-time">{{ item.createTime }}</view>
      </view>
      
      <!-- 加载状态 -->
      <wd-loadmore :state="loadState" />
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const searchValue = ref('')
const list = ref([])
const loadState = ref('loading')
const page = ref(1)
const pageSize = 10

const fetchList = async () => {
  loadState.value = 'loading'
  try {
    const res = await api.getList({
      keyword: searchValue.value,
      page: page.value,
      pageSize
    })
    if (page.value === 1) {
      list.value = res.data.list
    } else {
      list.value.push(...res.data.list)
    }
    loadState.value = res.data.list.length < pageSize ? 'finished' : 'loading'
  } catch (e) {
    loadState.value = 'error'
  }
}

const handleSearch = () => {
  page.value = 1
  fetchList()
}

const loadMore = () => {
  if (loadState.value === 'loading') return
  page.value++
  fetchList()
}

onMounted(() => {
  fetchList()
})
</script>

<style lang="scss" scoped>
.list-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.list-scroll {
  flex: 1;
  overflow: hidden;
}

.list-item {
  padding: 24rpx 32rpx;
  background: #fff;
  margin-bottom: 2rpx;
  
  .item-title {
    font-size: 32rpx;
    font-weight: 500;
    color: #333;
  }
  
  .item-desc {
    font-size: 28rpx;
    color: #666;
    margin-top: 8rpx;
  }
  
  .item-time {
    font-size: 24rpx;
    color: #999;
    margin-top: 12rpx;
  }
}
</style>
```

### 规范4：表单页面模板

```vue
<template>
  <view class="form-page">
    <wd-form ref="formRef" :model="formData">
      <wd-cell-group title="基本信息">
        <wd-input
          label="标题"
          v-model="formData.title"
          placeholder="请输入标题"
          :rules="[{ required: true, message: '请输入标题' }]"
        />
        <wd-textarea
          label="描述"
          v-model="formData.description"
          placeholder="请输入描述"
          :maxlength="200"
          show-word-limit
        />
        <wd-picker
          label="类型"
          v-model="formData.type"
          :columns="typeOptions"
          placeholder="请选择类型"
        />
        <wd-datetime-picker
          label="时间"
          v-model="formData.time"
          type="datetime"
          placeholder="请选择时间"
        />
      </wd-cell-group>
      
      <wd-cell-group title="图片上传">
        <wd-upload
          v-model:file-list="formData.images"
          :action="uploadUrl"
          :max-count="9"
        />
      </wd-cell-group>
    </wd-form>
    
    <!-- 底部按钮 -->
    <view class="bottom-bar">
      <wd-button type="primary" block @click="handleSubmit">
        提交
      </wd-button>
    </view>
  </view>
</template>
```

## 常用组件速查

| 场景 | WD UI 组件 |
|------|-----------|
| 按钮 | `wd-button` |
| 输入框 | `wd-input` |
| 多行输入 | `wd-textarea` |
| 选择器 | `wd-picker` |
| 日期选择 | `wd-datetime-picker` |
| 开关 | `wd-switch` |
| 单选 | `wd-radio-group` |
| 多选 | `wd-checkbox-group` |
| 图片上传 | `wd-upload` |
| 列表项 | `wd-cell` |
| 分组 | `wd-cell-group` |
| 弹窗 | `wd-popup` |
| 提示 | `wd-toast` |
| 加载更多 | `wd-loadmore` |
| 下拉刷新 | `wd-pull-refresh` |
| 标签页 | `wd-tabs` |

## 禁止事项

1. ❌ 禁止使用 Element Plus 组件（PC 端组件库）
2. ❌ 禁止使用 px 单位（应使用 rpx）
3. ❌ 禁止使用 PC 端布局方式
4. ❌ 禁止忽略安全区域适配

## 参考资源

- [WD UI 文档](https://wot-design-uni.gitee.io/)
- [uni-app 文档](https://uniapp.dcloud.net.cn/)
