import streamlit as st
import os
import pandas as pd

st.title("🔍 路径测试工具")

# 显示当前工作目录
st.write(f"**当前工作目录:** {os.getcwd()}")

# 显示当前目录内容
st.write("**当前目录内容:**")
try:
    current_files = os.listdir(".")
    st.write(current_files)
except Exception as e:
    st.write(f"读取当前目录失败: {e}")

# 检查data目录
st.write("**检查data目录:**")
if os.path.exists("data"):
    st.success("✅ data目录存在")
    try:
        data_files = os.listdir("data")
        st.write(f"data目录内容: {data_files}")
        
        # 检查子目录
        for subdir in ['redash_data', 'clicks', 'postingManager_data']:
            subdir_path = os.path.join("data", subdir)
            if os.path.exists(subdir_path):
                st.success(f"✅ data/{subdir} 目录存在")
                try:
                    subdir_files = os.listdir(subdir_path)
                    st.write(f"data/{subdir} 内容: {subdir_files}")
                except Exception as e:
                    st.error(f"❌ 读取 data/{subdir} 失败: {e}")
            else:
                st.error(f"❌ data/{subdir} 目录不存在")
    except Exception as e:
        st.error(f"❌ 读取data目录失败: {e}")
else:
    st.error("❌ data目录不存在")

# 测试文件路径
st.write("**测试文件路径:**")

# 测试accounts文件
accounts_paths = [
    "data/postingManager_data/accounts_detail.xlsx",
    "../data/postingManager_data/accounts_detail.xlsx",
    "./data/postingManager_data/accounts_detail.xlsx"
]

st.write("**Accounts文件测试:**")
for path in accounts_paths:
    if os.path.exists(path):
        st.success(f"✅ {path} 存在")
        try:
            df = pd.read_excel(path)
            st.write(f"   - 文件大小: {df.shape}")
        except Exception as e:
            st.error(f"   - 读取失败: {e}")
    else:
        st.error(f"❌ {path} 不存在")

# 测试redash文件
redash_paths = [
    "data/redash_data/redash_data_2025-07-14.csv",
    "../data/redash_data/redash_data_2025-07-14.csv",
    "./data/redash_data/redash_data_2025-07-14.csv"
]

st.write("**Redash文件测试:**")
for path in redash_paths:
    if os.path.exists(path):
        st.success(f"✅ {path} 存在")
        try:
            df = pd.read_csv(path)
            st.write(f"   - 文件大小: {df.shape}")
        except Exception as e:
            st.error(f"   - 读取失败: {e}")
    else:
        st.error(f"❌ {path} 不存在")

# 测试clicks文件
clicks_paths = [
    "data/clicks/20250714ClicksInsnap.csv",
    "data/clicks/20250711ClicksInsnap.csv",
    "data/clicks/your_clicks_file.csv",
    "../data/clicks/20250714ClicksInsnap.csv",
    "./data/clicks/20250714ClicksInsnap.csv"
]

st.write("**Clicks文件测试:**")
for path in clicks_paths:
    if os.path.exists(path):
        st.success(f"✅ {path} 存在")
        try:
            df = pd.read_csv(path)
            st.write(f"   - 文件大小: {df.shape}")
        except Exception as e:
            st.error(f"   - 读取失败: {e}")
    else:
        st.error(f"❌ {path} 不存在")

st.write("**测试完成！**") 