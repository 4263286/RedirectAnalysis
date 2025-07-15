import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import warnings
import sys
import os
import requests

# 设置页面配置
st.set_page_config(
    page_title="TikTok 增强分析看板 - 测试版",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔧 数据加载测试")

# 环境和数据完整性调试输出
st.write('Python version:', sys.version)
st.write('Current working dir:', os.getcwd())

# 自动创建所需的空目录（如果不存在）
for d in [
    "data",
    "data/redash_data",
    "data/clicks",
    "data/postingManager_data"
]:
    os.makedirs(d, exist_ok=True)

st.write('Files in data/:', os.listdir('data'))

# 添加 scripts 目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_dir = os.path.join(parent_dir, 'scripts')

if os.path.exists(scripts_dir):
    sys.path.insert(0, scripts_dir)
    st.write(f"Scripts目录已添加到路径: {scripts_dir}")

try:
    from enhanced_data_processor import EnhancedTikTokDataProcessor
    from enhanced_visualization import EnhancedVisualization
    st.success("✅ 模块导入成功")
except Exception as e:
    st.error(f"❌ 模块导入失败: {e}")
    st.stop()

@st.cache_data
def load_accounts_data():
    try:
        local_path = "data/postingManager_data/accounts_detail.xlsx"
        if os.path.exists(local_path):
            df = pd.read_excel(local_path)
            st.write("[DEBUG] 本地 accounts_detail.xlsx 加载成功，shape:", df.shape)
            return df
        
        # 尝试从云端加载
        try:
            try:
                url = st.secrets["ACCOUNTS_URL"]
            except Exception as secrets_error:
                st.error(f"无法获取云端数据URL: {secrets_error}")
                return None
            response = requests.get(url)
            response.raise_for_status()  # 检查HTTP错误
            tmp_path = "/tmp/accounts_detail.xlsx"
            with open(tmp_path, "wb") as f:
                f.write(response.content)
            st.write(f"[DEBUG] 从 {url} 下载 accounts_detail.xlsx 到 {tmp_path}")
            df = pd.read_excel(tmp_path)
            st.write("[DEBUG] 云端 accounts_detail.xlsx 加载成功，shape:", df.shape)
            return df
        except Exception as e:
            st.error(f"云端数据加载失败: {e}")
            return None
    except Exception as e:
        st.error(f"账号数据加载失败: {e}")
        return None

@st.cache_data
def load_redash_data():
    try:
        local_path = "data/redash_data/redash_data_2025-07-14.csv"
        if os.path.exists(local_path):
            df = pd.read_csv(local_path)
            st.write("[DEBUG] 本地 redash_data_2025-07-14.csv 加载成功，shape:", df.shape)
            return df
        
        # 尝试从云端加载
        try:
            try:
                url = st.secrets["REDASH_URL"]
            except Exception as secrets_error:
                st.error(f"无法获取云端数据URL: {secrets_error}")
                return None
            response = requests.get(url)
            response.raise_for_status()  # 检查HTTP错误
            tmp_path = "/tmp/redash_data.csv"
            with open(tmp_path, "wb") as f:
                f.write(response.content)
            st.write(f"[DEBUG] 从 {url} 下载 redash_data.csv 到 {tmp_path}")
            df = pd.read_csv(tmp_path)
            st.write("[DEBUG] 云端 redash_data.csv 加载成功，shape:", df.shape)
            return df
        except Exception as e:
            st.error(f"云端数据加载失败: {e}")
            return None
    except Exception as e:
        st.error(f"Redash数据加载失败: {e}")
        return None

@st.cache_data
def load_clicks_data():
    try:
        local_path = "data/clicks/your_clicks_file.csv"
        if os.path.exists(local_path):
            df = pd.read_csv(local_path)
            st.write("[DEBUG] 本地 clicks 加载成功，shape:", df.shape)
            return df
        
        # 尝试从云端加载
        try:
            try:
                url = st.secrets["CLICKS_URL"]
            except Exception as secrets_error:
                st.error(f"无法获取云端数据URL: {secrets_error}")
                return None
            response = requests.get(url)
            response.raise_for_status()  # 检查HTTP错误
            tmp_path = "/tmp/clicks.csv"
            with open(tmp_path, "wb") as f:
                f.write(response.content)
            st.write(f"[DEBUG] 从 {url} 下载 clicks.csv 到 {tmp_path}")
            df = pd.read_csv(tmp_path)
            st.write("[DEBUG] 云端 clicks.csv 加载成功，shape:", df.shape)
            return df
        except Exception as e:
            st.error(f"云端数据加载失败: {e}")
            return None
    except Exception as e:
        st.error(f"点击数据加载失败: {e}")
        return None

# 数据加载和错误处理
st.header("📊 数据加载测试")

try:
    accounts_df = load_accounts_data()
    st.write(f"[DEBUG] accounts_df shape: {accounts_df.shape if accounts_df is not None else 'None'}")
except Exception as e:
    st.error(f"❌ 账号数据加载失败: {e}")
    accounts_df = None

try:
    redash_df = load_redash_data()
    st.write(f"[DEBUG] redash_df shape: {redash_df.shape if redash_df is not None else 'None'}")
except Exception as e:
    st.error(f"❌ Redash数据加载失败: {e}")
    redash_df = None

try:
    clicks_df = load_clicks_data()
    st.write(f"[DEBUG] clicks_df shape: {clicks_df.shape if clicks_df is not None else 'None'}")
except Exception as e:
    st.error(f"❌ 点击数据加载失败: {e}")
    clicks_df = None

# 检查数据是否都加载成功
if accounts_df is None or redash_df is None or clicks_df is None:
    st.error("❌ 部分数据加载失败，请检查数据文件是否存在")
    st.stop()

# 初始化数据处理器
try:
    processor = EnhancedTikTokDataProcessor(
        accounts_df=accounts_df,
        redash_df=redash_df,
        clicks_df=clicks_df
    )
    st.write("[DEBUG] EnhancedTikTokDataProcessor 初始化成功")
except Exception as e:
    st.error(f"❌ 数据处理器初始化失败: {e}")
    st.stop()

# 合并数据
try:
    processor.merge_data()
    st.write(f"[DEBUG] merge_data() 完成，merged_df shape: {processor.merged_df.shape if processor.merged_df is not None else 'None'}")
except Exception as e:
    st.error(f"❌ 数据合并失败: {e}")
    st.stop()

if processor.merged_df is None or processor.merged_df.empty:
    st.error("❌ 数据合并后为空，请检查数据文件内容")
    st.stop()

st.success("✅ 所有数据加载和合并成功！")

# 显示数据摘要
st.header("📋 数据摘要")
summary = processor.get_data_summary()
if summary:
    st.write(summary)
else:
    st.warning("暂无数据摘要")

st.success("🎉 测试完成！如果看到这个消息，说明修复成功。") 