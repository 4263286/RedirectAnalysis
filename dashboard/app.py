import streamlit as st
import pandas as pd
import altair as alt
from sklearn.preprocessing import minmax_scale
import numpy as np

from datetime import datetime

st.set_page_config(page_title="TikTok 矩阵引流看板", layout="wide")

# ========== 数据读取 ==========
@st.cache_data
def load_posts():
    df_post = pd.read_excel("/Users/insnap/Downloads/all_published__20250708_014532.xlsx", dtype=str)
    df_post["Publish Time"] = pd.to_datetime(df_post["Publish Time"], errors='coerce')
    df_post = df_post.dropna(subset=["Publish Time"])
    df_post["date"] = df_post["Publish Time"].dt.date
    return df_post

# 加载原始数据（不筛选 group，用于图1）
df_post_raw = load_posts()
df_post_raw["Num View"] = pd.to_numeric(df_post_raw["Num View"], errors="coerce").fillna(0)

def classify_view(v):
    if v == 0:
        return "0播"
    elif v < 100:
        return "0–100"
    elif v < 500:
        return "100–500"
    else:
        return "500+"

df_post_raw["view_range"] = df_post_raw["Num View"].apply(classify_view)
df_post_raw["date"] = pd.to_datetime(df_post_raw["date"])
df_post_raw["date_str"] = df_post_raw["date"].astype(str)

# 加载主数据用于 group 筛选
df_post = df_post_raw.copy()

# ========== 分组关键词筛选 ==========
all_groups_raw = df_post["Groups"].dropna().unique().tolist()
all_keywords = sorted(set(g.strip() for entry in all_groups_raw for g in entry.split(",")))

selected_keywords = st.multiselect("🎯 筛选包含以下关键词的组（模糊匹配）", all_keywords, default=all_keywords)

# 筛选匹配关键词的记录
df_post["expanded_groups"] = df_post["Groups"].apply(
    lambda x: [g.strip() for g in str(x).split(",") if any(k in g for k in selected_keywords)]
)
df_post = df_post[df_post["expanded_groups"].str.len() > 0]
df_post = df_post.explode("expanded_groups").rename(columns={"expanded_groups": "Group"})

# ========== 日期范围筛选 ==========
df_post["date"] = pd.to_datetime(df_post["date"])
date_min = df_post["date"].min().to_pydatetime()
date_max = df_post["date"].max().to_pydatetime()

date_range = st.slider(
    "📅 选择日期范围",
    min_value=date_min,
    max_value=date_max,
    value=(date_min, date_max)
)

df_post = df_post[(df_post["date"] >= date_range[0]) & (df_post["date"] <= date_range[1])]
df_post["date_str"] = df_post["date"].astype(str)

st.title("📊 帖子发布情况（基于帖子明细表）")

# ========== 图1：每日总发帖数 + 播放占比（不受 group 筛选） ==========
# ========== 图1：每日总发帖数 + 播放占比 ==========
# ========== 图1：每日总发帖数 + 播放占比 ==========
# ========== 图1：每日总发帖数 + 播放占比（使用双Y轴） ==========
# ========== 图1：每日总发帖数 + 播放区间占比趋势 ==========
st.subheader("📊 每日总发帖数 + 播放区间占比趋势")

# 数据准备
view_summary = df_post_raw.groupby(["date_str", "view_range"]).size().reset_index(name="count")
daily_total = df_post_raw.groupby("date_str").size().reset_index(name="总发帖数")
view_summary = view_summary.merge(daily_total, on="date_str")
view_summary["percent"] = view_summary["count"] / view_summary["总发帖数"]

# 设置基础图
base = alt.Chart(view_summary).encode(
    x=alt.X("date_str:O", title="日期")
)

# 柱状图（左轴）
bar = base.mark_bar(color="#4C78A8").encode(
    y=alt.Y("总发帖数:Q", title="总发帖数", axis=alt.Axis(titleColor="#4C78A8")),
    tooltip=["date_str", "总发帖数"]
)

# 折线图（右轴）
line = base.mark_line(point=True).encode(
    y=alt.Y("percent:Q", title="播放占比", axis=alt.Axis(format="%", titleColor="#E45756")),
    color=alt.Color("view_range:N", title="播放区间"),
    tooltip=["date_str", "view_range", alt.Tooltip("percent:Q", format=".1%")]
)

