/**
 * 性能监控工具
 * 用于监控应用性能、内存使用等指标
 */

/**
 * 性能指标收集器
 */
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      // 页面加载性能
      pageLoad: null,
      // 首次内容绘制时间
      fcp: null,
      // 最大内容绘制时间
      lcp: null,
      // 首次输入延迟
      fid: null,
      // 累积布局偏移
      cls: null,
      // 内存使用情况
      memory: null
    }
    
    this.observers = []
    this.isMonitoring = false
  }

  /**
   * 开始性能监控
   */
  start() {
    if (this.isMonitoring || typeof PerformanceObserver === 'undefined') {
      console.warn('Performance API 不支持或已在监控中')
      return
    }

    this.isMonitoring = true
    console.log('性能监控已启动')

    // 监控 LCP（最大内容绘制时间）
    this.observeLCP()

    // 监控 FID（首次输入延迟）
    this.observeFID()

    // 监控 CLS（累积布局偏移）
    this.observeCLS()

    // 监控页面加载时间
    this.observePageLoad()

    // 监控内存使用（每30秒一次）
    this.memoryInterval = setInterval(() => {
      this.collectMemoryMetrics()
    }, 30000)
  }

  /**
   * 停止性能监控
   */
  stop() {
    if (!this.isMonitoring) return

    this.observers.forEach(observer => {
      observer.disconnect()
    })
    
    if (this.memoryInterval) {
      clearInterval(this.memoryInterval)
    }

    this.isMonitoring = false
    console.log('性能监控已停止')
  }

  /**
   * 监控最大内容绘制时间（LCP）
   */
  observeLCP() {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      const lastEntry = entries[entries.length - 1]
      this.metrics.lcp = lastEntry.startTime
      
      console.log(`LCP: ${lastEntry.startTime.toFixed(2)}ms`)
      this.reportMetric('lcp', lastEntry.startTime)
    })

    observer.observe({ entryTypes: ['largest-contentful-paint'] })
    this.observers.push(observer)
  }

  /**
   * 监控首次输入延迟（FID）
   */
  observeFID() {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      entries.forEach(entry => {
        this.metrics.fid = entry.processingStart - entry.startTime
        console.log(`FID: ${this.metrics.fid.toFixed(2)}ms`)
        this.reportMetric('fid', this.metrics.fid)
      })
    })

    observer.observe({ entryTypes: ['first-input'] })
    this.observers.push(observer)
  }

  /**
   * 监控累积布局偏移（CLS）
   */
  observeCLS() {
    let clsValue = 0
    let sessionValue = 0
    let sessionEntries = []

    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries()
      
      entries.forEach(entry => {
        if (!entry.hadRecentInput) {
          const firstSessionEntry = sessionEntries[0]
          const lastSessionEntry = sessionEntries[sessionEntries.length - 1]

          sessionEntries.push(entry)
          sessionValue += entry.value

          // 如果距离上次输入超过 1 秒，会话结束
          if (entry.startTime - firstSessionEntry.startTime > 1000) {
            if (sessionValue > clsValue) {
              clsValue = sessionValue
            }
            sessionEntries = []
            sessionValue = 0
          }
        }
      })

      this.metrics.cls = clsValue
      console.log(`CLS: ${clsValue.toFixed(4)}`)
      this.reportMetric('cls', clsValue)
    })

    observer.observe({ entryTypes: ['layout-shift'] })
    this.observers.push(observer)
  }

  /**
   * 监控页面加载性能
   */
  observePageLoad() {
    if (typeof window.performance === 'undefined') return

    window.addEventListener('load', () => {
      setTimeout(() => {
        const perfData = performance.getEntriesByType('navigation')[0]
        if (perfData) {
          this.metrics.pageLoad = {
            // DNS 查询时间
            dns: perfData.domainLookupEnd - perfData.domainLookupStart,
            // TCP 连接时间
            tcp: perfData.connectEnd - perfData.connectStart,
            // 请求响应时间
            request: perfData.responseEnd - perfData.requestStart,
            // DOM 解析时间
            domParse: perfData.domComplete - perfData.domInteractive,
            // 资源加载时间
            resource: perfData.loadEventEnd - perfData.domComplete,
            // 总加载时间
            total: perfData.loadEventEnd - perfData.fetchStart
          }

          console.log('页面加载性能:', this.metrics.pageLoad)
          this.reportMetric('pageLoad', this.metrics.pageLoad)
        }

        // 监控 FCP（首次内容绘制）
        const paintEntries = performance.getEntriesByType('paint')
        const fcpEntry = paintEntries.find(entry => entry.name === 'first-contentful-paint')
        if (fcpEntry) {
          this.metrics.fcp = fcpEntry.startTime
          console.log(`FCP: ${fcpEntry.startTime.toFixed(2)}ms`)
          this.reportMetric('fcp', fcpEntry.startTime)
        }
      }, 0)
    })
  }

  /**
   * 收集内存使用情况
   */
  collectMemoryMetrics() {
    if (typeof performance.memory === 'undefined') {
      return
    }

    const memory = performance.memory
    this.metrics.memory = {
      used: memory.usedJSHeapSize,
      total: memory.totalJSHeapSize,
      limit: memory.jsHeapSizeLimit,
      usedPercent: ((memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100).toFixed(2)
    }

    console.log(`内存使用: ${this.metrics.memory.usedPercent}%`)
    this.reportMetric('memory', this.metrics.memory)
  }

  /**
   * 报告性能指标
   */
  reportMetric(name, value) {
    // 可以在这里将指标发送到监控服务
    // 目前只在控制台输出
    const timestamp = new Date().toISOString()
    console.log(`[性能指标] ${timestamp} - ${name}:`, value)

    // 存储到 sessionStorage 用于分析
    const metrics = JSON.parse(sessionStorage.getItem('performanceMetrics') || '{}')
    metrics[name] = {
      value,
      timestamp
    }
    
    // 只保留最近的 10 条记录
    const keys = Object.keys(metrics)
    if (keys.length > 10) {
      delete metrics[keys[0]]
    }
    
    sessionStorage.setItem('performanceMetrics', JSON.stringify(metrics))
  }

  /**
   * 获取所有性能指标
   */
  getMetrics() {
    return { ...this.metrics }
  }

  /**
   * 导出性能报告
   */
  exportReport() {
    const report = {
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      metrics: this.metrics
    }

    console.log('性能报告:', report)
    return report
  }
}

