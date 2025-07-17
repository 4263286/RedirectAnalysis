import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import warnings
import sys
import os
import altair as alt
import requests
import pickle

# 环境和数据完整性调试输出
st.write('Python version:', sys.version)
try:
    import streamlit
    st.write('Streamlit version:', streamlit.__version__)
except Exception as e:
    st.write('Streamlit import error:', e)

st.write('Current working dir:', os.getcwd())
# 自动创建所需的空目录（如果不存在）
for d in [
    "data",
    "data/redash_data",
    "data/clicks",
    "data/postingManager_data"
]:
    os.makedirs(d, exist_ok=True)

# 检查目录内容，使用更健壮的路径处理
st.write(f'[DEBUG] 当前工作目录: {os.getcwd()}')
st.write(f'[DEBUG] 当前目录内容: {os.listdir(".")}')

try:
    if os.path.exists('data'):
        st.write('Files in data/:', os.listdir('data'))
        # 检查子目录
        for subdir in ['redash_data', 'clicks', 'postingManager_data']:
            subdir_path = os.path.join('data', subdir)
            if os.path.exists(subdir_path):
                st.write(f'Files in data/{subdir}/:', os.listdir(subdir_path))
            else:
                st.write(f'data/{subdir}/ 目录不存在')
    else:
        st.write('data/ 目录不存在')
except Exception as e:
    st.write('目录读取失败:', e)

# 添加 scripts 目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_dir = os.path.join(parent_dir, 'scripts')

if os.path.exists(scripts_dir):
    sys.path.insert(0, scripts_dir)

from enhanced_data_processor import EnhancedTikTokDataProcessor
from enhanced_visualization import EnhancedVisualization

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="TikTok 增强分析看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .chart-container {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .stAlert {
        background-color: #e8f4fd;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

import requests
import os
import pandas as pd

@st.cache_data
def load_accounts_data():
    try:
        # 尝试多个可能的路径
        possible_paths = [
            "data/postingManager_data/accounts_detail.xlsx",
            "../data/postingManager_data/accounts_detail.xlsx",
            "./data/postingManager_data/accounts_detail.xlsx",
            os.path.join(os.getcwd(), "data", "postingManager_data", "accounts_detail.xlsx")
        ]
        
        for local_path in possible_paths:
            if os.path.exists(local_path):
                df = pd.read_excel(local_path)
                st.write(f"[DEBUG] 本地 accounts_detail.xlsx 加载成功，路径: {local_path}, shape: {df.shape}")
                return df
        
        st.write(f"[DEBUG] 尝试的路径: {possible_paths}")
        st.write(f"[DEBUG] 当前工作目录: {os.getcwd()}")
        st.write(f"[DEBUG] 当前目录内容: {os.listdir('.')}")
        if os.path.exists('data'):
            st.write(f"[DEBUG] data目录内容: {os.listdir('data')}")
        else:
            st.write("[DEBUG] data目录不存在")
        
        # 如果本地文件不存在，尝试从云端加载
        
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

def load_redash_data():
    try:
        # 动态查找最新的 redash 数据文件
        def find_latest_redash_file():
            possible_dirs = [
                "data/redash_data",
                "../data/redash_data", 
                "./data/redash_data",
                os.path.join(os.getcwd(), "data", "redash_data")
            ]
            
            for data_dir in possible_dirs:
                if os.path.exists(data_dir):
                    redash_files = [f for f in os.listdir(data_dir) 
                                  if f.startswith('redash_data_') and f.endswith('.csv')]
                    if redash_files:
                        # 基于文件名中的日期选择最新文件
                        def extract_date_from_filename(filename):
                            try:
                                date_str = filename.replace('redash_data_', '').replace('.csv', '')
                                return pd.to_datetime(date_str)
                            except:
                                return pd.to_datetime('1900-01-01')
                        
                        latest_file = max(redash_files, key=extract_date_from_filename)
                        return os.path.join(data_dir, latest_file)
            return None
        
        latest_file_path = find_latest_redash_file()
        if latest_file_path:
            df = pd.read_csv(latest_file_path)
            st.write(f"[DEBUG] 本地 redash 数据加载成功，文件: {os.path.basename(latest_file_path)}, shape: {df.shape}")
            return df
        
        st.write(f"[DEBUG] 未找到本地 redash 数据文件")
        st.write(f"[DEBUG] 当前工作目录: {os.getcwd()}")
        if os.path.exists('data/redash_data'):
            st.write(f"[DEBUG] data/redash_data目录内容: {os.listdir('data/redash_data')}")
        else:
            st.write("[DEBUG] data/redash_data目录不存在")
        
        # 如果本地文件不存在，尝试从云端加载
        
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

def load_clicks_data():
    try:
        # 动态查找最新的 clicks 数据文件
        def find_latest_clicks_file():
            possible_dirs = [
                "data/clicks",
                "../data/clicks", 
                "./data/clicks",
                os.path.join(os.getcwd(), "data", "clicks")
            ]
            
            for data_dir in possible_dirs:
                if os.path.exists(data_dir):
                    clicks_files = [f for f in os.listdir(data_dir) 
                                  if f.endswith('.csv')]
                    if clicks_files:
                        # 基于文件名中的日期选择最新文件
                        def extract_date_from_clicks_filename(filename):
                            try:
                                date_str = filename[:8]  # 取前8位作为日期
                                return pd.to_datetime(date_str, format='%Y%m%d')
                            except:
                                return pd.to_datetime('1900-01-01')
                        
                        latest_file = max(clicks_files, key=extract_date_from_clicks_filename)
                        return os.path.join(data_dir, latest_file)
            return None
        
        latest_file_path = find_latest_clicks_file()
        if latest_file_path:
            df = pd.read_csv(latest_file_path)
            st.write(f"[DEBUG] 本地 clicks 数据加载成功，文件: {os.path.basename(latest_file_path)}, shape: {df.shape}")
            return df
        
        st.write(f"[DEBUG] 未找到本地 clicks 数据文件")
        st.write(f"[DEBUG] 当前工作目录: {os.getcwd()}")
        if os.path.exists('data/clicks'):
            st.write(f"[DEBUG] data/clicks目录内容: {os.listdir('data/clicks')}")
        else:
            st.write("[DEBUG] data/clicks目录不存在")
        
        # 如果本地文件不存在，尝试从云端加载
        
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
try:
    accounts_df = load_accounts_data()
    st.write(f"[DEBUG] accounts_df shape: {accounts_df.shape if accounts_df is not None else 'None'}")
    if accounts_df is not None:
        st.write(f"[DEBUG] accounts_df columns: {accounts_df.columns.tolist()}")
