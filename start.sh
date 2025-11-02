#!/bin/bash

# QuickFont 服务启动脚本

echo "🚀 启动 QuickFont 服务..."
echo ""

# 检查端口是否被占用
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  端口 $1 已被占用"
        return 1
    else
        return 0
    fi
}

# 启动后端服务
start_backend() {
    echo "📦 启动后端服务 (端口 3001)..."
    cd backend
    npm run dev > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../logs/backend.pid
    echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
    echo "   日志: logs/backend.log"
    cd ..
}

# 启动前端服务
start_frontend() {
    echo "📦 启动前端服务 (端口 5174)..."
    cd frontend
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../logs/frontend.pid
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
    echo "   日志: logs/frontend.log"
    cd ..
}

# 创建日志目录
mkdir -p logs

# 检查端口
check_port 3001 || exit 1
check_port 5174 || exit 1

# 启动服务
start_backend
sleep 2
start_frontend

echo ""
echo "✅ 所有服务已启动！"
echo ""
echo "📋 访问地址："
echo "   - 前端应用: http://localhost:5174"
echo "   - 后端API:  http://localhost:3001"
echo "   - 健康检查: http://localhost:3001/health"
echo ""
echo "📝 查看日志："
echo "   - 后端: tail -f logs/backend.log"
echo "   - 前端: tail -f logs/frontend.log"
echo ""
echo "🛑 停止服务："
echo "   - 运行: ./stop.sh"
echo "   - 或手动: kill \$(cat logs/backend.pid) \$(cat logs/frontend.pid)"

