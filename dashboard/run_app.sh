#!/bin/bash

# TikTok 账号分析看板启动脚本

echo "🚀 启动 TikTok 账号分析看板..."

# 检查是否在正确的目录
if [ ! -f "appDaily.py" ]; then
    echo "❌ 错误: 请在 dashboard 目录下运行此脚本"
    exit 1
fi

# 检查数据文件是否存在
if [ ! -f "../data/redash_data/redash_data_2025-07-08.csv" ]; then
    echo "❌ 错误: 找不到 redash 数据文件"
    echo "请确保文件存在: ../data/redash_data/redash_data_2025-07-08.csv"
    exit 1
fi

if [ ! -f "../data/postingManager_data/accounts_detail.xlsx" ]; then
    echo "❌ 错误: 找不到 accounts detail 数据文件"
    echo "请确保文件存在: ../data/postingManager_data/accounts_detail.xlsx"
    exit 1
fi

echo "✅ 数据文件检查通过"
echo "📊 启动 Streamlit 应用..."

# 启动 Streamlit 应用
streamlit run appDaily.py --server.port 8501 --server.address 0.0.0.0 