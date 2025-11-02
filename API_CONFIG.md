# API 配置说明

## ⚠️ 500 错误修复

如果您看到 **500 错误** 或 **401 错误**，这是因为 DeepSeek API 密钥配置问题。

## 📝 配置步骤

### 1. 获取 DeepSeek API 密钥

1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制您的 API Key

### 2. 配置 API 密钥

打开配置文件：`config/config.json`

```json
{
  "deepseek": {
    "apiKey": "sk-YOUR-ACTUAL-API-KEY-HERE",
    "apiUrl": "https://api.deepseek.com/v1/chat/completions"
  },
  "font": {
    "outputDir": "./output/fonts",
    "supportedFormats": ["ttf", "otf"]
  },
  "server": {
    "port": 3001,
    "corsOrigin": "http://localhost:5174"
  }
}
```

**替换 `sk-YOUR-ACTUAL-API-KEY-HERE` 为您的真实 API Key**

### 3. 重启服务

```bash
# 停止服务
./stop.sh

# 启动服务
./start.sh
```

## 🧪 测试 API 配置

您可以使用以下命令测试 API 是否配置正确：

```bash
curl -X POST http://localhost:3001/api/analyze-requirements \
  -H "Content-Type: application/json" \
  -d '{
    "textDescription": "A modern sans-serif font for tech products",
    "fontType": "sans-serif",
    "fontWeight": "normal",
    "characterSet": {
      "uppercase": true,
      "lowercase": true,
      "numbers": true,
      "punctuation": true
    }
  }'
```

## 🔧 常见问题

### Q: API 返回 401 错误

**原因**: API 密钥无效或过期

**解决方案**:
1. 检查 `config/config.json` 中的 API 密钥是否正确
2. 确保密钥以 `sk-` 开头
3. 重新生成 API 密钥并更新配置

### Q: API 返回 429 错误

**原因**: API 调用频率超限

**解决方案**:
1. 等待几分钟后重试
2. 检查您的 DeepSeek 账户余额和配额

### Q: 网络连接错误

**原因**: 无法连接到 DeepSeek API

**解决方案**:
1. 检查网络连接
2. 检查防火墙设置
3. 尝试使用代理

## 💡 临时测试方案（不使用真实 API）

如果您想快速测试前端界面而不调用真实 API，可以：

### 方案 1: 使用模拟数据

在 `backend/src/services/aiAnalyzer.ts` 中添加模拟模式：

```typescript
// 在文件顶部添加
const MOCK_MODE = process.env.MOCK_MODE === 'true'

// 在 analyzeRequirements 函数开头添加
if (MOCK_MODE) {
  return generateMockSpec(requirement)
}
```

然后在启动时设置环境变量：

```bash
cd backend
MOCK_MODE=true npm run dev
```

### 方案 2: 跳过 AI 分析步骤

暂时注释掉 AI 调用，返回固定的设计规格。

## 📞 需要帮助？

- 检查后端日志: `tail -f logs/backend.log`
- 检查前端控制台的错误信息
- 确保后端服务在 3001 端口运行: `lsof -i :3001`
- 确保前端服务在 5174 端口运行: `lsof -i :5174`

## ✅ 配置检查清单

- [ ] DeepSeek API 密钥已获取
- [ ] `config/config.json` 已更新
- [ ] 服务已重启
- [ ] 后端服务运行正常 (端口 3001)
- [ ] 前端服务运行正常 (端口 5174)
- [ ] 浏览器控制台无错误
- [ ] 后端日志无 401/500 错误


