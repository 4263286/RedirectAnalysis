import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import os
import re
from typing import Dict, List, Optional, Tuple
warnings.filterwarnings('ignore')

class EnhancedTikTokDataProcessor:
    """增强版 TikTok 数据处理类 - 支持基础信息展示和点击量分析"""
    
    def __init__(self, 
                 redash_data_dir: str = 'data/redash_data',
                 accounts_file_path: str = 'data/postingManager_data/accounts_detail.xlsx',
                 clicks_data_dir: str = 'data/clicks',
                 accounts_df: pd.DataFrame = None,
                 redash_df: pd.DataFrame = None,
                 clicks_df: pd.DataFrame = None):
        """
        初始化增强版数据处理器
        
        Args:
            redash_data_dir (str): redash 数据目录路径
            accounts_file_path (str): accounts detail 数据文件路径
            clicks_data_dir (str): clicks 数据目录路径
        """
        self.redash_data_dir = redash_data_dir
        self.accounts_file_path = accounts_file_path
        self.clicks_data_dir = clicks_data_dir
        
        # 数据存储
        self.merged_df = None
        self.group_mapping = None
        self.clicks_df = clicks_df
        self.accounts_df = accounts_df
        self.redash_df = redash_df
        
        # 链接到分组的映射
        self.link_group_mapping = {
            'https://insnap.ai/videos': 'yujie_main_avatar',
            'https://insnap.ai/zh/download': 'wan_produce101'
        }
        
    def load_latest_redash_data(self) -> Optional[pd.DataFrame]:
        """加载最新的 redash 数据文件"""
        try:
            if not os.path.exists(self.redash_data_dir):
                print(f"❌ Redash 数据目录不存在: {self.redash_data_dir}")
                return None
                
            # 获取最新的 redash 数据文件
            redash_files = [f for f in os.listdir(self.redash_data_dir) 
                          if f.startswith('redash_data_') and f.endswith('.csv')]
            
            if not redash_files:
                print(f"❌ 未找到 redash 数据文件在: {self.redash_data_dir}")
                return None
                
            latest_file = max(redash_files, key=lambda x: os.path.getctime(os.path.join(self.redash_data_dir, x)))
            file_path = os.path.join(self.redash_data_dir, latest_file)
            
            print(f"正在加载 redash 数据: {latest_file}")
            redash_df = pd.read_csv(file_path, low_memory=False)
            print("Redash columns:", redash_df.columns.tolist())
            
            # 数据预处理
            if 'YMDdate' in redash_df.columns:
                redash_df['date'] = pd.to_datetime(redash_df['YMDdate'], errors='coerce')
            elif 'date' in redash_df.columns:
                redash_df['date'] = pd.to_datetime(redash_df['date'], errors='coerce')
            
            redash_df = redash_df.dropna(subset=['date'])
            
            # 确保 user_id 为字符串类型
            redash_df['user_id'] = redash_df['user_id'].astype(str)
            
            # 确保数值列为数值类型
            numeric_columns = [
                'view_count', 'like_count', 'comment_count', 'share_count', 
                'post_count', 'view_per_post', 'like_per_post', 'comment_per_post', 
                'share_per_post', 'view_diff', 'like_diff', 'comment_diff', 
                'share_diff', 'post_diff'
            ]
            
            for col in numeric_columns:
                if col in redash_df.columns:
                    redash_df[col] = pd.to_numeric(redash_df[col], errors='coerce').fillna(0)
            
            print(f"✅ Redash 数据加载成功: {redash_df.shape}")
            return redash_df
            
        except Exception as e:
            print(f"❌ Redash 数据加载失败: {str(e)}")
            return None
    
    def load_accounts_data(self) -> Optional[pd.DataFrame]:
        """加载 accounts detail 数据"""
        try:
            print("正在加载 accounts detail 数据...")
            if not os.path.exists(self.accounts_file_path):
                print(f"❌ Accounts 文件不存在: {self.accounts_file_path}")
                return None
                
            accounts_df = pd.read_excel(self.accounts_file_path)
            self.accounts_df = accounts_df
            
            # 创建 group 映射
            group_mapping = accounts_df[['Tiktok ID', 'Groups']].drop_duplicates()
            group_mapping = group_mapping.rename(columns={'Tiktok ID': 'user_id', 'Groups': 'group'})
            
            # 确保 user_id 为字符串类型
            group_mapping['user_id'] = group_mapping['user_id'].astype(str)
            
            # 处理空值
            group_mapping['group'] = group_mapping['group'].fillna('Unknown')
            
            print(f"✅ Accounts 数据加载成功: {accounts_df.shape}")
            print(f"✅ Group 映射创建成功: {group_mapping.shape}")
            return group_mapping
            
        except Exception as e:
            print(f"❌ Accounts 数据加载失败: {str(e)}")
            return None
    
    def load_clicks_data(self) -> Optional[pd.DataFrame]:
        """加载点击数据"""
        try:
            if not os.path.exists(self.clicks_data_dir):
                print(f"❌ Clicks 数据目录不存在: {self.clicks_data_dir}")
                return None
                
            # 获取最新的 clicks 数据文件
            clicks_files = [f for f in os.listdir(self.clicks_data_dir) 
                          if f.endswith('.csv')]
            
            if not clicks_files:
                print(f"❌ 未找到 clicks 数据文件在: {self.clicks_data_dir}")
                return None
                
            latest_file = max(clicks_files, key=lambda x: os.path.getctime(os.path.join(self.clicks_data_dir, x)))
            file_path = os.path.join(self.clicks_data_dir, latest_file)
            
            print(f"正在加载 clicks 数据: {latest_file}")
            clicks_df = pd.read_csv(file_path, low_memory=False)
            
            # 数据预处理
            if 'timestamp' in clicks_df.columns:
                clicks_df['date'] = pd.to_datetime(clicks_df['timestamp']).dt.date
            elif 'date' in clicks_df.columns:
                clicks_df['date'] = pd.to_datetime(clicks_df['date']).dt.date
            
            # 提取页面类型和链接信息
            clicks_df['page_type'] = clicks_df.get('page_type', 'unknown')
            clicks_df['page_url'] = clicks_df.get('page_url', '')
            
            print(f"✅ Clicks 数据加载成功: {clicks_df.shape}")
            return clicks_df
            
        except Exception as e:
            print(f"❌ Clicks 数据加载失败: {str(e)}")
            return None
    
    def merge_data(self) -> bool:
        """合并所有数据"""
        try:
            print("正在合并数据...")
            import streamlit as st
            st.write("[DEBUG] 正在合并数据...")
            
            # 确保在云端也能看到调试信息
            import sys
            st.write(f"[DEBUG] Python路径: {sys.path[:3]}")  # 显示前3个路径
            
            # 优先用传入的 DataFrame
            redash_df = self.redash_df if self.redash_df is not None else self.load_latest_redash_data()
            print(f"[DEBUG] redash_df shape: {redash_df.shape if redash_df is not None else 'None'}")
            st.write(f"[DEBUG] redash_df shape: {redash_df.shape if redash_df is not None else 'None'}")
            
            group_mapping = None
            if self.accounts_df is not None:
                print(f"[DEBUG] 使用传入的 accounts_df, shape: {self.accounts_df.shape}")
                st.write(f"[DEBUG] 使用传入的 accounts_df, shape: {self.accounts_df.shape}")
                accounts_df = self.accounts_df
                print(f"[DEBUG] accounts_df columns: {accounts_df.columns.tolist()}")
                st.write(f"[DEBUG] accounts_df columns: {accounts_df.columns.tolist()}")
                # 检查必要的列是否存在
                if 'Tiktok ID' not in accounts_df.columns or 'Groups' not in accounts_df.columns:
                    print(f"[DEBUG] accounts_df columns: {accounts_df.columns.tolist()}")
                    st.error(f"[DEBUG] accounts_df columns: {accounts_df.columns.tolist()}")
                    raise ValueError("accounts_df 缺少必要的列: 'Tiktok ID' 或 'Groups'")
                # 强制类型转换
                accounts_df['Tiktok ID'] = accounts_df['Tiktok ID'].astype(str)
                print(f"[DEBUG] accounts_df['Tiktok ID'] dtype: {accounts_df['Tiktok ID'].dtype}")
                st.write(f"[DEBUG] accounts_df['Tiktok ID'] dtype: {accounts_df['Tiktok ID'].dtype}")
                print(f"[DEBUG] accounts_df['Tiktok ID'] sample: {accounts_df['Tiktok ID'].unique()[:5]}")
                st.write(f"[DEBUG] accounts_df['Tiktok ID'] sample: {accounts_df['Tiktok ID'].unique()[:5]}")
                group_mapping = accounts_df[['Tiktok ID', 'Groups']].drop_duplicates()
                group_mapping = group_mapping.rename(columns={'Tiktok ID': 'user_id', 'Groups': 'group'})
                group_mapping['user_id'] = group_mapping['user_id'].astype(str)
                group_mapping['group'] = group_mapping['group'].fillna('Unknown')
                print(f"[DEBUG] group_mapping shape: {group_mapping.shape}")
                st.write(f"[DEBUG] group_mapping shape: {group_mapping.shape}")
            else:
                group_mapping = self.load_accounts_data()
                print(f"[DEBUG] 从文件加载 group_mapping, shape: {group_mapping.shape if group_mapping is not None else 'None'}")
                st.write(f"[DEBUG] 从文件加载 group_mapping, shape: {group_mapping.shape if group_mapping is not None else 'None'}")
            
            clicks_df = self.clicks_df if self.clicks_df is not None else self.load_clicks_data()
            print(f"[DEBUG] clicks_df shape: {clicks_df.shape if clicks_df is not None else 'None'}")
            
            # 自动补齐 clicks_df 的 date 字段
            if clicks_df is not None and 'date' not in clicks_df.columns:
                if 'timestamp' in clicks_df.columns:
                    clicks_df['date'] = pd.to_datetime(clicks_df['timestamp']).dt.date
                else:
                    raise KeyError("clicks_df 缺少 'date' 或 'timestamp' 字段")
            
            if redash_df is None:
                print("[DEBUG] redash_df 为 None，合并失败")
                st.error("[DEBUG] redash_df 为 None，合并失败")
                self.merged_df = None
                return False
                
            if group_mapping is None:
                print("[DEBUG] group_mapping 为 None，合并失败")
                st.error("[DEBUG] group_mapping 为 None，合并失败")
                self.merged_df = None
                return False
            
            print(f"[DEBUG] 开始合并，redash_df columns: {redash_df.columns.tolist()}")
            st.write(f"[DEBUG] 开始合并，redash_df columns: {redash_df.columns.tolist()}")
            print(f"[DEBUG] group_mapping columns: {group_mapping.columns.tolist()}")
            st.write(f"[DEBUG] group_mapping columns: {group_mapping.columns.tolist()}")
            
            # 确保 redash_df 有正确的 date 列
            if 'date' not in redash_df.columns:
                print("[DEBUG] redash_df 缺少 'date' 列，尝试从其他列创建...")
                st.write("[DEBUG] redash_df 缺少 'date' 列，尝试从其他列创建...")
                if 'YMDdate' in redash_df.columns:
                    redash_df['date'] = pd.to_datetime(redash_df['YMDdate'], errors='coerce')
                    print("[DEBUG] 从 'YMDdate' 列创建 'date' 列")
                    st.write("[DEBUG] 从 'YMDdate' 列创建 'date' 列")
                else:
                    print("[DEBUG] redash_df 缺少日期列，实际列: ", redash_df.columns.tolist())
                    st.error("[DEBUG] redash_df 缺少日期列，实际列: " + str(redash_df.columns.tolist()))
                    raise ValueError("redash_df 缺少日期列")
            
            # 确保 date 列是 datetime 类型
            if not pd.api.types.is_datetime64_any_dtype(redash_df['date']):
                redash_df['date'] = pd.to_datetime(redash_df['date'], errors='coerce')
            
            # 移除无效的日期行
            redash_df = redash_df.dropna(subset=['date'])
            print(f"[DEBUG] 处理日期后 redash_df shape: {redash_df.shape}")
            st.write(f"[DEBUG] 处理日期后 redash_df shape: {redash_df.shape}")
            
            # 强制类型转换
            if 'user_id' in redash_df.columns:
                redash_df['user_id'] = redash_df['user_id'].astype(str)
                print(f"[DEBUG] redash_df['user_id'] dtype: {redash_df['user_id'].dtype}")
                st.write(f"[DEBUG] redash_df['user_id'] dtype: {redash_df['user_id'].dtype}")
                print(f"[DEBUG] redash_df['user_id'] sample: {redash_df['user_id'].unique()[:5]}")
                st.write(f"[DEBUG] redash_df['user_id'] sample: {redash_df['user_id'].unique()[:5]}")
            else:
                print("[DEBUG] redash_df 缺少 'user_id' 列，实际列: ", redash_df.columns.tolist())
                st.error("[DEBUG] redash_df 缺少 'user_id' 列，实际列: " + str(redash_df.columns.tolist()))
                raise ValueError("redash_df 缺少 'user_id' 列")
            
            # 合并 redash 和 accounts 数据
            st.write("[DEBUG] 开始执行 merge 操作...")
            merged_df = redash_df.merge(group_mapping, on='user_id', how='left')
            print(f"[DEBUG] 合并后 shape: {merged_df.shape}")
            st.write(f"[DEBUG] 合并后 shape: {merged_df.shape}")
            print(f"[DEBUG] merged_df['group'] value_counts: {merged_df['group'].value_counts(dropna=False) if 'group' in merged_df.columns else '无group列'}")
            st.write(f"[DEBUG] merged_df['group'] value_counts: {merged_df['group'].value_counts(dropna=False) if 'group' in merged_df.columns else '无group列'}")
            print(f"[DEBUG] merged_df head:\n{merged_df.head()}")
            st.write(f"[DEBUG] merged_df head:")
            st.dataframe(merged_df.head())
            
            # 强制统一分组字段名为 group
            if 'Groups' in merged_df.columns:
                merged_df = merged_df.rename(columns={'Groups': 'group'})
            merged_df['group'] = merged_df['group'].fillna('Unknown')

            self.merged_df = merged_df
            self.group_mapping = group_mapping
            self.clicks_df = clicks_df
            
            print(f"✅ 数据合并成功: {merged_df.shape}")
            st.success(f"✅ 数据合并成功: {merged_df.shape}")
            return True
            
        except Exception as e:
            print(f"❌ 数据合并失败: {str(e)}")
            st.error(f"❌ 数据合并失败: {str(e)}")
            self.merged_df = None
            return False
    
    def get_available_groups(self) -> List[str]:
        """获取所有可用的分组（支持模糊匹配）"""
        if self.merged_df is None:
            return []
        
        all_groups_raw = self.merged_df['group'].dropna().unique().tolist()
        split_groups = set()
        
        for g in all_groups_raw:
            if isinstance(g, str):
                for part in re.split(r'[\,\|/;，；]', g):
                    part = part.strip()
                    if part:
                        split_groups.add(part)
        
        return sorted(list(split_groups))
    
    def filter_data_by_groups(self, df: pd.DataFrame, selected_groups: List[str]) -> pd.DataFrame:
        """
        根据分组关键词筛选并归一化分组标签（只要包含关键词就归为该关键词）
        """
        if not selected_groups:
            return df
        # 归一化分组：只要 group 字段包含关键词，就归为该关键词
        def normalize_group(row):
            for sg in selected_groups:
                if sg in str(row['group']):
                    return sg
            return row['group']
        filtered_df = df[df['group'].apply(lambda x: any(sg in str(x) for sg in selected_groups))].copy()
        filtered_df['group'] = filtered_df.apply(normalize_group, axis=1)
        return filtered_df
    
    def get_daily_metrics(self, start_date: Optional[str] = None, 
                         end_date: Optional[str] = None,
                         groups: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取每日指标数据
        
        Args:
            start_date (str): 开始日期 (YYYY-MM-DD)
            end_date (str): 结束日期 (YYYY-MM-DD)
            groups (list): 分组列表
        
        Returns:
            pd.DataFrame: 每日指标数据
        """
        if self.merged_df is None:
            return pd.DataFrame()
        
        filtered_df = self.merged_df.copy()
        
        # 日期筛选
        if start_date:
            start_date = pd.Timestamp(start_date)
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
        
        if end_date:
            end_date = pd.Timestamp(end_date)
            filtered_df = filtered_df[filtered_df['date'] <= end_date]
        
        # 分组筛选
        if groups:
            filtered_df = self.filter_data_by_groups(filtered_df, groups)
        
        # 每日聚合
        metrics = ['view_count', 'like_count', 'comment_count', 'share_count', 'post_count']
        daily_data = filtered_df.groupby('date')[metrics].sum().reset_index()
        
        return daily_data
    
    def get_group_daily_metrics(self, start_date: Optional[str] = None,
                               end_date: Optional[str] = None,
                               groups: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取分组每日指标数据
        
        Args:
            start_date (str): 开始日期 (YYYY-MM-DD)
            end_date (str): 结束日期 (YYYY-MM-DD)
            groups (list): 分组列表
        
        Returns:
            pd.DataFrame: 分组每日指标数据
        """
        if self.merged_df is None:
            return pd.DataFrame()
        
        filtered_df = self.merged_df.copy()
        
        # 日期筛选
        if start_date:
            start_date = pd.Timestamp(start_date)
            filtered_df = filtered_df[filtered_df['date'] >= start_date]
        
        if end_date:
            end_date = pd.Timestamp(end_date)
            filtered_df = filtered_df[filtered_df['date'] <= end_date]
        
        # 分组筛选
        if groups:
            filtered_df = self.filter_data_by_groups(filtered_df, groups)
        
        # 分组每日聚合
        metrics = ['view_count', 'like_count', 'comment_count', 'share_count', 'post_count']
        group_daily_data = filtered_df.groupby(['date', 'group'])[metrics].sum().reset_index()
        
        return group_daily_data
    
    def get_clicks_metrics(self, start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> Dict:
        """
        获取点击量指标
        
        Args:
            start_date (str): 开始日期 (YYYY-MM-DD)
            end_date (str): 结束日期 (YYYY-MM-DD)
        
        Returns:
            Dict: 点击量指标数据
        """
        if self.clicks_df is None:
            return {}
        
        filtered_clicks = self.clicks_df.copy()
        print("[DEBUG] filtered_clicks columns:", filtered_clicks.columns)
        print("[DEBUG] filtered_clicks head:", filtered_clicks.head())
        print("[DEBUG] filtered_clicks shape:", filtered_clicks.shape)
        if filtered_clicks.empty:
            print("[DEBUG] filtered_clicks is empty")
            return {}
        if 'date' not in filtered_clicks.columns:
            if 'timestamp' in filtered_clicks.columns:
                filtered_clicks['date'] = pd.to_datetime(filtered_clicks['timestamp']).dt.date
            else:
                print("[DEBUG] filtered_clicks columns:", filtered_clicks.columns)
                raise KeyError("clicks 数据缺少 'date' 或 'timestamp' 字段")
        # 保证 date 字段为 pd.Timestamp 类型
        filtered_clicks['date'] = pd.to_datetime(filtered_clicks['date'])
        # 日期筛选
        if start_date:
            start_date = pd.to_datetime(start_date)
            filtered_clicks = filtered_clicks[filtered_clicks['date'] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date)
            filtered_clicks = filtered_clicks[filtered_clicks['date'] <= end_date]
        
        # 每日点击量统计
        daily_clicks = filtered_clicks.groupby('date').size().reset_index(name='clicks_count')
        
        # 计算增长率
        daily_clicks['clicks_growth'] = daily_clicks['clicks_count'].pct_change() * 100
        
        # 按页面类型统计
        page_type_clicks = filtered_clicks.groupby('page_type').size().reset_index(name='clicks_count')
        
        # 按链接统计
        link_clicks = filtered_clicks.groupby('page_url').size().reset_index(name='clicks_count')
        
        return {
            'daily_clicks': daily_clicks,
            'page_type_clicks': page_type_clicks,
            'link_clicks': link_clicks,
            'total_clicks': len(filtered_clicks),
            'unique_dates': filtered_clicks['date'].nunique()
        }
    
    def get_clicks_conversion_analysis(self, start_date: Optional[str] = None,
                                     end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取点击转化分析数据
        
        Args:
            start_date (str): 开始日期 (YYYY-MM-DD)
            end_date (str): 结束日期 (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: 转化分析数据
        """
        if self.clicks_df is None or self.merged_df is None:
            return pd.DataFrame()
        
        # 获取点击数据
        clicks_metrics = self.get_clicks_metrics(start_date, end_date)
        daily_clicks = clicks_metrics.get('daily_clicks', pd.DataFrame())
        
        if daily_clicks.empty:
            return pd.DataFrame()
        
        # 获取 TikTok 数据
        tiktok_daily = self.get_daily_metrics(start_date, end_date)
        
        if tiktok_daily.empty:
            return pd.DataFrame()
        
        # 合并数据前，确保日期类型一致
        if 'date' in daily_clicks.columns:
            daily_clicks['date'] = pd.to_datetime(daily_clicks['date'])
        if 'date' in tiktok_daily.columns:
            tiktok_daily['date'] = pd.to_datetime(tiktok_daily['date'])

        # 合并数据
        conversion_data = daily_clicks.merge(tiktok_daily, on='date', how='outer')
        conversion_data = conversion_data.fillna(0)
        
        # 计算转化率（避免除零错误）
        conversion_data['clicks_to_views_ratio'] = conversion_data.apply(
            lambda row: (row['clicks_count'] / row['view_count'] * 100) if row['view_count'] > 0 else 0, 
            axis=1
        )
        
        conversion_data['clicks_to_likes_ratio'] = conversion_data.apply(
            lambda row: (row['clicks_count'] / row['like_count'] * 100) if row['like_count'] > 0 else 0, 
            axis=1
        )
        
        return conversion_data
    
    def get_group_clicks_analysis(self, start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取分组点击分析数据
        
        Args:
            start_date (str): 开始日期 (YYYY-MM-DD)
            end_date (str): 结束日期 (YYYY-MM-DD)
        
        Returns:
            pd.DataFrame: 分组点击分析数据
        """
        if self.clicks_df is None or self.merged_df is None:
            return pd.DataFrame()
        
        # 获取分组 TikTok 数据
        group_daily = self.get_group_daily_metrics(start_date, end_date)
        
        if group_daily.empty:
            return pd.DataFrame()
        
        # 确保 clicks_df['date'] 为 pd.Timestamp 类型
        self.clicks_df['date'] = pd.to_datetime(self.clicks_df['date'])
        group_daily['date'] = pd.to_datetime(group_daily['date'])
        
        # 按链接映射分组
        link_group_data = []
        for link, target_group in self.link_group_mapping.items():
            # 筛选包含目标分组的数据
            group_data = group_daily[group_daily['group'].str.contains(target_group, case=False, na=False)]
            # 确保 group_data['date'] 也是 pd.Timestamp 类型
            group_data['date'] = pd.to_datetime(group_data['date'])
            
            if not group_data.empty:
                # 获取该链接的点击数据
                link_clicks = self.clicks_df[
                    (self.clicks_df['page_url'].str.contains(link, case=False, na=False)) &
                    (self.clicks_df['date'] >= group_data['date'].min()) &
                    (self.clicks_df['date'] <= group_data['date'].max())
                ]
                
                if not link_clicks.empty:
                    daily_link_clicks = link_clicks.groupby('date').size().reset_index(name='link_clicks')
                    
                    # 合并数据
                    merged_data = group_data.merge(daily_link_clicks, on='date', how='left')
                    merged_data['link'] = link
                    merged_data['target_group'] = target_group
                    merged_data['link_clicks'] = merged_data['link_clicks'].fillna(0)
                    
                    link_group_data.append(merged_data)
        
        if link_group_data:
            return pd.concat(link_group_data, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def get_data_summary(self) -> Dict:
        """获取数据摘要"""
        if self.merged_df is None:
            return {}
        
        try:
            import streamlit as st
            st.write("[DEBUG] 开始获取数据摘要...")
            st.write(f"[DEBUG] merged_df columns: {self.merged_df.columns.tolist()}")
            st.write(f"[DEBUG] merged_df shape: {self.merged_df.shape}")
            
            # 检查必要的列是否存在
            if 'date' not in self.merged_df.columns:
                st.error(f"[DEBUG] merged_df 缺少 'date' 列，实际列: {self.merged_df.columns.tolist()}")
                raise KeyError("merged_df 缺少 'date' 列")
            
            if 'user_id' not in self.merged_df.columns:
                st.error(f"[DEBUG] merged_df 缺少 'user_id' 列，实际列: {self.merged_df.columns.tolist()}")
                raise KeyError("merged_df 缺少 'user_id' 列")
            
            # 计算总浏览量
            total_views = self.merged_df['view_count'].sum() if 'view_count' in self.merged_df.columns else 0
            
            # 获取日期范围
            date_min = self.merged_df['date'].min()
            date_max = self.merged_df['date'].max()
            st.write(f"[DEBUG] 日期范围: {date_min} 到 {date_max}")
            
            summary = {
                'total_records': len(self.merged_df),
                'unique_accounts': self.merged_df['user_id'].nunique(),
                'total_views': total_views,  # 替换分组数量为总浏览量
                'date_range': {
                    'start': date_min,
                    'end': date_max
                },
                'matched_records': len(self.merged_df[self.merged_df['group'] != 'Unknown']),
                'unmatched_records': len(self.merged_df[self.merged_df['group'] == 'Unknown']),
                'match_rate': len(self.merged_df[self.merged_df['group'] != 'Unknown']) / len(self.merged_df) * 100
            }
            
            st.write("[DEBUG] 数据摘要获取成功")
            return summary
            
        except Exception as e:
            st.error(f"[DEBUG] 获取数据摘要失败: {str(e)}")
            print(f"[DEBUG] 获取数据摘要失败: {str(e)}")
            return {}
        
        if self.clicks_df is not None:
            summary['clicks_data'] = {
                'total_clicks': len(self.clicks_df),
                'unique_dates': self.clicks_df['date'].nunique(),
                'date_range': {
                    'start': self.clicks_df['date'].min(),
                    'end': self.clicks_df['date'].max()
                }
            }
        
        # 获取昨日对比数据
        yesterday_comparison = self.get_yesterday_comparison()
        if yesterday_comparison:
            summary['yesterday_comparison'] = yesterday_comparison
        
        return summary
    
    def get_yesterday_comparison(self) -> Dict:
        """
        获取昨日对比数据
        返回当前值与昨日值的对比信息
        """
        if self.merged_df is None:
            return {}
        
        try:
            # 获取最新日期和昨日日期
            latest_date = self.merged_df['date'].max()
            yesterday_date = latest_date - pd.Timedelta(days=1)
            
            # 获取最新日期的数据
            latest_data = self.merged_df[self.merged_df['date'] == latest_date]
            yesterday_data = self.merged_df[self.merged_df['date'] == yesterday_date]
            
            comparison = {}
            
            # 1. 总记录数对比
            current_records = len(latest_data)
            yesterday_records = len(yesterday_data)
            records_diff = current_records - yesterday_records
            records_pct = (records_diff / yesterday_records * 100) if yesterday_records > 0 else 0
            comparison['total_records'] = {
                'current': current_records,
                'yesterday': yesterday_records,
                'diff': records_diff,
                'pct': records_pct
            }
            
            # 2. 账号数量对比
            current_accounts = latest_data['user_id'].nunique()
            yesterday_accounts = yesterday_data['user_id'].nunique()
            accounts_diff = current_accounts - yesterday_accounts
            accounts_pct = (accounts_diff / yesterday_accounts * 100) if yesterday_accounts > 0 else 0
            comparison['unique_accounts'] = {
                'current': current_accounts,
                'yesterday': yesterday_accounts,
                'diff': accounts_diff,
                'pct': accounts_pct
            }
            
            # 3. 总浏览量对比
            current_views = latest_data['view_count'].sum() if 'view_count' in latest_data.columns else 0
            yesterday_views = yesterday_data['view_count'].sum() if 'view_count' in yesterday_data.columns else 0
            views_diff = current_views - yesterday_views
            views_pct = (views_diff / yesterday_views * 100) if yesterday_views > 0 else 0
            comparison['total_views'] = {
                'current': current_views,
                'yesterday': yesterday_views,
                'diff': views_diff,
                'pct': views_pct
            }
            
            # 4. 总点击量对比
            if self.clicks_df is not None:
                latest_clicks = self.clicks_df.copy()
                if 'timestamp' in latest_clicks.columns:
                    latest_clicks['date'] = pd.to_datetime(latest_clicks['timestamp']).dt.date
                elif 'date' in latest_clicks.columns:
                    latest_clicks['date'] = pd.to_datetime(latest_clicks['date']).dt.date
                
                current_clicks = len(latest_clicks[latest_clicks['date'] == latest_date])
                yesterday_clicks = len(latest_clicks[latest_clicks['date'] == yesterday_date])
                clicks_diff = current_clicks - yesterday_clicks
                clicks_pct = (clicks_diff / yesterday_clicks * 100) if yesterday_clicks > 0 else 0
                comparison['total_clicks'] = {
                    'current': current_clicks,
                    'yesterday': yesterday_clicks,
                    'diff': clicks_diff,
                    'pct': clicks_pct
                }
            
            # 5. 每日增量指标对比
            latest_increments = self.get_latest_day_increment_metrics()
            if not latest_increments.empty:
                latest_row = latest_increments.iloc[-1]  # 最新一天
                yesterday_row = latest_increments.iloc[-2] if len(latest_increments) > 1 else latest_row
                
                increment_metrics = ['view_count_inc', 'post_count_inc', 'like_count_inc', 'comment_count_inc', 'share_count_inc']
                for metric in increment_metrics:
                    if metric in latest_row and metric in yesterday_row:
                        current_val = latest_row[metric]
                        yesterday_val = yesterday_row[metric]
                        diff = current_val - yesterday_val
                        pct = (diff / yesterday_val * 100) if yesterday_val != 0 else 0
                        
                        comparison[f'{metric}_increment'] = {
                            'current': current_val,
                            'yesterday': yesterday_val,
                            'diff': diff,
                            'pct': pct
                        }
            
            return comparison
            
        except Exception as e:
            print(f"⚠️ 获取昨日对比数据失败: {e}")
            return {}
    
    def save_processed_data(self, output_dir: str = 'data/processed'):
        """保存处理后的数据"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            if self.merged_df is not None:
                merged_path = os.path.join(output_dir, 'enhanced_merged_tiktok_data.csv')
                self.merged_df.to_csv(merged_path, index=False)
                print(f"✅ 合并数据已保存: {merged_path}")
            
            if self.clicks_df is not None:
                clicks_path = os.path.join(output_dir, 'processed_clicks_data.csv')
                self.clicks_df.to_csv(clicks_path, index=False)
                print(f"✅ 点击数据已保存: {clicks_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据保存失败: {str(e)}")
            return False 

    def get_daily_increment_metrics(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        获取所有账号每日新增关键指标（以 user_id 为单位做 diff，再按日期聚合）
        """
        if self.merged_df is None:
            return pd.DataFrame()
        df = self.merged_df.copy()
        df = df.sort_values(['user_id', 'date'])
        for col in ['view_count', 'like_count', 'comment_count', 'share_count', 'post_count']:
            diff = df.groupby('user_id')[col].diff()
            if not isinstance(diff, pd.Series):
                diff = pd.Series([0.0]*len(df), index=df.index)
            else:
                diff = pd.Series(diff.values, index=df.index)
            diff = diff.fillna(0)
            df[f'{col}_inc'] = diff
        if start_date:
            start_date = pd.Timestamp(start_date)
            df = df[df['date'] >= start_date]
        if end_date:
            end_date = pd.Timestamp(end_date)
            df = df[df['date'] <= end_date]
        agg = df.groupby('date')[['view_count_inc', 'like_count_inc', 'comment_count_inc', 'share_count_inc', 'post_count_inc']].sum().reset_index()
        all_dates = pd.date_range(df['date'].min(), df['date'].max())
        agg = agg.set_index('date').reindex(all_dates, fill_value=0).rename_axis('date').reset_index()
        return agg

    def get_group_daily_increment_metrics(self, start_date: Optional[str] = None, end_date: Optional[str] = None, groups: Optional[List[str]] = None) -> pd.DataFrame:
        """
        获取分组每日新增关键指标（分组归一化后，user_id+date做diff，再按date+group聚合）
        """
        if self.merged_df is None:
            return pd.DataFrame()
        df = self.merged_df.copy()
        if groups:
            df = self.filter_data_by_groups(df, groups)
        df = df.sort_values(['user_id', 'date'])
        for col in ['view_count', 'like_count', 'comment_count', 'share_count', 'post_count']:
            diff = df.groupby('user_id')[col].diff()
            if not isinstance(diff, pd.Series):
                diff = pd.Series([0.0]*len(df), index=df.index)
            else:
                diff = pd.Series(diff.values, index=df.index)
            diff = diff.fillna(0)
            df[f'{col}_inc'] = diff
        if start_date:
            start_date = pd.Timestamp(start_date)
            df = df[df['date'] >= start_date]
        if end_date:
            end_date = pd.Timestamp(end_date)
            df = df[df['date'] <= end_date]
        agg = df.groupby(['date', 'group'])[['view_count_inc', 'like_count_inc', 'comment_count_inc', 'share_count_inc', 'post_count_inc']].sum().reset_index()
        all_dates = pd.date_range(df['date'].min(), df['date'].max())
        all_groups = agg['group'].unique()
        idx = pd.MultiIndex.from_product([all_dates, all_groups], names=['date', 'group'])
        agg = agg.set_index(['date', 'group']).reindex(idx, fill_value=0).reset_index()
        return agg 

    def get_link_conversion_analysis(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """
        获取 insnap.ai 链接每日点击与浏览趋势分析数据，包含PV（点击量）和UV（独立访客数）
        """
        if self.clicks_df is None or self.merged_df is None:
            return {}
        
        link_group_mapping = {
            'https://insnap.ai/videos': 'yujie_main_avatar',
            'https://insnap.ai/zh/download': 'wan_produce101'
        }
        result = {}
        for link_url, target_group in link_group_mapping.items():
            print(f"🔍 分析链接: {link_url} -> 目标分组: {target_group}")
            # 1. 获取链接点击数据
            link_clicks = self.clicks_df.copy()
            if 'timestamp' in link_clicks.columns:
                link_clicks['date'] = pd.to_datetime(link_clicks['timestamp']).dt.date
            elif 'date' in link_clicks.columns:
                link_clicks['date'] = pd.to_datetime(link_clicks['date']).dt.date
            else:
                print(f"❌ 点击数据中未找到时间字段")
                continue
            http_link = link_url.replace('https://', 'http://')
            https_link = link_url.replace('http://', 'https://')
            link_clicks = link_clicks[
                (link_clicks['page_url'] == link_url) |
                (link_clicks['page_url'] == http_link) |
                (link_clicks['page_url'] == https_link)
            ].copy()
            if start_date:
                start_date_ts = pd.Timestamp(start_date)
                link_clicks = link_clicks[link_clicks['date'] >= start_date_ts.date()]
            if end_date:
                end_date_ts = pd.Timestamp(end_date)
                link_clicks = link_clicks[link_clicks['date'] <= end_date_ts.date()]
            
            # 每日点击量（PV）和访客数（UV）
            if not link_clicks.empty:
                # 每日点击量（PV）- session_id去重
                daily_clicks = link_clicks.groupby('date')['session_id'].nunique().reset_index(name='daily_clicks')
                daily_clicks['date'] = pd.to_datetime(daily_clicks['date'])
                
                # 每日访客数（UV）- visitor_id去重
                daily_visitors = link_clicks.groupby('date')['visitor_id'].nunique().reset_index(name='daily_visitors')
                daily_visitors['date'] = pd.to_datetime(daily_visitors['date'])
                
                # 合并PV和UV数据
                daily_pv_uv = pd.merge(daily_clicks, daily_visitors, on='date', how='outer').fillna(0)
            else:
                daily_pv_uv = pd.DataFrame(columns=['date', 'daily_clicks', 'daily_visitors'])
            
            # 2. 获取目标分组的每日浏览量（view_diff）
            group_views = self.merged_df.copy()
            group_views['date'] = pd.to_datetime(group_views['date'])
            group_views = group_views[group_views['group'].str.contains(target_group, na=False, case=False)]
            if start_date:
                group_views = group_views[group_views['date'] >= start_date_ts]
            if end_date:
                group_views = group_views[group_views['date'] <= end_date_ts]
            # 用 view_diff 字段，若无则全为 0
            if 'view_diff' in group_views.columns:
                group_views['view_diff'] = pd.to_numeric(group_views['view_diff'], errors='coerce').fillna(0)
                daily_views = group_views.groupby(group_views['date'].dt.date)['view_diff'].sum().reset_index()
                daily_views.columns = ['date', 'daily_views']
                daily_views['date'] = pd.to_datetime(daily_views['date'])
            else:
                print(f"⚠️ merged_df 无 view_diff 字段，全部视为 0")
                daily_views = pd.DataFrame(columns=['date', 'daily_views'])
            
            # 3. 合并所有数据
            merged_data = pd.merge(daily_pv_uv, daily_views, on='date', how='outer').fillna(0)
            merged_data['date'] = pd.to_datetime(merged_data['date']).dt.date
            
            # 4. 计算每日转化率
            merged_data['daily_pv_conversion_rate'] = merged_data.apply(
                lambda row: round(row['daily_clicks'] / row['daily_views'] * 100, 2) if row['daily_views'] > 0 else 0.0,
                axis=1
            )
            merged_data['daily_uv_conversion_rate'] = merged_data.apply(
                lambda row: round(row['daily_visitors'] / row['daily_views'] * 100, 2) if row['daily_views'] > 0 else 0.0,
                axis=1
            )
            
            # 5. 日期连续化
            if not merged_data.empty:
                all_dates = pd.date_range(merged_data['date'].min(), merged_data['date'].max())
                merged_data = merged_data.set_index('date').reindex(all_dates, fill_value=0).reset_index()
                merged_data = merged_data.rename(columns={'index': 'date'})
                merged_data['date'] = pd.to_datetime(merged_data['date']).dt.date
            
            # 6. 今日新增数据
            today_row = merged_data.iloc[-1] if not merged_data.empty else None
            today_data = {
                'date': str(today_row['date']) if today_row is not None else '',
                'pv': int(today_row['daily_clicks']) if today_row is not None else 0,
                'uv': int(today_row['daily_visitors']) if today_row is not None else 0,
                'views': int(today_row['daily_views']) if today_row is not None else 0,
                'pv_rate': round(today_row['daily_clicks'] / today_row['daily_views'] * 100, 2) if today_row is not None and today_row['daily_views'] > 0 else 0.0,
                'uv_rate': round(today_row['daily_visitors'] / today_row['daily_views'] * 100, 2) if today_row is not None and today_row['daily_views'] > 0 else 0.0
            }
            
            # 7. 汇总结果
            result[link_url] = {
                'target_group': target_group,
                'total_clicks': int(link_clicks['session_id'].nunique()) if not link_clicks.empty else 0,
                'total_visitors': int(link_clicks['visitor_id'].nunique()) if not link_clicks.empty else 0,
                'total_views': int(group_views['view_count'].sum()) if 'view_count' in group_views.columns else 0,
                'avg_pv_conversion_rate': merged_data['daily_pv_conversion_rate'].mean() if not merged_data.empty else 0.0,
                'avg_uv_conversion_rate': merged_data['daily_uv_conversion_rate'].mean() if not merged_data.empty else 0.0,
                'data': merged_data,
                'today': today_data
            }
            print(f"✅ {link_url}: 总点击(PV) {result[link_url]['total_clicks']}, 总访客(UV) {result[link_url]['total_visitors']}, 总浏览 {result[link_url]['total_views']}")
            print(f"   平均PV转化率 {result[link_url]['avg_pv_conversion_rate']:.2f}%, 平均UV转化率 {result[link_url]['avg_uv_conversion_rate']:.2f}%")
        return result

    def get_latest_day_increment_metrics(self, target_date: Optional[str] = None) -> Dict:
        """
        获取指定日期（或最新日期）的每日增量指标
        
        Args:
            target_date (Optional[str]): 目标日期，格式为 'YYYY-MM-DD'，如果为None则使用最新日期
        
        Returns:
            Dict: 包含各项增量指标的字典
        """
        if self.merged_df is None:
            return {}
        
        try:
            # 确定目标日期
            if target_date:
                target_date = pd.Timestamp(target_date)
            else:
                # 使用最新日期
                target_date = self.merged_df['date'].max()
            
            # 获取目标日期的数据
            target_data = self.merged_df[self.merged_df['date'] == target_date].copy()
            
            if target_data.empty:
                return {}
            
            # 计算增量指标
            # 使用 diff 列（如果存在）或计算差值
            increment_metrics = {}
            
            # 处理观看量增量
            if 'view_diff' in target_data.columns:
                increment_metrics['view_increment'] = int(target_data['view_diff'].sum())
            else:
                # 如果没有 view_diff，尝试计算差值
                increment_metrics['view_increment'] = 0
            
            # 处理发帖量增量
            if 'post_diff' in target_data.columns:
                increment_metrics['post_increment'] = int(target_data['post_diff'].sum())
            else:
                increment_metrics['post_increment'] = 0
            
            # 处理点赞数增量
            if 'like_diff' in target_data.columns:
                increment_metrics['like_increment'] = int(target_data['like_diff'].sum())
            else:
                increment_metrics['like_increment'] = 0
            
            # 处理评论数增量
            if 'comment_diff' in target_data.columns:
                increment_metrics['comment_increment'] = int(target_data['comment_diff'].sum())
            else:
                increment_metrics['comment_increment'] = 0
            
            # 处理分享数增量
            if 'share_diff' in target_data.columns:
                increment_metrics['share_increment'] = int(target_data['share_diff'].sum())
            else:
                increment_metrics['share_increment'] = 0
            
            # 处理点击数增量（从点击数据获取）
            if self.clicks_df is not None:
                clicks_target_data = self.clicks_df.copy()
                if 'timestamp' in clicks_target_data.columns:
                    clicks_target_data['date'] = pd.to_datetime(clicks_target_data['timestamp']).dt.date
                elif 'date' in clicks_target_data.columns:
                    clicks_target_data['date'] = pd.to_datetime(clicks_target_data['date']).dt.date
                
                clicks_target_data = clicks_target_data[clicks_target_data['date'] == target_date.date()]
                increment_metrics['click_increment'] = len(clicks_target_data)
            else:
                increment_metrics['click_increment'] = 0
            
            # 添加目标日期信息
            increment_metrics['target_date'] = target_date.strftime('%Y-%m-%d')
            
            return increment_metrics
            
        except Exception as e:
            print(f"❌ 获取最新一天增量指标失败: {str(e)}")
            return {}

    def get_last_day_clicks_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
        """
        获取最后一天的点击统计数据（PV和UV）
        
        Args:
            start_date (Optional[str]): 开始日期，格式为 'YYYY-MM-DD'
            end_date (Optional[str]): 结束日期，格式为 'YYYY-MM-DD'
        
        Returns:
            Dict: 包含两个链接的最后一天点击统计数据
        """
        if self.clicks_df is None:
            print("⚠️ clicks_df 为空")
            return {}
        
        try:
            print(f"🔍 开始处理点击数据，原始数据行数: {len(self.clicks_df)}")
            
            # 筛选日期范围
            clicks_df = self.clicks_df.copy()
            
            # 处理日期字段
            if 'timestamp' in clicks_df.columns:
                print("📅 使用 timestamp 字段作为日期")
                clicks_df['date'] = pd.to_datetime(clicks_df['timestamp']).dt.date
            elif 'date' in clicks_df.columns:
                print("📅 使用 date 字段作为日期")
                clicks_df['date'] = pd.to_datetime(clicks_df['date']).dt.date
            else:
                print("❌ 未找到日期字段")
                return {}
            
            print(f"📊 日期处理后数据行数: {len(clicks_df)}")
            print(f"📅 日期范围: {clicks_df['date'].min()} 到 {clicks_df['date'].max()}")
            
            # 只保留日期范围内的数据
            if start_date:
                start_date_dt = pd.to_datetime(start_date).date()
                clicks_df = clicks_df[clicks_df['date'] >= start_date_dt]
                print(f"📅 应用开始日期过滤 {start_date_dt}，剩余行数: {len(clicks_df)}")
            if end_date:
                end_date_dt = pd.to_datetime(end_date).date()
                clicks_df = clicks_df[clicks_df['date'] <= end_date_dt]
                print(f"📅 应用结束日期过滤 {end_date_dt}，剩余行数: {len(clicks_df)}")
            
            if clicks_df.empty:
                print("⚠️ 日期过滤后数据为空")
                return {}
            
            # 取最后一天
            last_day = clicks_df['date'].max()
            last_day_df = clicks_df[clicks_df['date'] == last_day]
            print(f"📅 最后一天: {last_day}，数据行数: {len(last_day_df)}")
            
            # 检查必要的列是否存在
            required_cols = ['page_url', 'session_id', 'visitor_id']
            missing_cols = [col for col in required_cols if col not in last_day_df.columns]
            if missing_cols:
                print(f"❌ 缺少必要列: {missing_cols}")
                print(f"📋 可用列: {list(last_day_df.columns)}")
                return {}
            
            # 链接映射，忽略http/https
            link_targets = [
                'insnap.ai/videos',
                'insnap.ai/zh/download'
            ]
            
            result = {}
            for link in link_targets:
                print(f"🔗 处理链接: {link}")
                
                # 兼容http/https，去除协议后再比对
                def normalize_url(url):
                    if pd.isna(url):
                        return ""
                    url_str = str(url)
                    # 去除协议和查询参数
                    url_str = url_str.replace('http://', '').replace('https://', '').split('?')[0]
                    return url_str
                
                # 应用URL标准化
                last_day_df['normalized_url'] = last_day_df['page_url'].apply(normalize_url)
                mask = last_day_df['normalized_url'] == link
                link_df = last_day_df[mask]
                
                print(f"   📊 匹配到 {len(link_df)} 条记录")
                
                if not link_df.empty:
                    # 统计PV和UV
                    pv = link_df['session_id'].nunique()
                    uv = link_df['visitor_id'].nunique()
                    
                    print(f"   📈 PV (session_id去重): {pv}")
                    print(f"   👥 UV (visitor_id去重): {uv}")
                    
                    result[f'https://{link}'] = {
                        'date': str(last_day),
                        'pv': pv,
                        'uv': uv
                    }
                else:
                    print(f"   ⚠️ 未找到匹配记录")
                    result[f'https://{link}'] = {
                        'date': str(last_day),
                        'pv': 0,
                        'uv': 0
                    }
            
            print(f"✅ 处理完成，返回结果: {result}")
            return result
            
        except Exception as e:
            print(f'❌ get_last_day_clicks_summary error: {e}')
            import traceback
            traceback.print_exc()
            return {}

    def get_top_performing_accounts(self, start_date: Optional[str] = None, end_date: Optional[str] = None, top_n: int = 5) -> pd.DataFrame:
        """
        获取表现最好的账号Top N（按最后一天新增浏览量排序）
        
        Args:
            start_date (Optional[str]): 开始日期，格式为 'YYYY-MM-DD'
            end_date (Optional[str]): 结束日期，格式为 'YYYY-MM-DD'
            top_n (int): 返回前N个账号，默认5个
        
        Returns:
            pd.DataFrame: 包含账号信息的DataFrame
        """
        if self.merged_df is None or self.accounts_df is None:
            return pd.DataFrame()
        
        try:
            # 筛选日期范围
            df = self.merged_df.copy()
            if start_date:
                start_date_ts = pd.Timestamp(start_date)
                df = df[df['date'] >= start_date_ts]
            if end_date:
                end_date_ts = pd.Timestamp(end_date)
                df = df[df['date'] <= end_date_ts]
            
            # 只取最后一天的数据
            last_date = df['date'].max()
            last_day_data = df[df['date'] == last_date].copy()
            
            print(f"📅 使用最后一天数据: {last_date.strftime('%Y-%m-%d')}")
            
            if last_day_data.empty:
                print("⚠️ 最后一天没有数据")
                return pd.DataFrame()
            
            # 按user_id聚合最后一天的view_diff
            if 'view_diff' in last_day_data.columns:
                # 确保view_diff为数值类型
                last_day_data['view_diff'] = pd.to_numeric(last_day_data['view_diff'], errors='coerce').fillna(0)
                
                # 按user_id聚合最后一天的数据
                account_performance = last_day_data.groupby('user_id').agg({
                    'view_diff': 'sum'  # 只统计最后一天的新增浏览量
                }).reset_index()
                
                # 按view_diff降序排序，取前N个
                account_performance = account_performance.sort_values('view_diff', ascending=False).head(top_n)
                
                # 准备accounts_df用于合并
                accounts_info = self.accounts_df.copy()
                accounts_info['user_id'] = accounts_info['Tiktok ID'].astype(str)
                
                # 合并账号信息
                result = account_performance.merge(
                    accounts_info[['user_id', 'Tiktok Username', 'Total Followers', 'Total Like']], 
                    on='user_id', 
                    how='left'
                )
                
                # 处理缺失值
                result['Tiktok Username'] = result['Tiktok Username'].fillna('未知')
                result['Total Followers'] = pd.to_numeric(result['Total Followers'], errors='coerce').fillna(0)
                result['Total Like'] = pd.to_numeric(result['Total Like'], errors='coerce').fillna(0)
                
                # 构造主页链接
                result['profile_url'] = result['Tiktok Username'].apply(
                    lambda x: f"https://www.tiktok.com/@{x}" if x != '未知' else ''
                )
                
                # 重命名列
                result = result.rename(columns={
                    'Tiktok Username': 'username',
                    'Total Followers': 'follower_count',
                    'Total Like': 'like_count',
                    'view_diff': 'last_day_view_increment'
                })
                
                # 选择并排序列
                result = result[[
                    'profile_url', 'user_id', 'username', 'last_day_view_increment', 
                    'follower_count', 'like_count'
                ]]
                
                print(f"✅ 成功获取Top {len(result)} 账号，基于 {last_date.strftime('%Y-%m-%d')} 的新增浏览量")
                return result
            else:
                print("⚠️ 数据中未找到view_diff字段")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"❌ 获取表现最好账号失败: {str(e)}")
            return pd.DataFrame() 

    def get_selected_groups_latest_increments(self, selected_groups: List[str], target_date: Optional[str] = None) -> Dict:
        """
        获取当前选中分组的最新一天增量指标
        
        Args:
            selected_groups (List[str]): 选中的分组关键词列表
            target_date (Optional[str]): 目标日期，格式为 'YYYY-MM-DD'，默认为最新日期
        
        Returns:
            Dict: 包含每个分组的增量指标数据
        """
        if self.merged_df is None or not selected_groups:
            return {}
        
        try:
            # 获取目标日期
            if target_date:
                target_date = pd.Timestamp(target_date)
            else:
                target_date = self.merged_df['date'].max()
            
            print(f"📅 获取分组增量指标，目标日期: {target_date.strftime('%Y-%m-%d')}")
            
            # 筛选目标日期的数据
            target_data = self.merged_df[self.merged_df['date'] == target_date].copy()
            
            if target_data.empty:
                print(f"⚠️ 目标日期 {target_date.strftime('%Y-%m-%d')} 无数据")
                return {}
            
            result = {}
            
            for group_keyword in selected_groups:
                print(f"🔍 处理分组: {group_keyword}")
                
                # 使用模糊匹配筛选分组数据
                group_data = target_data[target_data['group'].str.contains(group_keyword, na=False, case=False)]
                
                if group_data.empty:
                    print(f"   ⚠️ 分组 '{group_keyword}' 无匹配数据")
                    result[group_keyword] = {
                        'date': target_date.strftime('%Y-%m-%d'),
                        'posts': 0,
                        'views': 0,
                        'likes': 0,
                        'comments': 0,
                        'shares': 0
                    }
                    continue
                
                print(f"   📊 找到 {len(group_data)} 条记录")
                
                # 计算各项增量指标
                group_metrics = {
                    'date': target_date.strftime('%Y-%m-%d'),
                    'posts': 0,
                    'views': 0,
                    'likes': 0,
                    'comments': 0,
                    'shares': 0
                }
                
                # 处理发帖量增量
                if 'post_diff' in group_data.columns:
                    group_metrics['posts'] = int(group_data['post_diff'].sum())
                
                # 处理浏览量增量
                if 'view_diff' in group_data.columns:
                    group_metrics['views'] = int(group_data['view_diff'].sum())
                
                # 处理点赞数增量
                if 'like_diff' in group_data.columns:
                    group_metrics['likes'] = int(group_data['like_diff'].sum())
                
                # 处理评论数增量
                if 'comment_diff' in group_data.columns:
                    group_metrics['comments'] = int(group_data['comment_diff'].sum())
                
                # 处理分享数增量
                if 'share_diff' in group_data.columns:
                    group_metrics['shares'] = int(group_data['share_diff'].sum())
                
                result[group_keyword] = group_metrics
                
                print(f"   📈 增量指标: 发帖{group_metrics['posts']}, 浏览{group_metrics['views']}, 点赞{group_metrics['likes']}, 评论{group_metrics['comments']}, 分享{group_metrics['shares']}")
            
            return result
            
        except Exception as e:
            print(f"❌ 获取分组增量指标失败: {str(e)}")
            return {} 