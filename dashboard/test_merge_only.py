import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

st.title("🔍 Merge Data 专门测试")

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

# 创建测试数据
st.header("📊 创建测试数据")

# 模拟 accounts 数据
accounts_data = {
    'Tiktok ID': ['user_001', 'user_002', 'user_003'],
    'Groups': ['group1', 'group2', 'group1'],
    'username': ['user1', 'user2', 'user3']
}
accounts_df = pd.DataFrame(accounts_data)
st.write("Accounts数据:")
st.dataframe(accounts_df)

# 模拟 redash 数据
redash_data = {
    'user_id': ['user_001', 'user_002', 'user_003'],
    'date': pd.date_range('2025-01-01', periods=3),
    'view_count': [1000, 2000, 3000],
    'like_count': [100, 200, 300]
}
redash_df = pd.DataFrame(redash_data)
st.write("Redash数据:")
st.dataframe(redash_df)

# 模拟 clicks 数据
clicks_data = {
    'timestamp': pd.date_range('2025-01-01', periods=3),
    'session_id': ['s1', 's2', 's3'],
    'visitor_id': ['v1', 'v2', 'v3']
}
clicks_df = pd.DataFrame(clicks_data)
st.write("Clicks数据:")
st.dataframe(clicks_df)

# 测试数据处理器
st.header("🔧 测试数据处理器")

try:
    st.write("[DEBUG] 创建 EnhancedTikTokDataProcessor...")
    processor = EnhancedTikTokDataProcessor(
        accounts_df=accounts_df,
        redash_df=redash_df,
        clicks_df=clicks_df
    )
    st.success("✅ 数据处理器创建成功")
    
    st.write(f"[DEBUG] processor.accounts_df shape: {processor.accounts_df.shape}")
    st.write(f"[DEBUG] processor.redash_df shape: {processor.redash_df.shape}")
    st.write(f"[DEBUG] processor.clicks_df shape: {processor.clicks_df.shape}")
    
    # 测试 merge_data
    st.write("[DEBUG] 开始测试 merge_data()...")
    merge_result = processor.merge_data()
    
    st.write(f"[DEBUG] merge_data() 返回值: {merge_result}")
    st.write(f"[DEBUG] processor.merged_df shape: {processor.merged_df.shape if processor.merged_df is not None else 'None'}")
    
    if merge_result:
        st.success("✅ merge_data() 成功")
        if processor.merged_df is not None:
            st.write("合并后的数据:")
            st.dataframe(processor.merged_df.head())
    else:
        st.error("❌ merge_data() 失败")
        
except Exception as e:
    st.error(f"❌ 测试失败: {e}")
    st.write(f"[DEBUG] 异常详情: {str(e)}")
    import traceback
    st.write(f"[DEBUG] 完整异常: {traceback.format_exc()}") 