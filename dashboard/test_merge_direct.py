import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pandas as pd
import streamlit as st
from enhanced_data_processor import EnhancedTikTokDataProcessor

st.title("🔧 直接测试 merge_data")

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
    
    # 直接测试 merge_data 的逻辑
    st.write("### 🔄 直接测试 merge_data 逻辑")
    
    # 获取数据
    redash_df = processor.redash_df
    accounts_df = processor.accounts_df
    clicks_df = processor.clicks_df
    
    st.write(f"[DEBUG] redash_df shape: {redash_df.shape if redash_df is not None else 'None'}")
    st.write(f"[DEBUG] accounts_df shape: {accounts_df.shape if accounts_df is not None else 'None'}")
    st.write(f"[DEBUG] clicks_df shape: {clicks_df.shape if clicks_df is not None else 'None'}")
    
    if redash_df is None:
        st.error("❌ redash_df 为 None")
        st.stop()
    
    if accounts_df is None:
        st.error("❌ accounts_df 为 None")
        st.stop()
    
    # 创建 group_mapping
    st.write("[DEBUG] 创建 group_mapping...")
    try:
        if 'Tiktok ID' not in accounts_df.columns or 'Groups' not in accounts_df.columns:
            st.error(f"❌ accounts_df 缺少必要的列，实际列: {accounts_df.columns.tolist()}")
            st.stop()
        
        accounts_df['Tiktok ID'] = accounts_df['Tiktok ID'].astype(str)
        group_mapping = accounts_df[['Tiktok ID', 'Groups']].drop_duplicates()
        group_mapping = group_mapping.rename(columns={'Tiktok ID': 'user_id', 'Groups': 'group'})
        group_mapping['user_id'] = group_mapping['user_id'].astype(str)
        group_mapping['group'] = group_mapping['group'].fillna('Unknown')
        
        st.write(f"[DEBUG] group_mapping shape: {group_mapping.shape}")
        st.write(f"[DEBUG] group_mapping columns: {group_mapping.columns.tolist()}")
        
    except Exception as e:
        st.error(f"❌ 创建 group_mapping 失败: {str(e)}")
        st.stop()
    
    # 处理 redash_df 的日期列
    st.write("[DEBUG] 处理 redash_df 日期列...")
    try:
        if 'date' not in redash_df.columns:
            if 'YMDdate' in redash_df.columns:
                redash_df['date'] = pd.to_datetime(redash_df['YMDdate'], errors='coerce')
                st.write("[DEBUG] 从 'YMDdate' 列创建 'date' 列")
            else:
                st.error(f"❌ redash_df 缺少日期列，实际列: {redash_df.columns.tolist()}")
                st.stop()
        
        if not pd.api.types.is_datetime64_any_dtype(redash_df['date']):
            redash_df['date'] = pd.to_datetime(redash_df['date'], errors='coerce')
        
        redash_df = redash_df.dropna(subset=['date'])
        st.write(f"[DEBUG] 处理日期后 redash_df shape: {redash_df.shape}")
        
    except Exception as e:
        st.error(f"❌ 处理日期列失败: {str(e)}")
        st.stop()
    
    # 处理 user_id 列
    st.write("[DEBUG] 处理 user_id 列...")
    try:
        if 'user_id' in redash_df.columns:
            redash_df['user_id'] = redash_df['user_id'].astype(str)
            st.write(f"[DEBUG] redash_df['user_id'] dtype: {redash_df['user_id'].dtype}")
        else:
            st.error(f"❌ redash_df 缺少 'user_id' 列，实际列: {redash_df.columns.tolist()}")
            st.stop()
    except Exception as e:
        st.error(f"❌ 处理 user_id 列失败: {str(e)}")
        st.stop()
    
    # 执行合并
    st.write("[DEBUG] 执行合并操作...")
    try:
        st.write(f"[DEBUG] redash_df shape: {redash_df.shape}")
        st.write(f"[DEBUG] group_mapping shape: {group_mapping.shape}")
        st.write(f"[DEBUG] redash_df columns: {redash_df.columns.tolist()}")
        st.write(f"[DEBUG] group_mapping columns: {group_mapping.columns.tolist()}")
        
        merged_df = redash_df.merge(group_mapping, on='user_id', how='left')
        
        st.write(f"[DEBUG] 合并后 shape: {merged_df.shape}")
        st.write(f"[DEBUG] merged_df columns: {merged_df.columns.tolist()}")
        
        # 处理 group 列
        if 'Groups' in merged_df.columns:
            merged_df = merged_df.rename(columns={'Groups': 'group'})
        merged_df['group'] = merged_df['group'].fillna('Unknown')
        
        st.success("✅ 合并成功")
        st.write("merged_df 前3行:")
        st.dataframe(merged_df.head(3))
        
        # 设置结果
        processor.merged_df = merged_df
        processor.group_mapping = group_mapping
        processor.clicks_df = clicks_df
        
        st.success("✅ 数据处理器更新成功")
        
    except Exception as e:
        st.error(f"❌ 合并操作失败: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")
        st.stop()
        
except Exception as e:
    st.error(f"❌ 错误: {str(e)}")
    import traceback
    st.error(f"详细错误: {traceback.format_exc()}") 