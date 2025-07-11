#!/bin/bash

# 增强版 TikTok 分析看板启动脚本

echo "🚀 启动 TikTok 增强分析看板..."

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建虚拟环境"
    echo "运行: python3 -m venv .venv"
    exit 1
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source .venv/bin/activate

# 检查必要的依赖
echo "🔍 检查依赖..."
python3 -c "import streamlit, pandas, altair" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要的依赖包"
    echo "请运行: pip install streamlit pandas altair openpyxl"
    exit 1
fi

# 检查数据文件
echo "📁 检查数据文件..."
if [ ! -d "data/redash_data" ]; then
    echo "⚠️  Redash 数据目录不存在"
    mkdir -p data/redash_data
fi

if [ ! -d "data/postingManager_data" ]; then
    echo "⚠️  PostingManager 数据目录不存在"
    mkdir -p data/postingManager_data
fi

if [ ! -d "data/clicks" ]; then
    echo "⚠️  Clicks 数据目录不存在"
    mkdir -p data/clicks
fi

# 检查是否有数据文件
redash_files=$(ls data/redash_data/*.csv 2>/dev/null | wc -l)
accounts_files=$(ls data/postingManager_data/*.xlsx 2>/dev/null | wc -l)
clicks_files=$(ls data/clicks/*.csv 2>/dev/null | wc -l)

echo "📊 数据文件检查结果:"
echo "  - Redash 数据文件: $redash_files 个"
echo "  - Accounts 数据文件: $accounts_files 个"
echo "  - Clicks 数据文件: $clicks_files 个"

if [ $redash_files -eq 0 ] || [ $accounts_files -eq 0 ]; then
    echo "⚠️  缺少必要的数据文件，应用可能无法正常运行"
    echo "请确保以下文件存在:"
    echo "  - data/redash_data/redash_data_*.csv"
    echo "  - data/postingManager_data/accounts_detail.xlsx"
fi

# 启动应用
echo "🌐 启动 Streamlit 应用..."
echo "📱 应用将在浏览器中打开: http://localhost:8501"
echo "🛑 按 Ctrl+C 停止应用"
echo ""

# 设置环境变量
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts:$(pwd)/config"

# 启动 Streamlit
streamlit run dashboard/enhanced_app.py --server.port 8501 --server.address 0.0.0.0 