# 🚀 Streamlit Cloud 部署指南

## 📋 部署前准备

### 1. 确保代码已修复
✅ 已修复 NameError 问题  
✅ 已添加完整的错误处理  
✅ 已创建模拟数据功能  
✅ 已优化数据加载逻辑  

### 2. 检查文件结构
```
RedirectDataAnalysis/
├── dashboard/
│   ├── enhanced_app.py          # 主应用文件
│   ├── test_fix.py             # 测试文件
│   ├── debug_merge.py          # 调试工具
│   └── requirements.txt        # 依赖文件
├── scripts/
│   ├── enhanced_data_processor.py
│   └── enhanced_visualization.py
└── .gitignore
```

## 🌐 Streamlit Cloud 部署步骤

### 步骤 1: 推送代码到 GitHub
```bash
# 确保在项目根目录
cd /Users/insnap/Documents/RedirectDataAnalysis

# 添加所有文件
git add .

# 提交更改
git commit -m "修复NameError和添加模拟数据功能"

# 推送到GitHub
git push origin main
```

### 步骤 2: 在 Streamlit Cloud 中设置 Secrets

1. 登录 [Streamlit Cloud](https://share.streamlit.io/)
2. 创建新应用或编辑现有应用
3. 在应用设置中找到 "Secrets" 部分
4. 添加以下 secrets：

```toml
[secrets]
ACCOUNTS_URL = "https://drive.google.com/uc?export=download&id=YOUR_ACCOUNTS_FILE_ID"
REDASH_URL = "https://drive.google.com/uc?export=download&id=YOUR_REDASH_FILE_ID"
CLICKS_URL = "https://drive.google.com/uc?export=download&id=YOUR_CLICKS_FILE_ID"
```

### 步骤 3: 配置应用设置

- **Main file path**: `dashboard/enhanced_app.py`
- **Python version**: 3.9 或更高
- **Requirements file**: `dashboard/requirements.txt`

## 🔧 本地测试

### 运行调试工具
```bash
cd dashboard
streamlit run debug_merge.py
```

### 运行测试版本
```bash
streamlit run test_fix.py
```

### 运行完整应用
```bash
streamlit run enhanced_app.py
```

## 📊 功能说明

### 本地运行
- ✅ 使用模拟数据进行演示
- ✅ 显示友好的提示信息
- ✅ 测试所有功能模块

### 云端部署
- ✅ 自动从Google Drive加载真实数据
- ✅ 使用Streamlit Secrets保护数据URL
- ✅ 完整的错误处理和调试信息

## 🐛 常见问题解决

### 问题 1: NameError: name 'main' is not defined
**解决方案**: 已修复，移除了对未定义main()函数的调用

### 问题 2: 数据加载失败
**解决方案**: 
- 本地：使用模拟数据
- 云端：检查secrets配置和数据文件URL

### 问题 3: 数据合并失败
**解决方案**: 已添加详细的调试信息和错误处理

### 问题 4: Secrets 未找到
**解决方案**: 
- 本地：正常现象，会使用模拟数据
- 云端：检查secrets.toml配置

## 📈 部署后验证

1. **检查应用是否正常启动**
2. **验证数据加载是否成功**
3. **测试各个功能模块**
4. **检查错误日志**

## 🔄 数据更新流程

1. 更新Google Drive中的数据文件
2. 获取新的直接下载链接
3. 更新Streamlit Cloud中的secrets
4. 重新部署应用

## 📞 技术支持

如果遇到问题：
1. 查看应用日志
2. 运行调试工具 `debug_merge.py`
3. 检查数据文件格式和内容
4. 验证secrets配置

---

**🎉 部署完成后，您的TikTok增强分析看板就可以正常使用了！** 