# uni-app 跨平台开发技能

## 触发条件
- 关键词：uni-app、条件编译、跨平台、多端、#ifdef、#ifndef
- 场景：当用户需要开发跨平台应用时

## 核心规范

### 规范1：条件编译语法

```vue
<template>
  <!-- 仅在微信小程序显示 -->
  <!-- #ifdef MP-WEIXIN -->
  <button open-type="share">分享给好友</button>
  <!-- #endif -->
  
  <!-- 仅在 H5 显示 -->
  <!-- #ifdef H5 -->
  <button @click="handleH5Share">分享</button>
  <!-- #endif -->
  
  <!-- 仅在 App 显示 -->
  <!-- #ifdef APP-PLUS -->
  <button @click="handleAppShare">分享</button>
  <!-- #endif -->
  
  <!-- 非微信小程序显示 -->
  <!-- #ifndef MP-WEIXIN -->
  <view>非微信小程序内容</view>
  <!-- #endif -->
  
  <!-- 多平台条件 -->
  <!-- #ifdef MP-WEIXIN || MP-ALIPAY -->
  <view>小程序专用</view>
  <!-- #endif -->
</template>

<script>
// #ifdef MP-WEIXIN
import WxApi from '@/utils/wx-api'
// #endif

// #ifdef H5
import H5Share from '@/utils/h5-share'
// #endif

export default {
  methods: {
    handleShare() {
      // #ifdef MP-WEIXIN
      // 微信小程序分享逻辑
      // #endif
      
      // #ifdef H5
      H5Share.share({
        title: '分享标题',
        desc: '分享描述'
      })
      // #endif
      
      // #ifdef APP-PLUS
      uni.share({
        provider: 'weixin',
        type: 0,
        title: '分享标题'
      })
      // #endif
    }
  }
}
</script>

<style lang="scss">
/* #ifdef MP-WEIXIN */
.wx-only {
  /* 微信小程序专用样式 */
}
/* #endif */

/* #ifdef H5 */
.h5-only {
  /* H5 专用样式 */
}
/* #endif */
</style>
```

### 规范2：平台标识速查表

| 标识 | 平台 | 说明 |
|------|------|------|
| `VUE3` | Vue 3 | HBuilderX 3.2.0+ |
| `APP-PLUS` | App | iOS 和 Android |
| `APP-PLUS-NVUE` | App nvue | 原生渲染 |
| `APP-ANDROID` | Android App | |
| `APP-IOS` | iOS App | |
| `H5` | H5 | Web 浏览器 |
| `MP-WEIXIN` | 微信小程序 | |
| `MP-ALIPAY` | 支付宝小程序 | |
| `MP-BAIDU` | 百度小程序 | |
| `MP-TOUTIAO` | 抖音小程序 | |
| `MP-QQ` | QQ 小程序 | |
| `MP-KUAISHOU` | 快手小程序 | |
| `MP` | 所有小程序 | |

### 规范3：API 差异处理

```javascript
// utils/platform.js

/**
 * 获取平台信息
 */
export function getPlatform() {
  // #ifdef MP-WEIXIN
  return 'weixin'
  // #endif
  
  // #ifdef MP-ALIPAY
  return 'alipay'
  // #endif
  
  // #ifdef H5
  return 'h5'
  // #endif
  
  // #ifdef APP-PLUS
  return 'app'
  // #endif
  
  return 'unknown'
}

/**
 * 跨平台登录
 */
export async function platformLogin() {
  // #ifdef MP-WEIXIN
  const { code } = await uni.login({ provider: 'weixin' })
  return api.wxLogin({ code })
  // #endif
  
  // #ifdef MP-ALIPAY
  const { authCode } = await my.getAuthCode({ scopes: 'auth_base' })
  return api.alipayLogin({ authCode })
  // #endif
  
  // #ifdef H5
  // H5 使用账号密码登录
  return null
  // #endif
  
  // #ifdef APP-PLUS
  // App 可使用多种登录方式
  return null
  // #endif
}

/**
 * 跨平台支付
 */
export async function platformPay(orderInfo) {
  // #ifdef MP-WEIXIN
  const res = await api.getWxPayParams(orderInfo)
  return uni.requestPayment({
    provider: 'wxpay',
    ...res.data
  })
  // #endif
  
  // #ifdef MP-ALIPAY
  const res = await api.getAlipayParams(orderInfo)
  return my.tradePay({
    tradeNO: res.data.tradeNo
  })
  // #endif
  
  // #ifdef H5
  // H5 跳转支付页面
  window.location.href = orderInfo.payUrl
  // #endif
  
  // #ifdef APP-PLUS
  const res = await api.getAppPayParams(orderInfo)
  return uni.requestPayment({
    provider: 'wxpay', // 或 'alipay'
    ...res.data
  })
  // #endif
}

/**
 * 跨平台分享
 */
export function platformShare(options) {
  // #ifdef MP-WEIXIN
  // 微信小程序使用 onShareAppMessage
  return
  // #endif
  
  // #ifdef H5
  // H5 使用 JSSDK 或自定义分享
  if (isWeixinBrowser()) {
    wx.updateAppMessageShareData({
      title: options.title,
      desc: options.desc,
      link: options.link,
      imgUrl: options.imageUrl
    })
  }
  // #endif
  
  // #ifdef APP-PLUS
  uni.share({
    provider: 'weixin',
    scene: 'WXSceneSession',
    type: 0,
    title: options.title,
    summary: options.desc,
    href: options.link,
    imageUrl: options.imageUrl
  })
  // #endif
}
```

