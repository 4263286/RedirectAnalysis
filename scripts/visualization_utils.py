"""
可视化工具模块
封装可复用的绘图逻辑
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def plot_diff_metrics_trend(data, metrics=None, title="Daily Metrics Trend", height=500):
    """
    绘制 _diff 指标趋势图
    
    Args:
        data (pd.DataFrame): 包含 date 和 _diff 指标的数据
        metrics (list): 要绘制的指标列表，如果为 None 则绘制所有 _diff 指标
        title (str): 图表标题
        height (int): 图表高度
    
    Returns:
        plotly.graph_objects.Figure: 趋势图
    """
    if data is None or data.empty:
        return None
    
    # 如果没有指定指标，则使用所有 _diff 指标
    if metrics is None:
        metrics = [col for col in data.columns if col.endswith('_diff')]
    
    # 确保数据包含必要的列
    required_cols = ['date'] + metrics
    if not all(col in data.columns for col in required_cols):
        st.error(f"数据缺少必要的列: {required_cols}")
        return None
    
    # 创建子图
    fig = make_subplots(
        rows=len(metrics), cols=1,
        subplot_titles=metrics,
        vertical_spacing=0.1,
        shared_xaxes=True
    )
    
    colors = px.colors.qualitative.Set3[:len(metrics)]
    
    for i, metric in enumerate(metrics):
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=data[metric],
                mode='lines+markers',
                name=metric,
                line=dict(color=colors[i]),
                showlegend=True
            ),
            row=i+1, col=1
        )
    
    fig.update_layout(
        title=title,
        height=height,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def plot_correlation_scatter(data, x_col, y_col, title="Correlation Analysis", height=500):
    """
    绘制相关性散点图
    
    Args:
        data (pd.DataFrame): 数据
        x_col (str): X 轴列名
        y_col (str): Y 轴列名
        title (str): 图表标题
        height (int): 图表高度
    
    Returns:
        plotly.graph_objects.Figure: 散点图
    """
    if data is None or data.empty:
        return None
    
    if x_col not in data.columns or y_col not in data.columns:
        st.error(f"数据缺少必要的列: {x_col}, {y_col}")
        return None
    
    # 计算相关系数
    correlation = data[x_col].corr(data[y_col])
    
    fig = px.scatter(
        data, x=x_col, y=y_col,
        title=f"{title} (Correlation: {correlation:.3f})",
        height=height
    )
    
    # 手动添加趋势线
    if len(data) > 1:
        z = np.polyfit(data[x_col], data[y_col], 1)
        p = np.poly1d(z)
        fig.add_trace(
            go.Scatter(
                x=data[x_col],
                y=p(data[x_col]),
                mode='lines',
                name='Trend Line',
                line=dict(color='red', dash='dash')
            )
        )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    
    return fig

def plot_comparison_line(data, x_col, y1_col, y2_col, title="Comparison Analysis", height=500):
    """
    绘制双线对比图
    
    Args:
        data (pd.DataFrame): 数据
        x_col (str): X 轴列名
        y1_col (str): 第一条线列名
        y2_col (str): 第二条线列名
        title (str): 图表标题
        height (int): 图表高度
    
    Returns:
        plotly.graph_objects.Figure: 对比图
    """
    if data is None or data.empty:
        return None
    
    required_cols = [x_col, y1_col, y2_col]
    if not all(col in data.columns for col in required_cols):
        st.error(f"数据缺少必要的列: {required_cols}")
        return None
    
    fig = go.Figure()
    
    # 添加第一条线
    fig.add_trace(
        go.Scatter(
            x=data[x_col],
            y=data[y1_col],
            mode='lines+markers',
            name=y1_col,
            line=dict(color='blue')
        )
    )
    
    # 添加第二条线
    fig.add_trace(
        go.Scatter(
            x=data[x_col],
            y=data[y2_col],
            mode='lines+markers',
            name=y2_col,
            line=dict(color='red'),
            yaxis='y2'
        )
    )
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis=dict(title=x_col),
        yaxis=dict(title=y1_col, side='left'),
        yaxis2=dict(title=y2_col, side='right', overlaying='y'),
        hovermode='x unified'
    )
    
    return fig

def plot_account_history(data, user_id, metrics=None, title=None, height=500):
    """
    绘制账号历史表现图
    
    Args:
        data (pd.DataFrame): 账号历史数据
        user_id (str): 账号ID
        metrics (list): 要绘制的指标列表
        title (str): 图表标题
        height (int): 图表高度
    
    Returns:
        plotly.graph_objects.Figure: 历史表现图
    """
    if data is None or data.empty:
        return None
    
    if metrics is None:
        metrics = ['view_diff', 'like_diff', 'comment_diff', 'share_diff']
    
    # 确保数据包含必要的列
    required_cols = ['date'] + metrics
    if not all(col in data.columns for col in required_cols):
        st.error(f"数据缺少必要的列: {required_cols}")
        return None
    
    if title is None:
        title = f"Account History: {user_id}"
    
    fig = make_subplots(
        rows=len(metrics), cols=1,
        subplot_titles=metrics,
        vertical_spacing=0.1,
        shared_xaxes=True
    )
    
    colors = px.colors.qualitative.Set3[:len(metrics)]
    
    for i, metric in enumerate(metrics):
        fig.add_trace(
            go.Scatter(
                x=data['date'],
                y=data[metric],
                mode='lines+markers',
                name=metric,
                line=dict(color=colors[i]),
                showlegend=True
            ),
            row=i+1, col=1
        )
    
    fig.update_layout(
        title=title,
        height=height,
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def plot_group_performance_table(data, title="Group Performance Summary"):
    """
    绘制分组表现表格
    
    Args:
        data (pd.DataFrame): 分组数据
        title (str): 表格标题
    
    Returns:
        plotly.graph_objects.Figure: 表格图
    """
    if data is None or data.empty:
        return None
    
    # 选择要显示的列
    display_cols = ['group']
    diff_cols = [col for col in data.columns if col.endswith('_diff')]
    display_cols.extend(diff_cols)
    
    display_data = data[display_cols].copy()
    
    # 格式化数值
    for col in diff_cols:
        if col in display_data.columns:
            display_data[col] = display_data[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=display_cols,
            fill_color='lightblue',
            align='left',
            font=dict(size=12)
        ),
        cells=dict(
            values=[display_data[col] for col in display_cols],
            fill_color='lavender',
            align='left',
            font=dict(size=11)
        )
    )])
    
    fig.update_layout(
        title=title,
        height=400
    )
    
    return fig

def plot_top_accounts_ranking(data, title="Top Accounts Ranking", height=500):
    """
    绘制账号排名图
    
    Args:
        data (pd.DataFrame): 排名数据
        title (str): 图表标题
        height (int): 图表高度
    
    Returns:
        plotly.graph_objects.Figure: 排名图
    """
    if data is None or data.empty:
        return None
    
    # 确保数据包含必要的列
    required_cols = ['user_id', 'group', 'view_diff']
    if not all(col in data.columns for col in required_cols):
        st.error(f"数据缺少必要的列: {required_cols}")
        return None
    
    # 创建排名
    data_sorted = data.sort_values('view_diff', ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            y=data_sorted['user_id'],
            x=data_sorted['view_diff'],
            orientation='h',
            text=data_sorted['view_diff'].apply(lambda x: f"{x:,.0f}"),
            textposition='auto',
            marker_color='lightblue'
        )
    )
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="View Difference",
        yaxis_title="User ID",
        showlegend=False
    )
    
    return fig

def create_metric_summary_card(metric_name, value, change=None, change_type="neutral"):
    """
    创建指标摘要卡片
    
    Args:
        metric_name (str): 指标名称
        value: 指标值
        change: 变化值
        change_type (str): 变化类型 ("positive", "negative", "neutral")
    
    Returns:
        str: HTML 格式的卡片
    """
    # 格式化数值
    if isinstance(value, (int, float)):
        formatted_value = f"{value:,.0f}"
    else:
        formatted_value = str(value)
    
    # 格式化变化值
    if change is not None:
        if isinstance(change, (int, float)):
            formatted_change = f"{change:+,.0f}"
        else:
            formatted_change = str(change)
        
        # 确定变化颜色
        if change_type == "positive":
            change_color = "green"
            change_icon = "↗"
        elif change_type == "negative":
            change_color = "red"
            change_icon = "↘"
        else:
            change_color = "gray"
            change_icon = "→"
        
        change_html = f'<span style="color: {change_color};">{change_icon} {formatted_change}</span>'
    else:
        change_html = ""
    
    html = f"""
    <div style="
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    ">
        <div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">
            {metric_name}
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: #333;">
            {formatted_value}
        </div>
        <div style="font-size: 0.8rem; margin-top: 0.25rem;">
            {change_html}
        </div>
    </div>
    """
    
    return html

def plot_cvr_analysis(data, title="Click Conversion Rate (CVR) Analysis", height=500):
    """
    绘制点击转化率分析图
    
    Args:
        data (pd.DataFrame): CVR 数据
        title (str): 图表标题
        height (int): 图表高度
    
    Returns:
        plotly.graph_objects.Figure: CVR 分析图
    """
    if data is None or data.empty:
        return None
    
    # 确保数据包含必要的列
    required_cols = ['group', 'cvr', 'click_count', 'view_diff']
    if not all(col in data.columns for col in required_cols):
        st.error(f"数据缺少必要的列: {required_cols}")
        return None
    
    fig = go.Figure()
    
    # 添加 CVR 柱状图
    fig.add_trace(
        go.Bar(
            x=data['group'],
            y=data['cvr'],
            name='CVR (%)',
            text=data['cvr'].apply(lambda x: f"{x:.2f}%"),
            textposition='auto',
            marker_color='lightcoral'
        )
    )
    
    # 添加点击量线图（双轴）
    fig.add_trace(
        go.Scatter(
            x=data['group'],
            y=data['click_count'],
            name='Click Count',
            yaxis='y2',
            line=dict(color='blue'),
            mode='lines+markers'
        )
    )
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="Group",
        yaxis=dict(title="CVR (%)", side='left'),
        yaxis2=dict(title="Click Count", side='right', overlaying='y'),
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def plot_efficiency_distribution(data, title="Efficiency Distribution by Group", height=500):
    """
    绘制效率分布图
    
    Args:
        data (pd.DataFrame): 效率分布数据
        title (str): 图表标题
        height (int): 图表高度
    
    Returns:
        plotly.graph_objects.Figure: 效率分布图
    """
    if data is None or data.empty:
        return None
    
    # 确保数据包含必要的列
    required_cols = ['group', 'mean_efficiency', 'median_efficiency', 'account_count']
    if not all(col in data.columns for col in required_cols):
        st.error(f"数据缺少必要的列: {required_cols}")
        return None
    
    fig = go.Figure()
    
    # 添加平均效率柱状图
    fig.add_trace(
        go.Bar(
            x=data['group'],
            y=data['mean_efficiency'],
            name='Mean Efficiency',
            text=data['mean_efficiency'].apply(lambda x: f"{x:,.0f}"),
            textposition='auto',
            marker_color='lightblue'
        )
    )
    
    # 添加中位数效率线
    fig.add_trace(
        go.Scatter(
            x=data['group'],
            y=data['median_efficiency'],
            name='Median Efficiency',
            line=dict(color='red', dash='dash'),
            mode='lines+markers'
        )
    )
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="Group",
        yaxis_title="Efficiency",
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def plot_interaction_growth_comparison(data, title="Interaction Growth Comparison", height=500):
    """
    绘制互动增长对比图
    
    Args:
        data (pd.DataFrame): 互动增长数据
        title (str): 图表标题
        height (int): 图表高度
    
    Returns:
        plotly.graph_objects.Figure: 互动增长对比图
    """
    if data is None or data.empty:
        return None
    
    # 确保数据包含必要的列
    required_cols = ['date', 'like_diff_growth', 'comment_diff_growth', 'share_diff_growth']
    if not all(col in data.columns for col in required_cols):
        st.error(f"数据缺少必要的列: {required_cols}")
        return None
    
    fig = go.Figure()
    
    # 添加各互动指标的增长线
    colors = ['blue', 'red', 'green', 'orange']
    metrics = ['like_diff_growth', 'comment_diff_growth', 'share_diff_growth', 'view_diff_growth']
    
    for i, metric in enumerate(metrics):
        if metric in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data['date'],
                    y=data[metric],
                    name=metric.replace('_diff_growth', '').title(),
                    line=dict(color=colors[i]),
                    mode='lines+markers'
                )
            )
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="Date",
        yaxis_title="Growth Rate (%)",
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def plot_clicks_key_metrics_cards(metrics, yesterday_metrics=None, pct_metrics=None):
    """
    创建 Clicks 关键指标卡片，支持昨日对比
    Args:
        metrics (dict): 今日关键指标
        yesterday_metrics (dict/Series): 昨日指标
        pct_metrics (dict): 增长率
    Returns:
        str: HTML 格式的指标卡片
    """
    if not metrics:
        return ""
    cards_html = ""
    metric_configs = [
        {'key': 'total_clicks', 'name': '总点击量', 'icon': '🖱️', 'color': '#007bff'},
        {'key': 'unique_visits', 'name': '独立访客', 'icon': '👥', 'color': '#28a745'},
        {'key': 'page_visits', 'name': '页面访问', 'icon': '📄', 'color': '#ffc107'},
        {'key': 'avg_clicks_per_visit', 'name': '平均点击/访客', 'icon': '📊', 'color': '#dc3545'}
    ]
    for config in metric_configs:
        if config['key'] in metrics:
            value = metrics[config['key']]
            if isinstance(value, float):
                formatted_value = f"{value:.2f}"
            else:
                formatted_value = f"{value:,}"
            # 昨日对比
            yesterday_value = None
            pct_value = None
            if yesterday_metrics is not None and config['key'] in yesterday_metrics:
                yv = yesterday_metrics[config['key']]
                yesterday_value = f"{yv:.2f}" if isinstance(yv, float) else f"{yv:,}"
            if pct_metrics is not None and config['key'] in pct_metrics:
                pv = pct_metrics[config['key']]
                if pv is not None and not pd.isna(pv):
                    pct_value = f"({pv:+.1f}%)"
            # 组装卡片
            card_html = (
                '<div style="background: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 4px solid {color}; margin: 0.5rem; display: inline-block; width: 200px; text-align: center;">'
                '<div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>'
                '<div style="font-size: 0.9rem; color: #666; margin-bottom: 0.5rem;">{name}</div>'
                '<div style="font-size: 1.5rem; font-weight: bold; color: #333;">{value}</div>'
            ).format(color=config['color'], icon=config['icon'], name=config['name'], value=formatted_value)
            if yesterday_value is not None:
                card_html += '<div style="font-size: 0.85rem; color: #888; margin-top: 0.25rem;">昨日：{} '.format(yesterday_value)
                if pct_value:
                    card_html += '<span style="color: #888;">{}</span>'.format(pct_value)
                card_html += '</div>'
            card_html += '</div>'
            cards_html += card_html
    return '<div style="display: flex; flex-wrap: wrap; justify-content: center; margin: 1rem 0;">{}</div>'.format(cards_html)

def plot_top_pages_analysis(data, title="Top Pages Analysis", height=500):
    """
    绘制 Top 页面分析图
    
    Args:
        data (pd.DataFrame): Top 页面数据
        title (str): 图表标题
        height (int): 图表高度
    
    Returns:
        plotly.graph_objects.Figure: Top 页面分析图
    """
    if data is None or data.empty:
        return None
    
    # 确保数据包含必要的列
    required_cols = ['page_type', 'total_clicks', 'unique_visitors']
    if not all(col in data.columns for col in required_cols):
        st.error(f"数据缺少必要的列: {required_cols}")
        return None
    
    fig = go.Figure()
    
    # 添加点击量柱状图
    fig.add_trace(
        go.Bar(
            x=data['page_type'],
            y=data['total_clicks'],
            name='Total Clicks',
            text=data['total_clicks'],
            textposition='auto',
            marker_color='lightblue'
        )
    )
    
    # 添加独立访客线图（双轴）
    fig.add_trace(
        go.Scatter(
            x=data['page_type'],
            y=data['unique_visitors'],
            name='Unique Visitors',
            yaxis='y2',
            line=dict(color='red'),
            mode='lines+markers'
        )
    )
    
    fig.update_layout(
        title=title,
        height=height,
        xaxis_title="Page Type",
        yaxis=dict(title="Total Clicks", side='left'),
        yaxis2=dict(title="Unique Visitors", side='right', overlaying='y'),
        showlegend=True,
        hovermode='x unified'
    )
    
    return fig

def create_account_table_with_links(data, title="Top Accounts with Details"):
    """
    创建带链接的账号表格
    
    Args:
        data (pd.DataFrame): 账号数据
        title (str): 表格标题
    
    Returns:
        plotly.graph_objects.Figure: 账号表格
    """
    if data is None or data.empty:
        return None
    
    # 选择要显示的列
    display_cols = ['user_id', 'Tiktok Username', 'group', 'view_diff', 'like_diff', 'comment_diff', 'share_diff']
    available_cols = [col for col in display_cols if col in data.columns]
    
    display_data = data[available_cols].copy()
    
    # 格式化数值
    for col in ['view_diff', 'like_diff', 'comment_diff', 'share_diff']:
        if col in display_data.columns:
            display_data[col] = display_data[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
    
    # 创建带链接的用户名列
    if 'Tiktok Username' in display_data.columns and 'tiktok_url' in data.columns:
        display_data['Tiktok Username'] = display_data.apply(
            lambda row: f"<a href='{row['tiktok_url']}' target='_blank'>{row['Tiktok Username']}</a>" 
            if pd.notna(row['tiktok_url']) else row['Tiktok Username'],
            axis=1
        )
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=available_cols,
            fill_color='lightblue',
            align='left',
            font=dict(size=12)
        ),
        cells=dict(
            values=[display_data[col] for col in available_cols],
            fill_color='lavender',
            align='left',
            font=dict(size=11),
            height=30
        )
    )])
    
    fig.update_layout(
        title=title,
        height=400
    )
    
    return fig 