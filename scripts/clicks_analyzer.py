import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import sys
import os

# 添加 config 目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from group_click_map import get_page_type_for_group, get_all_mappings, get_mapping_statistics

warnings.filterwarnings('ignore')

class ClicksAnalyzer:
    """Clicks 数据分析类"""
    
    def __init__(self, clicks_file_path, merged_data_path):
        """
        初始化 Clicks 分析器
        
        Args:
            clicks_file_path (str): clicks 数据文件路径
            merged_data_path (str): 合并后的 TikTok 数据文件路径
        """
        self.clicks_file_path = clicks_file_path
        self.merged_data_path = merged_data_path
        self.clicks_df = None
        self.merged_df = None
        self.processed_clicks = None
        
    def load_clicks_data(self):
        """加载 clicks 数据"""
        try:
            print("正在加载 clicks 数据...")
            self.clicks_df = pd.read_csv(self.clicks_file_path)
            
            # 处理时间戳
            self.clicks_df['timestamp'] = pd.to_datetime(self.clicks_df['timestamp'])
            self.clicks_df['date'] = pd.to_datetime(self.clicks_df['timestamp'].dt.date)
            
            print(f"✅ Clicks 数据加载成功: {self.clicks_df.shape}")
            return True
            
        except Exception as e:
            print(f"❌ Clicks 数据加载失败: {str(e)}")
            return False
    
    def load_merged_data(self):
        """加载合并后的 TikTok 数据"""
        try:
            print("正在加载合并后的 TikTok 数据...")
            self.merged_df = pd.read_csv(self.merged_data_path)
            
            # 处理日期
            self.merged_df['date'] = pd.to_datetime(self.merged_df['date'])
            
            print(f"✅ 合并数据加载成功: {self.merged_df.shape}")
            return True
            
        except Exception as e:
            print(f"❌ 合并数据加载失败: {str(e)}")
            return False
    
    def process_clicks_by_group(self):
        """处理 clicks 数据，按 group 和 page_type 聚合"""
        try:
            if self.clicks_df is None:
                print("❌ 请先加载 clicks 数据")
                return False
            
            # 使用配置文件中的映射函数
            def map_group_to_page_type(group):
                return get_page_type_for_group(str(group))
            
            # 按 page_type 和日期聚合 clicks
            clicks_agg = self.clicks_df.groupby(['page_type', 'date']).size().reset_index(name='click_count')
            
            # 按 group 和日期聚合 TikTok 数据
            tiktok_agg = self.merged_df.groupby(['group', 'date'])['view_diff'].sum().reset_index()
            
            # 添加 page_type 映射
            tiktok_agg['page_type'] = tiktok_agg['group'].apply(map_group_to_page_type)
            
            # 按 page_type 和日期聚合 TikTok 数据
            tiktok_agg = tiktok_agg.groupby(['page_type', 'date'])['view_diff'].sum().reset_index()
            
            self.processed_clicks = {
                'clicks': clicks_agg,
                'tiktok': tiktok_agg
            }
            
            print("✅ Clicks 数据处理完成")
            return True
            
        except Exception as e:
            print(f"❌ Clicks 数据处理失败: {str(e)}")
            return False
    
    def get_clicks_vs_views_data(self, page_type=None):
        """
        获取 clicks vs views 对比数据
        
        Args:
            page_type (str): 页面类型，如果为 None 则包含所有类型
        
        Returns:
            pd.DataFrame: 对比数据
        """
        if self.processed_clicks is None:
            print("❌ 请先处理 clicks 数据")
            return None
        
        clicks_df = self.processed_clicks['clicks'].copy()
        tiktok_df = self.processed_clicks['tiktok'].copy()
        
        # 筛选 page_type
        if page_type:
            clicks_df = clicks_df[clicks_df['page_type'] == page_type]
            tiktok_df = tiktok_df[tiktok_df['page_type'] == page_type]
        
        # 合并数据
        merged_data = pd.merge(
            clicks_df, 
            tiktok_df, 
            on=['page_type', 'date'], 
            how='outer',
            suffixes=('_clicks', '_views')
        )
        
        # 填充缺失值
        merged_data = merged_data.fillna(0)
        
        return merged_data
    
    def calculate_correlation(self, page_type=None):
        """
        计算 clicks 和 views 的相关性
        
        Args:
            page_type (str): 页面类型
        
        Returns:
            float: 相关系数
        """
        data = self.get_clicks_vs_views_data(page_type)
        if data is None or len(data) < 2:
            return None
        
        # 计算相关系数
        correlation = data['click_count'].corr(data['view_diff'])
        return correlation
    
    def get_group_mapping_summary(self):
        """获取 group 映射摘要"""
        if self.merged_df is None:
            print("❌ 请先加载合并数据")
            return None
        
        # 使用配置文件中的映射函数
        def get_page_type(group):
            return get_page_type_for_group(str(group))
        
        group_mapping = self.merged_df.groupby('group').agg({
            'user_id': 'nunique',
            'view_diff': 'sum'
        }).reset_index()
        
        group_mapping['page_type'] = group_mapping['group'].apply(get_page_type)
        
        return group_mapping
    
    def get_daily_comparison(self, page_type='videos'):
        """
        获取每日对比数据
        
        Args:
            page_type (str): 页面类型
        
        Returns:
            pd.DataFrame: 每日对比数据
        """
        data = self.get_clicks_vs_views_data(page_type)
        if data is None:
            return None
        
        # 按日期聚合
        daily_data = data.groupby('date').agg({
            'click_count': 'sum',
            'view_diff': 'sum'
        }).reset_index()
        
        return daily_data
    
    def get_mapping_config_info(self):
        """获取映射配置信息"""
        try:
            mappings = get_all_mappings()
            stats = get_mapping_statistics()
            
            return {
                'mappings': mappings,
                'statistics': stats
            }
        except Exception as e:
            print(f"❌ 获取映射配置信息失败: {str(e)}")
            return None
    
    def get_clicks_key_metrics(self, date=None):
        """
        获取 Clicks 关键指标
        
        Args:
            date: 指定日期，如果为None则使用最新日期
        
        Returns:
            dict: 关键指标字典
        """
        try:
            if self.clicks_df is None:
                print("❌ Clicks 数据尚未加载")
                return None
            
            # 日期筛选
            if date is None:
                date = self.clicks_df['timestamp'].dt.date.max()
            
            daily_clicks = self.clicks_df[
                self.clicks_df['timestamp'].dt.date == date
            ].copy()
            
            if daily_clicks.empty:
                print(f"❌ 指定日期 {date} 没有 clicks 数据")
                return None
            
            # 计算关键指标
            metrics = {
                'date': date,
                'total_clicks': len(daily_clicks),
                'unique_visits': daily_clicks['visitor_id'].nunique(),
                'page_visits': daily_clicks['session_id'].nunique(),
                'unique_pages': daily_clicks['page_type'].nunique(),
                'avg_clicks_per_visit': len(daily_clicks) / max(daily_clicks['visitor_id'].nunique(), 1),
                'avg_clicks_per_session': len(daily_clicks) / max(daily_clicks['session_id'].nunique(), 1)
            }
            
            return metrics
            
        except Exception as e:
            print(f"❌ 获取 Clicks 关键指标失败: {str(e)}")
            return None
    
    def get_clicks_vs_interaction_analysis(self, interaction_metric='like_diff'):
        """
        获取 Clicks 与互动指标的关系分析
        
        Args:
            interaction_metric (str): 互动指标类型
        
        Returns:
            pd.DataFrame: 关系分析数据
        """
        try:
            if self.merged_df is None or self.clicks_df is None:
                print("❌ 数据尚未加载")
                return None
            
            # 处理 clicks 数据
            clicks_daily = self.clicks_df.groupby(
                self.clicks_df['timestamp'].dt.date
            ).size().reset_index(name='click_count')
            clicks_daily.columns = ['date', 'click_count']
            
            # 处理互动数据
            interaction_daily = self.merged_df.groupby('date')[interaction_metric].sum().reset_index()
            
            # 合并数据
            combined_data = clicks_daily.merge(
                interaction_daily,
                on='date',
                how='inner'
            )
            
            if combined_data.empty:
                print("❌ 没有匹配的数据")
                return None
            
            # 计算相关性
            correlation = combined_data['click_count'].corr(combined_data[interaction_metric])
            combined_data['correlation'] = correlation
            
            return combined_data
            
        except Exception as e:
            print(f"❌ 获取 Clicks 与互动关系分析失败: {str(e)}")
            return None
    
    def get_cvr_analysis(self, date=None):
        """
        获取点击转化率 (CVR) 分析
        
        Args:
            date: 指定日期，如果为None则使用最新日期
        
        Returns:
            pd.DataFrame: CVR 分析数据
        """
        try:
            if self.merged_df is None or self.clicks_df is None:
                print("❌ 数据尚未加载")
                return None
            
            # 日期筛选
            if date is None:
                date = self.merged_df['date'].max()
            
            # 获取指定日期的数据
            daily_tiktok = self.merged_df[self.merged_df['date'] == date].copy()
            daily_clicks = self.clicks_df[
                self.clicks_df['timestamp'].dt.date == pd.Timestamp(date).date()
            ].copy()
            
            if daily_tiktok.empty or daily_clicks.empty:
                print(f"❌ 指定日期 {date} 数据不完整")
                return None
            
            # 按 group 聚合 TikTok 数据
            tiktok_by_group = daily_tiktok.groupby('group').agg({
                'view_diff': 'sum',
                'user_id': 'nunique'
            }).reset_index()
            tiktok_by_group.columns = ['group', 'view_diff', 'account_count']
            
            # 按 group 聚合 clicks 数据（使用映射）
            def get_group_from_page_type(page_type):
                return get_page_type_for_group(page_type)
            
            daily_clicks['mapped_group'] = daily_clicks['page_type'].apply(get_group_from_page_type)
            clicks_by_group = daily_clicks.groupby('mapped_group').size().reset_index(name='click_count')
            clicks_by_group.columns = ['group', 'click_count']
            
            # 合并数据
            cvr_data = tiktok_by_group.merge(
                clicks_by_group,
                on='group',
                how='left'
            ).fillna(0)
            
            # 计算 CVR
            cvr_data['cvr'] = (cvr_data['click_count'] / cvr_data['view_diff'].replace(0, 1)) * 100
            cvr_data['cvr'] = cvr_data['cvr'].clip(0, 100)  # 限制在 0-100% 范围内
            
            # 排序
            cvr_data = cvr_data.sort_values('cvr', ascending=False)
            
            return cvr_data
            
        except Exception as e:
            print(f"❌ 获取 CVR 分析失败: {str(e)}")
            return None
    
    def get_top_pages_analysis(self, date=None, top_n=10):
        """
        获取 Top 页面分析
        
        Args:
            date: 指定日期，如果为None则使用最新日期
            top_n (int): 返回前 N 名
        
        Returns:
            pd.DataFrame: Top 页面数据
        """
        try:
            if self.clicks_df is None:
                print("❌ Clicks 数据尚未加载")
                return None
            
            # 日期筛选
            if date is None:
                date = self.clicks_df['timestamp'].dt.date.max()
            
            daily_clicks = self.clicks_df[
                self.clicks_df['timestamp'].dt.date == date
            ].copy()
            
            if daily_clicks.empty:
                print(f"❌ 指定日期 {date} 没有 clicks 数据")
                return None
            
            # 按页面类型统计
            page_stats = daily_clicks.groupby('page_type').agg({
                'session_id': 'nunique',
                'visitor_id': 'nunique',
                'timestamp': 'count'
            }).reset_index()
            
            page_stats.columns = ['page_type', 'unique_sessions', 'unique_visitors', 'total_clicks']
            
            # 计算平均点击次数
            page_stats['avg_clicks_per_session'] = page_stats['total_clicks'] / page_stats['unique_sessions']
            page_stats['avg_clicks_per_visitor'] = page_stats['total_clicks'] / page_stats['unique_visitors']
            
            # 排序并获取 Top N
            top_pages = page_stats.sort_values('total_clicks', ascending=False).head(top_n)
            
            return top_pages
            
        except Exception as e:
            print(f"❌ 获取 Top 页面分析失败: {str(e)}")
            return None
    
    def get_click_trends_by_metric(self, metric='click_count', group_by='page_type'):
        """
        获取按指标分组的点击趋势
        
        Args:
            metric (str): 统计指标
            group_by (str): 分组字段
        
        Returns:
            pd.DataFrame: 趋势数据
        """
        try:
            if self.clicks_df is None:
                print("❌ Clicks 数据尚未加载")
                return None
            
            # 按日期和分组字段聚合
            trends = self.clicks_df.groupby([
                self.clicks_df['timestamp'].dt.date,
                group_by
            ]).size().reset_index(name=metric)
            
            trends.columns = ['date', group_by, metric]
            
            return trends
            
        except Exception as e:
            print(f"❌ 获取点击趋势失败: {str(e)}")
            return None

    def calculate_clicks_metrics_by_day(self):
        """
        计算每天的 clicks 关键指标及昨日对比
        Returns:
            pd.DataFrame: 每天的关键指标及昨日对比
        """
        if self.clicks_df is None:
            print("❌ Clicks 数据尚未加载")
            return None
        df = self.clicks_df.copy()
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        daily = df.groupby('date').agg(
            total_clicks=('timestamp', 'count'),
            unique_visits=('visitor_id', 'nunique'),
            page_visits=('session_id', 'nunique'),
        ).reset_index()
        daily['avg_clicks_per_visit'] = daily['total_clicks'] / daily['unique_visits'].replace(0, 1)
        # 昨日对比
        for col in ['total_clicks', 'unique_visits', 'page_visits', 'avg_clicks_per_visit']:
            daily[f'{col}_prev'] = daily[col].shift(1)
            daily[f'{col}_pct'] = ((daily[col] - daily[f'{col}_prev']) / daily[f'{col}_prev'].replace(0, 1)) * 100
        return daily

def main():
    """主函数 - 用于测试"""
    # 文件路径
    clicks_file = '../data/clicks/20250708ClicksInsnap.csv'
    merged_file = '../data/merged_tiktok_data.csv'
    
    # 创建分析器
    analyzer = ClicksAnalyzer(clicks_file, merged_file)
    
    # 加载数据
    if analyzer.load_clicks_data() and analyzer.load_merged_data():
        # 处理数据
        if analyzer.process_clicks_by_group():
            # 获取对比数据
            comparison_data = analyzer.get_clicks_vs_views_data('videos')
            print(f"\n=== Videos 页面对比数据 ===")
            print(comparison_data.head())
            
            # 计算相关性
            correlation = analyzer.calculate_correlation('videos')
            print(f"\n=== Videos 页面相关性 ===")
            print(f"相关系数: {correlation:.4f}")
            
            # 获取 group 映射摘要
            group_summary = analyzer.get_group_mapping_summary()
            print(f"\n=== Group 映射摘要 ===")
            print(group_summary.head(10))
            
            print("\n✅ Clicks 分析完成！")
        else:
            print("\n❌ Clicks 数据处理失败！")
    else:
        print("\n❌ 数据加载失败！")

if __name__ == "__main__":
    main() 