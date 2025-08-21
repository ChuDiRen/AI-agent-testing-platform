// 页面进度条组件封装
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
NProgress.configure({ showSpinner: false }) // 显示右上角螺旋加载提示

// NProgress.configure({
//   easing: 'ease', // 动画方式
//   speed: 1000, // 递增进度条的速度
//   showSpinner: false, // 是否显示加载ico
//   trickleSpeed: 200, // 自动递增间隔
//   minimum: 0.3, // 更改启动时使用的最小百分比
//   parent: 'body', //指定进度条的父容器
//   template: `<div class="bar" role="bar" :style="{'color': }"><div class="peg"></div></div><div class="spinner" role="spinner"><div class="spinner-icon"></div></div>`
// })

// 打开进度条
export const NProgressStart = (color: string = '#5180ee') => {
  document.getElementsByTagName('body')[0].style.setProperty('--nprogress-background-color', color);
  NProgress.start()
}

// 关闭进度条
export const NProgressDone = () => {
  NProgress.done()
}
