# 移动端设计规范技能

## 触发条件
- 关键词：移动端设计、rem、vw、rpx、适配、响应式、安全区域
- 场景：当用户需要了解移动端设计规范时

## 核心规范

### 规范1：尺寸单位

| 单位 | 说明 | 适用场景 |
|------|------|---------|
| rpx | 响应式像素（750rpx = 屏幕宽度） | uni-app 推荐 |
| rem | 相对根元素字体大小 | H5 项目 |
| vw/vh | 视口宽度/高度百分比 | 全屏元素 |
| px | 像素 | 边框、小图标 |

### 规范2：设计稿适配

```scss
// 设计稿宽度 750px（iPhone 6/7/8 二倍图）

// uni-app：直接使用 rpx
.container {
  width: 750rpx;      // 满屏宽度
  padding: 32rpx;     // 设计稿 32px
  font-size: 28rpx;   // 设计稿 28px
}

// H5：使用 rem + flexible
// 1rem = 75px（设计稿 / 10）
.container {
  width: 10rem;       // 750px
  padding: 0.427rem;  // 32px
  font-size: 0.373rem; // 28px
}

// H5：使用 vw
// 1vw = 7.5px（750 / 100）
.container {
  width: 100vw;
  padding: 4.267vw;   // 32px
  font-size: 3.733vw; // 28px
}
```

### 规范3：安全区域适配

```scss
// iOS 刘海屏、底部横条适配
.page {
  padding-top: constant(safe-area-inset-top);    // iOS < 11.2
  padding-top: env(safe-area-inset-top);         // iOS >= 11.2
  padding-bottom: constant(safe-area-inset-bottom);
  padding-bottom: env(safe-area-inset-bottom);
}

// 底部固定按钮
.bottom-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 24rpx 32rpx;
  padding-bottom: calc(24rpx + constant(safe-area-inset-bottom));
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
  background: #fff;
}

// uni-app 简化写法
.bottom-bar {
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
}
```

### 规范4：触摸规范

```scss
// 最小点击区域：44x44px（88x88rpx）
.btn {
  min-height: 88rpx;
  min-width: 88rpx;
  padding: 24rpx 48rpx;
}

// 列表项
.list-item {
  min-height: 96rpx;
  padding: 24rpx 32rpx;
}

// 表单输入框
.input {
  height: 88rpx;
  padding: 0 24rpx;
}

// 按钮间距
.btn-group {
  display: flex;
  gap: 24rpx;
}
```

### 规范5：字体规范

```scss
// 字体大小层级
$font-size-xs: 20rpx;    // 辅助文字
$font-size-sm: 24rpx;    // 小号文字
$font-size-base: 28rpx;  // 正文
$font-size-md: 32rpx;    // 标题
$font-size-lg: 36rpx;    // 大标题
$font-size-xl: 44rpx;    // 特大标题

// 行高
$line-height-tight: 1.2;
$line-height-normal: 1.5;
$line-height-loose: 1.8;

// 使用示例
.title {
  font-size: $font-size-lg;
  font-weight: 600;
  line-height: $line-height-tight;
  color: #333;
}

.content {
  font-size: $font-size-base;
  line-height: $line-height-normal;
  color: #666;
}

.tip {
  font-size: $font-size-sm;
  color: #999;
}
```

### 规范6：间距规范

```scss
// 间距层级（基于 8rpx 栅格）
$spacing-xs: 8rpx;
$spacing-sm: 16rpx;
$spacing-base: 24rpx;
$spacing-md: 32rpx;
$spacing-lg: 48rpx;
$spacing-xl: 64rpx;

// 页面边距
.page {
  padding: $spacing-md;  // 32rpx
}

// 卡片间距
.card {
  padding: $spacing-base;  // 24rpx
  margin-bottom: $spacing-sm;  // 16rpx
  border-radius: 16rpx;
}

// 元素间距
.section {
  margin-bottom: $spacing-lg;  // 48rpx
}
```

### 规范7：颜色规范

```scss
// 主色
$color-primary: #1890ff;
$color-success: #52c41a;
$color-warning: #faad14;
$color-danger: #ff4d4f;

// 文字颜色
$color-text-primary: #333333;
$color-text-regular: #666666;
$color-text-secondary: #999999;
$color-text-placeholder: #cccccc;

// 背景色
$color-bg-page: #f5f5f5;
$color-bg-card: #ffffff;
$color-bg-disabled: #f5f5f5;

// 边框色
$color-border: #e8e8e8;
$color-divider: #f0f0f0;
```

## 设计原则

1. **移动优先** - 先设计移动端，再适配 PC
2. **拇指友好** - 重要操作放在拇指可触及区域（屏幕下半部分）
3. **减少输入** - 尽量使用选择代替输入
4. **即时反馈** - 操作后立即给予视觉反馈
5. **清晰层级** - 通过大小、颜色、间距区分信息层级

## 检查清单

- [ ] 所有可点击元素 >= 88rpx
- [ ] 适配了安全区域（刘海屏、底部横条）
- [ ] 字体大小 >= 24rpx
- [ ] 颜色对比度符合无障碍标准
- [ ] 加载状态有明确提示
- [ ] 空状态有友好提示
