import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pandas as pd
import streamlit as st
from enhanced_data_processor import EnhancedTikTokDataProcessor

st.title("🔧 简单 merge_data 测试")

st.write("### 📋 基本信息")
st.write(f"Python 版本: {sys.version}")
st.write(f"当前工作目录: {os.getcwd()}")

# 初始化数据处理器
st.write("### 🔧 初始化数据处理器")
try:
    processor = EnhancedTikTokDataProcessor()
    st.success("✅ 数据处理器初始化成功")
    
    # 检查数据
    st.write("### 📊 数据检查")
    st.write(f"redash_df: {processor.redash_df.shape if processor.redash_df is not None else 'None'}")
    st.write(f"accounts_df: {processor.accounts_df.shape if processor.accounts_df is not None else 'None'}")
    st.write(f"clicks_df: {processor.clicks_df.shape if processor.clicks_df is not None else 'None'}")
    
    # 测试 merge_data
    st.write("### 🔄 测试 merge_data")
    
    # 强制刷新
    st.write("即将调用 merge_data()...")
    
    # 调用 merge_data
    result = processor.merge_data()
    
    st.write(f"merge_data() 返回: {result}")
    st.write(f"merged_df: {processor.merged_df.shape if processor.merged_df is not None else 'None'}")
    
    if result:
        st.success("✅ merge_data() 成功")
        if processor.merged_df is not None:
            st.write("merged_df 列名:", processor.merged_df.columns.tolist())
            st.write("merged_df 前3行:")
            st.dataframe(processor.merged_df.head(3))
    else:
        st.error("❌ merge_data() 失败")
        
except Exception as e:
    st.error(f"❌ 错误: {str(e)}")
    import traceback
    st.error(f"详细错误: {traceback.format_exc()}") 