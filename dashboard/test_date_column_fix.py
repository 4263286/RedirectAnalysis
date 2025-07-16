import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pandas as pd
import streamlit as st
from enhanced_data_processor import EnhancedTikTokDataProcessor

st.title("测试日期列修复")

# 初始化数据处理器，使用正确的相对路径
processor = EnhancedTikTokDataProcessor(
    redash_data_dir='../data/redash_data',
    accounts_file_path='../data/postingManager_data/accounts_detail.xlsx',
    clicks_data_dir='../data/clicks'
)

# 尝试合并数据
st.write("正在合并数据...")
merge_success = processor.merge_data()

if merge_success:
    st.success("✅ 数据合并成功")
    
    # 检查 merged_df 的列
    if processor.merged_df is not None:
        st.write(f"merged_df 列名: {processor.merged_df.columns.tolist()}")
        st.write(f"merged_df 形状: {processor.merged_df.shape}")
        
        # 检查是否有 date 列
        if 'date' in processor.merged_df.columns:
            st.success("✅ merged_df 包含 'date' 列")
            st.write(f"date 列数据类型: {processor.merged_df['date'].dtype}")
            st.write(f"date 列前5个值: {processor.merged_df['date'].head().tolist()}")
            
            # 尝试获取数据摘要
            st.write("正在获取数据摘要...")
            try:
                summary = processor.get_data_summary()
                st.success("✅ 数据摘要获取成功")
                st.write("数据摘要:", summary)
            except Exception as e:
                st.error(f"❌ 获取数据摘要失败: {str(e)}")
        else:
            st.error("❌ merged_df 缺少 'date' 列")
    else:
        st.error("❌ merged_df 为 None")
else:
    st.error("❌ 数据合并失败") 