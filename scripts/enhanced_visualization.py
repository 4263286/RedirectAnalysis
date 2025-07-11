import altair as alt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import streamlit as st

# 设置 Altair 主题
alt.themes.enable('default')

class EnhancedVisualization:
    """增强版可视化工具类 - 使用 Altair 进行数据可视化"""
    
    def __init__(self):
        """初始化可视化工具"""
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#8c564b'
        }
        
        self.metric_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
    
    def create_daily_trend_chart(self, df: pd.DataFrame, metric: str, 
                                title: str, color: str = '#1f77b4') -> alt.Chart:
        """
        创建每日趋势图
        
        Args:
            df (pd.DataFrame): 数据框
            metric (str): 指标名称
            title (str): 图表标题
            color (str): 线条颜色
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        # 计算数据范围，设置自适应纵轴
        min_value = df[metric].min()
        max_value = df[metric].max()
        
        # 设置纵轴范围，避免从0开始，增强趋势可读性
        if min_value != max_value:
            # 计算数据范围，设置适当的边距
            data_range = max_value - min_value
            y_min = max(0, min_value - data_range * 0.05)  # 最小不低于0
            y_max = max_value + data_range * 0.05
        else:
            # 如果数据都相同，设置一个小的范围
            y_min = max(0, min_value * 0.95)
            y_max = max_value * 1.05
        
        chart = alt.Chart(df).mark_line(
            point=True,
            color=color,
            strokeWidth=3
        ).encode(
            x=alt.X('date:T', title='日期', axis=alt.Axis(format='%Y-%m-%d')),
            y=alt.Y(f'{metric}:Q', 
                   title=metric.replace('_', ' ').title(),
                   scale=alt.Scale(domain=[y_min, y_max], zero=False)),  # 设置自适应范围，不从0开始
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip(f'{metric}:Q', title=metric.replace('_', ' ').title(), format=',.0f')
            ]
        ).properties(
            title=title,
            width='container',
            height=300
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        return chart
    
    def create_group_comparison_chart(self, df: pd.DataFrame, metric: str,
                                    title: str) -> alt.Chart:
        """
        创建分组对比条形图
        
        Args:
            df (pd.DataFrame): 数据框
            metric (str): 指标名称
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        # 按分组聚合数据
        group_data = df.groupby('group')[metric].sum().reset_index()
        group_data = group_data.sort_values(metric, ascending=True)
        
        chart = alt.Chart(group_data).mark_bar(
            color=self.color_scheme['primary']
        ).encode(
            x=alt.X(f'{metric}:Q', title=metric.replace('_', ' ').title()),
            y=alt.Y('group:N', title='分组', sort='-x'),
            tooltip=[
                alt.Tooltip('group:N', title='分组'),
                alt.Tooltip(f'{metric}:Q', title=metric.replace('_', ' ').title(), format=',.0f')
            ]
        ).properties(
            title=title,
            width='container',
            height=400
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        return chart
    
    def create_stacked_area_chart(self, df: pd.DataFrame, metric: str,
                                 title: str) -> alt.Chart:
        """
        创建堆叠面积图
        
        Args:
            df (pd.DataFrame): 数据框
            metric (str): 指标名称
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        chart = alt.Chart(df).mark_area(
            opacity=0.7
        ).encode(
            x=alt.X('date:T', title='日期', axis=alt.Axis(format='%Y-%m-%d')),
            y=alt.Y(f'{metric}:Q', title=metric.replace('_', ' ').title(), stack='zero'),
            color=alt.Color('group:N', title='分组', scale=alt.Scale(scheme='category10')),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('group:N', title='分组'),
                alt.Tooltip(f'{metric}:Q', title=metric.replace('_', ' ').title(), format=',.0f')
            ]
        ).properties(
            title=title,
            width='container',
            height=400
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        return chart
    
    def create_conversion_chart(self, df: pd.DataFrame, 
                               clicks_col: str, views_col: str,
                               title: str) -> alt.Chart:
        """
        创建转化率图表
        
        Args:
            df (pd.DataFrame): 数据框
            clicks_col (str): 点击量列名
            views_col (str): 浏览量列名
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        # 计算转化率
        df_copy = df.copy()
        df_copy['conversion_rate'] = (
            df_copy[clicks_col] / df_copy[views_col].replace(0, 1) * 100
        )
        
        chart = alt.Chart(df_copy).mark_line(
            point=True,
            color=self.color_scheme['success'],
            strokeWidth=3
        ).encode(
            x=alt.X('date:T', title='日期', axis=alt.Axis(format='%Y-%m-%d')),
            y=alt.Y('conversion_rate:Q', title='转化率 (%)'),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('conversion_rate:Q', title='转化率', format='.2f'),
                alt.Tooltip(f'{clicks_col}:Q', title='点击量', format=',.0f'),
                alt.Tooltip(f'{views_col}:Q', title='浏览量', format=',.0f')
            ]
        ).properties(
            title=title,
            width='container',
            height=300
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        return chart
    
    def create_clicks_analysis_chart(self, df: pd.DataFrame,
                                   title: str) -> alt.Chart:
        """
        创建点击量分析图表
        
        Args:
            df (pd.DataFrame): 数据框
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        chart = alt.Chart(df).mark_line(
            point=True,
            color=self.color_scheme['secondary'],
            strokeWidth=3
        ).encode(
            x=alt.X('date:T', title='日期', axis=alt.Axis(format='%Y-%m-%d')),
            y=alt.Y('clicks_count:Q', title='点击量'),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('clicks_count:Q', title='点击量', format=',.0f'),
                alt.Tooltip('clicks_growth:Q', title='增长率', format='.2f')
            ]
        ).properties(
            title=title,
            width='container',
            height=300
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        return chart
    
    def create_group_clicks_correlation(self, df: pd.DataFrame,
                                      clicks_col: str, metric_col: str,
                                      title: str) -> alt.Chart:
        """
        创建分组点击相关性散点图
        
        Args:
            df (pd.DataFrame): 数据框
            clicks_col (str): 点击量列名
            metric_col (str): 指标列名
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        chart = alt.Chart(df).mark_circle(
            size=60,
            opacity=0.7
        ).encode(
            x=alt.X(f'{clicks_col}:Q', title='点击量'),
            y=alt.Y(f'{metric_col}:Q', title=metric_col.replace('_', ' ').title()),
            color=alt.Color('group:N', title='分组', scale=alt.Scale(scheme='category10')),
            tooltip=[
                alt.Tooltip('group:N', title='分组'),
                alt.Tooltip(f'{clicks_col}:Q', title='点击量', format=',.0f'),
                alt.Tooltip(f'{metric_col}:Q', title=metric_col.replace('_', ' ').title(), format=',.0f'),
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d')
            ]
        ).properties(
            title=title,
            width='container',
            height=400
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        return chart
    
    def create_metrics_dashboard(self, daily_data: pd.DataFrame,
                               group_data: pd.DataFrame,
                               clicks_data: pd.DataFrame) -> alt.Chart:
        """
        创建综合指标仪表板
        
        Args:
            daily_data (pd.DataFrame): 每日数据
            group_data (pd.DataFrame): 分组数据
            clicks_data (pd.DataFrame): 点击数据
        
        Returns:
            alt.Chart: 组合图表
        """
        charts = []
        
        # 1. 每日趋势图
        if not daily_data.empty:
            trend_chart = self.create_daily_trend_chart(
                daily_data, 'view_count', '每日浏览量趋势'
            )
            charts.append(trend_chart)
        
        # 2. 分组对比图
        if not group_data.empty:
            group_chart = self.create_group_comparison_chart(
                group_data, 'view_count', '分组浏览量对比'
            )
            charts.append(group_chart)
        
        # 3. 点击量分析图
        if not clicks_data.empty:
            clicks_chart = self.create_clicks_analysis_chart(
                clicks_data, '每日点击量趋势'
            )
            charts.append(clicks_chart)
        
        # 组合图表
        if charts:
            combined_chart = alt.vconcat(*charts, spacing=20)
            return combined_chart
        else:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据")
    
    def create_efficiency_heatmap(self, df: pd.DataFrame,
                                 metrics: List[str],
                                 title: str) -> alt.Chart:
        """
        创建效率指标热力图
        
        Args:
            df (pd.DataFrame): 数据框
            metrics (List[str]): 指标列表
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        # 准备热力图数据
        heatmap_data = []
        for _, row in df.iterrows():
            for metric in metrics:
                heatmap_data.append({
                    'date': row['date'],
                    'metric': metric.replace('_', ' ').title(),
                    'value': row[metric]
                })
        
        heatmap_df = pd.DataFrame(heatmap_data)
        
        chart = alt.Chart(heatmap_df).mark_rect().encode(
            x=alt.X('date:T', title='日期', axis=alt.Axis(format='%Y-%m-%d')),
            y=alt.Y('metric:N', title='指标'),
            color=alt.Color('value:Q', title='数值', scale=alt.Scale(scheme='viridis')),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('metric:N', title='指标'),
                alt.Tooltip('value:Q', title='数值', format='.2f')
            ]
        ).properties(
            title=title,
            width='container',
            height=300
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        return chart
    
    def create_multi_metric_comparison(self, df: pd.DataFrame,
                                     metrics: List[str],
                                     title: str) -> alt.Chart:
        """
        创建多指标对比图
        
        Args:
            df (pd.DataFrame): 数据框
            metrics (List[str]): 指标列表
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        # 准备多指标数据
        multi_data = []
        for _, row in df.iterrows():
            for metric in metrics:
                multi_data.append({
                    'date': row['date'],
                    'metric': metric.replace('_', ' ').title(),
                    'value': row[metric]
                })
        
        multi_df = pd.DataFrame(multi_data)
        
        # 计算所有指标的数据范围，设置自适应纵轴
        all_values = multi_df['value'].dropna()
        if not all_values.empty:
            min_value = all_values.min()
            max_value = all_values.max()
            
            # 设置纵轴范围，避免从0开始，增强趋势可读性
            if min_value != max_value:
                data_range = max_value - min_value
                y_min = max(0, min_value - data_range * 0.05)  # 最小不低于0
                y_max = max_value + data_range * 0.05
            else:
                y_min = max(0, min_value * 0.95)
                y_max = max_value * 1.05
        else:
            y_min = 0
            y_max = 100
        
        chart = alt.Chart(multi_df).mark_line(
            point=True,
            strokeWidth=2
        ).encode(
            x=alt.X('date:T', title='日期', axis=alt.Axis(format='%Y-%m-%d')),
            y=alt.Y('value:Q', 
                   title='数值',
                   scale=alt.Scale(domain=[y_min, y_max], zero=False)),  # 设置自适应范围，不从0开始
            color=alt.Color('metric:N', title='指标', scale=alt.Scale(scheme='category10')),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('metric:N', title='指标'),
                alt.Tooltip('value:Q', title='数值', format=',.0f')
            ]
        ).properties(
            title=title,
            width='container',
            height=400
        ).configure_axis(
            gridColor='#f0f0f0'
        ).configure_view(
            strokeWidth=0
        )
        
        return chart
    
    def create_summary_cards(self, summary_data: Dict) -> str:
        """
        创建摘要卡片 HTML
        
        Args:
            summary_data (Dict): 摘要数据
        
        Returns:
            str: HTML 字符串
        """
        html = "<div style='display: flex; justify-content: space-between; margin-bottom: 20px;'>"
        
        # 数据概览区域 - 第一行
        if 'total_records' in summary_data:
            yesterday_info = ""
            if 'yesterday_comparison' in summary_data and 'total_records' in summary_data['yesterday_comparison']:
                comp = summary_data['yesterday_comparison']['total_records']
                diff = comp['diff']
                pct = comp['pct']
                if diff > 0:
                    yesterday_info = f"<div style='font-size: 12px; color: #28a745;'>🔺 较昨日 +{diff:,} ({pct:+.1f}%)</div>"
                elif diff < 0:
                    yesterday_info = f"<div style='font-size: 12px; color: #dc3545;'>🔻 较昨日 {diff:,} ({pct:+.1f}%)</div>"
                else:
                    yesterday_info = f"<div style='font-size: 12px; color: #6c757d;'>➖ 较昨日 0 (0.0%)</div>"
            
            html += (
                "<div style='background-color: #f0f2f6; padding: 15px; border-radius: 8px; flex: 1; margin: 0 5px; text-align: center; display: inline-block;'>"
                "<h3 style='margin: 0; color: #1f77b4;'>总记录数</h3>"
                f"<p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{summary_data['total_records']:,}</p>"
                f"{yesterday_info}"
                "</div>"
            )
        
        if 'unique_accounts' in summary_data:
            yesterday_info = ""
            if 'yesterday_comparison' in summary_data and 'unique_accounts' in summary_data['yesterday_comparison']:
                comp = summary_data['yesterday_comparison']['unique_accounts']
                diff = comp['diff']
                pct = comp['pct']
                if diff > 0:
                    yesterday_info = f"<div style='font-size: 12px; color: #28a745;'>🔺 较昨日 +{diff:,} ({pct:+.1f}%)</div>"
                elif diff < 0:
                    yesterday_info = f"<div style='font-size: 12px; color: #dc3545;'>🔻 较昨日 {diff:,} ({pct:+.1f}%)</div>"
                else:
                    yesterday_info = f"<div style='font-size: 12px; color: #6c757d;'>➖ 较昨日 0 (0.0%)</div>"
            
            html += (
                "<div style='background-color: #f0f2f6; padding: 15px; border-radius: 8px; flex: 1; margin: 0 5px; text-align: center; display: inline-block;'>"
                "<h3 style='margin: 0; color: #ff7f0e;'>账号数量</h3>"
                f"<p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{summary_data['unique_accounts']:,}</p>"
                f"{yesterday_info}"
                "</div>"
            )
        
        if 'total_views' in summary_data:
            yesterday_info = ""
            if 'yesterday_comparison' in summary_data and 'total_views' in summary_data['yesterday_comparison']:
                comp = summary_data['yesterday_comparison']['total_views']
                diff = comp['diff']
                pct = comp['pct']
                if diff > 0:
                    yesterday_info = f"<div style='font-size: 12px; color: #28a745;'>🔺 较昨日 +{diff:,} ({pct:+.1f}%)</div>"
                elif diff < 0:
                    yesterday_info = f"<div style='font-size: 12px; color: #dc3545;'>🔻 较昨日 {diff:,} ({pct:+.1f}%)</div>"
                else:
                    yesterday_info = f"<div style='font-size: 12px; color: #6c757d;'>➖ 较昨日 0 (0.0%)</div>"
            
            html += (
                "<div style='background-color: #f0f2f6; padding: 15px; border-radius: 8px; flex: 1; margin: 0 5px; text-align: center; display: inline-block;'>"
                "<h3 style='margin: 0; color: #2ca02c;'>总浏览量</h3>"
                f"<p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{summary_data['total_views']:,}</p>"
                f"{yesterday_info}"
                "</div>"
            )
        
        if 'clicks_data' in summary_data and 'total_clicks' in summary_data['clicks_data']:
            yesterday_info = ""
            if 'yesterday_comparison' in summary_data and 'total_clicks' in summary_data['yesterday_comparison']:
                comp = summary_data['yesterday_comparison']['total_clicks']
                diff = comp['diff']
                pct = comp['pct']
                if diff > 0:
                    yesterday_info = f"<div style='font-size: 12px; color: #28a745;'>🔺 较昨日 +{diff:,} ({pct:+.1f}%)</div>"
                elif diff < 0:
                    yesterday_info = f"<div style='font-size: 12px; color: #dc3545;'>🔻 较昨日 {diff:,} ({pct:+.1f}%)</div>"
                else:
                    yesterday_info = f"<div style='font-size: 12px; color: #6c757d;'>➖ 较昨日 0 (0.0%)</div>"
            
            html += (
                "<div style='background-color: #f0f2f6; padding: 15px; border-radius: 8px; flex: 1; margin: 0 5px; text-align: center; display: inline-block;'>"
                "<h3 style='margin: 0; color: #d62728;'>总点击量</h3>"
                f"<p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{summary_data['clicks_data']['total_clicks']:,}</p>"
                f"{yesterday_info}"
                "</div>"
            )
        
        html += "</div>"
        
        # 每日增量指标区域 - 第二行
        if 'latest_day_increments' in summary_data:
            increments = summary_data['latest_day_increments']
            target_date = increments.get('target_date', '最新日期')
            
            html += f"<div style='margin-bottom: 20px;'><h4 style='color: #333; margin-bottom: 10px;'>📈 {target_date} 每日增量指标</h4>"
            html += "<div style='display: flex; justify-content: space-between; flex-wrap: nowrap;'>"
            
            # 新增观看量
            if 'view_increment' in increments:
                yesterday_info = ""
                if 'yesterday_comparison' in summary_data and 'view_count_inc_increment' in summary_data['yesterday_comparison']:
                    comp = summary_data['yesterday_comparison']['view_count_inc_increment']
                    diff = comp['diff']
                    pct = comp['pct']
                    if diff > 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #28a745;'>📈 较昨日 +{diff:,}</div>"
                    elif diff < 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #dc3545;'>📉 较昨日 {diff:,}</div>"
                    else:
                        yesterday_info = f"<div style='font-size: 11px; color: #6c757d;'>➖ 较昨日 0</div>"
                
                html += (
                    "<div style='background-color: #f0f2f6; padding: 12px; border-radius: 8px; flex: 1; margin: 0 3px; text-align: center; display: inline-block; min-width: 120px;'>"
                    "<h3 style='margin: 0; color: #1f77b4; font-size: 13px;'>新增观看量</h3>"
                    f"<p style='font-size: 18px; font-weight: bold; margin: 5px 0;'>{increments['view_increment']:,}</p>"
                    f"{yesterday_info}"
                    "</div>"
                )
            
            # 新增发帖量
            if 'post_increment' in increments:
                yesterday_info = ""
                if 'yesterday_comparison' in summary_data and 'post_count_inc_increment' in summary_data['yesterday_comparison']:
                    comp = summary_data['yesterday_comparison']['post_count_inc_increment']
                    diff = comp['diff']
                    pct = comp['pct']
                    if diff > 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #28a745;'>📈 较昨日 +{diff:,}</div>"
                    elif diff < 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #dc3545;'>📉 较昨日 {diff:,}</div>"
                    else:
                        yesterday_info = f"<div style='font-size: 11px; color: #6c757d;'>➖ 较昨日 0</div>"
                
                html += (
                    "<div style='background-color: #f0f2f6; padding: 12px; border-radius: 8px; flex: 1; margin: 0 3px; text-align: center; display: inline-block; min-width: 120px;'>"
                    "<h3 style='margin: 0; color: #ff7f0e; font-size: 13px;'>新增发帖量</h3>"
                    f"<p style='font-size: 18px; font-weight: bold; margin: 5px 0;'>{increments['post_increment']:,}</p>"
                    f"{yesterday_info}"
                    "</div>"
                )
            
            # 新增点赞数
            if 'like_increment' in increments:
                yesterday_info = ""
                if 'yesterday_comparison' in summary_data and 'like_count_inc_increment' in summary_data['yesterday_comparison']:
                    comp = summary_data['yesterday_comparison']['like_count_inc_increment']
                    diff = comp['diff']
                    pct = comp['pct']
                    if diff > 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #28a745;'>📈 较昨日 +{diff:,}</div>"
                    elif diff < 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #dc3545;'>📉 较昨日 {diff:,}</div>"
                    else:
                        yesterday_info = f"<div style='font-size: 11px; color: #6c757d;'>➖ 较昨日 0</div>"
                
                html += (
                    "<div style='background-color: #f0f2f6; padding: 12px; border-radius: 8px; flex: 1; margin: 0 3px; text-align: center; display: inline-block; min-width: 120px;'>"
                    "<h3 style='margin: 0; color: #2ca02c; font-size: 13px;'>新增点赞数</h3>"
                    f"<p style='font-size: 18px; font-weight: bold; margin: 5px 0;'>{increments['like_increment']:,}</p>"
                    f"{yesterday_info}"
                    "</div>"
                )
            
            # 新增评论数
            if 'comment_increment' in increments:
                yesterday_info = ""
                if 'yesterday_comparison' in summary_data and 'comment_count_inc_increment' in summary_data['yesterday_comparison']:
                    comp = summary_data['yesterday_comparison']['comment_count_inc_increment']
                    diff = comp['diff']
                    pct = comp['pct']
                    if diff > 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #28a745;'>📈 较昨日 +{diff:,}</div>"
                    elif diff < 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #dc3545;'>📉 较昨日 {diff:,}</div>"
                    else:
                        yesterday_info = f"<div style='font-size: 11px; color: #6c757d;'>➖ 较昨日 0</div>"
                
                html += (
                    "<div style='background-color: #f0f2f6; padding: 12px; border-radius: 8px; flex: 1; margin: 0 3px; text-align: center; display: inline-block; min-width: 120px;'>"
                    "<h3 style='margin: 0; color: #d62728; font-size: 13px;'>新增评论数</h3>"
                    f"<p style='font-size: 18px; font-weight: bold; margin: 5px 0;'>{increments['comment_increment']:,}</p>"
                    f"{yesterday_info}"
                    "</div>"
                )
            
            # 新增分享数
            if 'share_increment' in increments:
                yesterday_info = ""
                if 'yesterday_comparison' in summary_data and 'share_count_inc_increment' in summary_data['yesterday_comparison']:
                    comp = summary_data['yesterday_comparison']['share_count_inc_increment']
                    diff = comp['diff']
                    pct = comp['pct']
                    if diff > 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #28a745;'>📈 较昨日 +{diff:,}</div>"
                    elif diff < 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #dc3545;'>📉 较昨日 {diff:,}</div>"
                    else:
                        yesterday_info = f"<div style='font-size: 11px; color: #6c757d;'>➖ 较昨日 0</div>"
                
                html += (
                    "<div style='background-color: #f0f2f6; padding: 12px; border-radius: 8px; flex: 1; margin: 0 3px; text-align: center; display: inline-block; min-width: 120px;'>"
                    "<h3 style='margin: 0; color: #9467bd; font-size: 13px;'>新增分享数</h3>"
                    f"<p style='font-size: 18px; font-weight: bold; margin: 5px 0;'>{increments['share_increment']:,}</p>"
                    f"{yesterday_info}"
                    "</div>"
                )
            
            # 新增点击数
            if 'click_increment' in increments:
                yesterday_info = ""
                if 'yesterday_comparison' in summary_data and 'total_clicks' in summary_data['yesterday_comparison']:
                    comp = summary_data['yesterday_comparison']['total_clicks']
                    diff = comp['diff']
                    pct = comp['pct']
                    if diff > 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #28a745;'>📈 较昨日 +{diff:,}</div>"
                    elif diff < 0:
                        yesterday_info = f"<div style='font-size: 11px; color: #dc3545;'>📉 较昨日 {diff:,}</div>"
                    else:
                        yesterday_info = f"<div style='font-size: 11px; color: #6c757d;'>➖ 较昨日 0</div>"
                
                html += (
                    "<div style='background-color: #f0f2f6; padding: 12px; border-radius: 8px; flex: 1; margin: 0 3px; text-align: center; display: inline-block; min-width: 120px;'>"
                    "<h3 style='margin: 0; color: #8c564b; font-size: 13px;'>新增点击数</h3>"
                    f"<p style='font-size: 18px; font-weight: bold; margin: 5px 0;'>{increments['click_increment']:,}</p>"
                    f"{yesterday_info}"
                    "</div>"
                )
            
            html += "</div></div>"
        
        return html.replace('\n', '') 