// AI绘画API
import { AxiosResponse } from 'axios'
import http from '@/api/http'

// AI绘画相关接口定义
export interface PaintingRequest {
  prompt: string
  negative_prompt?: string
  style: string
  size: string
  model_name?: string
  seed?: number
  steps?: number
  cfg_scale?: number
  sampler?: string
}

export interface PaintingResponse {
  id: string
  user_id: number
  prompt: string
  negative_prompt?: string
  style: string
  size: string
  model_name?: string
  seed?: number
  steps: number
  cfg_scale: number
  sampler?: string
  status: string
  image_url?: string
  thumbnail_url?: string
  generation_time?: number
  cost?: number
  width?: number
  height?: number
  file_size?: number
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface PaintingStyleInfo {
  key: string
  name: string
  description: string
  preview_image?: string
  recommended_settings?: Record<string, any>
}

export interface PaintingModelInfo {
  key: string
  name: string
  description: string
  version?: string
  supported_sizes: string[]
  supported_styles: string[]
  max_steps: number
  default_cfg_scale: number
}

// AI绘画API
export const aiPaintingApi = {
  // 生成图片
  generateImage(data: PaintingRequest): Promise<AxiosResponse<any>> {
    return http.post('/ai-painting/generate', data)
  },

  // 获取绘画历史
  getPaintingHistory(params: {
    page?: number
    page_size?: number
    style?: string
  } = {}): Promise<AxiosResponse<any>> {
    return http.get('/ai-painting/history', { params })
  },

  // 获取绘画详情
  getPaintingDetail(paintingId: string): Promise<AxiosResponse<any>> {
    return http.get(`/ai-painting/${paintingId}`)
  },

  // 删除绘画记录
  deletePainting(paintingId: string): Promise<AxiosResponse<any>> {
    return http.delete(`/ai-painting/${paintingId}`)
  },

  // 重新生成图片
  regenerateImage(paintingId: string): Promise<AxiosResponse<any>> {
    return http.post(`/ai-painting/${paintingId}/regenerate`)
  },

  // 获取绘画风格列表
  getPaintingStyles(): Promise<AxiosResponse<any>> {
    return http.get('/ai-painting/styles/list')
  },

  // 获取绘画模型列表
  getPaintingModels(): Promise<AxiosResponse<any>> {
    return http.get('/ai-painting/models/list')
  }
}

// AI绘画工具函数
export const aiPaintingUtils = {
  // 格式化生成时间
  formatGenerationTime(seconds: number): string {
    if (seconds < 60) {
      return `${seconds.toFixed(1)}秒`
    } else {
      const minutes = Math.floor(seconds / 60)
      const remainingSeconds = seconds % 60
      return `${minutes}分${remainingSeconds.toFixed(0)}秒`
    }
  },

  // 格式化文件大小
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  },

  // 获取状态标签类型
  getStatusTagType(status: string): string {
    switch (status) {
      case 'completed':
        return 'success'
      case 'generating':
        return 'warning'
      case 'failed':
        return 'danger'
      default:
        return 'info'
    }
  },

  // 获取状态文本
  getStatusText(status: string): string {
    switch (status) {
      case 'completed':
        return '已完成'
      case 'generating':
        return '生成中'
      case 'failed':
        return '失败'
      default:
        return '未知'
    }
  },

  // 获取风格标签类型
  getStyleTagType(style: string): string {
    switch (style) {
      case 'realistic':
        return 'primary'
      case 'cartoon':
        return 'success'
      case 'oil-painting':
        return 'warning'
      case 'watercolor':
        return 'info'
      case 'sketch':
        return 'default'
      case 'sci-fi':
        return 'danger'
      default:
        return 'default'
    }
  },

  // 解析图片尺寸
  parseImageSize(size: string): { width: number; height: number } {
    const [width, height] = size.split('x').map(Number)
    return { width: width || 512, height: height || 512 }
  },

  // 计算宽高比
  getAspectRatio(size: string): string {
    const { width, height } = this.parseImageSize(size)
    const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b)
    const divisor = gcd(width, height)
    return `${width / divisor}:${height / divisor}`
  },

  // 生成随机种子
  generateRandomSeed(): number {
    return Math.floor(Math.random() * 2147483647)
  },

  // 验证提示词
  validatePrompt(prompt: string): { valid: boolean; message?: string } {
    if (!prompt || prompt.trim().length === 0) {
      return { valid: false, message: '提示词不能为空' }
    }
    if (prompt.length > 2000) {
      return { valid: false, message: '提示词不能超过2000个字符' }
    }
    return { valid: true }
  },

  // 估算生成时间
  estimateGenerationTime(steps: number, size: string): number {
    const baseTime = 5 // 基础时间5秒
    const stepTime = steps * 0.2 // 每步0.2秒
    const sizeMultiplier = this.getSizeMultiplier(size)
    return baseTime + stepTime * sizeMultiplier
  },

  // 获取尺寸倍数
  getSizeMultiplier(size: string): number {
    const sizeMultipliers: Record<string, number> = {
      '512x512': 1.0,
      '768x768': 2.25,
      '1024x1024': 4.0,
      '1024x768': 3.0,
      '768x1024': 3.0
    }
    return sizeMultipliers[size] || 1.0
  },

  // 估算生成成本
  estimateCost(request: PaintingRequest): number {
    const baseCost = 0.01
    const sizeMultiplier = this.getSizeMultiplier(request.size)
    const stepMultiplier = (request.steps || 20) / 20
    return baseCost * sizeMultiplier * stepMultiplier
  },

  // 获取推荐设置
  getRecommendedSettings(style: string): Partial<PaintingRequest> {
    const recommendations: Record<string, Partial<PaintingRequest>> = {
      realistic: { cfg_scale: 7.0, steps: 30, sampler: 'DPM++ 2M Karras' },
      cartoon: { cfg_scale: 8.0, steps: 25, sampler: 'Euler a' },
      'oil-painting': { cfg_scale: 6.0, steps: 35, sampler: 'DPM++ SDE Karras' },
      watercolor: { cfg_scale: 5.5, steps: 25, sampler: 'DPM++ 2M' },
      sketch: { cfg_scale: 6.5, steps: 20, sampler: 'Euler' },
      'sci-fi': { cfg_scale: 8.5, steps: 40, sampler: 'DPM++ 2M Karras' }
    }
    return recommendations[style] || { cfg_scale: 7.0, steps: 20 }
  },

  // 提取关键词
  extractKeywords(prompt: string): string[] {
    // 简单的关键词提取，实际可以使用更复杂的NLP算法
    return prompt
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2)
      .slice(0, 10)
  },

  // 生成相似提示词
  generateSimilarPrompts(originalPrompt: string): string[] {
    const keywords = this.extractKeywords(originalPrompt)
    const variations = [
      'high quality, detailed',
      'masterpiece, best quality',
      'ultra realistic, 4k',
      'artistic, professional',
      'vibrant colors, sharp focus'
    ]
    
    return variations.map(variation => `${originalPrompt}, ${variation}`)
  }
}
