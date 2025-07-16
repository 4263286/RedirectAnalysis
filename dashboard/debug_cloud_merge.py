import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pandas as pd
import streamlit as st
from enhanced_data_processor import EnhancedTikTokDataProcessor

st.title("🌐 云端 merge_data 调试工具")

st.write("### 📋 调试信息")
st.write(f"Python 版本: {sys.version}")
st.write(f"当前工作目录: {os.getcwd()}")
st.write(f"当前目录内容: {os.listdir('.')}")

# 检查数据目录
data_dir = 'data'
if os.path.exists(data_dir):
    st.write(f"✅ {data_dir} 目录存在")
    st.write(f"{data_dir} 目录内容: {os.listdir(data_dir)}")
    
    # 检查子目录
    for subdir in ['redash_data', 'clicks', 'postingManager_data']:
        subdir_path = os.path.join(data_dir, subdir)
        if os.path.exists(subdir_path):
            files = os.listdir(subdir_path)
            st.write(f"📁 {subdir_path}: {files}")
        else:
            st.write(f"❌ {subdir_path} 不存在")
else:
    st.write(f"❌ {data_dir} 目录不存在")

# 初始化数据处理器
st.write("### 🔧 初始化数据处理器")
try:
    processor = EnhancedTikTokDataProcessor()
    st.success("✅ 数据处理器初始化成功")
    
    # 检查数据加载
    st.write("### 📊 数据加载状态")
    
    if processor.redash_df is not None:
        st.success(f"✅ redash_df 加载成功: {processor.redash_df.shape}")
        st.write(f"redash_df 列名: {processor.redash_df.columns.tolist()}")
    else:
        st.error("❌ redash_df 为 None")
    
    if processor.accounts_df is not None:
        st.success(f"✅ accounts_df 加载成功: {processor.accounts_df.shape}")
        st.write(f"accounts_df 列名: {processor.accounts_df.columns.tolist()}")
    else:
        st.error("❌ accounts_df 为 None")
    
    if processor.clicks_df is not None:
        st.success(f"✅ clicks_df 加载成功: {processor.clicks_df.shape}")
        st.write(f"clicks_df 列名: {processor.clicks_df.columns.tolist()}")
    else:
        st.error("❌ clicks_df 为 None")
    
    # 测试 merge_data
    st.write("### 🔄 测试 merge_data")
    st.write("[DEBUG] 开始调用 merge_data()...")
    
    try:
        merge_result = processor.merge_data()
        st.write(f"[DEBUG] merge_data() 返回值: {merge_result}")
        st.write(f"[DEBUG] merge_data() 完成，merged_df shape: {processor.merged_df.shape if processor.merged_df is not None else 'None'}")
        
        if merge_result:
            st.success("✅ merge_data() 成功")
            if processor.merged_df is not None:
                st.write(f"merged_df 列名: {processor.merged_df.columns.tolist()}")
                st.write(f"merged_df 前5行:")
                st.dataframe(processor.merged_df.head())
                
                # 测试 get_data_summary
                st.write("### 📈 测试 get_data_summary")
                try:
                    summary = processor.get_data_summary()
                    st.success("✅ get_data_summary() 成功")
                    st.write("数据摘要:", summary)
                except Exception as e:
                    st.error(f"❌ get_data_summary() 失败: {str(e)}")
                    import traceback
                    st.error(f"详细错误: {traceback.format_exc()}")
        else:
            st.error("❌ merge_data() 失败")
            
    except Exception as e:
        st.error(f"❌ merge_data() 异常: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")
        
except Exception as e:
    st.error(f"❌ 数据处理器初始化失败: {str(e)}")
    import traceback
    st.error(f"详细错误: {traceback.format_exc()}") 