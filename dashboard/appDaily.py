import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta, date
import warnings
import sys
import os
import re # Added for group filtering

# 添加 scripts 目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scripts_dir = os.path.join(parent_dir, 'scripts')
config_dir = os.path.join(parent_dir, 'config')

# 确保路径存在
if os.path.exists(scripts_dir):
    sys.path.insert(0, scripts_dir)
if os.path.exists(config_dir):
    sys.path.insert(0, config_dir)

from data_processor import TikTokDataProcessor
from clicks_analyzer import ClicksAnalyzer
from visualization_utils import (
    plot_diff_metrics_trend,
    plot_correlation_scatter,
    plot_comparison_line,
    plot_account_history,
    plot_group_performance_table,
    plot_top_accounts_ranking,
    create_metric_summary_card,
    plot_cvr_analysis,
    plot_efficiency_distribution,
    plot_interaction_growth_comparison,
    plot_clicks_key_metrics_cards,
    plot_top_pages_analysis,
    create_account_table_with_links
)

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="TikTok 账号分析看板",
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
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """加载和预处理数据"""
    try:
        # 创建数据处理器
        processor = TikTokDataProcessor(
            redash_file_path='data/redash_data/redash_data_2025-07-08.csv',
            accounts_file_path='data/postingManager_data/accounts_detail.xlsx'
        )
        
        # 合并数据
        if processor.merge_data():
            return processor.merged_df, processor.group_mapping
        else:
            st.error("数据合并失败")
            return None, None
        
    except Exception as e:
        st.error(f"数据加载错误: {str(e)}")
        return None, None

@st.cache_data
def load_clicks_data():
    """加载 clicks 数据"""
    try:
        # 创建 clicks 分析器
        analyzer = ClicksAnalyzer(
            clicks_file_path='data/clicks/20250708ClicksInsnap.csv',
            merged_data_path='data/merged_tiktok_data.csv'
        )
        
        # 加载数据
        if analyzer.load_clicks_data() and analyzer.load_merged_data():
            if analyzer.process_clicks_by_group():
                return analyzer
            else:
                st.error("Clicks 数据处理失败")
                return None
        else:
            st.error("Clicks 数据加载失败")
            return None
        
    except Exception as e:
        st.error(f"Clicks 数据加载错误: {str(e)}")
        return None


def create_daily_trend_chart(df, metric, title, color='#1f77b4'):
    """创建每日趋势图"""
    daily_data = df.groupby('date')[metric].sum().reset_index()

    fig = px.line(
        daily_data,
        x='date',
        y=metric,
        title=title,
        labels={'date': '日期', metric: metric.replace('_', ' ').title()},
        line_shape='linear',
        render_mode='svg'
    )

    fig.update_layout(
        xaxis_title="日期",
        yaxis_title=metric.replace('_', ' ').title(),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )

    fig.update_traces(
        line=dict(color=color, width=3),
        marker=dict(size=6)
    )

    return fig


def create_efficiency_trend_chart(df, selected_metric):
    """创建效率指标趋势图"""
    daily_data = df.groupby('date')[selected_metric].mean().reset_index()

    fig = px.line(
        daily_data,
        x='date',
        y=selected_metric,
        title=f"每日 {selected_metric.replace('_', ' ').title()} 趋势",
        labels={'date': '日期', selected_metric: selected_metric.replace('_', ' ').title()},
        line_shape='linear',
        render_mode='svg'
    )

    fig.update_layout(
        xaxis_title="日期",
        yaxis_title=selected_metric.replace('_', ' ').title(),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )

    fig.update_traces(
        line=dict(color='#ff7f0e', width=3),
        marker=dict(size=6)
    )

    return fig


def create_group_performance_table(df, latest_date):
    """创建分组表现表格"""
    latest_data = df[df['date'] == latest_date].copy()
    
    if latest_data.empty:
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

def create_daily_diff_chart(df, metric, groups=None):
    """创建每日新增量趋势图"""
    if groups:
        filtered_df = df[df['group'].isin(groups)]
    else:
        filtered_df = df
    
    # 使用新的可视化工具
    daily_diff = filtered_df.groupby(['date', 'group'])[metric].sum().reset_index()
    
    # 按 group 分组绘制
    fig = px.line(
        daily_diff,
        x='date',
        y=metric,
        color='group',
        title=f"每日 {metric.replace('_', ' ').title()} 趋势",
        labels={'date': '日期', metric: metric.replace('_', ' ').title(), 'group': '分组'},
        line_shape='linear',
        render_mode='svg'
    )

    fig.update_layout(
        xaxis_title="日期",
        yaxis_title=metric.replace('_', ' ').title(),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )

    return fig

