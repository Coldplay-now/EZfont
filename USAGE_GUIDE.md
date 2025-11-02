# QuickFont 使用指南

## 系统架构

QuickFont 是一个基于AI的字体创作系统，包含以下主要组件：

- **前端 (Frontend)**: React + TypeScript + Tailwind CSS
- **后端 (Backend)**: Node.js + Express + TypeScript
- **数据库**: SQLite
- **AI服务**: DeepSeek API
- **字体生成**: Python脚本

## 快速启动

### 1. 环境准备

确保已安装：
- Node.js (v16+)
- Python 3
- npm

### 2. 配置

复制配置文件并填写API密钥：

```bash
cd QuickFont
cp config/config.json.example config/config.json
```

编辑 `config/config.json`，填写 DeepSeek API 密钥：

```json
{
  "deepseek": {
    "apiKey": "your-api-key-here",
    "apiUrl": "https://api.deepseek.com/v1/chat/completions"
  }
}
```

### 3. 启动系统

使用启动脚本：

```bash
chmod +x start.sh
./start.sh
```

或手动启动：

```bash
# 启动后端 (终端1)
cd backend
npm install
npm run dev

# 启动前端 (终端2)
cd frontend
npm install
npm run dev
```

### 4. 访问应用

打开浏览器访问: `http://localhost:5174`

## 功能使用

### 页面1: 字体列表 (/)

- 查看所有已创建的字体
- 点击 "Create New Font" 创建新字体
- 点击 "Preview" 预览字体效果
- 点击 "Download" 下载字体文件
- 点击菜单 "..." 可以查看详情或删除字体

### 页面2: AI 生成页 (/create)

1. **描述字体风格**: 输入您想要的字体特征描述
   - 例如: "A retro handwritten script font with a slightly playful feel"

2. **选择字体类型**: 
   - Serif (衬线体)
   - Sans-serif (无衬线体)
   - Monospace (等宽字体)

3. **选择字重**: 使用滑块选择从 Thin 到 Black

4. **选择字符集**: 勾选需要包含的字符类型

5. **实时预览**: 右侧预览区域实时显示效果

6. **生成字体**: 点击 "Generate My Font" 按钮

生成完成后会自动跳转到规格详情页。

### 页面3: 规格详情页 (/fonts/:fontId/spec)

查看字体的详细设计规格：

- **Basic Information**: 字体基本信息（名称、版本、格式等）
- **Design Parameters**: 设计参数
  - Metrics (度量参数)
  - Spacing (间距参数)  
  - Proportions (比例参数)
- **Style Definition**: 风格定义标签
- **Live Preview**: 实时预览效果
- **Character Set**: 字符集展示

操作：
- 点击 "Edit" 跳转到预览调整页
- 点击 "Download Font" 下载字体文件

### 页面4: 预览调整页 (/fonts/:fontId/preview)

实时调整和预览字体效果：

- **Live Preview**: 主预览区，可自定义文本
- **Uppercase**: 大写字母预览
- **Lowercase**: 小写字母预览
- **Numerals & Punctuation**: 数字和标点符号预览

**字体调整**（右侧面板）：
- Weight (字重): 100-900
- Spacing (间距): -50 到 50
- Line Height (行高): 1.0 到 3.0

调整后点击 "Export Font" 下载字体。

## API 端点

### 字体管理

- `GET /api/fonts` - 获取字体列表
- `GET /api/fonts/:fontId` - 获取字体详情
- `DELETE /api/fonts/:fontId` - 删除字体
- `GET /api/fonts/:fontId/status` - 获取字体生成状态

### 字体生成

- `POST /api/analyze-requirements` - 分析需求生成设计规格
- `POST /api/generate-font` - 生成字体文件
- `GET /api/font/:fontId/preview` - 获取字体预览
- `GET /api/font/:fontId/download` - 下载字体文件

## 数据库

系统使用 SQLite 存储字体元数据，数据库文件位于 `backend/data/quickfont.db`。

表结构：
- **fonts**: 字体基本信息
- **font_specs**: 字体设计规格（JSON）

## 故障排除

### 前端无法连接后端

检查 `frontend/.env` 或代码中的 API_BASE_URL 配置。

### 字体生成失败

1. 检查 DeepSeek API 密钥是否正确
2. 查看 `backend` 终端的错误日志
3. 确保 Python 环境正确安装

### 数据库错误

删除 `backend/data/quickfont.db` 文件，重启后端会自动重新创建。

## 技术栈

### 前端
- React 18
- TypeScript
- Tailwind CSS + @tailwindcss/forms
- React Router v6
- Axios

### 后端
- Node.js + Express
- TypeScript
- better-sqlite3
- DeepSeek API

### 字体生成
- Python 3
- FontForge (未来集成)

## 目录结构

```
QuickFont/
├── frontend/          # 前端应用
│   ├── src/
│   │   ├── components/  # 共享组件
│   │   ├── pages/       # 页面组件
│   │   ├── services/    # API服务
│   │   └── types/       # 类型定义
│   └── ...
├── backend/           # 后端服务
│   ├── src/
│   │   ├── database/    # 数据库相关
│   │   ├── routes/      # API路由
│   │   ├── services/    # 业务逻辑
│   │   └── ...
│   └── data/           # SQLite数据库文件
├── shared/            # 共享类型定义
├── font-generator/    # 字体生成脚本
├── output/            # 生成的字体文件
└── config/            # 配置文件
```

## 开发说明

### 添加新功能

1. 后端：在 `backend/src/routes/` 添加新路由
2. 前端：在 `frontend/src/pages/` 添加新页面
3. 类型：在 `shared/types.ts` 添加共享类型

### 调试模式

后端使用 `tsx watch` 支持热重载，前端使用 Vite 的 HMR。

### 构建生产版本

```bash
# 后端
cd backend
npm run build

# 前端
cd frontend
npm run build
```

## 许可证

请查看项目根目录的 LICENSE 文件。

## 支持

如有问题，请查看 README.md 或联系开发团队。

