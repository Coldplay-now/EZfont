import { spawn } from 'child_process'
import path from 'path'
import fs from 'fs'
import { v4 as uuidv4 } from 'uuid'
// 类型定义
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

const OUTPUT_DIR = path.join(process.cwd(), '..', 'output', 'fonts')
const GENERATOR_SCRIPT = path.join(process.cwd(), '..', 'font-generator', 'generator.py')

// 确保输出目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true })
}

export async function generateFont(designSpec: FontDesignSpec): Promise<{
  fontId: string
  downloadUrl: string
  previewUrl: string
}> {
  const fontId = designSpec.metadata.fontId || `font_${uuidv4()}`

  // 保存设计规格到临时文件
  const specFilePath = path.join(OUTPUT_DIR, `${fontId}_spec.json`)
  fs.writeFileSync(specFilePath, JSON.stringify(designSpec, null, 2))

  return new Promise((resolve, reject) => {
    // 调用Python字体生成脚本
    const pythonProcess = spawn('python3', [
      GENERATOR_SCRIPT,
      '--spec', specFilePath,
      '--output', OUTPUT_DIR,
      '--font-id', fontId,
    ])

    let stdout = ''
    let stderr = ''

    pythonProcess.stdout.on('data', (data) => {
      stdout += data.toString()
    })

    pythonProcess.stderr.on('data', (data) => {
      stderr += data.toString()
    })

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        console.error('字体生成失败:', stderr)
        reject(new Error(`字体生成失败: ${stderr || '未知错误'}`))
        return
      }

      // 检查生成的文件
      const fontPath = path.join(OUTPUT_DIR, `${fontId}.ttf`)
      if (!fs.existsSync(fontPath)) {
        reject(new Error('字体文件生成失败：文件不存在'))
        return
      }

      resolve({
        fontId,
        downloadUrl: `/api/font/${fontId}/download`,
        previewUrl: `/api/font/${fontId}/preview`,
      })
    })

    pythonProcess.on('error', (error) => {
      reject(new Error(`无法启动字体生成进程: ${error.message}`))
    })
  })
}

