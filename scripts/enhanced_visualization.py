import altair as alt
import pandas as pd
import numpy as np
from typing import List, Dict, Union
import streamlit as st

# 设置 Altair 主题
alt.themes.enable('default')

class EnhancedVisualization:
    """
    增强的可视化工具类
    """
    
    def __init__(self):
        pass
    
    def create_daily_trend_chart(self, df: pd.DataFrame, metric: str, 
                                title: str, color: str = '#1f77b4') -> alt.Chart:
        """
        创建每日趋势图
        
        Args:
            df (pd.DataFrame): 数据框
            metric (str): 指标列名
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
            data_range = max_value - min_value
            y_min = max(0, min_value - data_range * 0.05)  # 最小不低于0
            y_max = max_value + data_range * 0.05
        else:
            y_min = max(0, min_value * 0.95)
            y_max = max_value * 1.05
        
        chart = alt.Chart(df).mark_line(point=True, color=color).encode(
            x=alt.X('date:T', title='日期'),
            y=alt.Y(f'{metric}:Q',
                   title=f'每日{metric.replace("_", " ").title()}',
                   scale=alt.Scale(domain=[y_min, y_max], zero=False)),  # 设置自适应范围，不从0开始
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip(f'{metric}:Q', title=metric.replace("_", " ").title(), format=',.0f')
            ]
        ).properties(
            title=title,
            height=300
        )
        return chart
    
    def create_group_comparison_chart(self, df: pd.DataFrame, metric: str,
                                    title: str) -> alt.Chart:
        """
        创建分组对比图
        
        Args:
            df (pd.DataFrame): 数据框
            metric (str): 指标列名
            title (str): 图表标题
        
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
            data_range = max_value - min_value
            y_min = max(0, min_value - data_range * 0.05)  # 最小不低于0
            y_max = max_value + data_range * 0.05
        else:
            y_min = max(0, min_value * 0.95)
            y_max = max_value * 1.05
        
        chart = alt.Chart(df).mark_line(point=True).encode(
            x=alt.X('date:T', title='日期'),
            y=alt.Y(f'{metric}:Q',
                   title=f'每日{metric.replace("_", " ").title()}',
                   scale=alt.Scale(domain=[y_min, y_max], zero=False)),  # 设置自适应范围，不从0开始
            color=alt.Color('group:N', title='分组'),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('group:N', title='分组'),
                alt.Tooltip(f'{metric}:Q', title=metric.replace("_", " ").title(), format=',.0f')
            ]
        ).properties(
            title=title,
            height=300
        )
        return chart
    
    def create_stacked_area_chart(self, df: pd.DataFrame, metric: str,
                                 title: str) -> alt.Chart:
        """
        创建堆叠面积图
        
        Args:
            df (pd.DataFrame): 数据框
            metric (str): 指标列名
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        chart = alt.Chart(df).mark_area().encode(
            x=alt.X('date:T', title='日期'),
            y=alt.Y(f'{metric}:Q', title=f'累计{metric.replace("_", " ").title()}'),
            color=alt.Color('group:N', title='分组'),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('group:N', title='分组'),
                alt.Tooltip(f'{metric}:Q', title=metric.replace("_", " ").title(), format=',.0f')
            ]
        ).properties(
            title=title,
            height=300
        )
        return chart
    
    def create_conversion_chart(self, df: pd.DataFrame, 
                               clicks_col: str, views_col: str,
                               title: str) -> alt.Chart:
        """
        创建转化率图表
        
        Args:
            df (pd.DataFrame): 数据框
            clicks_col (str): 点击数列名
            views_col (str): 浏览数列名
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        # 计算转化率
        df_copy = df.copy()
        df_copy['conversion_rate'] = (df_copy[clicks_col] / df_copy[views_col] * 100).fillna(0)
        
        chart = alt.Chart(df_copy).mark_line(point=True, color='#d62728').encode(
            x=alt.X('date:T', title='日期'),
            y=alt.Y('conversion_rate:Q', title='转化率 (%)'),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('conversion_rate:Q', title='转化率', format='.2f'),
                alt.Tooltip(f'{clicks_col}:Q', title='点击量', format=',.0f'),
                alt.Tooltip(f'{views_col}:Q', title='浏览量', format=',.0f')
            ]
        ).properties(
            title=title,
            height=300
        )
        return chart
    
    def create_clicks_analysis_chart(self, df: pd.DataFrame,
                                   title: str) -> alt.Chart:
        """
        创建点击分析图表
        
        Args:
            df (pd.DataFrame): 数据框
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        # 准备数据
        chart_data = df[['date', 'daily_clicks', 'daily_visitors']].copy()
        chart_data = chart_data.melt(
            id_vars=['date'],
            value_vars=['daily_clicks', 'daily_visitors'],
            var_name='type',
            value_name='value'
        )
        chart_data['type'] = chart_data['type'].map({
            'daily_clicks': '点击量(PV)',
            'daily_visitors': '访客数(UV)'
        })
        
        chart = alt.Chart(chart_data).mark_line(point=True).encode(
            x=alt.X('date:T', title='日期'),
            y=alt.Y('value:Q', title='数值'),
            color=alt.Color('type:N', title='类型'),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('type:N', title='类型'),
                alt.Tooltip('value:Q', title='数值', format=',.0f')
            ]
        ).properties(
            title=title,
            height=300
        )
        return chart
    
    def create_group_clicks_correlation(self, df: pd.DataFrame,
                                      clicks_col: str, metric_col: str,
                                      title: str) -> alt.Chart:
        """
        创建分组点击相关性图表
        
        Args:
            df (pd.DataFrame): 数据框
            clicks_col (str): 点击数列名
            metric_col (str): 指标列名
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        chart = alt.Chart(df).mark_circle(size=60).encode(
            x=alt.X(f'{clicks_col}:Q', title='点击量'),
            y=alt.Y(f'{metric_col}:Q', title=metric_col.replace('_', ' ').title()),
            color=alt.Color('group:N', title='分组'),
            tooltip=[
                alt.Tooltip('group:N', title='分组'),
                alt.Tooltip(f'{clicks_col}:Q', title='点击量', format=',.0f'),
                alt.Tooltip(f'{metric_col}:Q', title=metric_col.replace('_', ' ').title(), format=',.0f')
            ]
        ).properties(
            title=title,
            height=300
        )
        return chart
    
    def create_metrics_dashboard(self, daily_data: pd.DataFrame,
                               group_data: pd.DataFrame,
                               clicks_data: pd.DataFrame) -> alt.Chart:
        """
        创建指标仪表板
        
        Args:
            daily_data (pd.DataFrame): 每日数据
            group_data (pd.DataFrame): 分组数据
            clicks_data (pd.DataFrame): 点击数据
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        # 这里可以创建复杂的仪表板布局
        # 暂时返回一个简单的图表
        if not daily_data.empty:
            return self.create_daily_trend_chart(daily_data, 'view_count', '指标仪表板')
        else:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title="指标仪表板")
    
    def create_efficiency_heatmap(self, df: pd.DataFrame,
                                 metrics: List[str],
                                 title: str) -> alt.Chart:
        """
        创建效率热力图
        
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
            x=alt.X('date:T', title='日期'),
            y=alt.Y('metric:N', title='指标'),
            color=alt.Color('value:Q', title='数值', scale=alt.Scale(scheme='viridis')),
            tooltip=[
                alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                alt.Tooltip('metric:N', title='指标'),
                alt.Tooltip('value:Q', title='数值', format=',.0f')
            ]
        ).properties(
            title=title,
            height=300
        )
        return chart
    
    def create_multi_metric_comparison(self, df: pd.DataFrame,
                                     metrics: List[str],
                                     title: str) -> Union[alt.Chart, alt.VConcatChart]:
        """
        创建多指标对比图 - 将浏览量和其他指标分开展示
        
        Args:
            df (pd.DataFrame): 数据框
            metrics (List[str]): 指标列表
            title (str): 图表标题
        
        Returns:
            alt.Chart: Altair 图表对象
        """
        if df.empty:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
        
        # 分离浏览量和其他指标
        view_metrics = [m for m in metrics if 'view' in m.lower()]
        other_metrics = [m for m in metrics if 'view' not in m.lower()]
        
        # 创建浏览量图表
        if view_metrics:
            view_data = []
            for _, row in df.iterrows():
                for metric in view_metrics:
                    view_data.append({
                        'date': row['date'],
                        'metric': metric.replace('_', ' ').title(),
                        'value': row[metric]
                    })
            
            view_df = pd.DataFrame(view_data)
            
            # 计算浏览量数据范围
            view_values = view_df['value'].dropna()
            if not view_values.empty:
                min_value = view_values.min()
                max_value = view_values.max()
                if min_value != max_value:
                    data_range = max_value - min_value
                    y_min = max(0, min_value - data_range * 0.05)
                    y_max = max_value + data_range * 0.05
                else:
                    y_min = max(0, min_value * 0.95)
                    y_max = max_value * 1.05
            else:
                y_min = 0
                y_max = 100
            
            view_chart = alt.Chart(view_df).mark_line(
                point=True,
                strokeWidth=2
            ).encode(
                x=alt.X('date:T', title='日期', axis=alt.Axis(format='%Y-%m-%d')),
                y=alt.Y('value:Q', 
                       title='浏览量',
                       scale=alt.Scale(domain=[y_min, y_max], zero=False)),
                color=alt.Color('metric:N', title='指标', scale=alt.Scale(scheme='category10')),
                tooltip=[
                    alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                    alt.Tooltip('metric:N', title='指标'),
                    alt.Tooltip('value:Q', title='数值', format=',.0f')
                ]
            ).properties(
                title=f"{title} - 浏览量指标",
                width='container',
                height=300
            )
        else:
            view_chart = None
        
        # 创建其他指标图表
        if other_metrics:
            other_data = []
            for _, row in df.iterrows():
                for metric in other_metrics:
                    other_data.append({
                        'date': row['date'],
                        'metric': metric.replace('_', ' ').title(),
                        'value': row[metric]
                    })
            
            other_df = pd.DataFrame(other_data)
            
            # 计算其他指标数据范围
            other_values = other_df['value'].dropna()
            if not other_values.empty:
                min_value = other_values.min()
                max_value = other_values.max()
                if min_value != max_value:
                    data_range = max_value - min_value
                    y_min = max(0, min_value - data_range * 0.05)
                    y_max = max_value + data_range * 0.05
                else:
                    y_min = max(0, min_value * 0.95)
                    y_max = max_value * 1.05
            else:
                y_min = 0
                y_max = 100
            
            other_chart = alt.Chart(other_df).mark_line(
                point=True,
                strokeWidth=2
            ).encode(
                x=alt.X('date:T', title='日期', axis=alt.Axis(format='%Y-%m-%d')),
                y=alt.Y('value:Q', 
                       title='其他指标数值',
                       scale=alt.Scale(domain=[y_min, y_max], zero=False)),
                color=alt.Color('metric:N', title='指标', scale=alt.Scale(scheme='category10')),
                tooltip=[
                    alt.Tooltip('date:T', title='日期', format='%Y-%m-%d'),
                    alt.Tooltip('metric:N', title='指标'),
                    alt.Tooltip('value:Q', title='数值', format=',.0f')
                ]
            ).properties(
                title=f"{title} - 互动指标（点赞、评论、分享）",
                width='container',
                height=300
            )
        else:
            other_chart = None
        
        # 如果两个图表都存在，垂直组合
        if view_chart and other_chart:
            combined_chart = alt.vconcat(view_chart, other_chart, spacing=20).configure_axis(
                gridColor='#f0f0f0'
            ).configure_view(
                strokeWidth=0
            )
            return combined_chart
        elif view_chart:
            return view_chart.configure_axis(
                gridColor='#f0f0f0'
            ).configure_view(
                strokeWidth=0
            )
        elif other_chart:
            return other_chart.configure_axis(
                gridColor='#f0f0f0'
            ).configure_view(
                strokeWidth=0
            )
        else:
            return alt.Chart(pd.DataFrame()).mark_text(text="无数据").properties(title=title)
    
    def create_summary_cards(self, summary_data: Dict) -> str:
        """
        创建摘要卡片 HTML
        
        Args:
            summary_data (Dict): 摘要数据
        
        Returns:
            str: HTML 字符串
        """
        html = "<div style='display: flex; justify-content: space-between; margin-bottom: 20px;'>"
        
        # 数据概览区域 - 四个指标：账号数量、总浏览量、总发帖数、总点击数
        
        # 1. 账号数量
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
                "<h3 style='margin: 0; color: #1f77b4;'>账号数量</h3>"
                f"<p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{summary_data['unique_accounts']:,}</p>"
                f"{yesterday_info}"
                "</div>"
            )
        
        # 2. 总浏览量
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
                "<h3 style='margin: 0; color: #ff7f0e;'>总浏览量</h3>"
                f"<p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{summary_data['total_views']:,}</p>"
                f"{yesterday_info}"
                "</div>"
            )
        
        # 3. 总发帖数
        if 'total_posts' in summary_data:
            yesterday_info = ""
            if 'yesterday_comparison' in summary_data and 'total_posts' in summary_data['yesterday_comparison']:
                comp = summary_data['yesterday_comparison']['total_posts']
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
                "<h3 style='margin: 0; color: #2ca02c;'>总发帖数</h3>"
                f"<p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{summary_data['total_posts']:,}</p>"
                f"{yesterday_info}"
                "</div>"
            )
        
        # 4. 总点击数
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
                "<h3 style='margin: 0; color: #d62728;'>总点击数</h3>"
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