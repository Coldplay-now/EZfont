import axios from 'axios'
import type { 
  UserRequirement, 
  FontDesignSpec, 
  APIResponse, 
  FontListResponse, 
  FontListItem,
  FontWithSpec 
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const fontApi = {
  // 获取字体列表
  async getFonts(params?: {
    status?: string
    style?: string
    limit?: number
    offset?: number
  }): Promise<APIResponse<FontListResponse>> {
    const response = await apiClient.get('/fonts', { params })
    return response.data
  },

  // 获取单个字体详情
  async getFontDetail(fontId: string): Promise<APIResponse<FontWithSpec>> {
    const response = await apiClient.get(`/fonts/${fontId}`)
    return response.data
  },

  // 删除字体
  async deleteFont(fontId: string): Promise<APIResponse<{ fontId: string }>> {
    const response = await apiClient.delete(`/fonts/${fontId}`)
    return response.data
  },

  // 获取字体状态
  async getFontStatus(fontId: string): Promise<APIResponse<{ fontId: string; status: string; updatedAt: string }>> {
    const response = await apiClient.get(`/fonts/${fontId}/status`)
    return response.data
  },

  // 分析需求并生成设计规格
  async analyzeRequirements(requirement: UserRequirement): Promise<APIResponse<FontDesignSpec>> {
    const response = await apiClient.post('/analyze-requirements', requirement)
    return response.data
  },

  // 生成字体文件
  async generateFont(designSpec: FontDesignSpec): Promise<APIResponse<{ fontId: string; downloadUrl: string; previewUrl: string }>> {
    const response = await apiClient.post('/generate-font', { designSpec })
    return response.data
  },

  // 获取字体预览
  async getFontPreview(fontId: string, text?: string, size?: number): Promise<APIResponse<{ previewImage: string }>> {
    const params = new URLSearchParams()
    if (text) params.append('text', text)
    if (size) params.append('size', size.toString())
    const response = await apiClient.get(`/font/${fontId}/preview?${params.toString()}`)
    return response.data
  },

  // 下载字体文件
  getDownloadUrl(fontId: string): string {
    return `${API_BASE_URL}/font/${fontId}/download`
  },
}