# 合并图层，设置独立双Y轴
final_chart = alt.layer(bar, line).resolve_scale(y="independent").properties(
    height=400
)

st.altair_chart(final_chart, use_container_width=True)


# ========== 衍生分析表格 ==========
from datetime import timedelta

# 基础准备
latest_date = df_post_raw["date"].max()
prev_date = latest_date - timedelta(days=1)

today_df = df_post_raw[df_post_raw["date"] == latest_date]
yesterday_df = df_post_raw[df_post_raw["date"] == prev_date]

# 分析组别列表
target_groups = ["main_avatar", "alt_avatar", "traffic_seeding", "waterworming", "test_account", "new_account"]

# ========== 表格 1：各组发帖表现 ==========
def count_group_posts(df):
    df = df.copy()
    df["Groups"] = df["Groups"].fillna("")

    # 找出该行属于哪些目标组
    df["matched_group"] = df["Groups"].apply(
        lambda g: [k for k in target_groups if k in g]
    )

    # 只保留至少匹配一个的行
    df = df[df["matched_group"].str.len() > 0]

    # 多组展开计数
    df = df.explode("matched_group")
    return df.groupby("matched_group").size()


today_counts = count_group_posts(today_df)
yesterday_counts = count_group_posts(yesterday_df)
total_today = today_counts.sum()

group_table = pd.DataFrame({
    "今日发帖数": today_counts,
    "占比": today_counts / total_today,
    "昨日发帖数": yesterday_counts,
})

group_table["增长率"] = (group_table["今日发帖数"] - group_table["昨日发帖数"]) / group_table["昨日发帖数"]
group_table = group_table.drop(columns="昨日发帖数")
group_table = group_table.reset_index().rename(columns={"Groups": "Group"})
group_table["占比"] = group_table["占比"].map("{:.1%}".format)
group_table["增长率"] = group_table["增长率"].map("{:+.1%}".format)

st.subheader("📋 今日各组发帖表现")
st.dataframe(group_table)



st.subheader("🔥 今日播放量 Top 5 帖子")

top5_posts = (
    today_df.sort_values(by="Num View", ascending=False)
    .head(5)
    .copy()
)

# 如果之前已经 explode 过 Group，你可以直接用 Group，否则用原始 Groups 字段
top5_posts["Groups"] = top5_posts["Groups"].fillna("")

top5_table = top5_posts[[
    "Groups", "KOL ID", "Account ID", "Publish Time",
    "Num View", "Num Like", "Num Comment", "Num Share"
]].rename(columns={
    "Groups": "所属组别",
    "KOL ID": "账号ID",
    "Account ID": "平台ID",
    "Publish Time": "发布时间",
    "Num View": "浏览量",
    "Num Like": "点赞量",
    "Num Comment": "评论量",
    "Num Share": "分享量"
})

st.dataframe(top5_table, use_container_width=True)


# ========== 表格 2：播放区间表现 ==========
def count_views(df):
    return df["view_range"].value_counts()

view_today = count_views(today_df)
view_yesterday = count_views(yesterday_df)
total_views_today = view_today.sum()

view_df = pd.DataFrame({
    "今日帖子数": view_today,
    "占比": view_today / total_views_today,
    "昨日帖子数": view_yesterday
})

view_df["增长率"] = (view_df["今日帖子数"] - view_df["昨日帖子数"]) / view_df["昨日帖子数"]
view_df = view_df.drop(columns="昨日帖子数").reset_index().rename(columns={"index": "播放区间"})
view_df["占比"] = view_df["占比"].map("{:.1%}".format)
view_df["增长率"] = view_df["增长率"].map("{:+.1%}".format)

st.subheader("📋 今日播放区间表现")
st.dataframe(view_df)



# ========== 图2：每日发帖数（按组别） ==========
st.subheader("📌 每日发帖数（按组别）")

post_group_daily = df_post.groupby(["date_str", "Group"]).size().reset_index(name="Count")

bar2 = alt.Chart(post_group_daily).mark_bar().encode(
    x=alt.X("date_str:O", axis=alt.Axis(title="日期")),
    y=alt.Y("Count:Q", title="发帖数"),
    color="Group:N",
    tooltip=["date_str", "Group", "Count"]
).properties(width=800, height=300)

