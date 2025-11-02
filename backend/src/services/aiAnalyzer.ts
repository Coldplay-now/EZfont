import axios from 'axios'
import fs from 'fs'
import path from 'path'

// 类型定义
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

// 加载配置（优先使用环境变量，其次使用配置文件）

let configData: any = {}
const configPath = path.join(process.cwd(), '..', 'config', 'config.json')
try {
  if (fs.existsSync(configPath)) {
    configData = JSON.parse(fs.readFileSync(configPath, 'utf-8'))
  }
} catch (e) {
  console.warn('无法读取配置文件，使用环境变量')
}

const DEEPSEEK_API_URL = process.env.DEEPSEEK_API_URL || configData.deepseek?.apiUrl || 'https://api.deepseek.com/v1/chat/completions'
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY || configData.deepseek?.apiKey || ''

// 生成字体设计规格的提示词
const generateSystemPrompt = (): string => {
  return `你是一个专业的字体设计师AI助手。你的任务是根据用户的需求生成详细的字体设计规格文档。

请严格按照以下JSON Schema格式生成设计规格，确保所有必填字段都包含在内：

{
  "metadata": {
    "specVersion": "1.0",
    "generatedAt": "ISO时间戳",
    "requestId": "唯一请求ID",
    "fontId": "唯一字体ID"
  },
  "basicInfo": {
    "fontFamily": "字体族名称（英文）",
    "fontName": "完整字体名称",
    "style": "serif|sans-serif|monospace",
    "weight": "thin|light|normal|bold",
    "category": "display|text|decorative",
    "language": "latin",
    "version": "1.0.0"
  },
  "designParameters": {
    "metrics": {
      "unitsPerEm": 1000,
      "xHeight": 500-600,
      "capHeight": 700-800,
      "ascender": 800-900,
      "descender": -200到-250,
      "lineHeight": 1200,
      "baseline": 0
    },
    "spacing": {
      "letterSpacing": 0-50,
      "wordSpacing": 200-300,
      "tracking": 0,
      "kerning": true
    },
    "proportions": {
      "contrast": "none|low|medium|high",
      "strokeWidth": 60-120,
      "xHeightRatio": 0.5-0.6,
      "capHeightRatio": 0.7-0.8,
      "aspectRatio": "condensed|normal|extended"
    }
  },
  "styleDefinition": {
    "concept": "设计理念描述",
    "characteristics": ["简短英文关键词1", "简短英文关键词2", "简短英文关键词3", "简短英文关键词4", "简短英文关键词5"],
    "visualStyle": {
      "terminals": "straight|curved|angled",
      "corners": "sharp|rounded|soft",
      "aperture": "closed|semi-open|open",
      "axis": "vertical|angled|mixed",
      "stress": "none|vertical|angled|reverse"
    }
  },
  "characterSet": {
    "uppercase": ["A-Z所有字母"],
    "lowercase": ["a-z所有字母"],
    "numbers": ["0-9所有数字"],
    "punctuation": [".", ",", "!", "?", ";", ":", "'", "\"", "-", "(", ")", "[", "]", "{", "}", "/", "\\", "@", "#", "$", "%", "&", "*", "+", "="]
  },
  "designRules": {
    "consistency": {
      "strokeWeight": "uniform|varied|modulated",
      "characterWidth": "monospace|proportional",
      "baseline": "aligned",
      "opticalCorrection": true
    },
    "legibility": {
      "minSize": 8,
      "maxSize": 144,
      "screenOptimized": true,
      "printOptimized": true
    }
  },
  "technicalSpecs": {
    "format": ["TTF", "OTF"],
    "encoding": "Unicode",
    "hinting": "TrueType",
    "compression": "standard",
    "features": {
      "kerning": true,
      "ligatures": false,
      "alternates": false,
      "numerals": "lining"
    }
  },
  "qualityMetrics": {
    "readabilityScore": 80-95,
    "aestheticScore": 80-95,
    "technicalScore": 85-95,
    "overallScore": 82-95
  }
}

请确保生成的JSON格式完全正确，可以直接解析使用。

【关键参数说明】：

1. **proportions.contrast** - 笔画对比度（横竖笔画粗细差异，优先选择极端值）：
   - "none": 无对比，横竖笔画等宽（现代几何字体、极简风格）
   - "low": 轻微对比，25%差异（简洁sans-serif）
   - "medium": 中等对比，40%差异（平衡的设计）
   - "high": 高对比，60%差异（优雅的serif字体、书法风格）
   
   **重要**：为增强视觉差异，优先选择"none"或"high"，避免总是选择medium！

2. **proportions.strokeWidth** - 基础笔画宽度（优先选择极端值以增强视觉差异）：
   - 55-65: 极细线条（thin, elegant, delicate, lightweight）
   - 70-80: 细线条（light, refined）
   - 85-95: 标准线条（normal, balanced, regular）
   - 100-110: 粗线条（bold, strong, heavy）
   - 115-125: 超粗线条（black, extra-bold, display, impactful）
   
   **重要**：根据用户描述的风格，优先选择两个极端（55-65或115-125），避免中间值！

3. **visualStyle.terminals** - 笔画末端样式：
   - "straight": 直线末端，干净利落（现代、极简、几何）
   - "curved": 圆形末端，柔和优雅（友好、圆润、有机）
   - "angled": 斜切末端，动感锐利（时尚、创意、动态）

4. **visualStyle.corners** - 拐角处理：
   - "sharp": 尖锐拐角，0%圆角（现代、几何、锐利）
   - "rounded": 圆润拐角，30%圆角（友好、平易近人）
   - "soft": 柔和拐角，50%圆角（温柔、有机、流畅）

5. **visualStyle.aperture** - 字怀开口度（C、G、a、e等字母的开口大小）：
   - "closed": 小开口，10%（紧凑、正式、传统）
   - "semi-open": 中等开口，25%（平衡、实用）
   - "open": 大开口，40%（现代、清晰、易读）

6. **visualStyle.axis** - 笔画轴线倾斜：
   - "vertical": 垂直轴线（稳定、正式、现代）
   - "angled": 倾斜轴线（动感、优雅、书法风格）
   - "mixed": 混合轴线（创意、独特、变化）

7. **visualStyle.stress** - 笔画重心分布：
   - "none": 无应力，笔画均匀（几何、现代）
   - "vertical": 垂直应力，上下粗左右细（经典serif）
   - "angled": 倾斜应力（书法风格、动态）
   - "reverse": 反向应力，左右粗上下细（创意、独特）

【智能参数选择指南】：
- 几何/现代风格 → contrast:none, terminals:straight, corners:sharp|rounded, axis:vertical, stress:none
- 优雅/衬线风格 → contrast:medium|high, terminals:curved, corners:soft, axis:angled, stress:vertical
- 友好/圆润风格 → contrast:low, terminals:curved, corners:soft, aperture:open, stress:none
- 动感/创意风格 → terminals:angled, corners:sharp, axis:angled, stress:angled
- 哥特/尖锐风格 → contrast:high, terminals:angled, corners:sharp, strokeWidth:85-100, stress:vertical
- 简洁/清晰风格 → contrast:low|medium, terminals:straight, aperture:open, strokeWidth:70-80`
}