except Exception as e:
    st.error(f"❌ 账号数据加载失败: {e}")
    accounts_df = None

try:
    redash_df = load_redash_data()
    st.write(f"[DEBUG] redash_df shape: {redash_df.shape if redash_df is not None else 'None'}")
    if redash_df is not None:
        st.write(f"[DEBUG] redash_df columns: {redash_df.columns.tolist()}")
except Exception as e:
    st.error(f"❌ Redash数据加载失败: {e}")
    redash_df = None

try:
    clicks_df = load_clicks_data()
    st.write(f"[DEBUG] clicks_df shape: {clicks_df.shape if clicks_df is not None else 'None'}")
    if clicks_df is not None:
        st.write(f"[DEBUG] clicks_df columns: {clicks_df.columns.tolist()}")
except Exception as e:
    st.error(f"❌ 点击数据加载失败: {e}")
    clicks_df = None

# 检查数据是否都加载成功
if accounts_df is None or redash_df is None or clicks_df is None:
    st.warning("⚠️ 部分数据加载失败")
    
    # 检查是否在云端环境（通过检查是否有secrets来判断）
    try:
        # 尝试访问secrets，如果成功说明在云端
        test_secret = st.secrets.get("ACCOUNTS_URL", None)
        is_cloud = test_secret is not None
    except:
        is_cloud = False
    
    if is_cloud:
        st.error("❌ 云端数据加载失败，请检查secrets配置和数据文件URL")
        st.stop()
    else:
        st.info("💡 本地数据文件不存在，创建模拟数据进行演示")
        
        # 创建模拟数据
        import numpy as np
        from datetime import datetime, timedelta
        
        # 模拟 accounts 数据
        mock_accounts_data = {
            'Tiktok ID': [f'user_{i:03d}' for i in range(1, 21)],
            'Groups': ['yujie_main_avatar'] * 10 + ['wan_produce101'] * 10,
            'username': [f'user_{i:03d}' for i in range(1, 21)],
            'follower_count': np.random.randint(1000, 100000, 20),
            'like_count': np.random.randint(100, 10000, 20)
        }
        accounts_df = pd.DataFrame(mock_accounts_data)
        
        # 模拟 redash 数据
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
        
        # 模拟 clicks 数据
        mock_clicks_data = []
        for date in dates[:10]:  # 只创建前10天的点击数据
            for _ in range(np.random.randint(50, 200)):  # 每天50-200次点击
                mock_clicks_data.append({
                    'date': date.date(),
                    'timestamp': date,
                    'session_id': f'session_{np.random.randint(1, 1000)}',
                    'visitor_id': f'visitor_{np.random.randint(1, 500)}',
                    'page_url': np.random.choice(['https://insnap.ai/videos', 'https://insnap.ai/zh/download']),
                    'page_type': np.random.choice(['videos', 'download']),
                    'view_diff': np.random.randint(1, 100)
                })
        
        clicks_df = pd.DataFrame(mock_clicks_data)
        
        st.info("💡 使用模拟数据进行演示。请确保本地数据文件存在：")
        st.info("📁 data/postingManager_data/accounts_detail.xlsx")
        st.info("📁 data/redash_data/redash_data_2025-07-14.csv")
        st.info("📁 data/clicks/your_clicks_file.csv")

# 初始化 session_state
if 'merge_successful' not in st.session_state:
    st.session_state.merge_successful = False
if 'merged_df' not in st.session_state:
    st.session_state.merged_df = None
if 'group_mapping' not in st.session_state:
    st.session_state.group_mapping = None
if 'clicks_df' not in st.session_state:
    st.session_state.clicks_df = None

# 调试 session_state 状态
st.write("[DEBUG] === Session State 调试信息 ===")
st.write(f"[DEBUG] st.session_state.merge_successful: {st.session_state.merge_successful}")
st.write(f"[DEBUG] st.session_state.merged_df 是否为 None: {st.session_state.merged_df is None}")
st.write(f"[DEBUG] st.session_state.group_mapping 是否为 None: {st.session_state.group_mapping is None}")
st.write(f"[DEBUG] st.session_state.clicks_df 是否为 None: {st.session_state.clicks_df is None}")
if st.session_state.merged_df is not None:
    st.write(f"[DEBUG] st.session_state.merged_df shape: {st.session_state.merged_df.shape}")
st.write("[DEBUG] === Session State 调试信息结束 ===")

# === 自动检测数据文件变化，必要时清空合并结果 ===
def get_file_mtime(path):
    return os.path.getmtime(path) if os.path.exists(path) else 0

# 你可以根据实际情况调整这些路径
file1 = os.path.join(os.path.dirname(__file__), '..', 'data', 'posts_detail.xlsx')
file2_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'redash_data')
file2 = None
if os.path.exists(file2_dir):
    redash_files = [f for f in os.listdir(file2_dir) if f.startswith('redash_data_') and f.endswith('.csv')]
    if redash_files:
        # 取最新日期的文件
        def extract_date_from_filename(filename):
            try:
                date_str = filename.replace('redash_data_', '').replace('.csv', '')
                return pd.to_datetime(date_str)
            except:
                return pd.to_datetime('1900-01-01')
        latest_file = max(redash_files, key=extract_date_from_filename)
        file2 = os.path.join(file2_dir, latest_file)

current_mtime = (get_file_mtime(file1), get_file_mtime(file2) if file2 else 0)

if "last_mtime" not in st.session_state or st.session_state["last_mtime"] != current_mtime:
    st.session_state.pop("merged_df", None)
    st.session_state.pop("merge_successful", None)
    st.session_state["last_mtime"] = current_mtime

# === 页面顶部添加强制刷新按钮 ===
if st.button("强制刷新数据（重新合并）"):
    st.session_state.pop("merged_df", None)
    st.session_state.pop("merge_successful", None)
    st.rerun()

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

# 检查是否之前已经成功合并
st.write("[DEBUG] 检查 session_state 条件...")
st.write(f"[DEBUG] st.session_state.merge_successful: {st.session_state.merge_successful}")
st.write(f"[DEBUG] st.session_state.merged_df is not None: {st.session_state.merged_df is not None}")
st.write(f"[DEBUG] 条件结果: {st.session_state.merge_successful and st.session_state.merged_df is not None}")

MERGED_PATH = '/tmp/merged_result.parquet'
GROUP_MAPPING_PATH = '/tmp/group_mapping.pkl'
CLICKS_PATH = '/tmp/clicks_df.parquet'

