/**
 * 菜单配置
 * 用于控制菜单的显示模式和行为
 */

// 菜单模式配置
export const MENU_MODE = {
  STATIC: 'static',    // 静态菜单
  DYNAMIC: 'dynamic'   // 动态菜单（从后端获取）
}

// 当前菜单模式 - 可在此切换
export const CURRENT_MENU_MODE = MENU_MODE.STATIC

// 菜单配置选项
export const menuConfig = {
  // 是否使用静态菜单
  useStaticMenu: CURRENT_MENU_MODE === MENU_MODE.STATIC,
  
  // 菜单主题配置
  theme: {
    // 主色调
    primaryColor: '#2563eb',
    // 激活状态背景色
    activeBgColor: 'rgba(37, 99, 235, 0.1)',
    // 悬停状态背景色
    hoverBgColor: '#f3f4f6',
    // 文字颜色
    textColor: '#374151',
    // 激活状态文字颜色
    activeTextColor: '#2563eb'
  },
  
  // 菜单行为配置
  behavior: {
    // 是否只保持一个子菜单展开
    uniqueOpened: true,
    // 是否启用折叠动画
    collapseTransition: false,
    // 是否启用路由切换动画
    enableTransition: true
  },
  
  // 图标配置
  icons: {
    // 默认图标大小
    size: '18px',
    // 图标间距
    marginRight: '10px'
  }
}

// 根据配置获取菜单模式参数
export function getMenuModeParam() {
  return menuConfig.useStaticMenu
}

// 切换菜单模式的辅助函数
export function switchMenuMode(mode) {
  if (mode === MENU_MODE.STATIC || mode === MENU_MODE.DYNAMIC) {
    return mode === MENU_MODE.STATIC
  }
  return menuConfig.useStaticMenu
}

export default {
  MENU_MODE,
  CURRENT_MENU_MODE,
  menuConfig,
  getMenuModeParam,
  switchMenuMode
}
