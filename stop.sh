#!/bin/bash

# QuickFont 服务停止脚本

echo "🛑 停止 QuickFont 服务..."
echo ""

# 停止进程的函数（先尝试优雅停止，如果失败则强制停止）
stop_process() {
    local PID=$1
    local NAME=$2
    
    if ps -p $PID > /dev/null 2>&1; then
        echo "📍 正在停止 $NAME (PID: $PID)..."
        
        # 尝试优雅停止 (SIGTERM)
        kill $PID 2>/dev/null
        
        # 等待最多5秒
        for i in {1..10}; do
            if ! ps -p $PID > /dev/null 2>&1; then
                echo "✅ $NAME 已停止"
                return 0
            fi
            sleep 0.5
        done
        
        # 如果还在运行，强制停止 (SIGKILL)
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  $NAME 未响应，强制停止..."
            kill -9 $PID 2>/dev/null
            sleep 1
            
            if ! ps -p $PID > /dev/null 2>&1; then
                echo "✅ $NAME 已强制停止"
                return 0
            else
                echo "❌ $NAME 停止失败 (PID: $PID)"
                return 1
            fi
        fi
    else
        echo "⚠️  $NAME 未运行 (PID: $PID)"
        return 0
    fi
}

# 通过端口杀掉进程
kill_by_port() {
    local PORT=$1
    local NAME=$2
    
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "📍 发现占用端口 $PORT 的 $NAME 进程"
        local PIDS=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
        
        for PID in $PIDS; do
            stop_process $PID "$NAME (端口 $PORT)"
        done
    fi
}

# 停止后端服务
echo "🔵 停止后端服务..."
BACKEND_STOPPED=false

if [ -f logs/backend.pid ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    stop_process $BACKEND_PID "后端服务"
    BACKEND_STOPPED=true
    rm logs/backend.pid 2>/dev/null
else
    echo "⚠️  未找到后端进程ID文件，尝试通过端口查找..."
fi

# 如果通过 PID 文件没有停止成功，尝试通过端口停止
if [ "$BACKEND_STOPPED" = false ]; then
    kill_by_port 3001 "后端服务"
fi

echo ""

# 停止前端服务
echo "🟢 停止前端服务..."
FRONTEND_STOPPED=false

if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    stop_process $FRONTEND_PID "前端服务"
    FRONTEND_STOPPED=true
    rm logs/frontend.pid 2>/dev/null
else
    echo "⚠️  未找到前端进程ID文件，尝试通过端口查找..."
fi

# 如果通过 PID 文件没有停止成功，尝试通过端口停止
if [ "$FRONTEND_STOPPED" = false ]; then
    kill_by_port 5174 "前端服务"
fi

echo ""

# 清理所有可能的 Node.js 进程（QuickFont 相关）
echo "🧹 清理残留进程..."
QUICKFONT_PIDS=$(ps aux | grep -E "node.*quickfont|tsx.*index.ts|vite.*5174" | grep -v grep | awk '{print $2}')

if [ ! -z "$QUICKFONT_PIDS" ]; then
    echo "📍 发现残留进程: $QUICKFONT_PIDS"
    for PID in $QUICKFONT_PIDS; do
        kill -9 $PID 2>/dev/null && echo "✅ 已清理进程 $PID" || true
    done
else
    echo "✅ 没有发现残留进程"
fi

echo ""

# 最终验证
echo "🔍 验证服务状态..."
BACKEND_RUNNING=$(lsof -Pi :3001 -sTCP:LISTEN -t 2>/dev/null)
FRONTEND_RUNNING=$(lsof -Pi :5174 -sTCP:LISTEN -t 2>/dev/null)

if [ -z "$BACKEND_RUNNING" ] && [ -z "$FRONTEND_RUNNING" ]; then
    echo "✅ 所有服务已完全停止"
    echo ""
    echo "📊 端口状态："
    echo "   - 端口 3001 (后端): 空闲 ✅"
    echo "   - 端口 5174 (前端): 空闲 ✅"
else
    echo "⚠️  警告：仍有进程在运行"
    
    if [ ! -z "$BACKEND_RUNNING" ]; then
        echo "   - 端口 3001 (后端): 占用中 (PID: $BACKEND_RUNNING)"
        echo "     手动停止: kill -9 $BACKEND_RUNNING"
    fi
    
    if [ ! -z "$FRONTEND_RUNNING" ]; then
        echo "   - 端口 5174 (前端): 占用中 (PID: $FRONTEND_RUNNING)"
        echo "     手动停止: kill -9 $FRONTEND_RUNNING"
    fi
fi

echo ""

