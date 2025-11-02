#!/bin/bash

# QuickFont 端口清理脚本

echo "🧹 清理占用的端口..."

# 清理 3001 端口
if lsof -Pi :3001 -sTCP:LISTEN -t >/dev/null ; then
    echo "🔍 发现占用端口 3001 的进程"
    PID=$(lsof -Pi :3001 -sTCP:LISTEN -t)
    kill -9 $PID 2>/dev/null && echo "✅ 已杀掉进程 $PID (端口 3001)" || echo "⚠️  无法杀掉进程 $PID，请尝试: sudo kill -9 $PID"
fi

# 清理 5174 端口
if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
    echo "🔍 发现占用端口 5174 的进程"
    PID=$(lsof -Pi :5174 -sTCP:LISTEN -t)
    kill -9 $PID 2>/dev/null && echo "✅ 已杀掉进程 $PID (端口 5174)" || echo "⚠️  无法杀掉进程 $PID，请尝试: sudo kill -9 $PID"
fi

echo ""
echo "✅ 端口清理完成！"
echo "现在可以运行: ./start.sh"

