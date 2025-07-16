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
    page_title="数据合并调试",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 数据合并问题调试")

# 添加 scripts 目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_dir = os.path.join(parent_dir, 'scripts')

if os.path.exists(scripts_dir):
    sys.path.insert(0, scripts_dir)

try:
    from enhanced_data_processor import EnhancedTikTokDataProcessor
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
                st.warning(f"本地运行时无法获取云端数据URL: {secrets_error}")
                st.info("💡 提示：这是正常的，因为本地运行时没有设置secrets。在Streamlit Cloud上部署时会自动从云端加载数据。")
                return None
            response = requests.get(url)
            response.raise_for_status()
            tmp_path = "/tmp/accounts_detail.xlsx"
            with open(tmp_path, "wb") as f:
                f.write(response.content)
            st.write(f"[DEBUG] 从云端下载 accounts_detail.xlsx")
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
                st.warning(f"本地运行时无法获取云端数据URL: {secrets_error}")
                st.info("💡 提示：这是正常的，因为本地运行时没有设置secrets。在Streamlit Cloud上部署时会自动从云端加载数据。")
                return None
            response = requests.get(url)
            response.raise_for_status()
            tmp_path = "/tmp/redash_data.csv"
            with open(tmp_path, "wb") as f:
                f.write(response.content)
            st.write(f"[DEBUG] 从云端下载 redash_data.csv")
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
                st.warning(f"本地运行时无法获取云端数据URL: {secrets_error}")
                st.info("💡 提示：这是正常的，因为本地运行时没有设置secrets。在Streamlit Cloud上部署时会自动从云端加载数据。")
                return None
            response = requests.get(url)
            response.raise_for_status()
            tmp_path = "/tmp/clicks.csv"
            with open(tmp_path, "wb") as f:
                f.write(response.content)
            st.write(f"[DEBUG] 从云端下载 clicks.csv")
            df = pd.read_csv(tmp_path)
            st.write("[DEBUG] 云端 clicks.csv 加载成功，shape:", df.shape)
            return df
        except Exception as e:
            st.error(f"云端数据加载失败: {e}")
            return None
    except Exception as e:
        st.error(f"点击数据加载失败: {e}")
        return None

# 数据加载测试
st.header("📊 数据加载测试")

accounts_df = load_accounts_data()
redash_df = load_redash_data()
clicks_df = load_clicks_data()

# 显示数据详情
if accounts_df is not None:
    st.subheader("📋 Accounts 数据详情")
    st.write(f"Shape: {accounts_df.shape}")
    st.write(f"Columns: {accounts_df.columns.tolist()}")
    st.write("前5行数据:")
    st.dataframe(accounts_df.head())
    
    # 检查关键列
    if 'Tiktok ID' in accounts_df.columns:
        st.success("✅ 找到 'Tiktok ID' 列")
        st.write(f"Tiktok ID 唯一值数量: {accounts_df['Tiktok ID'].nunique()}")
    else:
        st.error("❌ 缺少 'Tiktok ID' 列")
    
    if 'Groups' in accounts_df.columns:
        st.success("✅ 找到 'Groups' 列")
        st.write(f"Groups 唯一值数量: {accounts_df['Groups'].nunique()}")
    else:
        st.error("❌ 缺少 'Groups' 列")

if redash_df is not None:
    st.subheader("📋 Redash 数据详情")
    st.write(f"Shape: {redash_df.shape}")
    st.write(f"Columns: {redash_df.columns.tolist()}")
    st.write("前5行数据:")
    st.dataframe(redash_df.head())
    
    # 检查关键列
    if 'user_id' in redash_df.columns:
        st.success("✅ 找到 'user_id' 列")
        st.write(f"user_id 唯一值数量: {redash_df['user_id'].nunique()}")
    else:
        st.error("❌ 缺少 'user_id' 列")

if clicks_df is not None:
    st.subheader("📋 Clicks 数据详情")
    st.write(f"Shape: {clicks_df.shape}")
    st.write(f"Columns: {clicks_df.columns.tolist()}")
    st.write("前5行数据:")
    st.dataframe(clicks_df.head())

# 数据合并测试
st.header("🔗 数据合并测试")

