# API密钥配置说明

QuickFont支持两种方式配置DeepSeek API密钥：

## 方式1：使用配置文件（推荐）

1. 复制配置文件示例：
   ```bash
   cp config/config.json.example config/config.json
   ```

2. 编辑 `config/config.json`，填入你的API密钥：
   ```json
   {
     "deepseek": {
       "apiKey": "你的DeepSeek API密钥",
       "apiUrl": "https://api.deepseek.com/v1/chat/completions"
     }
   }
   ```

## 方式2：使用环境变量

1. 复制环境变量示例：
   ```bash
   cp backend/.env.example backend/.env
   ```

2. 编辑 `backend/.env`，填入你的API密钥：
   ```bash
   DEEPSEEK_API_KEY=你的DeepSeek API密钥
   ```

## 优先级

系统会按以下优先级读取配置：
1. **环境变量** (`process.env.DEEPSEEK_API_KEY`) - 最高优先级
2. **配置文件** (`config/config.json`) - 次优先级
3. **默认值** - 空字符串（会报错）

## 获取DeepSeek API密钥

1. 访问 https://platform.deepseek.com/
2. 注册/登录账号
3. 进入API密钥管理页面
4. 创建新的API密钥
5. 复制密钥并填入配置

## 验证配置

启动后端服务后，如果没有配置API密钥，会在控制台看到错误提示。

正确配置后，应该不会出现API密钥相关的错误。