const generateUserPrompt = (requirement: UserRequirement): string => {
  return `请根据以下需求生成字体设计规格：

用户描述：${requirement.textDescription}
字体类型：${requirement.fontType === 'serif' ? '衬线体' : requirement.fontType === 'sans-serif' ? '无衬线体' : '等宽字体'}
字重：${requirement.fontWeight === 'normal' ? '正常' : '粗体'}
字符集：${requirement.characterSet.uppercase ? '大写字母' : ''} ${requirement.characterSet.lowercase ? '小写字母' : ''} ${requirement.characterSet.numbers ? '数字' : ''} ${requirement.characterSet.punctuation ? '标点符号' : ''}

【重要】请特别注意以下字段：

1. **styleDefinition.characteristics**: 
   - 必须是 5-8 个简短的英文关键词标签（1-3个单词）
   - 示例格式：["Modern", "Geometric", "Clean", "Professional", "Elegant"]
   - 不要使用中文，不要使用完整句子
   - 描述字体的视觉风格和特征

2. **visualStyle参数**: 请根据用户描述的风格特征，智能选择合适的参数值
   - 分析描述中的关键词（如：现代、优雅、动感、几何、哥特、友好等）
   - 参考上面的【智能参数选择指南】
   - 确保各参数之间协调一致，形成统一的视觉风格

3. **strokeWidth**: 根据用户描述的字重和风格选择（优先极端值）
   - 描述中提到"细腻/纤细/轻盈/精致/优雅" → 55-65（极细）
   - 描述中提到"细/清晰" → 70-80（细）
   - 描述中提到"粗/厚/强" → 100-110（粗）
   - 描述中提到"粗壮/厚重/黑体/醒目/冲击" → 115-125（超粗）
   - **默认/普通情况** → 随机选择 65 或 110（避免中间值85！）

4. **contrast**: 根据字体类型和风格选择（优先极端值）
   - 几何/现代/极简/统一 → "none"（优先）
   - 简洁/清晰sans-serif → "low"
   - 优雅/书法/传统serif → "high"（优先）
   - 平衡设计 → "medium"
   - **重要**：优先选择"none"或"high"，制造明显对比！

请生成完整的设计规格JSON，确保所有参数值都准确且协调一致。`
}

export async function analyzeRequirements(requirement: UserRequirement): Promise<FontDesignSpec> {
  if (!DEEPSEEK_API_KEY) {
    throw new Error('DeepSeek API密钥未配置')
  }

  try {
    const response = await axios.post(
      DEEPSEEK_API_URL,
      {
        model: 'deepseek-chat',
        messages: [
          { role: 'system', content: generateSystemPrompt() },
          { role: 'user', content: generateUserPrompt(requirement) },
        ],
        temperature: 0.7,
        max_tokens: 4000,
      },
      {
        headers: {
          'Authorization': `Bearer ${DEEPSEEK_API_KEY}`,
          'Content-Type': 'application/json',
        },
      }
    )

    const content = response.data.choices[0]?.message?.content
    if (!content) {
      throw new Error('AI返回内容为空')
    }

    // 提取JSON内容（可能包含markdown代码块）
    let jsonStr = content.trim()
    if (jsonStr.startsWith('```json')) {
      jsonStr = jsonStr.replace(/^```json\n?/, '').replace(/\n?```$/, '')
    } else if (jsonStr.startsWith('```')) {
      jsonStr = jsonStr.replace(/^```\n?/, '').replace(/\n?```$/, '')
    }

    const designSpec: FontDesignSpec = JSON.parse(jsonStr)

    // 生成唯一ID
    const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    const fontId = `font_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

    // 确保metadata字段正确
    designSpec.metadata = {
      specVersion: '1.0',
      generatedAt: new Date().toISOString(),
      requestId,
      fontId,
      generator: 'DeepSeek AI',
    }

    return designSpec
  } catch (error) {
    console.error('调用DeepSeek API失败:', error)
    if (axios.isAxiosError(error)) {
      throw new Error(`API调用失败: ${error.response?.status} - ${error.message}`)
    }
    throw error
  }
}

