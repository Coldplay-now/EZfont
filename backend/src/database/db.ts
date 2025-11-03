import Database from 'better-sqlite3'
import path from 'path'
import fs from 'fs'

const DB_DIR = path.join(process.cwd(), 'data')
const DB_PATH = path.join(DB_DIR, 'quickfont.db')

// 确保数据目录存在
if (!fs.existsSync(DB_DIR)) {
  fs.mkdirSync(DB_DIR, { recursive: true })
}

// 创建数据库连接
const db = new Database(DB_PATH, { verbose: console.log })

// 启用外键约束
db.pragma('foreign_keys = ON')

// 初始化数据库表结构
const initDatabase = () => {
  // 字体表
  db.exec(`
    CREATE TABLE IF NOT EXISTS fonts (
      font_id TEXT PRIMARY KEY,
      font_family TEXT NOT NULL,
      font_name TEXT NOT NULL,
      style TEXT NOT NULL,
      weight TEXT NOT NULL,
      category TEXT NOT NULL,
      status TEXT NOT NULL DEFAULT 'generating',
      file_path TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
  `)

  // 字体规格表
  db.exec(`
    CREATE TABLE IF NOT EXISTS font_specs (
      font_id TEXT PRIMARY KEY,
      spec_json TEXT NOT NULL,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      FOREIGN KEY (font_id) REFERENCES fonts(font_id) ON DELETE CASCADE
    )
  `)

  // 创建索引
  db.exec(`
    CREATE INDEX IF NOT EXISTS idx_fonts_status ON fonts(status);
    CREATE INDEX IF NOT EXISTS idx_fonts_created_at ON fonts(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_fonts_style ON fonts(style);
  `)

  console.log('数据库初始化完成')
}

// 初始化数据库
initDatabase()

export default db