# 启动时优先加载持久化合并结果
if os.path.exists(MERGED_PATH):
    st.success("✅ 已加载持久化的合并结果，无需重新合并")
    merged_df = pd.read_parquet(MERGED_PATH)
    processor.merged_df = merged_df
    # group_mapping
    if os.path.exists(GROUP_MAPPING_PATH):
        with open(GROUP_MAPPING_PATH, 'rb') as f:
            processor.group_mapping = pickle.load(f)
    # clicks_df
    if os.path.exists(CLICKS_PATH):
        processor.clicks_df = pd.read_parquet(CLICKS_PATH)
    merge_result = True
else:
    # 合并数据
    try:
        st.write("[DEBUG] 开始调用 merge_data()...")
        st.write(f"[DEBUG] processor.redash_df shape: {processor.redash_df.shape if processor.redash_df is not None else 'None'}")
        st.write(f"[DEBUG] processor.accounts_df shape: {processor.accounts_df.shape if processor.accounts_df is not None else 'None'}")
        st.write(f"[DEBUG] processor.clicks_df shape: {processor.clicks_df.shape if processor.clicks_df is not None else 'None'}")
        
        # 强制刷新输出
        st.write("[DEBUG] 即将调用 merge_data()，请等待...")
        
        merge_result = processor.merge_data()
        
        st.write(f"[DEBUG] merge_data() 返回值: {merge_result}")
        st.write(f"[DEBUG] merge_data() 完成，merged_df shape: {processor.merged_df.shape if processor.merged_df is not None else 'None'}")
        
        if not merge_result:
            st.error("❌ merge_data() 返回 False，合并失败")
            st.write("[DEBUG] 请检查上面的调试信息，找出合并失败的具体原因")
            
            # 尝试获取更多调试信息
            st.write("[DEBUG] 尝试检查 processor 状态...")
            st.write(f"[DEBUG] processor.redash_df 是否为 None: {processor.redash_df is None}")
            st.write(f"[DEBUG] processor.accounts_df 是否为 None: {processor.accounts_df is None}")
            st.write(f"[DEBUG] processor.clicks_df 是否为 None: {processor.clicks_df is None}")
            st.write(f"[DEBUG] processor.merged_df 是否为 None: {processor.merged_df is None}")
            
            # 提供直接测试选项
            st.write("### 🔧 调试选项")
            if st.button("运行直接合并测试"):
                st.write("### 🔄 直接测试合并逻辑")
                
                # 获取数据
                redash_df = processor.redash_df
                accounts_df = processor.accounts_df
                clicks_df = processor.clicks_df
                
                if redash_df is None or accounts_df is None:
                    st.error("❌ 数据为 None，无法测试")
                    st.stop()
                
                # 创建 group_mapping
                st.write("[DEBUG] 创建 group_mapping...")
                try:
                    accounts_df['Tiktok ID'] = accounts_df['Tiktok ID'].astype(str)
                    group_mapping = accounts_df[['Tiktok ID', 'Groups']].drop_duplicates()
                    group_mapping = group_mapping.rename(columns={'Tiktok ID': 'user_id', 'Groups': 'group'})
                    group_mapping['user_id'] = group_mapping['user_id'].astype(str)
                    group_mapping['group'] = group_mapping['group'].fillna('Unknown')
                    st.write(f"[DEBUG] group_mapping shape: {group_mapping.shape}")
                except Exception as e:
                    st.error(f"❌ 创建 group_mapping 失败: {str(e)}")
                    st.stop()
                
                # 处理日期列
                st.write("[DEBUG] 处理日期列...")
                try:
                    if 'date' not in redash_df.columns and 'YMDdate' in redash_df.columns:
                        redash_df['date'] = pd.to_datetime(redash_df['YMDdate'], errors='coerce')
                    redash_df = redash_df.dropna(subset=['date'])
                    st.write(f"[DEBUG] 处理日期后 shape: {redash_df.shape}")
                except Exception as e:
                    st.error(f"❌ 处理日期列失败: {str(e)}")
                    st.stop()
                
                # 执行合并
                st.write("[DEBUG] 执行合并...")
                try:
                    # 确保 user_id 列的数据类型一致
                    st.write(f"[DEBUG] redash_df['user_id'] dtype: {redash_df['user_id'].dtype}")
                    st.write(f"[DEBUG] group_mapping['user_id'] dtype: {group_mapping['user_id'].dtype}")
                    
                    # 将 redash_df 的 user_id 转换为字符串
                    redash_df['user_id'] = redash_df['user_id'].astype(str)
                    st.write(f"[DEBUG] 转换后 redash_df['user_id'] dtype: {redash_df['user_id'].dtype}")
                    
                    merged_df = redash_df.merge(group_mapping, on='user_id', how='left')
                    st.write(f"[DEBUG] 合并成功，shape: {merged_df.shape}")
                    
                    # 更新 processor
                    processor.merged_df = merged_df
                    processor.group_mapping = group_mapping
                    processor.clicks_df = clicks_df
                    
                    # 持久化保存
                    merged_df.to_parquet('/tmp/merged_result.parquet')
                    import pickle
                    with open('/tmp/group_mapping.pkl', 'wb') as f:
                        pickle.dump(group_mapping, f)
                    if clicks_df is not None:
                        clicks_df.to_parquet('/tmp/clicks_df.parquet')

                    st.success("✅ 直接合并测试成功！")
                    
                    # 使用 session_state 来标记合并成功
                    st.session_state.merge_successful = True
                    st.session_state.merged_df = merged_df
                    st.session_state.group_mapping = group_mapping
                    st.session_state.clicks_df = clicks_df
                    
                    st.success("🔄 数据已更新，请刷新页面查看完整仪表板")
                    st.info("💡 提示：点击浏览器刷新按钮或按 F5 键刷新页面")
                    
                    # 显示合并后的数据摘要
                    st.write("### 📊 合并后的数据摘要")
                    st.write(f"- 总行数: {len(merged_df)}")
                    st.write(f"- 日期范围: {merged_df['date'].min()} 到 {merged_df['date'].max()}")
                    st.write(f"- 用户数: {merged_df['user_id'].nunique()}")
                    st.write(f"- 分组数: {merged_df['group'].nunique()}")
                    
                    st.stop()
            
                except Exception as e:
                    st.error(f"❌ 合并失败: {str(e)}")
                    import traceback
                    st.error(f"详细错误: {traceback.format_exc()}")
            
            st.stop()
            
    except Exception as e:
        st.error(f"❌ 数据合并失败: {e}")
        st.write(f"[DEBUG] 异常详情: {str(e)}")
        import traceback
        st.error(f"[DEBUG] 完整错误堆栈: {traceback.format_exc()}")
        st.stop()

