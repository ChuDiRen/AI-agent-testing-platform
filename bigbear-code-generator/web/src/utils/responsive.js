/**
 * 响应式布局工具函数
 */

import { computed, onMounted, onUnmounted } from 'vue'
import { useAppStore, BREAKPOINTS } from '~/stores/app.js'

/**
 * 获取当前窗口尺寸
 */
export function useWindowSize() {
  const width = window.innerWidth
  const height = window.innerHeight

  return {
    width,
    height,
    isMobile: width <= BREAKPOINTS.mobile,
    isTablet: width > BREAKPOINTS.mobile && width <= BREAKPOINTS.tablet,
    isLaptop: width > BREAKPOINTS.tablet && width <= BREAKPOINTS.laptop,
    isDesktop: width > BREAKPOINTS.laptop
  }
}

/**
 * 响应式监听窗口尺寸变化
 */
export function useResponsive() {
  const appStore = useAppStore()

  const updateDimensions = () => {
    appStore.updateWindowSize(window.innerWidth, window.innerHeight)
  }

  onMounted(() => {
    updateDimensions()
    window.addEventListener('resize', updateDimensions)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateDimensions)
  })

  return {
    isMobile: computed(() => appStore.isMobile),
    isTablet: computed(() => appStore.isTablet),
    isLaptop: computed(() => appStore.isLaptop),
    isDesktop: computed(() => appStore.isDesktop),
    isLargeDesktop: computed(() => appStore.isLargeDesktop),
    deviceType: computed(() => appStore.deviceType),
    windowWidth: computed(() => appStore.windowWidth),
    windowHeight: computed(() => appStore.windowHeight)
  }
}

/**
 * 获取设备类型名称
 */
export function getDeviceTypeName(width) {
  if (width <= BREAKPOINTS.mobile) return 'mobile'
  if (width <= BREAKPOINTS.tablet) return 'tablet'
  if (width <= BREAKPOINTS.laptop) return 'laptop'
  if (width <= BREAKPOINTS.desktop) return 'desktop'
  return 'large-desktop'
}

/**
 * 根据设备类型获取侧边栏宽度
 */
export function getAsideWidthByDevice(deviceType, isCollapsed = false) {
  const collapsedWidth = '64px'
  const mobileWidth = '0px'

  switch (deviceType) {
    case 'mobile':
      return mobileWidth
    case 'tablet':
    case 'laptop':
      return isCollapsed ? collapsedWidth : '200px'
    case 'desktop':
    case 'large-desktop':
      return isCollapsed ? collapsedWidth : '250px'
    default:
      return '250px'
  }
}

/**
 * 响应式样式计算
 */
export function useResponsiveStyle() {
  const { isMobile, windowWidth } = useResponsive()

  return {
    // 计算边距
    getPadding: (mobile, tablet, desktop, largeDesktop) => {
      if (isMobile.value) return mobile
      if (windowWidth.value <= BREAKPOINTS.tablet) return tablet
      if (windowWidth.value <= BREAKPOINTS.desktop) return desktop
      return largeDesktop
    },

    // 计算字体大小
    getFontSize: (mobile, tablet, desktop, largeDesktop) => {
      if (isMobile.value) return mobile
      if (windowWidth.value <= BREAKPOINTS.tablet) return tablet
      if (windowWidth.value <= BREAKPOINTS.desktop) return desktop
      return largeDesktop
    },

    // 计算间距
    getGap: (mobile, tablet, desktop, largeDesktop) => {
      if (isMobile.value) return mobile
      if (windowWidth.value <= BREAKPOINTS.tablet) return tablet
      if (windowWidth.value <= BREAKPOINTS.desktop) return desktop
      return largeDesktop
    }
  }
}

/**
 * 防抖函数
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 */
export function throttle(fn, delay = 300) {
  let last = 0
  return function (...args) {
    const now = Date.now()
    if (now - last >= delay) {
      last = now
      fn.apply(this, args)
    }
  }
}