/**
 * 创建性能监控单例
 */
let monitorInstance = null

export function getPerformanceMonitor() {
  if (!monitorInstance) {
    monitorInstance = new PerformanceMonitor()
  }
  return monitorInstance
}

/**
 * 性能优化建议
 */
export const PerformanceTips = {
  /**
   * 检查性能问题并提供建议
   */
  analyze() {
    const tips = []
    const metrics = monitorInstance?.getMetrics()

    if (!metrics) {
      tips.push('性能监控未启动，无法进行分析')
      return tips
    }

    // LCP 分析
    if (metrics.lcp > 2500) {
      tips.push('LCP (最大内容绘制) 过慢 (>2.5s)，建议优化资源加载和渲染')
    } else if (metrics.lcp > 1800) {
      tips.push('LCP 需要改进 (>1.8s)，建议优化关键渲染路径')
    }

    // FID 分析
    if (metrics.fid > 100) {
      tips.push('FID (首次输入延迟) 过高 (>100ms)，建议减少主线程工作')
    }

    // CLS 分析
    if (metrics.cls > 0.25) {
      tips.push('CLS (累积布局偏移) 过高 (>0.25)，建议减少布局变化')
    }

    // 内存分析
    if (metrics.memory && metrics.memory.usedPercent > 80) {
      tips.push('内存使用率过高 (>80%)，建议检查内存泄漏')
    }

    return tips
  }
}

export default PerformanceMonitor