if processor.merged_df is None or processor.merged_df.empty:
    st.error("❌ 数据合并后为空，请检查数据文件内容")
    st.stop()

# 获取数据摘要
summary = processor.get_data_summary()

# 获取最新一天的增量指标
latest_increments = processor.get_latest_day_increment_metrics()
if latest_increments:
    summary['latest_day_increments'] = latest_increments

# 显示数据摘要卡片
if summary:
    st.markdown("### 📊 数据概览")
    summary_html = EnhancedVisualization().create_summary_cards(summary)
    st.markdown(summary_html, unsafe_allow_html=True)

# 侧边栏 - 筛选器
st.sidebar.header("📋 筛选设置")

# 日期范围选择
if processor.merged_df is not None:
    # Debug: 显示 merged_df['date'] 的唯一值和类型
    st.sidebar.write(f"DEBUG: merged_df['date'] unique: {processor.merged_df['date'].unique()}")
    st.sidebar.write(f"DEBUG: merged_df['date'] dtype: {processor.merged_df['date'].dtype}")

    min_date = processor.merged_df['date'].min()
    max_date = processor.merged_df['date'].max()
    st.sidebar.write(f"DEBUG: min_date={min_date} ({type(min_date)}), max_date={max_date} ({type(max_date)})")
    # 修复 NaT 问题
    if pd.isna(min_date) or min_date is pd.NaT:
        min_date = date.today()
    if pd.isna(max_date) or max_date is pd.NaT:
        max_date = date.today()
    if isinstance(min_date, pd.Timestamp):
        min_date = min_date.date()
    if isinstance(max_date, pd.Timestamp):
        max_date = max_date.date()
    st.sidebar.write(f"DEBUG: after convert, min_date={min_date}, max_date={max_date}")
    date_range = st.sidebar.date_input(
        "选择日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
    else:
        start_date_str = None
        end_date_str = None
else:
    start_date_str = None
    end_date_str = None

# Group 筛选
available_groups = processor.get_available_groups()
selected_groups = st.sidebar.multiselect(
    "选择分组 (支持模糊匹配)",
    options=available_groups,
    default=available_groups[:5] if len(available_groups) > 5 else available_groups,
    help="可以选择多个分组进行对比分析"
)

# 主要内容区域
if processor.merged_df is None or processor.merged_df.empty:
    st.warning("所选筛选条件下没有数据")

# 创建标签页
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 基础分析",
    "📈 每日趋势",
    "🔗 点击分析",
    "🎯 转化分析",
    "📊 链接点击量 & 转化率分析",
    "📋 数据详情"
])

# 初始化可视化工具
viz = EnhancedVisualization()

