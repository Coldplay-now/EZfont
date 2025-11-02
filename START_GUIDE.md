# QuickFont 启动指南

## 快速启动

### 方式1：手动启动（推荐）

打开两个终端窗口，分别运行：

**终端1 - 后端服务：**
```bash
cd /Users/xt/LXT/code/trae/1101-cursor2/QuickFont/backend
npm run dev
```

**终端2 - 前端服务：**
```bash
cd /Users/xt/LXT/code/trae/1101-cursor2/QuickFont/frontend
npm start
```

### 方式2：使用启动脚本

```bash
cd /Users/xt/LXT/code/trae/1101-cursor2/QuickFont
./start.sh
```

## 访问地址

- 前端应用: http://localhost:3000
- 后端API: http://localhost:3001
- 健康检查: http://localhost:3001/health

## 停止服务

在运行服务的终端中按 `Ctrl+C`，或者运行：
```bash
./stop.sh
```

## 常见问题

### 端口被占用
如果端口 3000 或 3001 被占用，可以：
1. 停止占用端口的进程
2. 修改配置文件中的端口号

### 后端无法启动
检查是否配置了 DeepSeek API 密钥：
```bash
cat config/config.json
```

### 前端无法访问后端
检查后端服务是否正常运行：
```bash
curl http://localhost:3001/health
```

## 开发模式特性

- 前端：热重载（修改代码自动刷新）
- 后端：自动重启（修改代码自动重启）
- 实时日志输出

## UI 更新说明

最新版本采用现代简约风格：
- 纯白背景
- 黑白灰配色
- 极简交互
- 优雅排版

刷新浏览器即可看到最新UI效果。


