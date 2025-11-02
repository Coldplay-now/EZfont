# 快速修复指南

## 🚨 当前报告的问题及修复

### 问题 1: 字重滑块标签显示异常 ✅ 已修复

**现象**: "Thin Regular Medium Bold Black" 显示在一起

**原因**: 之前缺少 `postcss.config.js` 导致 Tailwind CSS 样式未生成

**修复**: 已创建 `postcss.config.js` 文件

**验证**: 
1. 重启前端服务
2. 硬刷新浏览器 (`Ctrl/Cmd + Shift + R`)
3. 字重滑块下方应正确显示5个标签，均匀分布

---

### 问题 2: 500 错误 (API 调用失败) ⚠️ 需要配置

**现象**: 点击"Generate My Font"后显示 500 错误

**原因**: DeepSeek API 密钥未正确配置

**修复步骤**:

1. **获取 API 密钥**
   - 访问 https://platform.deepseek.com/
   - 注册并获取 API Key

2. **更新配置文件**
   ```bash
   # 编辑配置文件
   nano config/config.json
   ```

3. **替换 API 密钥**
   ```json
   {
     "deepseek": {
       "apiKey": "sk-YOUR-REAL-API-KEY-HERE",
       "apiUrl": "https://api.deepseek.com/v1/chat/completions"
     }
   }
   ```

4. **重启后端服务**
   ```bash
   ./stop.sh
   ./start.sh
   ```

**查看详细配置**: 参考 `API_CONFIG.md`

---

### 问题 3: 点击 Generate My Font 无反馈 ✅ 已修复

**现象**: 点击按钮没有任何反应

**原因**: 
- 表单事件处理不当
- 缺少加载状态反馈

**已修复**:
- ✅ 修改按钮为 `type="button"`
- ✅ 添加 console.log 调试信息
- ✅ 添加加载状态动画
- ✅ 改进错误处理和显示

**验证方法**:
1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 选项卡
3. 输入字体描述（至少10个字符）
4. 点击 "Generate My Font"
5. 应该看到:
   - 按钮变为 "Generating..." 并显示旋转动画
   - Console 中显示 "开始生成字体..."
   - 如果有错误，会在表单下方显示红色错误框

---

## 🔍 问题排查步骤

### 1. 检查服务状态

```bash
# 检查后端
lsof -i :3001

# 检查前端
lsof -i :5174
```

### 2. 查看日志

```bash
# 后端日志
tail -f logs/backend.log

# 前端日志
tail -f logs/frontend.log
```

### 3. 浏览器调试

1. 打开开发者工具 (F12)
2. **Console** 选项卡：查看 JavaScript 错误
3. **Network** 选项卡：查看 API 请求
4. **Elements** 选项卡：检查样式是否加载

---

## 🚀 完整重启流程

如果遇到问题，尝试完整重启：

```bash
# 1. 停止所有服务
./stop.sh

# 2. 清除缓存
cd frontend
rm -rf node_modules/.vite
cd ..

# 3. 检查配置
cat config/config.json

# 4. 重启服务
./start.sh

# 5. 等待启动完成（约5秒）

# 6. 打开浏览器
open http://localhost:5174
```

---

## ✅ 测试清单

测试前端是否正常工作：

- [ ] 页面样式正确加载（侧边栏、布局等）
- [ ] 字重滑块标签正确显示（Thin, Regular, Medium, Bold, Black）
- [ ] 输入框可以输入文字
- [ ] 字体类型按钮可以切换
- [ ] 字符集复选框可以勾选
- [ ] 实时预览区域显示正常
- [ ] 点击"Generate My Font"按钮有反馈
  - 按钮显示 "Generating..."
  - 控制台有日志输出
  - 如果API配置正确，应该开始生成

---

## 🐛 如果仍有问题

1. **清除浏览器缓存**
   - 硬刷新: `Ctrl/Cmd + Shift + R`
   - 或清除站点数据

2. **重新安装依赖**
   ```bash
   cd frontend
   rm -rf node_modules
   npm install
   cd ../backend
   rm -rf node_modules
   npm install
   cd ..
   ```

3. **检查端口冲突**
   ```bash
   # 杀掉占用端口的进程
   lsof -ti :3001 | xargs kill -9
   lsof -ti :5174 | xargs kill -9
   ```

4. **查看完整错误信息**
   - 后端: `cat logs/backend.log`
   - 浏览器控制台: 截图发送

---

## 📝 当前状态

✅ **已修复**:
- PostCSS 配置已创建
- 按钮事件绑定已修复
- 加载状态已添加
- 错误处理已改进

⚠️ **需要配置**:
- DeepSeek API 密钥（参考 `API_CONFIG.md`）

🎉 **可以测试的功能**:
- 前端界面浏览
- 表单输入
- 按钮交互
- 错误提示

💡 **需要 API 密钥才能测试**:
- AI 字体分析
- 字体生成
- 完整的工作流