st.altair_chart(bar2, use_container_width=True)

# ========== 图3：播放量区间堆叠图 ==========
st.subheader("📶 各组每日播放量区间分布（横向堆叠柱 + 标签）")

view_thresholds = st.multiselect(
    "选择播放量区间（默认包含所有）",
    ["0播", "0–100", "100–500", "500+"],
    default=["0播", "0–100", "100–500", "500+"]
)

df_post_filtered = df_post[df_post["view_range"].isin(view_thresholds)]

view_dist_count = (
    df_post_filtered
    .groupby(["date_str", "Group", "view_range"])
    .size()
    .reset_index(name="count")
)

grouped_stacked_bar = alt.Chart(view_dist_count).mark_bar().encode(
    x=alt.X("date_str:O", title="日期"),
    xOffset="Group:N",
    y=alt.Y("count:Q", title="发帖数"),
    color=alt.Color("view_range:N", title="播放量区间"),
    tooltip=["date_str", "Group", "view_range", "count"]
)

text_labels = alt.Chart(view_dist_count).mark_text(
    align="left",
    baseline="middle",
    dy=10,
    angle=270,  # 垂直显示
    fontSize=10
).encode(
    x=alt.X("date_str:O"),
    xOffset="Group:N",
    text="Group:N"
)


st.altair_chart(
    alt.layer(grouped_stacked_bar, text_labels).resolve_scale(x='shared'),
    use_container_width=True
)

##图4
st.subheader("📈 单组别趋势分析（发帖数 + 播放区间占比）")

# 单独获取所有组
available_groups = df_post["Group"].unique().tolist()
selected_group = st.selectbox("选择一个组别查看：", available_groups)

# 过滤该组别数据
df_single_group = df_post[df_post["Group"] == selected_group]

# 汇总
group_summary = df_single_group.groupby(["date_str", "view_range"]).size().reset_index(name="count")
daily_total_g = df_single_group.groupby("date_str").size().reset_index(name="总发帖数")
group_summary = group_summary.merge(daily_total_g, on="date_str")
group_summary["percent"] = group_summary["count"] / group_summary["总发帖数"]

# 绘图
base_g = alt.Chart(group_summary).encode(
    x=alt.X("date_str:O", title="日期")
)

bar_g = base_g.mark_bar(color="#4C78A8").encode(
    y=alt.Y("总发帖数:Q", title="总发帖数", axis=alt.Axis(titleColor="#4C78A8")),
    tooltip=["date_str", "总发帖数"]
)

line_g = base_g.mark_line(point=True).encode(
    y=alt.Y("percent:Q", title="播放占比", axis=alt.Axis(format="%", titleColor="#E45756")),
    color=alt.Color("view_range:N", title="播放区间"),
    tooltip=["date_str", "view_range", alt.Tooltip("percent:Q", format=".1%")]
)

st.altair_chart(alt.layer(bar_g, line_g).resolve_scale(y="independent").properties(height=400), use_container_width=True)


### 浏览量分析
st.subheader("📈 每日浏览量趋势")

daily_view = df_post_raw.groupby("date").agg(新增浏览量=("Num View", "sum")).reset_index()

chart_view_trend = alt.Chart(daily_view).mark_line(point=True).encode(
    x=alt.X("date:T", title="日期"),
    y=alt.Y("新增浏览量:Q", title="新增浏览量"),
    tooltip=["date:T", "新增浏览量"]
).properties(width=800, height=300)

st.altair_chart(chart_view_trend, use_container_width=True)

# 图二
st.subheader("📊 浏览量 vs 发帖量 对比")

daily_eff = df_post_raw.groupby("date").agg(
    浏览量总和=("Num View", "sum"),
    发帖数=("Num View", "count")
).reset_index()

daily_eff["view_per_post"] = daily_eff["浏览量总和"] / daily_eff["发帖数"]

base = alt.Chart(daily_eff).encode(x=alt.X("date:T", title="日期"))

bar = base.mark_bar(color="#4C78A8").encode(
    y=alt.Y("发帖数:Q", title="发帖数", axis=alt.Axis(titleColor="#4C78A8"))
)

line = base.mark_line(point=True).encode(
    y=alt.Y("view_per_post:Q", title="平均浏览量/帖", axis=alt.Axis(titleColor="#E45756")),
    color=alt.value("#E45756")
)