# 如果没有真实数据，创建模拟数据进行测试
if accounts_df is None or redash_df is None:
    st.warning("⚠️ 缺少真实数据文件，创建模拟数据进行测试")
    
    # 创建模拟数据
    import numpy as np
    from datetime import datetime, timedelta
    
    # 模拟 accounts 数据
    st.subheader("📋 创建模拟 Accounts 数据")
    mock_accounts_data = {
        'Tiktok ID': [f'user_{i:03d}' for i in range(1, 21)],
        'Groups': ['yujie_main_avatar'] * 10 + ['wan_produce101'] * 10,
        'username': [f'user_{i:03d}' for i in range(1, 21)],
        'follower_count': np.random.randint(1000, 100000, 20),
        'like_count': np.random.randint(100, 10000, 20)
    }
    accounts_df = pd.DataFrame(mock_accounts_data)
    st.write("模拟 accounts 数据:")
    st.dataframe(accounts_df.head())
    
    # 模拟 redash 数据
    st.subheader("📋 创建模拟 Redash 数据")
    dates = pd.date_range(start='2025-01-01', end='2025-01-31', freq='D')
    mock_redash_data = []
    
    for date in dates:
        for user_id in mock_accounts_data['Tiktok ID']:
            mock_redash_data.append({
                'date': date,
                'user_id': user_id,
                'view_count': np.random.randint(1000, 50000),
                'like_count': np.random.randint(100, 5000),
                'comment_count': np.random.randint(10, 500),
                'share_count': np.random.randint(5, 200),
                'post_count': np.random.randint(1, 10),
                'view_diff': np.random.randint(-1000, 5000),
                'like_diff': np.random.randint(-100, 500),
                'comment_diff': np.random.randint(-10, 50),
                'share_diff': np.random.randint(-5, 20),
                'post_diff': np.random.randint(-1, 3)
            })
    
    redash_df = pd.DataFrame(mock_redash_data)
    st.write("模拟 redash 数据:")
    st.dataframe(redash_df.head())
    
    st.success("✅ 模拟数据创建成功，继续测试合并功能")

# 创建 group_mapping
st.subheader("📋 Group Mapping 创建")
try:
    group_mapping = accounts_df[['Tiktok ID', 'Groups']].drop_duplicates()
    group_mapping = group_mapping.rename(columns={'Tiktok ID': 'user_id', 'Groups': 'group'})
    group_mapping['user_id'] = group_mapping['user_id'].astype(str)
    group_mapping['group'] = group_mapping['group'].fillna('Unknown')
    
    st.write(f"Group mapping shape: {group_mapping.shape}")
    st.write("Group mapping 前5行:")
    st.dataframe(group_mapping.head())
    
    st.success("✅ Group mapping 创建成功")
except Exception as e:
    st.error(f"❌ Group mapping 创建失败: {e}")
    st.stop()

# 测试合并
st.subheader("🔗 数据合并测试")
try:
    # 确保 redash_df 的 user_id 为字符串
    redash_df['user_id'] = redash_df['user_id'].astype(str)
    
    # 执行合并
    merged_df = redash_df.merge(group_mapping, on='user_id', how='left')
    
    st.write(f"合并前 redash_df shape: {redash_df.shape}")
    st.write(f"合并前 group_mapping shape: {group_mapping.shape}")
    st.write(f"合并后 merged_df shape: {merged_df.shape}")
    
    if merged_df.empty:
        st.error("❌ 合并后数据为空")
    else:
        st.success("✅ 数据合并成功")
        st.write("合并后数据前5行:")
        st.dataframe(merged_df.head())
        
        # 检查分组信息
        if 'group' in merged_df.columns:
            st.write(f"分组数量: {merged_df['group'].nunique()}")
            st.write("分组统计:")
            st.write(merged_df['group'].value_counts())
        
except Exception as e:
    st.error(f"❌ 数据合并失败: {e}")
    st.write("错误详情:")
    st.exception(e)

# 测试数据处理器
st.header("🔧 数据处理器测试")
try:
    processor = EnhancedTikTokDataProcessor(
        accounts_df=accounts_df,
        redash_df=redash_df,
        clicks_df=clicks_df
    )
    st.success("✅ 数据处理器初始化成功")
    
    # 测试合并
    merge_result = processor.merge_data()
    st.write(f"合并结果: {merge_result}")
    
    if processor.merged_df is not None:
        st.write(f"处理器合并后 shape: {processor.merged_df.shape}")
        st.success("✅ 处理器合并成功")
    else:
        st.error("❌ 处理器合并失败")
        
except Exception as e:
    st.error(f"❌ 数据处理器测试失败: {e}")
    st.exception(e) 