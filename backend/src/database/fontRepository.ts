import db from './db'
import type { FontDesignSpec } from '../../../shared/types'

export interface FontRecord {
  font_id: string
  font_family: string
  font_name: string
  style: string
  weight: string
  category: string
  status: 'generating' | 'completed' | 'failed'
  file_path: string | null
  created_at: string
  updated_at: string
}

export interface FontWithSpec extends FontRecord {
  spec: FontDesignSpec
}

export class FontRepository {
  // 创建新字体记录
  createFont(fontId: string, spec: FontDesignSpec): void {
    const now = new Date().toISOString()
    const { basicInfo } = spec

    const insertFont = db.prepare(`
      INSERT INTO fonts (
        font_id, font_family, font_name, style, weight, category, 
        status, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, 'generating', ?, ?)
    `)

    const insertSpec = db.prepare(`
      INSERT INTO font_specs (font_id, spec_json, created_at, updated_at)
      VALUES (?, ?, ?, ?)
    `)

    const transaction = db.transaction(() => {
      insertFont.run(
        fontId,
        basicInfo.fontFamily,
        basicInfo.fontName,
        basicInfo.style,
        basicInfo.weight,
        basicInfo.category,
        now,
        now
      )

      insertSpec.run(
        fontId,
        JSON.stringify(spec),
        now,
        now
      )
    })

    transaction()
  }

  // 更新字体状态
  updateFontStatus(
    fontId: string, 
    status: 'generating' | 'completed' | 'failed',
    filePath?: string
  ): void {
    const now = new Date().toISOString()
    const stmt = db.prepare(`
      UPDATE fonts 
      SET status = ?, file_path = ?, updated_at = ?
      WHERE font_id = ?
    `)
    stmt.run(status, filePath || null, now, fontId)
  }

  // 获取所有字体列表（支持分页和筛选）
  getFonts(params?: {
    status?: string
    style?: string
    limit?: number
    offset?: number
  }): FontRecord[] {
    let query = 'SELECT * FROM fonts WHERE 1=1'
    const queryParams: any[] = []

    if (params?.status) {
      query += ' AND status = ?'
      queryParams.push(params.status)
    }

    if (params?.style) {
      query += ' AND style = ?'
      queryParams.push(params.style)
    }

    query += ' ORDER BY created_at DESC'

    if (params?.limit) {
      query += ' LIMIT ?'
      queryParams.push(params.limit)
      
      if (params?.offset) {
        query += ' OFFSET ?'
        queryParams.push(params.offset)
      }
    }

    const stmt = db.prepare(query)
    return stmt.all(...queryParams) as FontRecord[]
  }

  // 获取字体总数
  getFontsCount(params?: { status?: string; style?: string }): number {
    let query = 'SELECT COUNT(*) as count FROM fonts WHERE 1=1'
    const queryParams: any[] = []

    if (params?.status) {
      query += ' AND status = ?'
      queryParams.push(params.status)
    }

    if (params?.style) {
      query += ' AND style = ?'
      queryParams.push(params.style)
    }

    const stmt = db.prepare(query)
    const result = stmt.get(...queryParams) as { count: number }
    return result.count
  }

  // 获取单个字体详情
  getFontById(fontId: string): FontRecord | undefined {
    const stmt = db.prepare('SELECT * FROM fonts WHERE font_id = ?')
    return stmt.get(fontId) as FontRecord | undefined
  }

  // 获取字体及其规格
  getFontWithSpec(fontId: string): FontWithSpec | undefined {
    const stmt = db.prepare(`
      SELECT 
        f.*,
        fs.spec_json
      FROM fonts f
      LEFT JOIN font_specs fs ON f.font_id = fs.font_id
      WHERE f.font_id = ?
    `)
    
    const result = stmt.get(fontId) as any
    
    if (!result) {
      return undefined
    }

    const { spec_json, ...fontData } = result
    
    return {
      ...fontData,
      spec: spec_json ? JSON.parse(spec_json) : null
    }
  }

  // 更新字体规格
  updateFontSpec(fontId: string, spec: FontDesignSpec): void {
    const now = new Date().toISOString()
    const stmt = db.prepare(`
      UPDATE font_specs 
      SET spec_json = ?, updated_at = ?
      WHERE font_id = ?
    `)
    stmt.run(JSON.stringify(spec), now, fontId)
  }

  // 删除字体
  deleteFont(fontId: string): void {
    const transaction = db.transaction(() => {
      db.prepare('DELETE FROM font_specs WHERE font_id = ?').run(fontId)
      db.prepare('DELETE FROM fonts WHERE font_id = ?').run(fontId)
    })
    transaction()
  }

  // 检查字体是否存在
  fontExists(fontId: string): boolean {
    const stmt = db.prepare('SELECT 1 FROM fonts WHERE font_id = ? LIMIT 1')
    return stmt.get(fontId) !== undefined
  }
}

// 导出单例
export const fontRepository = new FontRepository()







