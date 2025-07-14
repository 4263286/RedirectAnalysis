# 📊 数据更新指南

## 🔄 快速更新方法

### 1. 使用自动化脚本（推荐）

```bash
# 更新单个数据文件
python scripts/update_data.py --redash /path/to/new_redash_data.csv
python scripts/update_data.py --clicks /path/to/new_clicks_data.csv
python scripts/update_data.py --accounts /path/to/new_accounts_data.xlsx

# 一次性更新所有数据
python scripts/update_data.py --all /path/to/redash.csv /path/to/clicks.csv /path/to/accounts.xlsx

# 重启看板应用
python scripts/update_data.py --restart
```

### 2. 手动更新方法

#### 更新 Redash 数据
```bash
# 将新文件复制到 data/redash_data/ 目录
cp your_new_redash_data.csv data/redash_data/redash_data_2025-01-XX.csv
```

#### 更新 Clicks 数据
```bash
# 将新文件复制到 data/clicks/ 目录
cp your_new_clicks_data.csv data/clicks/202501XXClicksInsnap.csv
```

#### 更新 Accounts 数据
```bash
# 替换 accounts detail 文件
cp your_new_accounts_data.xlsx data/postingManager_data/accounts_detail.xlsx
```

### 3. 重新加载看板

#### 方法一：重启应用
```bash
# 停止当前应用 (Ctrl+C)
# 重新启动
cd dashboard
streamlit run enhanced_app.py
```

#### 方法二：清除缓存
1. 在 Streamlit 应用中点击右上角 "⋮" 菜单
2. 选择 "Clear cache"
3. 刷新页面

#### 方法三：使用启动脚本
```bash
./start_enhanced_dashboard.sh
```

## 📁 数据文件结构

```
data/
├── redash_data/
│   ├── redash_data_2025-01-01.csv    # Redash 数据（自动检测最新）
│   └── redash_data_2025-01-02.csv
├── clicks/
│   ├── 20250101ClicksInsnap.csv      # Clicks 数据（自动检测最新）
│   └── 20250102ClicksInsnap.csv
└── postingManager_data/
    └── accounts_detail.xlsx           # Accounts 数据
```

## ✅ 验证更新成功

1. **检查数据概览卡片** - 总记录数、账号数等是否更新
2. **查看日期范围** - 侧边栏日期选择器显示新的日期范围
3. **确认分组列表** - 新的分组信息已加载
4. **查看最新数据** - 图表显示最新的数据趋势

## 🔧 故障排除

### 问题：数据没有更新
- 检查文件路径是否正确
- 确认文件格式是否符合要求
- 清除 Streamlit 缓存后重试

### 问题：应用启动失败
- 检查数据文件是否存在
- 确认文件格式是否正确
- 查看控制台错误信息

### 问题：图表显示异常
- 检查数据是否为空
- 确认数据格式是否正确
- 尝试刷新页面

## 📋 数据格式要求

### Redash 数据 (CSV)
- `user_id`: 账号ID
- `date` 或 `YMDdate`: 日期
- `view_count`: 浏览量
- `like_count`: 点赞数
- `comment_count`: 评论数
- `share_count`: 分享数
- `post_count`: 发帖数
- `view_diff`, `like_diff`, `comment_diff`, `share_diff`, `post_diff`: 增量数据

### Clicks 数据 (CSV)
- `timestamp`: 时间戳
- `page_url`: 页面链接
- `page_type`: 页面类型
- `session_id`: 会话ID
- `visitor_id`: 访客ID

### Accounts 数据 (Excel)
- `Tiktok ID`: 对应 Redash 中的 user_id
- `Groups`: 分组信息

## 🚀 自动化建议

### 定时更新脚本
```bash
# 创建定时任务，每天自动更新数据
crontab -e

# 添加以下行（每天凌晨2点更新）
0 2 * * * cd /path/to/RedirectDataAnalysis && python scripts/update_data.py --all /path/to/redash.csv /path/to/clicks.csv /path/to/accounts.xlsx
```

### 监控脚本
```bash
# 检查数据文件是否更新
python scripts/check_data_freshness.py
```

## 📞 技术支持

如果遇到问题，请检查：
1. 数据文件格式是否正确
2. 文件路径是否存在
3. 应用日志中的错误信息
4. 网络连接是否正常 