import path from 'path'
import fs from 'fs'

const OUTPUT_DIR = path.join(process.cwd(), '..', 'output', 'fonts')

export function getFontFile(fontId: string): string {
  const fontPath = path.join(OUTPUT_DIR, `${fontId}.ttf`)
  
  if (!fs.existsSync(fontPath)) {
    throw new Error('字体文件不存在')
  }

  return fontPath
}

export async function getFontPreview(
  fontId: string,
  text?: string,
  size?: number
): Promise<string> {
  // MVP版本：返回base64编码的预览图
  // 实际实现可以使用canvas或图片生成库
  const fontPath = getFontFile(fontId)
  
  // 这里应该使用canvas或图片库生成预览图
  // 暂时返回一个占位符
  return Promise.resolve('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==')
}








