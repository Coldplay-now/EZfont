import { Router } from 'express'
import { analyzeRequirements } from '../services/aiAnalyzer'
import { generateFont } from '../services/fontGenerator'
import { getFontFile, getFontPreview } from '../services/fontService'
import { fontRepository } from '../database/fontRepository'
import path from 'path'

// 类型定义（简化版本，避免跨目录引用问题）
interface UserRequirement {
  textDescription: string
  fontType: 'serif' | 'sans-serif' | 'monospace'
  fontWeight: 'normal' | 'bold'
  characterSet: {
    uppercase: boolean
    lowercase: boolean
    numbers: boolean
    punctuation: boolean
  }
  useCase?: string
}

interface FontDesignSpec {
  metadata: any
  basicInfo: any
  designParameters: any
  styleDefinition: any
  characterSet: any
  designRules: any
  technicalSpecs: any
  qualityMetrics: any
}

const router = Router()

// 获取字体列表
router.get('/fonts', async (req, res) => {
  try {
    const { status, style, limit = '50', offset = '0' } = req.query

    const fonts = fontRepository.getFonts({
      status: status as string,
      style: style as string,
      limit: parseInt(limit as string),
      offset: parseInt(offset as string),
    })

    const total = fontRepository.getFontsCount({
      status: status as string,
      style: style as string,
    })

    res.json({
      code: 200,
      message: 'success',
      data: {
        fonts,
        total,
        limit: parseInt(limit as string),
        offset: parseInt(offset as string),
      },
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('获取字体列表失败:', error)
    res.status(500).json({
      code: 500,
      message: error instanceof Error ? error.message : '获取字体列表失败',
      data: null,
      timestamp: new Date().toISOString(),
    })
  }
})

// 获取单个字体详情及规格
router.get('/fonts/:fontId', async (req, res) => {
  try {
    const { fontId } = req.params

    const fontWithSpec = fontRepository.getFontWithSpec(fontId)

    if (!fontWithSpec) {
      return res.status(404).json({
        code: 404,
        message: '字体不存在',
        data: null,
        timestamp: new Date().toISOString(),
      })
    }

    res.json({
      code: 200,
      message: 'success',
      data: fontWithSpec,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('获取字体详情失败:', error)
    res.status(500).json({
      code: 500,
      message: error instanceof Error ? error.message : '获取字体详情失败',
      data: null,
      timestamp: new Date().toISOString(),
    })
  }
})

// 删除字体
router.delete('/fonts/:fontId', async (req, res) => {
  try {
    const { fontId } = req.params

    if (!fontRepository.fontExists(fontId)) {
      return res.status(404).json({
        code: 404,
        message: '字体不存在',
        data: null,
        timestamp: new Date().toISOString(),
      })
    }

    // 删除数据库记录
    fontRepository.deleteFont(fontId)

    // TODO: 删除字体文件（如需要）

    res.json({
      code: 200,
      message: 'success',
      data: { fontId },
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('删除字体失败:', error)
    res.status(500).json({
      code: 500,
      message: error instanceof Error ? error.message : '删除字体失败',
      data: null,
      timestamp: new Date().toISOString(),
    })
  }
})

// 获取字体生成状态
router.get('/fonts/:fontId/status', async (req, res) => {
  try {
    const { fontId } = req.params

    const font = fontRepository.getFontById(fontId)

    if (!font) {
      return res.status(404).json({
        code: 404,
        message: '字体不存在',
        data: null,
        timestamp: new Date().toISOString(),
      })
    }

    res.json({
      code: 200,
      message: 'success',
      data: {
        fontId: font.font_id,
        status: font.status,
        updatedAt: font.updated_at,
      },
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('获取字体状态失败:', error)
    res.status(500).json({
      code: 500,
      message: error instanceof Error ? error.message : '获取字体状态失败',
      data: null,
      timestamp: new Date().toISOString(),
    })
  }
})

// 分析需求并生成设计规格
router.post('/analyze-requirements', async (req, res) => {
  try {
    const requirement: UserRequirement = req.body

    // 验证输入
    if (!requirement.textDescription || requirement.textDescription.length < 10) {
      return res.status(400).json({
        code: 400,
        message: '描述长度必须至少10个字符',
        data: null,
        timestamp: new Date().toISOString(),
      })
    }

    const designSpec = await analyzeRequirements(requirement)

    // 保存到数据库
    try {
      fontRepository.createFont(designSpec.metadata.fontId, designSpec)
    } catch (dbError) {
      console.warn('保存字体记录到数据库失败:', dbError)
      // 继续返回结果，不中断流程
    }

    res.json({
      code: 200,
      message: 'success',
      data: designSpec,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('分析需求失败:', error)
    res.status(500).json({
      code: 500,
      message: error instanceof Error ? error.message : '分析需求失败',
      data: null,
      timestamp: new Date().toISOString(),
    })
  }
})

// 生成字体文件
router.post('/generate-font', async (req, res) => {
  try {
    const { designSpec }: { designSpec: FontDesignSpec } = req.body

    if (!designSpec) {
      return res.status(400).json({
        code: 400,
        message: '设计规格不能为空',
        data: null,
        timestamp: new Date().toISOString(),
      })
    }

    const fontId = designSpec.metadata.fontId

    // 更新状态为生成中（如果还不存在则创建）
    if (!fontRepository.fontExists(fontId)) {
      fontRepository.createFont(fontId, designSpec)
    }

    try {
      const result = await generateFont(designSpec)

      // 更新字体文件路径和状态为完成
      const fontPath = path.join(process.cwd(), '..', 'output', 'fonts', `${fontId}.ttf`)
      fontRepository.updateFontStatus(fontId, 'completed', fontPath)

      res.json({
        code: 200,
        message: 'success',
        data: result,
        timestamp: new Date().toISOString(),
      })
    } catch (genError) {
      // 更新状态为失败
      fontRepository.updateFontStatus(fontId, 'failed')
      throw genError
    }
  } catch (error) {
    console.error('生成字体失败:', error)
    res.status(500).json({
      code: 500,
      message: error instanceof Error ? error.message : '生成字体失败',
      data: null,
      timestamp: new Date().toISOString(),
    })
  }
})

// 获取字体预览
router.get('/font/:fontId/preview', async (req, res) => {
  try {
    const { fontId } = req.params
    const { text, size } = req.query

    const previewImage = await getFontPreview(
      fontId,
      text as string,
      size ? parseInt(size as string) : undefined
    )

    res.json({
      code: 200,
      message: 'success',
      data: { previewImage },
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error('获取预览失败:', error)
    res.status(500).json({
      code: 500,
      message: error instanceof Error ? error.message : '获取预览失败',
      data: null,
      timestamp: new Date().toISOString(),
    })
  }
})

// 下载字体文件
router.get('/font/:fontId/download', async (req, res) => {
  try {
    const { fontId } = req.params

    // 检查字体是否存在
    const font = fontRepository.getFontById(fontId)
    if (!font) {
      return res.status(404).json({
        code: 404,
        message: '字体不存在',
        data: null,
        timestamp: new Date().toISOString(),
      })
    }

    // 检查字体状态
    if (font.status !== 'completed') {
      return res.status(400).json({
        code: 400,
        message: '字体还未生成完成',
        data: { status: font.status },
        timestamp: new Date().toISOString(),
      })
    }

    const fontPath = await getFontFile(fontId)

    res.download(fontPath, `${font.font_family}.ttf`, (err) => {
      if (err) {
        console.error('下载文件失败:', err)
        if (!res.headersSent) {
          res.status(500).json({
            code: 500,
            message: '下载文件失败',
            data: null,
            timestamp: new Date().toISOString(),
          })
        }
      }
    })
  } catch (error) {
    console.error('获取字体文件失败:', error)
    res.status(500).json({
      code: 500,
      message: error instanceof Error ? error.message : '获取字体文件失败',
      data: null,
      timestamp: new Date().toISOString(),
    })
  }
})

export default router