def create_clicks_vs_views_chart(analyzer, page_type='videos'):
    """创建 clicks vs views 对比图"""
    data = analyzer.get_clicks_vs_views_data(page_type)
    if data is None or data.empty:
        return None
    
    # 创建双轴图
    fig = go.Figure()
    
    # 添加 clicks 数据
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['click_count'],
        mode='lines+markers',
        name='Clicks',
        line=dict(color='#1f77b4', width=2),
        yaxis='y'
    ))
    
    # 添加 views 数据
    fig.add_trace(go.Scatter(
        x=data['date'],
        y=data['view_diff'],
        mode='lines+markers',
        name='Views',
        line=dict(color='#ff7f0e', width=2),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f"{page_type.title()} 页面: Clicks vs Views 对比",
        xaxis_title="日期",
        yaxis=dict(title="Clicks", side="left"),
        yaxis2=dict(title="Views", side="right", overlaying="y"),
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig

def create_correlation_scatter(analyzer, page_type='videos'):
    """创建相关性散点图"""
    data = analyzer.get_clicks_vs_views_data(page_type)
    if data is None or data.empty:
        return None
    
    fig = px.scatter(
        data,
        x='click_count',
        y='view_diff',
        title=f"{page_type.title()} 页面: Clicks vs Views 相关性分析",
        labels={'click_count': 'Clicks', 'view_diff': 'Views'},
        trendline="ols"
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig

def create_top_accounts_table(df, date, top_n=5):
    """创建 Top 账号表格"""
    daily_data = df[df['date'] == date].copy()
    
    if daily_data.empty:
        return None
    
    # 按 view_diff 排序并获取前 N 名
    top_accounts = daily_data.nlargest(top_n, 'view_diff')[
        ['user_id', 'group', 'view_diff', 'like_diff', 'comment_diff', 'share_diff']
    ].copy()
    
    return top_accounts

def create_account_history_chart(df, user_id, start_date=None, end_date=None):
    """创建账号历史数据图表"""
    account_data = df[df['user_id'] == user_id].copy()
    
    if account_data.empty:
        return None
    
    # 日期筛选
    if start_date:
        account_data = account_data[account_data['date'] >= pd.Timestamp(start_date)]
    if end_date:
        account_data = account_data[account_data['date'] <= pd.Timestamp(end_date)]
    
    account_data = account_data.sort_values('date')
    
    # 创建多指标图表
    fig = go.Figure()
    
    metrics = ['view_diff', 'like_diff', 'comment_diff', 'share_diff']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for metric, color in zip(metrics, colors):
        fig.add_trace(go.Scatter(
            x=account_data['date'],
            y=account_data[metric],
            mode='lines+markers',
            name=metric.replace('_', ' ').title(),
            line=dict(color=color, width=2)
        ))
    
    fig.update_layout(
        title=f"账号 {user_id} 历史数据趋势",
        xaxis_title="日期",
        yaxis_title="数值",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12)
    )
    
    return fig


def main():
    # 页面标题
    st.markdown('<h1 class="main-header">📊 TikTok 账号分析看板</h1>', unsafe_allow_html=True)
    
    # 加载数据
    with st.spinner('正在加载数据...'):
        merged_df, group_mapping = load_data()
        clicks_analyzer = load_clicks_data()
        
        # 创建数据处理器实例
        processor = TikTokDataProcessor(
            redash_file_path='data/redash_data/redash_data_2025-07-08.csv',
            accounts_file_path='data/postingManager_data/accounts_detail.xlsx'
        )
        
        # 加载数据到处理器
        processor.load_redash_data()
        processor.load_accounts_data()
        processor.merge_data()
    
    if merged_df is None:
        st.error("无法加载数据，请检查数据文件路径")
        return
    
    # 侧边栏 - 筛选器
    st.sidebar.header("📋 筛选设置")
    
    # 日期范围选择
    min_date = merged_df['date'].min()
    max_date = merged_df['date'].max()
    # 修复 NaT 问题，确保为 datetime.date 类型
    if pd.isna(min_date) or min_date is pd.NaT:
        min_date = date.today()
    if pd.isna(max_date) or max_date is pd.NaT:
        max_date = date.today()
    if isinstance(min_date, pd.Timestamp):
        min_date = min_date.date()
    if isinstance(max_date, pd.Timestamp):
        max_date = max_date.date()
    date_range = st.sidebar.date_input(
        "选择日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = merged_df[
            (merged_df['date'] >= pd.Timestamp(start_date)) & 
            (merged_df['date'] <= pd.Timestamp(end_date))
        ]
    else:
        filtered_df = merged_df
    
    # Group 筛选（支持 contains 匹配，选项为 accounts_detail.xlsx 里所有组别，分隔符为 , 或 | 或 / 或 ;）
    # 先获取所有 group 字段，拆分去重
    all_groups_raw = merged_df['group'].dropna().unique().tolist()
    split_groups = set()
    for g in all_groups_raw:
        if isinstance(g, str):
            for part in re.split(r'[\,\|/;，；]', g):
                part = part.strip()
                if part:
                    split_groups.add(part)
    available_groups = sorted(split_groups)
    # 多选框支持模糊匹配
    selected_groups = st.sidebar.multiselect(
        "选择分组 (支持模糊匹配)",
        options=available_groups,
        default=available_groups,
        help="可以选择多个分组进行对比分析"
    )
    # contains 过滤
    if selected_groups:
        filtered_df = filtered_df[filtered_df['group'].apply(lambda x: any(sg in str(x) for sg in selected_groups))]
    
    # 映射配置管理
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔧 映射配置")
    if st.sidebar.button("查看映射配置"):
        st.session_state.show_mapping_config = True
    
    if st.sidebar.button("隐藏映射配置"):
        st.session_state.show_mapping_config = False
    
    # 映射配置显示
    if hasattr(st.session_state, 'show_mapping_config') and st.session_state.show_mapping_config:
        st.markdown("### 🔧 映射配置管理")
        
        try:
            # 导入映射配置
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
            from group_click_map import get_all_mappings, get_mapping_statistics
            
            mappings = get_all_mappings()
            stats = get_mapping_statistics()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📋 当前映射规则")
                for group, page_type in mappings['mappings'].items():
                    description = mappings['descriptions'].get(group, "无描述")
                    st.info(f"**{group}** → **{page_type}**\n\n{description}")
            
            with col2:
                st.markdown("#### 📊 映射统计")
                st.metric("总映射数", stats['total_mappings'])
                st.metric("页面类型数", len(stats['page_types']))
                st.metric("分组数", len(stats['groups']))
                
                st.markdown("#### 📝 页面类型")
                for page_type in stats['page_types']:
                    st.write(f"• {page_type}")
        
        except Exception as e:
            st.error(f"加载映射配置失败: {str(e)}")
        
        st.markdown("---")
    
    # 主要内容区域
    if filtered_df.empty:
        st.warning("所选筛选条件下没有数据")
        return
    
    # 创建标签页
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 基础分析", 
        "📈 每日新增量", 
        "🔁 Clicks 对照", 
        "🌟 Top5 账号"
    ])
    
    with tab1:
        # 1. 关键指标卡片
        st.markdown("### 📊 关键指标概览")
        
        latest_date = filtered_df['date'].max()
        latest_data = filtered_df[filtered_df['date'] == latest_date]
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_views = latest_data['view_count'].sum()
            st.metric("总浏览量", f"{total_views:,}")
        
        with col2:
            total_posts = latest_data['post_count'].sum()
            st.metric("总发帖数", f"{total_posts:,}")
        
        with col3:
            avg_view_per_post = latest_data['view_per_post'].mean()
            st.metric("平均浏览效率", f"{avg_view_per_post:.0f}")
        
        with col4:
            total_likes = latest_data['like_count'].sum()
            st.metric("总点赞数", f"{total_likes:,}")
        
        st.markdown("---")
        
        # 2. 趋势图表
        st.markdown("### 📈 趋势分析")
        
        # 创建两列布局
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_views = create_daily_trend_chart(filtered_df, 'view_count', "每日总浏览量趋势")
            st.plotly_chart(fig_views, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig_posts = create_daily_trend_chart(filtered_df, 'post_count', "每日总发帖数趋势", '#2ca02c')
            st.plotly_chart(fig_posts, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 3. 效率指标趋势
        st.markdown("### 🎯 效率指标趋势")
        
        efficiency_metric = st.radio(
            "选择效率指标",
            options=['view_per_post', 'like_per_post', 'comment_per_post', 'share_per_post'],
            format_func=lambda x: x.replace('_', ' ').title(),
            horizontal=True
        )
        
        fig_efficiency = create_efficiency_trend_chart(filtered_df, efficiency_metric)
        st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # 4. 分组表现表格
        st.markdown("### 📋 分组表现详情")
        
        group_stats = create_group_performance_table(filtered_df, latest_date)
        
        if group_stats is not None:
            # 格式化表格显示
            display_stats = group_stats.copy()
            
            # 格式化大数字
            for col in ['view_count', 'post_count', 'like_count', 'comment_count', 'share_count']:
                display_stats[col] = display_stats[col].apply(lambda x: f"{x:,.0f}")
            
            # 格式化效率指标
            for col in ['view_per_post', 'like_per_post', 'comment_per_post', 'share_per_post']:
                display_stats[col] = display_stats[col].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(
                display_stats,
                use_container_width=True,
                hide_index=True
            )
            
            # 下载按钮
            csv = group_stats.to_csv(index=False)
            st.download_button(
                label="📥 下载分组表现数据",
                data=csv,
                file_name=f"group_performance_{latest_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # 5. 数据洞察
        st.markdown("### 💡 数据洞察")
        
        if len(filtered_df['date'].unique()) > 1:
            # 计算增长率
            dates_sorted = sorted(filtered_df['date'].unique())
            if len(dates_sorted) >= 2:
                latest_date = dates_sorted[-1]
                previous_date = dates_sorted[-2]
                
                latest_views = filtered_df[filtered_df['date'] == latest_date]['view_count'].sum()
                previous_views = filtered_df[filtered_df['date'] == previous_date]['view_count'].sum()
                
                if previous_views > 0:
                    growth_rate = ((latest_views - previous_views) / previous_views) * 100
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.info(f"📈 浏览量环比增长: {growth_rate:.1f}%")
                    
                    with col2:
                        best_group = group_stats.iloc[0]['group'] if group_stats is not None else "N/A"
                        st.success(f"🏆 表现最佳分组: {best_group}")
                    
                    with col3:
                        total_accounts = len(filtered_df['user_id'].unique())
                        st.warning(f"👥 活跃账号数: {total_accounts}")
    
    with tab2:
        # 每日新增量分析模块
        st.markdown("### 📈 每日新增量分析")
        
        # 获取当日汇总指标
        latest_date = filtered_df['date'].max()
        daily_summary = processor.get_daily_summary_metrics(latest_date)
        
        if daily_summary:
            st.markdown("#### 📊 当日关键指标概览")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("总发帖数", f"{daily_summary['total_posts']:,}")
                st.metric("总浏览量增长", f"{daily_summary['total_views']:,}")
            
            with col2:
                st.metric("新增点赞", f"{daily_summary['total_likes']:,}")
                st.metric("新增评论", f"{daily_summary['total_comments']:,}")
            
            with col3:
                st.metric("新增分享", f"{daily_summary['total_shares']:,}")
                st.metric("新增粉丝", f"{daily_summary['total_followers']:,}")
            
            with col4:
                st.metric("活跃账号数", f"{daily_summary['active_accounts']:,}")
                st.metric("平均播放效率", f"{daily_summary['avg_view_per_post']:.0f}")
        
        st.markdown("---")
        
        # 选择指标
        diff_metrics = ['view_diff', 'like_diff', 'comment_diff', 'share_diff', 'post_diff']
        selected_diff_metric = st.selectbox(
            "选择新增量指标",
            options=diff_metrics,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        # 分组筛选
        diff_groups = st.multiselect(
            "选择分组 (可选)",
            options=available_groups,
            default=available_groups[:5] if len(available_groups) > 5 else available_groups,
            help="选择要分析的分组，留空则显示所有分组"
        )
        
        # 创建图表
        fig_diff = create_daily_diff_chart(filtered_df, selected_diff_metric, diff_groups if diff_groups else None)
        st.plotly_chart(fig_diff, use_container_width=True)
        
        # 显示统计信息
        if diff_groups:
            st.markdown("### 📊 分组新增量统计")
            diff_stats = filtered_df[filtered_df['group'].isin(diff_groups)].groupby('group')[selected_diff_metric].sum().sort_values(ascending=False)
            st.bar_chart(diff_stats)
        
        # 效率分布分析
        st.markdown("### 🎯 效率分布分析")
        
        efficiency_metric = st.selectbox(
            "选择效率指标",
            options=['view_per_post', 'like_per_post', 'comment_per_post', 'share_per_post'],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        efficiency_data = processor.get_efficiency_distribution(latest_date, efficiency_metric)
        if efficiency_data is not None:
            fig_efficiency = plot_efficiency_distribution(efficiency_data, f"{efficiency_metric.replace('_', ' ').title()} Distribution")
            st.plotly_chart(fig_efficiency, use_container_width=True)
        
        # 互动增长对比
        st.markdown("### 📈 互动增长对比")
        interaction_data = processor.get_interaction_growth_comparison()
        if interaction_data is not None:
            fig_interaction = plot_interaction_growth_comparison(interaction_data)
            st.plotly_chart(fig_interaction, use_container_width=True)
    
    with tab3:
        # Clicks 对照分析模块
        st.markdown("### 🔁 Clicks 对照分析")
        
        if clicks_analyzer is None:
            st.warning("Clicks 数据加载失败，请检查数据文件")
        else:
            # 获取 Clicks 关键指标
            clicks_metrics = clicks_analyzer.get_clicks_key_metrics()
            
            if clicks_metrics:
                st.markdown("#### 📊 Clicks 关键指标")
                # 新增昨日对比
                daily_clicks_df = clicks_analyzer.calculate_clicks_metrics_by_day()
                today = clicks_metrics['date'] if 'date' in clicks_metrics else None
                yesterday = None
                yesterday_metrics = None
                pct_metrics = None
                if today and daily_clicks_df is not None:
                    today_row = daily_clicks_df[daily_clicks_df['date'] == today]
                    if not today_row.empty:
                        yesterday = today_row['date'].values[0] - timedelta(days=1)
                        yesterday_row = daily_clicks_df[daily_clicks_df['date'] == yesterday]
                        if not yesterday_row.empty:
                            yesterday_metrics = yesterday_row.iloc[0]
                            pct_metrics = {col: today_row.iloc[0][f"{col}_pct"] for col in ['total_clicks', 'unique_visits', 'page_visits', 'avg_clicks_per_visit']}
                clicks_cards_html = plot_clicks_key_metrics_cards(clicks_metrics, yesterday_metrics, pct_metrics)
                st.markdown(clicks_cards_html, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # 选择分析类型
            analysis_type = st.selectbox(
                "选择分析类型",
                options=["浏览量对比", "互动量对比", "CVR分析", "Top页面分析"],
                index=0
            )
            
            if analysis_type == "浏览量对比":
                # 页面类型选择
                page_types = ['videos', 'download']
                selected_page_type = st.selectbox(
                    "选择页面类型",
                    options=page_types,
                    help="main_avatar 对应 videos，wan_produce101 对应 download"
                )
                
                # 创建对比图表
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📈 Clicks vs Views 趋势对比")
                    fig_comparison = create_clicks_vs_views_chart(clicks_analyzer, selected_page_type)
                    if fig_comparison:
                        st.plotly_chart(fig_comparison, use_container_width=True)
                    else:
                        st.warning("暂无数据")
                
                with col2:
                    st.markdown("#### 📊 相关性分析")
                    fig_correlation = create_correlation_scatter(clicks_analyzer, selected_page_type)
                    if fig_correlation:
                        st.plotly_chart(fig_correlation, use_container_width=True)
                        
                        # 计算并显示相关系数
                        correlation = clicks_analyzer.calculate_correlation(selected_page_type)
                        if correlation is not None:
                            st.metric("相关系数", f"{correlation:.4f}")
                    else:
                        st.warning("暂无数据")
            
            elif analysis_type == "互动量对比":
                # 选择互动指标
                interaction_metrics = ['like_diff', 'comment_diff', 'share_diff']
                selected_interaction = st.selectbox(
                    "选择互动指标",
                    options=interaction_metrics,
                    format_func=lambda x: x.replace('_', ' ').title()
                )
                
                # 获取互动对比数据
                interaction_data = clicks_analyzer.get_clicks_vs_interaction_analysis(selected_interaction)
                
                if interaction_data is not None:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # 趋势对比图
                        fig_trend = plot_comparison_line(
                            interaction_data, 'date', 'click_count', selected_interaction,
                            f"Clicks vs {selected_interaction.replace('_', ' ').title()}"
                        )
                        if fig_trend:
                            st.plotly_chart(fig_trend, use_container_width=True)
                    
                    with col2:
                        # 散点图
                        fig_scatter = plot_correlation_scatter(
                            interaction_data, 'click_count', selected_interaction,
                            f"Clicks vs {selected_interaction.replace('_', ' ').title()}"
                        )
                        if fig_scatter:
                            st.plotly_chart(fig_scatter, use_container_width=True)
            
            elif analysis_type == "CVR分析":
                # CVR 分析
                cvr_data = clicks_analyzer.get_cvr_analysis()
                
                if cvr_data is not None:
                    fig_cvr = plot_cvr_analysis(cvr_data)
                    if fig_cvr:
                        st.plotly_chart(fig_cvr, use_container_width=True)
                    
                    # 显示 CVR 数据表格
                    st.markdown("### 📋 CVR 详细数据")
                    st.dataframe(cvr_data, use_container_width=True)
            
            elif analysis_type == "Top页面分析":
                # Top 页面分析
                top_pages_data = clicks_analyzer.get_top_pages_analysis()
                
                if top_pages_data is not None:
                    fig_top_pages = plot_top_pages_analysis(top_pages_data)
                    if fig_top_pages:
                        st.plotly_chart(fig_top_pages, use_container_width=True)
                    
                    # 显示 Top 页面数据表格
                    st.markdown("### 📋 Top 页面详细数据")
                    st.dataframe(top_pages_data, use_container_width=True)
            
            # 显示映射关系
            st.markdown("### 📋 Group 映射关系")
            mapping_summary = clicks_analyzer.get_group_mapping_summary()
            if mapping_summary is not None:
                st.dataframe(mapping_summary, use_container_width=True)
    
    with tab4:
        # Top5 账号榜单模块
        st.markdown("### 🌟 当日 Top5 账号榜单")
        
        # 日期选择
        available_dates = sorted(filtered_df['date'].unique())
        selected_date = st.selectbox(
            "选择日期",
            options=available_dates,
            index=len(available_dates) - 1,  # 默认选择最新日期
            format_func=lambda x: x.strftime('%Y-%m-%d') if x else "N/A"
        )
        
        # 获取带详细信息的 Top5 账号
        top_accounts_with_details = processor.get_top_accounts_with_details(selected_date, 5, 'view_diff')
        
        if top_accounts_with_details is not None and not top_accounts_with_details.empty:
            st.markdown(f"#### 📅 {selected_date.strftime('%Y-%m-%d') if selected_date else 'N/A'} Top5 账号")
            
            # 创建带链接的账号表格
            fig_account_table = create_account_table_with_links(top_accounts_with_details)
            if fig_account_table:
                st.plotly_chart(fig_account_table, use_container_width=True)
            
            # 创建可展开的详细视图
            for idx, row in top_accounts_with_details.iterrows():
                username = row.get('Tiktok Username', f"User {row['user_id']}")
                group = row.get('group', 'Unknown')
                followers = row.get('Total Followers', 'N/A')
                total_likes = row.get('Total Like', 'N/A')
                
                with st.expander(f"#{idx+1} - {username} ({group})"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("浏览量增长", f"{row['view_diff']:,.0f}")
                        if followers != 'N/A':
                            st.metric("总粉丝数", f"{followers:,}")
                    
                    with col2:
                        st.metric("点赞增长", f"{row['like_diff']:,.0f}")
                        if total_likes != 'N/A':
                            st.metric("总点赞数", f"{total_likes:,}")
                    
                    with col3:
                        st.metric("评论增长", f"{row['comment_diff']:,.0f}")
                        st.metric("所属分组", group)
                    
                    with col4:
                        st.metric("分享增长", f"{row['share_diff']:,.0f}")
                        if 'tiktok_url' in row and pd.notna(row['tiktok_url']):
                            st.markdown(f"[🔗 查看 TikTok 主页]({row['tiktok_url']})")
                    
                    # 显示历史数据图表
                    st.markdown("#### 📈 历史数据趋势")
                    history_chart = create_account_history_chart(filtered_df, row['user_id'])
                    if history_chart:
                        st.plotly_chart(history_chart, use_container_width=True)
        else:
            st.warning(f"所选日期 {selected_date.strftime('%Y-%m-%d') if selected_date else 'N/A'} 没有数据")

if __name__ == "__main__":
    main()
