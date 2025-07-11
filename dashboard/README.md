# TikTok 账号分析可视化看板

这是一个基于 Streamlit 的 TikTok 账号数据分析可视化看板，用于分析账号表现和趋势。

## 功能特性

### 📊 数据整合
- 使用独立的数据处理脚本 (`scripts/data_processor.py`)
- 自动合并 Redash 数据和 Accounts Detail 数据
- 根据 `user_id` 关联账号信息
- 补充每个账号的 group 字段

### 📈 可视化内容

#### 📊 基础分析模块
1. **关键指标概览** - 总浏览量、发帖数、效率指标等
2. **每日趋势图** - 浏览量和发帖数趋势
3. **效率指标趋势** - 可切换查看不同效率指标
4. **分组表现表格** - 最新数据的分组对比
5. **数据洞察** - 自动分析增长趋势和表现

#### 📈 每日新增量分析模块
1. **新增量趋势图** - 每日 `*_diff` 指标的趋势折线图
2. **分组筛选** - 支持按 group 筛选特定分组
3. **指标选择** - 支持选择不同的新增量指标（view_diff, like_diff 等）
4. **分组统计** - 显示各分组的新增量统计

#### 🔁 Clicks 对照分析模块
1. **Group 映射** - 自动映射 main_avatar → videos，wan_produce101 → download
2. **趋势对比** - Clicks vs Views 双轴趋势对比图
3. **相关性分析** - 散点图 + 线性回归分析
4. **相关系数** - 实时计算并显示相关系数

#### 🌟 Top5 账号榜单模块
1. **每日榜单** - 按 view_diff 排序的 Top5 账号
2. **日期选择** - 可选择不同日期查看榜单
3. **账号详情** - 点击展开查看账号详细指标
4. **历史趋势** - 显示选中账号的历史数据趋势图

### 🎛️ 交互功能
- 日期范围选择器
- Group 多选筛选（支持模糊匹配）
- 实时数据过滤和更新

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 确保数据文件存在
- `data/redash_data/redash_data_2025-07-08.csv`
- `data/postingManager_data/accounts_detail.xlsx`

### 3. 运行应用

#### 方法一：使用启动脚本（推荐）
```bash
./run_app.sh
```

#### 方法二：直接运行
```bash
streamlit run appDaily.py
```

应用将在浏览器中自动打开，默认地址为 `http://localhost:8501`

## 数据格式要求

### Redash 数据 (CSV)
必须包含以下字段：
- `user_id`: 账号ID
- `date`: 日期 (格式: DD/MM/YY)
- `view_count`: 浏览量
- `like_count`: 点赞数
- `comment_count`: 评论数
- `share_count`: 分享数
- `post_count`: 发帖数
- `view_per_post`: 每帖浏览量
- `like_per_post`: 每帖点赞数
- `comment_per_post`: 每帖评论数
- `share_per_post`: 每帖分享数

### Accounts Detail 数据 (Excel)
必须包含以下字段：
- `Tiktok ID`: 对应 Redash 中的 user_id
- `Groups`: 分组信息

## 使用说明

1. **筛选数据**: 使用侧边栏的日期范围和分组筛选器
2. **查看趋势**: 浏览各种趋势图表了解数据变化
3. **分析效率**: 使用 radio 按钮切换不同的效率指标
4. **导出数据**: 点击下载按钮获取分组表现数据

## 技术栈

- **前端框架**: Streamlit
- **数据处理**: Pandas (通过 `scripts/data_processor.py`)
- **可视化**: Plotly
- **数据格式**: CSV, Excel

## 项目结构

```
RedirectDataAnalysis/
├── dashboard/
│   ├── appDaily.py          # Streamlit 主应用
│   ├── requirements.txt     # 依赖包列表
│   ├── README.md           # 使用说明
│   └── run_app.sh          # 启动脚本
├── scripts/
│   ├── data_processor.py   # TikTok 数据处理类
│   ├── clicks_analyzer.py  # Clicks 数据分析类
│   └── README.md           # 数据处理说明
└── data/
    ├── redash_data/        # Redash 数据
    ├── postingManager_data/ # Accounts Detail 数据
    ├── clicks/             # Clicks 数据
    └── merged_tiktok_data.csv # 合并后的数据
```

## 注意事项

- 确保数据文件路径正确
- 大文件加载可能需要一些时间
- 建议使用现代浏览器以获得最佳体验 