### 规范4：样式适配

```scss
// styles/platform.scss

// 状态栏高度
.status-bar {
  // #ifdef APP-PLUS || MP-WEIXIN
  height: var(--status-bar-height);
  // #endif
  
  // #ifdef H5
  height: 0;
  // #endif
}

// 导航栏高度
.nav-bar {
  // #ifdef APP-PLUS || MP
  height: calc(var(--status-bar-height) + 44px);
  padding-top: var(--status-bar-height);
  // #endif
  
  // #ifdef H5
  height: 44px;
  // #endif
}

// 底部安全区域
.safe-area-bottom {
  // #ifdef APP-PLUS || MP
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
  // #endif
}

// 单位适配
.container {
  // #ifdef MP
  // 小程序使用 rpx
  padding: 32rpx;
  font-size: 28rpx;
  // #endif
  
  // #ifdef H5
  // H5 使用 rem 或 vw
  padding: 16px;
  font-size: 14px;
  // #endif
}
```

### 规范5：页面配置差异

```json
// pages.json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页",
        // 微信小程序特有配置
        "mp-weixin": {
          "navigationStyle": "custom"
        },
        // H5 特有配置
        "h5": {
          "titleNView": false
        },
        // App 特有配置
        "app-plus": {
          "titleNView": {
            "buttons": []
          }
        }
      }
    }
  ],
  // 平台特有的 TabBar 配置
  "tabBar": {
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "static/tab/home.png",
        "selectedIconPath": "static/tab/home-active.png"
      }
    ],
    // 微信小程序自定义 TabBar
    "mp-weixin": {
      "custom": true
    }
  }
}
```

### 规范6：原生组件处理

```vue
<template>
  <view class="page">
    <!-- 地图组件 - 各平台差异较大 -->
    <!-- #ifdef MP-WEIXIN -->
    <map
      :latitude="location.lat"
      :longitude="location.lng"
      :markers="markers"
      @markertap="onMarkerTap"
    />
    <!-- #endif -->
    
    <!-- #ifdef H5 -->
    <div ref="mapContainer" class="map-container"></div>
    <!-- #endif -->
    
    <!-- 视频组件 -->
    <video
      :src="videoUrl"
      controls
      <!-- #ifdef MP-WEIXIN -->
      :enable-danmu="true"
      :danmu-list="danmuList"
      <!-- #endif -->
    />
  </view>
</template>

<script setup>
// #ifdef H5
import { onMounted, ref } from 'vue'

const mapContainer = ref(null)

onMounted(() => {
  // H5 使用第三方地图 SDK
  const map = new AMap.Map(mapContainer.value, {
    zoom: 15,
    center: [location.lng, location.lat]
  })
})
// #endif
</script>
```

## 最佳实践

1. **抽象差异** - 将平台差异封装在工具函数中，业务代码保持统一
2. **最小化条件编译** - 尽量使用 uni-app 统一 API，减少条件编译代码
3. **充分测试** - 每个平台都要测试，特别是原生组件
4. **渐进增强** - 先保证基础功能，再针对特定平台增强
5. **文档记录** - 记录各平台的特殊处理，便于维护

## 检查清单

- [ ] 条件编译语法正确（#ifdef / #ifndef / #endif）
- [ ] 各平台 API 差异已处理
- [ ] 样式单位适配（rpx / rem / vw）
- [ ] 原生组件兼容性处理
- [ ] 各平台功能测试通过
- [ ] pages.json 平台配置正确

## 禁止事项

1. ❌ 禁止在非条件编译区域使用平台特有 API
2. ❌ 禁止忽略平台差异直接上线
3. ❌ 禁止在小程序中使用 DOM 操作
4. ❌ 禁止在 nvue 中使用 HTML 标签