st.altair_chart(alt.layer(bar, line).resolve_scale(y='independent'), use_container_width=True)


# 图五
st.subheader("📈 各组每日浏览量趋势")

all_groups_text = df_post_raw["Groups"].dropna().unique().tolist()
group_keywords_4 = sorted(set(k.strip() for item in all_groups_text for k in item.split(",")))

selected_keywords_4 = st.multiselect("🔍 选择组关键词（模糊匹配，仅作用于该图）", group_keywords_4, default=group_keywords_4[:5])

df_post_4 = df_post_raw.copy()
df_post_4["expanded_groups"] = df_post_4["Groups"].apply(
    lambda x: [g.strip() for g in str(x).split(",") if any(k in g for k in selected_keywords_4)]
)
df_post_4 = df_post_4[df_post_4["expanded_groups"].str.len() > 0]
df_post_4 = df_post_4.explode("expanded_groups").rename(columns={"expanded_groups": "Group"})

group_daily_view = df_post_4.groupby(["date", "Group"])["Num View"].sum().reset_index()

chart_group_view = alt.Chart(group_daily_view).mark_line(point=True).encode(
    x=alt.X("date:T", title="日期"),
    y=alt.Y("Num View:Q", title="浏览量"),
    color=alt.Color("Group:N", title="组别"),
    tooltip=["date:T", "Group", "Num View"]
).properties(
    title="📈 各组每日浏览量趋势",
    height=400
)

st.altair_chart(chart_group_view, use_container_width=True)


# ========== 模块：浏览效率分析 ==========
st.subheader("📊 浏览效率分析：浏览量 / 发帖数")

mode_view = st.radio(
    "🎛 请选择查看模式 - 浏览效率",
    ["全部账号", "按组别模糊筛选"],
    key="view_eff_mode"
)

if mode_view == "全部账号":
    df_view_eff = df_post_raw.copy()
    df_view_eff["Group"] = "全部账号"
else:
    selected_keys_view = st.multiselect(
        "🔍 模糊匹配组关键词 - 浏览效率",
        all_group_keywords,
        default=all_group_keywords[:5],
        key="view_eff_keys"
    )
    df_view_eff = df_post_raw.copy()
    df_view_eff["expanded_groups"] = df_view_eff["Groups"].apply(
        lambda x: [g.strip() for g in str(x).split(",") if any(k in g for k in selected_keys_view)]
    )
    df_view_eff = df_view_eff[df_view_eff["expanded_groups"].str.len() > 0]
    df_view_eff = df_view_eff.explode("expanded_groups").rename(columns={"expanded_groups": "Group"})

df_view_eff["date_only"] = pd.to_datetime(df_view_eff["date"]).dt.date
df_view_eff["date_only"] = pd.to_datetime(df_view_eff["date_only"])
# 按日按组计算浏览效率
daily_view_sum = df_view_eff.groupby(["date_only", "Group"])["Num View"].sum().reset_index()
daily_post_count = df_view_eff.groupby(["date_only", "Group"]).size().reset_index(name="发帖数")
merged_view = pd.merge(daily_view_sum, daily_post_count, on=["date_only", "Group"])
merged_view["浏览效率"] = merged_view["Num View"] / merged_view["发帖数"]

# 画图
chart_view_eff = alt.Chart(merged_view).mark_line(point=True).encode(
    x=alt.X("date_only:T", title="日期"),
    y=alt.Y("浏览效率:Q", title="浏览量 / 发帖数"),
    color=alt.Color("Group:N", title="Group"),
    tooltip=["date_only", "Group", "浏览效率"]
).properties(height=350)

st.altair_chart(chart_view_eff, use_container_width=True)



#互动量分析


st.subheader("💬 互动量分析模块：点赞 / 评论 / 分享")

# 确保数值字段转换
# 确保数值字段转换
for col in ["Num Like", "Num Comment", "Num Share"]:
    df_post_raw[col] = pd.to_numeric(df_post_raw[col], errors="coerce").fillna(0)

# 统一为 datetime 日期类型，并转换为仅含日期的字段
df_post_raw["date"] = pd.to_datetime(df_post_raw["date"])
df_post_raw["date_only"] = df_post_raw["date"].dt.date  # ✅ 用于绘图

