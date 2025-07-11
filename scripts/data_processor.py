import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class TikTokDataProcessor:
    """TikTok 数据处理类"""
    
    def __init__(self, redash_file_path, accounts_file_path):
        """
        初始化数据处理器
        
        Args:
            redash_file_path (str): redash 数据文件路径
            accounts_file_path (str): accounts detail 数据文件路径
        """
        self.redash_file_path = redash_file_path
        self.accounts_file_path = accounts_file_path
        self.merged_df = None
        self.group_mapping = None
        
    def load_redash_data(self):
        """加载 redash 数据"""
        try:
            print("正在加载 redash 数据...")
            redash_df = pd.read_csv(self.redash_file_path, low_memory=False)
            print("Redash columns:", redash_df.columns)
            
            # 数据预处理
            redash_df['date'] = pd.to_datetime(redash_df['YMDdate'], format='%d/%m/%y', errors='coerce')
            redash_df = redash_df.dropna(subset=['date'])
            
            # 确保 user_id 为字符串类型
            redash_df['user_id'] = redash_df['user_id'].astype(str)
            
            # 确保数值列为数值类型
            numeric_columns = [
                'view_count', 'like_count', 'comment_count', 'share_count', 
                'post_count', 'view_per_post', 'like_per_post', 'comment_per_post', 
                'share_per_post'
            ]
            
            for col in numeric_columns:
                if col in redash_df.columns:
                    redash_df[col] = pd.to_numeric(redash_df[col], errors='coerce')
            
            print(f"✅ Redash 数据加载成功: {redash_df.shape}")
            return redash_df
            
        except Exception as e:
            print(f"❌ Redash 数据加载失败: {str(e)}")
            return None
    
    def load_accounts_data(self):
        """加载 accounts detail 数据"""
        try:
            print("正在加载 accounts detail 数据...")
            accounts_df = pd.read_excel(self.accounts_file_path)
            self.accounts_df = accounts_df  # 修复：保存为实例属性
            
            # 创建 group 映射
            group_mapping = accounts_df[['Tiktok ID', 'Groups']].drop_duplicates()
            group_mapping = group_mapping.rename(columns={'Tiktok ID': 'user_id', 'Groups': 'group'})
            
            # 确保 user_id 为字符串类型
            group_mapping['user_id'] = group_mapping['user_id'].astype(str)
            
            print(f"✅ Accounts 数据加载成功: {accounts_df.shape}")
            print(f"✅ Group 映射创建成功: {group_mapping.shape}")
            return group_mapping
            
        except Exception as e:
            print(f"❌ Accounts 数据加载失败: {str(e)}")
            return None
    
    def merge_data(self):
        """合并数据"""
        try:
            print("正在合并数据...")
            
            # 加载数据
            redash_df = self.load_redash_data()
            group_mapping = self.load_accounts_data()
            
            if redash_df is None or group_mapping is None:
                return False
            
            # 合并数据
            merged_df = redash_df.merge(group_mapping, on='user_id', how='left')
            merged_df['group'] = merged_df['group'].fillna('Unknown')
            
            self.merged_df = merged_df
            self.group_mapping = group_mapping
            
            print(f"✅ 数据合并成功: {merged_df.shape}")
            return True
            
        except Exception as e:
            print(f"❌ 数据合并失败: {str(e)}")
            return False
    
    def get_data_summary(self):
        """获取数据摘要"""
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        summary = {
            'total_records': len(self.merged_df),
            'unique_accounts': self.merged_df['user_id'].nunique(),
            'unique_groups': self.merged_df['group'].nunique(),
            'date_range': {
                'start': self.merged_df['date'].min(),
                'end': self.merged_df['date'].max()
            },
            'matched_records': len(self.merged_df[self.merged_df['group'] != 'Unknown']),
            'unmatched_records': len(self.merged_df[self.merged_df['group'] == 'Unknown']),
            'match_rate': len(self.merged_df[self.merged_df['group'] != 'Unknown']) / len(self.merged_df) * 100
        }
        
        return summary
    
    def get_group_statistics(self):
        """获取分组统计信息"""
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        group_stats = self.merged_df.groupby('group')['user_id'].nunique().sort_values(ascending=False)
        return group_stats
    
    def filter_data(self, start_date=None, end_date=None, groups=None):
        """
        筛选数据
        
        Args:
            start_date (str): 开始日期 (YYYY-MM-DD)
            end_date (str): 结束日期 (YYYY-MM-DD)
            groups (list): 分组列表
        
        Returns:
            pd.DataFrame: 筛选后的数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
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
            filtered_df = filtered_df[filtered_df['group'].isin(groups)]
        
        return filtered_df
    
    def get_daily_aggregates(self, metrics=None):
        """
        获取每日聚合数据
        
        Args:
            metrics (list): 要聚合的指标列表
        
        Returns:
            pd.DataFrame: 每日聚合数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if metrics is None:
            metrics = ['view_count', 'like_count', 'comment_count', 'share_count', 'post_count']
        
        daily_data = self.merged_df.groupby('date')[metrics].sum().reset_index()
        return daily_data
    
    def get_efficiency_metrics(self, metric='view_per_post'):
        """
        获取效率指标数据
        
        Args:
            metric (str): 效率指标名称
        
        Returns:
            pd.DataFrame: 效率指标数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if metric not in self.merged_df.columns:
            print(f"❌ 指标 {metric} 不存在")
            return None
        
        efficiency_data = self.merged_df.groupby('date')[metric].mean().reset_index()
        return efficiency_data
    
    def get_group_performance(self, date=None):
        """
        获取分组表现数据
        
        Args:
            date: 指定日期，如果为 None 则使用最新日期
        
        Returns:
            pd.DataFrame: 分组表现数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if date is None:
            date = self.merged_df['date'].max()
        
        latest_data = self.merged_df[self.merged_df['date'] == date].copy()
        
        if latest_data.empty:
            print(f"❌ 指定日期 {date} 没有数据")
            return None
        
        group_stats = latest_data.groupby('group').agg({
            'view_count': 'sum',
            'post_count': 'sum',
            'like_count': 'sum',
            'comment_count': 'sum',
            'share_count': 'sum',
            'view_per_post': 'mean',
            'like_per_post': 'mean',
            'comment_per_post': 'mean',
            'share_per_post': 'mean'
        }).round(2)
        
        group_stats = group_stats.reset_index()
        group_stats = group_stats.sort_values('view_count', ascending=False)
        
        return group_stats
    
    def save_merged_data(self, output_path):
        """
        保存合并后的数据
        
        Args:
            output_path (str): 输出文件路径
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return False
        
        try:
            self.merged_df.to_csv(output_path, index=False)
            print(f"✅ 数据已保存到: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 数据保存失败: {str(e)}")
            return False
    
    def get_daily_diff_metrics(self, metric='view_diff', groups=None):
        """
        获取每日新增量指标数据
        
        Args:
            metric (str): 指标名称 (以 _diff 结尾)
            groups (list): 分组列表，如果为 None 则包含所有分组
        
        Returns:
            pd.DataFrame: 每日新增量数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if metric not in self.merged_df.columns:
            print(f"❌ 指标 {metric} 不存在")
            return None
        
        # 筛选数据
        filtered_df = self.merged_df.copy()
        if groups:
            filtered_df = filtered_df[filtered_df['group'].isin(groups)]
        
        # 按日期和分组聚合
        daily_diff = filtered_df.groupby(['date', 'group'])[metric].sum().reset_index()
        return daily_diff
    
    def get_top_accounts(self, date=None, top_n=5, metric='view_diff'):
        """
        获取指定日期的 Top 账号
        
        Args:
            date: 指定日期，如果为 None 则使用最新日期
            top_n (int): 返回前 N 名账号
            metric (str): 排序指标
        
        Returns:
            pd.DataFrame: Top 账号数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if date is None:
            date = self.merged_df['date'].max()
        
        # 筛选指定日期的数据
        daily_data = self.merged_df[self.merged_df['date'] == date].copy()
        
        if daily_data.empty:
            print(f"❌ 指定日期 {date} 没有数据")
            return None
        
        # 按指标排序并获取前 N 名
        top_accounts = daily_data.nlargest(top_n, metric)[
            ['user_id', 'group', 'view_diff', 'like_diff', 'comment_diff', 'share_diff']
        ].copy()
        
        return top_accounts
    
    def get_account_history(self, user_id, start_date=None, end_date=None):
        """
        获取指定账号的历史数据
        
        Args:
            user_id (str): 账号ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            pd.DataFrame: 账号历史数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        # 筛选账号数据
        account_data = self.merged_df[self.merged_df['user_id'] == user_id].copy()
        
        if account_data.empty:
            print(f"❌ 账号 {user_id} 不存在")
            return None
        
        # 日期筛选
        if start_date:
            start_date = pd.Timestamp(start_date)
            account_data = account_data[account_data['date'] >= start_date]
        
        if end_date:
            end_date = pd.Timestamp(end_date)
            account_data = account_data[account_data['date'] <= end_date]
        
        return account_data.sort_values('date')
    
    def get_diff_metrics_summary(self, date=None):
        """
        获取指定日期的 _diff 指标汇总
        
        Args:
            date: 指定日期，如果为 None 则使用最新日期
        
        Returns:
            pd.DataFrame: _diff 指标汇总
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if date is None:
            date = self.merged_df['date'].max()
        
        daily_data = self.merged_df[self.merged_df['date'] == date].copy()
        
        if daily_data.empty:
            print(f"❌ 指定日期 {date} 没有数据")
            return None
        
        # 获取所有 _diff 列
        diff_columns = [col for col in daily_data.columns if col.endswith('_diff')]
        
        # 按 group 聚合
        group_summary = daily_data.groupby('group')[diff_columns].sum().reset_index()
        
        return group_summary
    
    def get_account_performance_ranking(self, date=None, metric='view_diff', top_n=10):
        """
        获取账号表现排名
        
        Args:
            date: 指定日期
            metric (str): 排序指标
            top_n (int): 返回前 N 名
        
        Returns:
            pd.DataFrame: 账号排名数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if date is None:
            date = self.merged_df['date'].max()
        
        daily_data = self.merged_df[self.merged_df['date'] == date].copy()
        
        if daily_data.empty:
            print(f"❌ 指定日期 {date} 没有数据")
            return None
        
        if metric not in daily_data.columns:
            print(f"❌ 指标 {metric} 不存在")
            return None
        
        # 按指标排序并获取前 N 名
        ranking = daily_data.nlargest(top_n, metric)[
            ['user_id', 'group', 'view_diff', 'like_diff', 'comment_diff', 'share_diff']
        ].copy()
        
        return ranking
    
    def get_group_performance_trend(self, group_name, start_date=None, end_date=None):
        """
        获取指定分组的表现趋势
        
        Args:
            group_name (str): 分组名称
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            pd.DataFrame: 分组趋势数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        # 筛选分组数据
        group_data = self.merged_df[self.merged_df['group'] == group_name].copy()
        
        if group_data.empty:
            print(f"❌ 分组 {group_name} 不存在")
            return None
        
        # 日期筛选
        if start_date:
            start_date = pd.Timestamp(start_date)
            group_data = group_data[group_data['date'] >= start_date]
        
        if end_date:
            end_date = pd.Timestamp(end_date)
            group_data = group_data[group_data['date'] <= end_date]
        
        # 按日期聚合
        trend_data = group_data.groupby('date').agg({
            'view_diff': 'sum',
            'like_diff': 'sum',
            'comment_diff': 'sum',
            'share_diff': 'sum',
            'user_id': 'nunique'
        }).reset_index()
        
        trend_data = trend_data.rename(columns={'user_id': 'account_count'})
        
        return trend_data.sort_values('date')
    
    def get_account_details(self, user_ids=None):
        """
        获取账号详细信息
        
        Args:
            user_ids (list): 账号ID列表，如果为None则返回所有账号
        
        Returns:
            pd.DataFrame: 账号详情数据
        """
        try:
            if self.accounts_df is None:
                print("❌ 账号详情数据尚未加载")
                return None
            
            if user_ids is not None:
                # 根据 user_id 筛选账号
                account_details = self.accounts_df[
                    self.accounts_df['KOL ID'].astype(str).isin([str(uid) for uid in user_ids])
                ].copy()
            else:
                account_details = self.accounts_df.copy()
            
            # 选择关键字段
            key_columns = [
                'KOL ID', 'Tiktok Username', 'Tiktok Display Name', 
                'Total Followers', 'Total Like', 'Total View', 'Total Post',
                'Groups', 'Level', 'Tag'
            ]
            
            # 确保所有列都存在
            available_columns = [col for col in key_columns if col in account_details.columns]
            account_details = account_details[available_columns].copy()
            
            # 清理数据
            account_details = account_details.dropna(subset=['KOL ID'])
            
            return account_details
            
        except Exception as e:
            print(f"❌ 获取账号详情失败: {str(e)}")
            return None
    
    def get_daily_summary_metrics(self, date=None):
        """
        获取指定日期的汇总指标
        
        Args:
            date: 指定日期，如果为None则使用最新日期
        
        Returns:
            dict: 汇总指标字典
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if date is None:
            date = self.merged_df['date'].max()
        
        daily_data = self.merged_df[self.merged_df['date'] == date].copy()
        
        if daily_data.empty:
            print(f"❌ 指定日期 {date} 没有数据")
            return None
        
        # 计算汇总指标
        summary = {
            'date': date,
            'total_posts': daily_data['post_diff'].sum(),
            'total_views': daily_data['view_diff'].sum(),
            'total_likes': daily_data['like_diff'].sum(),
            'total_comments': daily_data['comment_diff'].sum(),
            'total_shares': daily_data['share_diff'].sum(),
            'total_followers': daily_data.get('follower_diff', pd.Series([0])).sum(),
            'active_accounts': len(daily_data['user_id'].unique()),
            'avg_view_per_post': daily_data['view_diff'].sum() / max(daily_data['post_diff'].sum(), 1),
            'avg_like_per_post': daily_data['like_diff'].sum() / max(daily_data['post_diff'].sum(), 1),
            'avg_comment_per_post': daily_data['comment_diff'].sum() / max(daily_data['post_diff'].sum(), 1),
            'avg_share_per_post': daily_data['share_diff'].sum() / max(daily_data['post_diff'].sum(), 1)
        }
        
        return summary
    
    def get_efficiency_distribution(self, date=None, metric='view_per_post'):
        """
        获取效率分布数据
        
        Args:
            date: 指定日期
            metric (str): 效率指标类型
        
        Returns:
            pd.DataFrame: 效率分布数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if date is None:
            date = self.merged_df['date'].max()
        
        daily_data = self.merged_df[self.merged_df['date'] == date].copy()
        
        if daily_data.empty:
            print(f"❌ 指定日期 {date} 没有数据")
            return None
        
        # 计算效率指标
        if metric == 'view_per_post':
            daily_data['efficiency'] = daily_data['view_diff'] / daily_data['post_diff'].replace(0, 1)
        elif metric == 'like_per_post':
            daily_data['efficiency'] = daily_data['like_diff'] / daily_data['post_diff'].replace(0, 1)
        elif metric == 'comment_per_post':
            daily_data['efficiency'] = daily_data['comment_diff'] / daily_data['post_diff'].replace(0, 1)
        elif metric == 'share_per_post':
            daily_data['efficiency'] = daily_data['share_diff'] / daily_data['post_diff'].replace(0, 1)
        else:
            print(f"❌ 不支持的效率指标: {metric}")
            return None
        
        # 按分组聚合效率分布
        efficiency_dist = daily_data.groupby('group').agg({
            'efficiency': ['mean', 'median', 'std', 'count'],
            'user_id': 'nunique'
        }).reset_index()
        
        # 扁平化列名
        efficiency_dist.columns = [
            'group', 'mean_efficiency', 'median_efficiency', 
            'std_efficiency', 'total_posts', 'account_count'
        ]
        
        return efficiency_dist.sort_values('mean_efficiency', ascending=False)
    
    def get_interaction_growth_comparison(self, start_date=None, end_date=None):
        """
        获取互动增长对比数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            pd.DataFrame: 互动增长对比数据
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        # 日期筛选
        filtered_data = self.merged_df.copy()
        
        if start_date:
            start_date = pd.Timestamp(start_date)
            filtered_data = filtered_data[filtered_data['date'] >= start_date]
        
        if end_date:
            end_date = pd.Timestamp(end_date)
            filtered_data = filtered_data[filtered_data['date'] <= end_date]
        
        # 按日期聚合互动指标
        interaction_data = filtered_data.groupby('date').agg({
            'like_diff': 'sum',
            'comment_diff': 'sum',
            'share_diff': 'sum',
            'view_diff': 'sum'
        }).reset_index()
        
        # 计算增长率
        interaction_data = interaction_data.sort_values('date')
        
        for col in ['like_diff', 'comment_diff', 'share_diff', 'view_diff']:
            interaction_data[f'{col}_growth'] = interaction_data[col].pct_change() * 100
        
        return interaction_data
    
    def get_top_accounts_with_details(self, date=None, top_n=5, metric='view_diff'):
        """
        获取带详细信息的 Top 账号
        
        Args:
            date: 指定日期
            top_n (int): 返回前 N 名
            metric (str): 排序指标
        
        Returns:
            pd.DataFrame: Top 账号详细信息
        """
        if self.merged_df is None:
            print("❌ 数据尚未加载，请先调用 merge_data()")
            return None
        
        if date is None:
            date = self.merged_df['date'].max()
        
        daily_data = self.merged_df[self.merged_df['date'] == date].copy()
        
        if daily_data.empty:
            print(f"❌ 指定日期 {date} 没有数据")
            return None
        
        if metric not in daily_data.columns:
            print(f"❌ 指标 {metric} 不存在")
            return None
        
        # 获取 Top 账号
        top_accounts = daily_data.nlargest(top_n, metric)[
            ['user_id', 'group', 'view_diff', 'like_diff', 'comment_diff', 'share_diff']
        ].copy()
        
        # 获取账号详情
        account_details = self.get_account_details(top_accounts['user_id'].tolist())
        
        if account_details is not None:
            # 合并账号详情
            top_accounts = top_accounts.merge(
                account_details,
                left_on='user_id',
                right_on='KOL ID',
                how='left'
            )
            
            # 生成 TikTok 链接
            top_accounts['tiktok_url'] = top_accounts['Tiktok Username'].apply(
                lambda x: f"https://www.tiktok.com/@{x}" if pd.notna(x) else None
            )
        
        return top_accounts

def main():
    """主函数 - 用于测试"""
    # 文件路径
    redash_file = '../data/redash_data/redash_data_2025-07-08.csv'
    accounts_file = '../data/postingManager_data/accounts_detail.xlsx'
    
    # 创建数据处理器
    processor = TikTokDataProcessor(redash_file, accounts_file)
    
    # 合并数据
    if processor.merge_data():
        # 获取数据摘要
        summary = processor.get_data_summary()
        print("\n=== 数据摘要 ===")
        for key, value in summary.items():
            print(f"{key}: {value}")
        
        # 获取分组统计
        group_stats = processor.get_group_statistics()
        print("\n=== 分组统计 (前10名) ===")
        print(group_stats.head(10))
        
        # 保存合并后的数据
        processor.save_merged_data('../data/merged_tiktok_data.csv')
        
        print("\n✅ 数据处理完成！")
    else:
        print("\n❌ 数据处理失败！")

if __name__ == "__main__":
    main() 