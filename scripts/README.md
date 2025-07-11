# TikTok 数据处理脚本

这个目录包含了 TikTok 账号数据分析的数据处理脚本。

## 文件说明

### `data_processor.py`
TikTok 数据处理类，提供以下功能：

### `clicks_analyzer.py`
Clicks 数据分析类，提供以下功能：

#### 主要功能
- **数据加载**: 加载 clicks 数据和合并后的 TikTok 数据
- **Group 映射**: 自动映射 group 到 page_type
- **对比分析**: Clicks vs Views 的对比分析
- **相关性计算**: 计算 clicks 和 views 的相关系数
- **数据聚合**: 按日期和页面类型聚合数据

#### 核心类: `ClicksAnalyzer`

##### 初始化
```python
analyzer = ClicksAnalyzer(
    clicks_file_path='path/to/clicks.csv',
    merged_data_path='path/to/merged_tiktok_data.csv'
)
```

##### 主要方法

1. **load_clicks_data()**
   - 加载 clicks 数据
   - 返回: bool (成功/失败)

2. **load_merged_data()**
   - 加载合并后的 TikTok 数据
   - 返回: bool (成功/失败)

3. **process_clicks_by_group()**
   - 处理 clicks 数据，按 group 和 page_type 聚合
   - 返回: bool (成功/失败)

4. **get_clicks_vs_views_data(page_type)**
   - 获取 clicks vs views 对比数据
   - 返回: pd.DataFrame

5. **calculate_correlation(page_type)**
   - 计算 clicks 和 views 的相关性
   - 返回: float (相关系数)

6. **get_group_mapping_summary()**
   - 获取 group 映射摘要
   - 返回: pd.DataFrame

## 使用示例

### Clicks 分析
```python
from clicks_analyzer import ClicksAnalyzer

# 创建分析器
analyzer = ClicksAnalyzer(
    clicks_file_path='../data/clicks/20250708ClicksInsnap.csv',
    merged_data_path='../data/merged_tiktok_data.csv'
)

# 加载和处理数据
if analyzer.load_clicks_data() and analyzer.load_merged_data():
    if analyzer.process_clicks_by_group():
        # 获取对比数据
        comparison_data = analyzer.get_clicks_vs_views_data('videos')
        
        # 计算相关性
        correlation = analyzer.calculate_correlation('videos')
        print(f"相关系数: {correlation:.4f}")
```

## 数据格式要求

### Clicks 数据 (CSV)
- `timestamp`: 时间戳
- `page_type`: 页面类型 (videos, download 等)
- 其他字段: 根据实际数据文件

### Group 映射规则
- `group` 包含 `'main_avatar'` → `page_type = "videos"`
- `group` 包含 `'wan_produce101'` → `page_type = "download"`
- 其他 group → `page_type = "other"`

---

### `data_processor.py`
TikTok 数据处理类，提供以下功能：

#### 主要功能
- **数据加载**: 加载 redash 数据和 accounts detail 数据
- **数据合并**: 根据 user_id 合并两个数据源
- **数据筛选**: 支持按日期和分组筛选数据
- **统计分析**: 提供各种统计和分析功能
- **数据导出**: 支持保存处理后的数据

#### 核心类: `TikTokDataProcessor`

##### 初始化
```python
processor = TikTokDataProcessor(
    redash_file_path='path/to/redash_data.csv',
    accounts_file_path='path/to/accounts_detail.xlsx'
)
```

##### 主要方法

1. **merge_data()**
   - 合并 redash 数据和 accounts detail 数据
   - 返回: bool (成功/失败)

2. **get_data_summary()**
   - 获取数据摘要信息
   - 返回: dict (包含记录数、账号数、分组数等)

3. **filter_data(start_date, end_date, groups)**
   - 按日期和分组筛选数据
   - 返回: pd.DataFrame

4. **get_daily_aggregates(metrics)**
   - 获取每日聚合数据
   - 返回: pd.DataFrame

5. **get_efficiency_metrics(metric)**
   - 获取效率指标数据
   - 返回: pd.DataFrame

6. **get_group_performance(date)**
   - 获取分组表现数据
   - 返回: pd.DataFrame

7. **save_merged_data(output_path)**
   - 保存合并后的数据
   - 返回: bool

## 使用示例

### 基本使用
```python
from data_processor import TikTokDataProcessor

# 创建处理器
processor = TikTokDataProcessor(
    redash_file_path='../data/redash_data/redash_data_2025-07-08.csv',
    accounts_file_path='../data/postingManager_data/accounts_detail.xlsx'
)

# 合并数据
if processor.merge_data():
    # 获取数据摘要
    summary = processor.get_data_summary()
    print(summary)
    
    # 保存数据
    processor.save_merged_data('../data/merged_tiktok_data.csv')
```

### 数据筛选
```python
# 筛选特定日期范围的数据
filtered_data = processor.filter_data(
    start_date='2025-07-01',
    end_date='2025-07-05',
    groups=['waterworming', 'traffic_seeding']
)
```

### 获取统计信息
```python
# 获取每日聚合数据
daily_data = processor.get_daily_aggregates(['view_count', 'post_count'])

# 获取效率指标
efficiency_data = processor.get_efficiency_metrics('view_per_post')

# 获取分组表现
group_performance = processor.get_group_performance()
```

## 数据格式要求

### Redash 数据 (CSV)
- `user_id`: 账号ID (字符串)
- `date`: 日期 (DD/MM/YY 格式)
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
- `Tiktok ID`: 对应 redash 中的 user_id
- `Groups`: 分组信息

## 输出数据

合并后的数据包含所有原始字段，并添加了 `group` 字段，用于标识每个账号所属的分组。

## 注意事项

1. 确保数据文件路径正确
2. 大文件处理可能需要较长时间
3. 数据类型会自动转换以确保兼容性
4. 缺失的 group 信息会被标记为 'Unknown' 