with tab1:
    st.markdown("### 📊 基础信息展示")

    # 获取每日指标数据
    daily_metrics = processor.get_daily_metrics(
        start_date=start_date_str,
        end_date=end_date_str,
        groups=selected_groups
    )

    if not daily_metrics.empty:
        # 创建两列布局
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_views = viz.create_daily_trend_chart(
                daily_metrics, 'view_count', "每日总浏览量趋势"
            )
            st.altair_chart(fig_views, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_posts = viz.create_daily_trend_chart(
                daily_metrics, 'post_count', "每日总发帖数趋势", '#2ca02c'
            )
            st.altair_chart(fig_posts, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 多指标对比图
        st.markdown("### 📈 多指标对比")
        required_columns = ['view_count', 'like_count', 'comment_count', 'share_count']
        if daily_metrics is not None and not daily_metrics.empty:
            missing_columns = [col for col in required_columns if col not in daily_metrics.columns]
            if missing_columns:
                st.warning(f"缺少必要的列: {missing_columns}")
                st.write("可用的列:", list(daily_metrics.columns))
            else:
                metrics_comparison = viz.create_multi_metric_comparison(
                    daily_metrics,
                    required_columns,
                    "每日指标对比"
                )
                st.altair_chart(metrics_comparison, use_container_width=True)
        else:
            st.warning("daily_metrics 数据为空或不存在")

    # 表现最好账号Top 5板块
    st.markdown("### 📊 表现最好账号 Top 5（按最后一天新增浏览量）")

    # 获取表现最好的账号
    top_accounts = processor.get_top_performing_accounts(
        start_date=start_date_str,
        end_date=end_date_str,
        top_n=5
    )

    if not top_accounts.empty:
        # 格式化数据用于显示
        display_df = top_accounts.copy()

        # 创建可点击的用户名列
        display_df['用户名'] = display_df.apply(
            lambda row: f"[{row['username']}]({row['profile_url']})" if row['username'] != '未知' and row['profile_url'] else row['username'],
            axis=1
        )

        # 格式化数字字段
        for col in ['last_day_view_increment', 'follower_count', 'like_count']:
            if col in display_df.columns:
                # 先转换为数值，处理NaN，然后格式化
                numeric_series = pd.to_numeric(display_df[col], errors='coerce')
                numeric_series = numeric_series.fillna(0)
                display_df[col] = numeric_series.astype(int).apply(lambda x: f"{x:,}")

        # 重命名列用于显示
        display_df = display_df.rename(columns={
            'user_id': '账号 ID',
            'last_day_view_increment': '最后一天新增浏览量',
            'follower_count': '总粉丝数',
            'like_count': '点赞数'
        })

        # 选择显示的列
        display_columns = ['用户名', '账号 ID', '最后一天新增浏览量', '总粉丝数', '点赞数']
        display_df = display_df[display_columns]

        # 显示表格
        st.markdown("""
        <style>
        .dataframe {
            font-size: 14px;
        }
        .dataframe th {
            background-color: #f0f2f6;
            font-weight: bold;
            text-align: center;
        }
        .dataframe td {
            text-align: center;
        }
        </style>
        """, unsafe_allow_html=True)

        # 使用st.markdown显示表格，支持链接点击
        st.markdown("#### 📋 账号表现排名")

        # 创建表格头部
        table_header = "| 用户名 | 账号 ID | 最后一天新增浏览量 | 总粉丝数 | 点赞数 |\n"
        table_separator = "|--------|---------|-------------------|----------|--------|\n"

        # 创建表格内容
        table_rows = []
        for _, row in display_df.iterrows():
            username = row['用户名']
            user_id = row['账号 ID']
            view_increment = row['最后一天新增浏览量']
            followers = row['总粉丝数']
            likes = row['点赞数']
            table_rows.append(f"| {username} | {user_id} | {view_increment} | {followers} | {likes} |")

        # 组合完整表格
        full_table = table_header + table_separator + "\n".join(table_rows)

        # 显示表格
        st.markdown(full_table)

        # 添加说明
        st.markdown("""
        <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;'>
        <small>
        📝 <strong>说明：</strong><br>
        • 最后一天新增浏览量：基于选定日期范围内最后一天的 view_diff 字段<br>
        • 总粉丝数/点赞数：来自 accounts_detail 表的最新数据<br>
        • 用户名：点击可跳转到 TikTok 主页<br>
        • 数据范围：当前筛选的日期范围
        </small>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.info("暂无表现数据或数据不足")

with tab2:
    st.markdown("## 📊 每日新增趋势分析")

    # 模式切换
    mode = st.radio("展示模式", ["所有账号", "分组模式"], horizontal=True)

    # 定义指标配置
    metric_configs = [
        ("view_count_inc", "新增浏览量", "#1f77b4", "次"),
        ("like_count_inc", "新增点赞量", "#ff7f0e", "个"),
        ("comment_count_inc", "新增评论数", "#2ca02c", "条"),
        ("share_count_inc", "新增分享数", "#d62728", "次"),
        ("post_count_inc", "新增发帖数", "#9467bd", "条")
    ]

    def create_increment_chart(data, metric_col, title, color, unit):
        """创建单个新增指标图表"""
        import altair as alt

        # 计算数据范围，设置自适应纵轴
        min_value = data[metric_col].min()
        max_value = data[metric_col].max()

        # 设置纵轴范围，避免从0开始，增强趋势可读性
        if min_value != max_value:
            data_range = max_value - min_value
            y_min = max(0, min_value - data_range * 0.05)  # 最小不低于0
            y_max = max_value + data_range * 0.05
        else:
            y_min = max(0, min_value * 0.95)
            y_max = max_value * 1.05

        chart = alt.Chart(data).mark_line(point=True, color=color).encode(
            x=alt.X('date:T', title='日期'),
            y=alt.Y(f'{metric_col}:Q',
                   title=f'每日新增 ({unit})',
                   scale=alt.Scale(domain=[y_min, y_max], zero=False)),  # 设置自适应范围，不从0开始
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip(f'{metric_col}:Q', title=title, format=',.0f')
            ]
        ).properties(
            title=f"📈 {title}趋势",
            height=300
        )
        return chart

    if mode == "所有账号":
        inc_df = processor.get_daily_increment_metrics(start_date_str, end_date_str)
        if not inc_df.empty:
            st.markdown("### 📊 所有账号每日新增指标")
            st.markdown("*以下图表展示基于 redash_data 计算的每日新增数据*")

            # 创建两列布局展示图表
            for i in range(0, len(metric_configs), 2):
                col1, col2 = st.columns(2)

                with col1:
                    metric_col, title, color, unit = metric_configs[i]
                    chart = create_increment_chart(inc_df, metric_col, title, color, unit)
                    st.altair_chart(chart, use_container_width=True)

                # 如果还有下一个指标，在第二列显示
                if i + 1 < len(metric_configs):
                    with col2:
                        metric_col, title, color, unit = metric_configs[i + 1]
                        chart = create_increment_chart(inc_df, metric_col, title, color, unit)
                        st.altair_chart(chart, use_container_width=True)

            # 如果指标数量是奇数，最后一个指标单独占一行
            if len(metric_configs) % 2 == 1:
                metric_col, title, color, unit = metric_configs[-1]
                chart = create_increment_chart(inc_df, metric_col, title, color, unit)
                st.altair_chart(chart, use_container_width=True)

        else:
            st.info("暂无数据")

    else:
        # 分组模式
        all_groups = processor.get_available_groups()
        selected_groups = st.multiselect(
            "选择分组关键词（模糊匹配）",
            options=all_groups,
            default=all_groups[:2] if len(all_groups) > 2 else all_groups,
            help="选择后将所有包含该关键词的账号归为一组，每张图显示该组的合并表现"
        )

        if selected_groups:
            # 获取当前选中分组的最新一天增量指标
            latest_increments = processor.get_selected_groups_latest_increments(selected_groups)

            if latest_increments:
                st.markdown("### 📊 分组每日新增指标")
                st.markdown("*以下图表展示基于 redash_data 计算的每日新增数据，按分组关键词聚合*")

                # 显示分组增量指标摘要卡片
                st.markdown("#### 📈 今日分组增量指标摘要")

                # 为每个分组显示摘要卡片
                for group_keyword, metrics in latest_increments.items():
                    st.markdown(f"**🎯 分组: {group_keyword}** ({metrics['date']})")

                    # 创建5列布局显示各项指标
                    col1, col2, col3, col4, col5 = st.columns(5)

                    with col1:
                        st.metric("📄 新增发帖量", f"{metrics['posts']:,}")

                    with col2:
                        st.metric("👀 新增浏览量", f"{metrics['views']:,}")

                    with col3:
                        st.metric("👍 新增点赞数", f"{metrics['likes']:,}")

                    with col4:
                        st.metric("💬 新增评论数", f"{metrics['comments']:,}")

                    with col5:
                        st.metric("🔄 新增分享数", f"{metrics['shares']:,}")

                    st.markdown("---")  # 分隔线

                # 获取分组每日增量数据用于图表
                inc_df = processor.get_group_daily_increment_metrics(start_date_str, end_date_str, selected_groups)
            else:
                st.markdown("### 📊 分组每日新增指标")
                st.markdown("*以下图表展示基于 redash_data 计算的每日新增数据，按分组关键词聚合*")
                st.info("⚠️ 暂无分组增量指标数据")
                inc_df = processor.get_group_daily_increment_metrics(start_date_str, end_date_str, selected_groups)

            if not inc_df.empty:
                # 为每个分组关键词创建图表
                for group_keyword in selected_groups:
                    st.markdown(f"#### 🎯 分组: {group_keyword}")

                    # 筛选该分组的数据
                    group_data = inc_df[inc_df['group'] == group_keyword].copy()
                    if not group_data.empty:
                        # 创建两列布局展示图表
                        for i in range(0, len(metric_configs), 2):
                            col1, col2 = st.columns(2)

                            with col1:
                                metric_col, title, color, unit = metric_configs[i]
                                chart = create_increment_chart(group_data, metric_col, f"{group_keyword} - {title}", color, unit)
                                st.altair_chart(chart, use_container_width=True)

                            # 如果还有下一个指标，在第二列显示
                            if i + 1 < len(metric_configs):
                                with col2:
                                    metric_col, title, color, unit = metric_configs[i + 1]
                                    chart = create_increment_chart(group_data, metric_col, f"{group_keyword} - {title}", color, unit)
                                    st.altair_chart(chart, use_container_width=True)
                    else:
                        st.warning(f"分组 '{group_keyword}' 暂无数据")

                    st.markdown("---")  # 分隔线
            else:
                st.info("无数据或所选分组无数据")
        else:
            st.info("请选择至少一个分组关键词")

with tab3:
    st.markdown("### 🔗 点击量分析")

    if processor.clicks_df is not None:
        # 获取点击量指标
        clicks_metrics = processor.get_clicks_metrics(
            start_date=start_date_str,
            end_date=end_date_str
        )

        if clicks_metrics and 'daily_clicks' in clicks_metrics:
            daily_clicks = clicks_metrics['daily_clicks']

            if not daily_clicks.empty:
                # 检查数据格式，确保包含必要的列
                required_cols = ['date', 'daily_clicks', 'daily_visitors']
                available_cols = daily_clicks.columns.tolist()
                
                # 如果缺少必要的列，尝试从其他数据源获取或创建
                if not all(col in available_cols for col in required_cols):
                    st.warning("⚠️ 点击数据格式不完整，正在尝试修复...")
                    
                    # 检查是否有其他可用的列
                    if 'date' in available_cols:
                        # 创建临时的点击量数据
                        fixed_data = daily_clicks.copy()
                        
                        # 如果缺少 daily_clicks 列，尝试从其他列推断或使用默认值
                        if 'daily_clicks' not in available_cols:
                            if 'clicks_count' in available_cols:
                                fixed_data['daily_clicks'] = fixed_data['clicks_count']
                            elif 'pv' in available_cols:
                                fixed_data['daily_clicks'] = fixed_data['pv']
                            else:
                                # 使用默认值
                                fixed_data['daily_clicks'] = 0
                        
                        # 如果缺少 daily_visitors 列，尝试从其他列推断或使用默认值
                        if 'daily_visitors' not in available_cols:
                            if 'visitors_count' in available_cols:
                                fixed_data['daily_visitors'] = fixed_data['visitors_count']
                            elif 'uv' in available_cols:
                                fixed_data['daily_visitors'] = fixed_data['uv']
                            else:
                                # 使用默认值
                                fixed_data['daily_visitors'] = 0
                        
                        daily_clicks = fixed_data
                        st.success("✅ 数据格式已修复")
                    else:
                        st.error("❌ 无法修复数据格式，缺少必要的列")
                        st.stop()
                
                # 点击量趋势图
                st.markdown("#### 📈 每日点击量趋势")
                try:
                    clicks_chart = viz.create_clicks_analysis_chart(
                        daily_clicks, "每日点击量趋势"
                    )
                    st.altair_chart(clicks_chart, use_container_width=True)
                except Exception as e:
                    st.error(f"❌ 创建点击量趋势图失败: {str(e)}")
                    st.write("调试信息：")
                    st.write(f"数据列: {daily_clicks.columns.tolist()}")
                    st.write(f"数据形状: {daily_clicks.shape}")
                    st.write(f"数据前5行: {daily_clicks.head()}")

                # 点击量统计
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("总点击量", f"{clicks_metrics['total_clicks']:,}")
                with col2:
                    st.metric("统计天数", f"{clicks_metrics['unique_dates']}")
                with col3:
                    avg_clicks = clicks_metrics['total_clicks'] / clicks_metrics['unique_dates'] if clicks_metrics['unique_dates'] > 0 else 0
                    st.metric("日均点击量", f"{avg_clicks:.0f}")

                # 页面类型点击统计
                if 'page_type_clicks' in clicks_metrics and not clicks_metrics['page_type_clicks'].empty:
                    st.markdown("#### 📊 页面类型点击统计")
                    page_type_data = clicks_metrics['page_type_clicks']
                    st.dataframe(page_type_data, use_container_width=True)

                # 链接点击统计
                if 'link_clicks' in clicks_metrics and not clicks_metrics['link_clicks'].empty:
                    st.markdown("#### 🔗 链接点击统计")
                    link_data = clicks_metrics['link_clicks'].head(10)
                    st.dataframe(link_data, use_container_width=True)
    else:
        st.warning("暂无点击数据")

with tab4:
    st.markdown("### 🎯 转化分析")

    if processor.clicks_df is not None and processor.merged_df is not None:
        # 获取最后一天的点击统计摘要
        last_day_summary = processor.get_last_day_clicks_summary(
            start_date=start_date_str,
            end_date=end_date_str
        )

        if last_day_summary:
            st.markdown("### 📊 最后一天点击情况摘要")

            # 显示最后一天日期
            sample_link = list(last_day_summary.keys())[0]
            last_day_date = last_day_summary[sample_link]['date']
            st.markdown(f"**统计日期：{last_day_date}**")

            # 创建两列布局，分别显示两个链接的统计卡片
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🔗 https://insnap.ai/videos")
                if 'https://insnap.ai/videos' in last_day_summary:
                    data = last_day_summary['https://insnap.ai/videos']
                    # 添加字段检查，避免KeyError
                    pv_value = data.get('pv', 0)
                    uv_value = data.get('uv', 0)
                    st.metric("今日点击量(PV)", f"{pv_value:,}")
                    st.metric("今日访客数(UV)", f"{uv_value:,}")
                else:
                    st.metric("今日点击量(PV)", "0")
                    st.metric("今日访客数(UV)", "0")

            with col2:
                st.markdown("#### 🔗 https://insnap.ai/zh/download")
                if 'https://insnap.ai/zh/download' in last_day_summary:
                    data = last_day_summary['https://insnap.ai/zh/download']
                    # 添加字段检查，避免KeyError
                    pv_value = data.get('pv', 0)
                    uv_value = data.get('uv', 0)
                    st.metric("今日点击量(PV)", f"{pv_value:,}")
                    st.metric("今日访客数(UV)", f"{uv_value:,}")
                else:
                    st.metric("今日点击量(PV)", "0")
                    st.metric("今日访客数(UV)", "0")

            # 添加说明
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>
            <small>
            📝 <strong>说明：</strong><br>
            • 今日点击量(PV)：基于不同 session_id 统计的点击次数<br>
            • 今日访客数(UV)：基于不同 visitor_id 统计的独立访客数<br>
            • 数据来源：链接点击数据表，统计当前选择日期范围的最后一天
            </small>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")  # 分隔线

            # 获取转化分析数据
            conversion_data = processor.get_clicks_conversion_analysis(
                start_date=start_date_str,
                end_date=end_date_str
            )

            if not conversion_data.empty:
                # 转化率图表
                st.markdown("#### 📈 点击到浏览量转化率")
                conversion_chart = viz.create_conversion_chart(
                    conversion_data, 'clicks_count', 'view_count', "点击到浏览量转化率"
                )
                st.altair_chart(conversion_chart, use_container_width=True)

                # 分组点击分析
                group_clicks_data = processor.get_group_clicks_analysis(
                    start_date=start_date_str,
                    end_date=end_date_str
                )

                if not group_clicks_data.empty:
                    st.markdown("#### 📊 分组点击相关性分析")

                    # 选择指标进行相关性分析
                    metric_options = ['view_count', 'like_count', 'comment_count', 'share_count']
                    selected_corr_metric = st.selectbox(
                        "选择相关性分析指标",
                        options=metric_options,
                        format_func=lambda x: x.replace('_', ' ').title()
                    )

                    correlation_chart = viz.create_group_clicks_correlation(
                        group_clicks_data, 'link_clicks', selected_corr_metric,
                        f"点击量与{selected_corr_metric.replace('_', ' ').title()}相关性"
                    )
                    st.altair_chart(correlation_chart, use_container_width=True)

                    # 显示分组点击数据
                    st.markdown("#### 📋 分组点击数据详情")
                    st.dataframe(group_clicks_data, use_container_width=True)
        else:
            st.warning("暂无转化分析数据")

with tab5:
    st.markdown("## 📊 链接点击量 & 转化率分析")

    if processor.clicks_df is not None and processor.merged_df is not None:
        # 获取链接转化率分析数据
        link_conversion_data = processor.get_link_conversion_analysis(
            start_date=start_date_str,
            end_date=end_date_str
        )

        if link_conversion_data:
            st.markdown("### 🔗 链接映射关系")
            st.markdown("""
            - `https://insnap.ai/videos` → 目标分组：`yujie_main_avatar`
            - `https://insnap.ai/zh/download` → 目标分组：`wan_produce101`
            """)

            # 为每个链接创建分析图表
            for link_url, analysis_data in link_conversion_data.items():
                st.markdown(f"#### 🎯 {link_url}")
                st.markdown(f"*目标分组: {analysis_data['target_group']}*")

                # 确保data为DataFrame
                data = analysis_data['data'].copy()
                required_cols = ['date', 'daily_clicks', 'daily_visitors', 'daily_views']
                if not isinstance(data, pd.DataFrame) or data.empty:
                    st.error('数据为空或格式不正确，请检查数据源。')
                    st.stop()
                missing_cols = [col for col in required_cols if col not in data.columns]
                if missing_cols:
                    st.error(f'数据缺少必要字段: {missing_cols}')
                    st.stop()

                # 显示统计信息卡片
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("总点击量(PV)", f"{analysis_data['total_clicks']:,}")
                with col2:
                    st.metric("总访客数(UV)", f"{analysis_data['total_visitors']:,}")
                with col3:
                    st.metric("总浏览量", f"{analysis_data['total_views']:,}")
                with col4:
                    st.metric("PV转化率", f"{analysis_data['avg_pv_conversion_rate']:.2f}%")
                with col5:
                    st.metric("UV转化率", f"{analysis_data['avg_uv_conversion_rate']:.2f}%")

                # 新增：今日新增卡片
                today = analysis_data.get('today', {})
                st.markdown(f"#### 📅 今日新增（{today.get('date', '')}）")
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("今日新增点击量(PV)", f"{today.get('pv', 0):,}")
                with col2:
                    st.metric("今日新增访客数(UV)", f"{today.get('uv', 0):,}")
                with col3:
                    st.metric("今日新增浏览量", f"{today.get('views', 0):,}")
                with col4:
                    st.metric("今日PV转化率", f"{today.get('pv_rate', 0.0):.2f}%")
                with col5:
                    st.metric("今日UV转化率", f"{today.get('uv_rate', 0.0):.2f}%")

                # 调试输出
                with st.expander("🔍 调试数据"):
                    st.write("原始数据样本:")
                    st.dataframe(analysis_data['data'].head(), use_container_width=True)
                    st.write(f"数据形状: {analysis_data['data'].shape}")
                    st.write(f"列名: {list(analysis_data['data'].columns)}")

                # 图表显示选择
                st.markdown("### 📈 趋势图表")
                chart_options = st.multiselect(
                    "选择要显示的指标",
                    options=["点击量(PV)", "访客数(UV)", "浏览量", "PV转化率", "UV转化率"],
                    default=["点击量(PV)", "访客数(UV)", "浏览量"],
                    key=f"chart_options_{link_url}"
                )

                # 创建双轴图表：PV和UV对比
                import altair as alt

                # 构建PV/UV趋势图所需数据
                required_cols = ['date', 'daily_clicks']
                missing_cols = [col for col in required_cols if col not in data.columns]
                if missing_cols:
                    st.error(f'数据缺少必要字段: {missing_cols}')
                    st.stop()
                pv_data = data[['date', 'daily_clicks']].copy()
                pv_data['type'] = '点击量(PV)'
                pv_data['value'] = pv_data['daily_clicks']
                uv_data = data[['date', 'daily_visitors']].copy()
                uv_data['type'] = '访客数(UV)'
                uv_data['value'] = uv_data['daily_visitors']
                combined_data = pd.concat([pv_data, uv_data], ignore_index=True)
                base = alt.Chart(combined_data).encode(
                    x=alt.X('date:T', title='日期', axis=alt.Axis(format='%Y-%m-%d'))
                )

                # 只保留PV/UV两线趋势图
                pv_chart = base.transform_filter(alt.datum.type == '点击量(PV)').mark_line(
                    color='#1f77b4', point=True, strokeWidth=2
                ).encode(
                    y=alt.Y('value:Q', title='点击量/访客数',
                            scale=alt.Scale(domain=[0, max(1, combined_data[combined_data['type'].isin(['点击量(PV)','访客数(UV)'])]['value'].max() * 1.1)]),
                            axis=alt.Axis(format=',')),
                    tooltip=[
                        alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                        alt.Tooltip('value:Q', title='点击量(PV)', format=',.0f')
                    ]
                )
                uv_chart = base.transform_filter(alt.datum.type == '访客数(UV)').mark_line(
                    color='#ff7f0e', point=True, strokeWidth=2
                ).encode(
                    y=alt.Y('value:Q', title='点击量/访客数',
                            scale=alt.Scale(domain=[0, max(1, combined_data[combined_data['type'].isin(['点击量(PV)','访客数(UV)'])]['value'].max() * 1.1)]),
                            axis=alt.Axis(format=',')),
                    tooltip=[
                        alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                        alt.Tooltip('value:Q', title='访客数(UV)', format=',.0f')
                    ]
                )

                chart = alt.layer(pv_chart, uv_chart).resolve_scale(
                    y='independent'
                ).properties(
                    title=f"📈 {link_url} - PV vs UV 趋势对比",
                    height=400
                ).configure_axis(
                    gridColor='#f0f0f0'
                ).configure_view(
                    strokeWidth=0
                )

                st.altair_chart(chart, use_container_width=True)

                # 每日数据表格
                st.markdown("#### 📋 每日数据明细")

                # 准备表格数据
                table_data = data[['date', 'daily_clicks', 'daily_visitors', 'daily_views']].copy()
                table_data = table_data.rename(columns={
                    'date': '日期',
                    'daily_clicks': '点击量(PV)',
                    'daily_visitors': '访客数(UV)',
                    'daily_views': '浏览量'
                })

                # 格式化数字显示
                table_data['点击量(PV)'] = table_data['点击量(PV)'].apply(lambda x: f"{int(x):,}")
                table_data['访客数(UV)'] = table_data['访客数(UV)'].apply(lambda x: f"{int(x):,}")
                table_data['浏览量'] = table_data['浏览量'].apply(lambda x: f"{int(x):,}")

                # 显示表格
                st.dataframe(
                    table_data,
                    use_container_width=True,
                    hide_index=True
                )

                # 添加表格说明
                st.markdown("""
                <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px;'>
                <small>
                📝 <strong>数据说明：</strong><br>
                • 点击量(PV)：基于不同 session_id 统计的每日点击次数<br>
                • 访客数(UV)：基于不同 visitor_id 统计的每日独立访客数<br>
                • 浏览量(View)：基于 view_diff 字段计算的每日浏览量增量<br>
                • 图表显示：三条折线在同一坐标系中对比，便于观察趋势关系<br>
                • 数据范围：当前筛选的日期范围
                </small>
                </div>
                """, unsafe_allow_html=True)

            # 浏览量图表
            if "浏览量" in chart_options:
                st.markdown("#### 📊 每日浏览量趋势")
                views_chart = alt.Chart(data).mark_line(
                    color='#2ca02c', point=True, strokeWidth=2
                ).encode(
                    x=alt.X('date:T', title='日期'),
                    y=alt.Y('daily_views:Q', title='每日浏览量',
                           scale=alt.Scale(domain=[0, data['daily_views'].max() * 1.1]),
                           axis=alt.Axis(format=',')),
                    tooltip=[
                        alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                        alt.Tooltip('daily_views:Q', title='浏览量', format=',.0f')
                    ]
                ).properties(
                    title=f"📊 {link_url} - 每日浏览量趋势",
                    height=300
                )

                st.altair_chart(views_chart, use_container_width=True)

            # 转化率图表
            if "PV转化率" in chart_options or "UV转化率" in chart_options:
                st.markdown("#### 📊 转化率趋势")

                # 准备转化率数据
                conversion_data = data[['date', 'daily_pv_conversion_rate', 'daily_uv_conversion_rate']].copy()
                conversion_data = conversion_data.melt(
                    id_vars=['date'],
                    value_vars=['daily_pv_conversion_rate', 'daily_uv_conversion_rate'],
                    var_name='type',
                    value_name='rate'
                )
                conversion_data['type'] = conversion_data['type'].map({
                    'daily_pv_conversion_rate': 'PV转化率',
                    'daily_uv_conversion_rate': 'UV转化率'
                })

                # 筛选选中的转化率类型
                if "PV转化率" in chart_options and "UV转化率" in chart_options:
                    filtered_conversion_data = conversion_data
                elif "PV转化率" in chart_options:
                    filtered_conversion_data = conversion_data[conversion_data['type'] == 'PV转化率']
                else:
                    filtered_conversion_data = conversion_data[conversion_data['type'] == 'UV转化率']

                conversion_chart = alt.Chart(filtered_conversion_data).mark_line(
                    point=True, strokeWidth=2
                ).encode(
                    x=alt.X('date:T', title='日期'),
                    y=alt.Y('rate:Q', title='转化率 (%)',
                           scale=alt.Scale(domain=[0, filtered_conversion_data['rate'].max() * 1.1])),
                    color=alt.Color('type:N', title='转化率类型'),
                    tooltip=[
                        alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                        alt.Tooltip('rate:Q', title='转化率', format='.2f'),
                        alt.Tooltip('type:N', title='类型')
                    ]
                ).properties(
                    title=f"📊 {link_url} - 转化率趋势",
                    height=300
                )

                st.altair_chart(conversion_chart, use_container_width=True)

            # 显示数据表格
            with st.expander(f"📋 {link_url} 详细数据"):
                # 重命名列用于显示
                display_data = data.copy()
                display_data = display_data.rename(columns={
                    'daily_clicks': '每日点击量(PV)',
                    'daily_visitors': '每日访客数(UV)',
                    'daily_views': '每日浏览量',
                    'daily_pv_conversion_rate': 'PV转化率(%)',
                    'daily_uv_conversion_rate': 'UV转化率(%)'
                })

                st.dataframe(display_data, use_container_width=True)

                # 下载按钮
                csv_data = display_data.to_csv(index=False)
                st.download_button(
                    label=f"📥 下载 {link_url} 数据",
                    data=csv_data,
                    file_name=f"link_conversion_{link_url.replace('https://', '').replace('/', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

            st.markdown("---")  # 分隔线
        else:
            st.warning(f"链接 {link_url} 暂无数据")
    else:
        st.warning("暂无点击数据或账号数据")

with tab6:
    st.markdown("### 📋 数据详情")

    # 数据统计信息
    if summary:
        st.markdown("#### 📊 数据统计")
        summary_html = EnhancedVisualization().create_summary_cards(summary)
        st.markdown(summary_html, unsafe_allow_html=True)

    # 原始数据预览
    if processor.merged_df is not None:
        st.markdown("#### 📄 合并数据预览")
        st.dataframe(processor.merged_df.head(100), use_container_width=True)

        # 数据下载
        csv = processor.merged_df.to_csv(index=False)
        st.download_button(
            label="📥 下载合并数据",
            data=csv,
            file_name=f"enhanced_tiktok_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    # 点击数据预览
    if processor.clicks_df is not None:
        st.markdown("#### 📄 点击数据预览")
        st.dataframe(processor.clicks_df.head(100), use_container_width=True)

        # 点击数据下载
        clicks_csv = processor.clicks_df.to_csv(index=False)
        st.download_button(
            label="📥 下载点击数据",
            data=clicks_csv,
            file_name=f"clicks_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# 移除对未定义main()函数的调用
# if __name__ == "__main__":
#     main() 