# 所有分组关键词
group_texts = df_post_raw["Groups"].dropna().unique().tolist()
all_group_keywords = sorted(set(g.strip() for gtxt in group_texts for g in gtxt.split(",")))

# 定义通用可视化函数
def plot_interaction_metric(metric_col, metric_label):
    st.subheader(f"📈 每日{metric_label}趋势")

    mode = st.radio(
        f"🎛 请选择查看模式 - {metric_label}",
        ["全部账号", "按组别模糊筛选"],
        key=f"{metric_col}_mode"
    )

    if mode == "全部账号":
        df_metric = df_post_raw.copy()
        df_metric["Group"] = "全部账号"
    else:
        selected_keys = st.multiselect(
            f"🔍 模糊匹配组关键词 - {metric_label}",
            all_group_keywords,
            default=all_group_keywords[:5],
            key=f"{metric_col}_keys"
        )
        df_metric = df_post_raw.copy()
        df_metric["expanded_groups"] = df_metric["Groups"].apply(
            lambda x: [g.strip() for g in str(x).split(",") if any(k in g for k in selected_keys)]
        )
        df_metric = df_metric[df_metric["expanded_groups"].str.len() > 0]
        df_metric = df_metric.explode("expanded_groups").rename(columns={"expanded_groups": "Group"})

    # 每日聚合
    daily_data = df_metric.groupby(["date_only", "Group"])[metric_col].sum().reset_index()

    # 折线图
    chart = alt.Chart(daily_data).mark_line(point=True).encode(
        x=alt.X("date_only:T", title="日期"),
        y=alt.Y(f"{metric_col}:Q", title=metric_label),
        color=alt.Color("Group:N", title="Group"),
        tooltip=["date_only", "Group", f"{metric_col}"]
    ).properties(height=350)

    st.altair_chart(chart, use_container_width=True)

# 模块分别绘制
plot_interaction_metric("Num Like", "点赞数")
plot_interaction_metric("Num Comment", "评论数")
plot_interaction_metric("Num Share", "分享数")


# ========== 模块：互动效率分析 ==========
st.subheader("📊 互动效率分析：互动数 / 发帖数")

# 定义函数：按日计算效率
def plot_interaction_efficiency(metric_col, label):
    st.subheader(f"📈 每日{label}效率趋势（{label}/发帖数）")

    mode = st.radio(
        f"🎛 请选择查看模式 - {label}效率",
        ["全部账号", "按组别模糊筛选"],
        key=f"{metric_col}_eff_mode"
    )

    if mode == "全部账号":
        df_eff = df_post_raw.copy()
        df_eff["Group"] = "全部账号"
    else:
        selected_keys = st.multiselect(
            f"🔍 模糊匹配组关键词 - {label}效率",
            all_group_keywords,
            default=all_group_keywords[:5],
            key=f"{metric_col}_eff_keys"
        )
        df_eff = df_post_raw.copy()
        df_eff["expanded_groups"] = df_eff["Groups"].apply(
            lambda x: [g.strip() for g in str(x).split(",") if any(k in g for k in selected_keys)]
        )
        df_eff = df_eff[df_eff["expanded_groups"].str.len() > 0]
        df_eff = df_eff.explode("expanded_groups").rename(columns={"expanded_groups": "Group"})

    # 计算效率 = 互动数 / 发帖数
    daily_metric = df_eff.groupby(["date_only", "Group"])[metric_col].sum().reset_index()
    daily_count = df_eff.groupby(["date_only", "Group"]).size().reset_index(name="发帖数")
    merged = pd.merge(daily_metric, daily_count, on=["date_only", "Group"])
    merged["效率"] = merged[metric_col] / merged["发帖数"]

    # 画图
    chart = alt.Chart(merged).mark_line(point=True).encode(
        x=alt.X("date_only:T", title="日期"),
        y=alt.Y("效率:Q", title=f"{label}/发帖数"),
        color=alt.Color("Group:N", title="Group"),
        tooltip=["date_only", "Group", "效率"]
    ).properties(height=350)

    st.altair_chart(chart, use_container_width=True)

# 三个互动指标分别绘图
plot_interaction_efficiency("Num Like", "点赞")
plot_interaction_efficiency("Num Comment", "评论")
plot_interaction_efficiency("Num Share", "分享")
