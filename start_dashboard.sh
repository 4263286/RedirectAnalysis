#!/bin/bash

# TikTok 数据分析看板启动脚本

echo "🚀 启动 TikTok 数据分析看板..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    exit 1
fi

# 激活虚拟环境
source .venv/bin/activate

# 检查依赖
echo "📦 检查依赖..."
python -c "import streamlit, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要依赖，请安装：pip install streamlit pandas plotly openpyxl"
    exit 1
fi

# 检查数据文件
echo "📁 检查数据文件..."
if [ ! -f "data/merged_tiktok_data.csv" ]; then
    echo "❌ 缺少数据文件: data/merged_tiktok_data.csv"
    exit 1
fi

if [ ! -f "data/postingManager_data/accounts_detail.xlsx" ]; then
    echo "❌ 缺少数据文件: data/postingManager_data/accounts_detail.xlsx"
    exit 1
fi

if [ ! -f "data/clicks/20250708ClicksInsnap.csv" ]; then
    echo "❌ 缺少数据文件: data/clicks/20250708ClicksInsnap.csv"
    exit 1
fi

echo "✅ 所有依赖和数据文件检查通过"

# 启动应用
echo "🌐 启动 Streamlit 应用..."
echo "📱 应用将在浏览器中打开: http://localhost:8501"
echo "⏹️  按 Ctrl+C 停止应用"

cd dashboard
streamlit run appDaily.py --server.port 8501 --server.headless false 