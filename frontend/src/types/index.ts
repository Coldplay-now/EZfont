// 导出共享类型
export * from '../../../shared/types'

// 前端特定类型
export interface FontGenerationStatus {
  status: 'idle' | 'analyzing' | 'generating' | 'completed' | 'error'
  fontId?: string
  progress?: number
  message?: string
}

