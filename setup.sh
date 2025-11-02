#!/bin/bash

# QuickFont 开发环境启动脚本

echo "🚀 启动 QuickFont 开发环境..."

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python3"
    exit 1
fi

# 检查配置文件
if [ ! -f "config/config.json" ]; then
    echo "⚠️  配置文件不存在，正在创建..."
    cp config/config.json.example config/config.json
    echo "📝 请编辑 config/config.json 填入你的 DeepSeek API 密钥"
fi

# 检查前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    cd ..
fi

# 检查后端依赖
if [ ! -d "backend/node_modules" ]; then
    echo "📦 安装后端依赖..."
    cd backend
    npm install
    cd ..
fi

# 检查Python依赖
if ! python3 -c "import fontTools" &> /dev/null; then
    echo "📦 安装Python依赖..."
    cd font-generator
    pip3 install -r requirements.txt
    cd ..
fi

# 创建输出目录
mkdir -p output/fonts

echo "✅ 环境准备完成！"
echo ""
echo "使用以下命令启动服务："
echo "  后端: cd backend && npm run dev"
echo "  前端: cd frontend && npm start"
echo ""


