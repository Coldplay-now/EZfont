import dotenv from 'dotenv'
import path from 'path'

dotenv.config()

// 从环境变量或配置文件加载配置
const configPath = path.join(process.cwd(), '..', 'config', 'config.json')

let config: any = {}

try {
  if (require('fs').existsSync(configPath)) {
    config = require(configPath)
  }
} catch (e) {
  // 配置文件不存在，使用环境变量
}

export const config_env = {
  deepseek: {
    apiKey: process.env.DEEPSEEK_API_KEY || config.deepseek?.apiKey || '',
    apiUrl: process.env.DEEPSEEK_API_URL || config.deepseek?.apiUrl || 'https://api.deepseek.com/v1/chat/completions',
  },
  font: {
    outputDir: process.env.FONT_OUTPUT_DIR || config.font?.outputDir || path.join(process.cwd(), '..', 'output', 'fonts'),
    supportedFormats: config.font?.supportedFormats || ['ttf', 'otf'],
  },
  server: {
    port: process.env.PORT || config.server?.port || 3001,
    corsOrigin: process.env.CORS_ORIGIN || config.server?.corsOrigin || 'http://localhost:3000',
  },
}


