#!/usr/bin/env python3
"""
增强版功能测试脚本
测试新的数据处理器和可视化工具
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(parent_dir, 'config'))

def test_enhanced_data_processor():
    """测试增强版数据处理器"""
    print("🧪 测试增强版数据处理器...")
    
    try:
        from enhanced_data_processor import EnhancedTikTokDataProcessor
        
        # 创建处理器实例
        processor = EnhancedTikTokDataProcessor()
        print("✅ 处理器实例创建成功")
        
        # 测试数据加载
        print("📊 测试数据加载...")
        
        # 测试 redash 数据加载
        redash_df = processor.load_latest_redash_data()
        if redash_df is not None:
            print(f"✅ Redash 数据加载成功: {redash_df.shape}")
        else:
            print("⚠️  Redash 数据加载失败（可能是文件不存在）")
        
        # 测试 accounts 数据加载
        group_mapping = processor.load_accounts_data()
        if group_mapping is not None:
            print(f"✅ Accounts 数据加载成功: {group_mapping.shape}")
        else:
            print("⚠️  Accounts 数据加载失败（可能是文件不存在）")
        
        # 测试 clicks 数据加载
        clicks_df = processor.load_clicks_data()
        if clicks_df is not None:
            print(f"✅ Clicks 数据加载成功: {clicks_df.shape}")
        else:
            print("⚠️  Clicks 数据加载失败（可能是文件不存在）")
        
        # 测试数据合并
        print("🔄 测试数据合并...")
        if redash_df is not None and group_mapping is not None:
            success = processor.merge_data()
            if success:
                print("✅ 数据合并成功")
                
                # 测试分组获取
                groups = processor.get_available_groups()
                print(f"✅ 可用分组: {len(groups)} 个")
                if groups:
                    print(f"   示例分组: {groups[:5]}")
                
                # 测试数据摘要
                summary = processor.get_data_summary()
                if summary:
                    print("✅ 数据摘要获取成功")
                    print(f"   总记录数: {summary.get('total_records', 0)}")
                    print(f"   账号数量: {summary.get('unique_accounts', 0)}")
                    print(f"   分组数量: {summary.get('unique_groups', 0)}")
            else:
                print("❌ 数据合并失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强版数据处理器测试失败: {str(e)}")
        return False

def test_enhanced_visualization():
    """测试增强版可视化工具"""
    print("\n🎨 测试增强版可视化工具...")
    
    try:
        from enhanced_visualization import EnhancedVisualization
        
        # 创建可视化工具实例
        viz = EnhancedVisualization()
        print("✅ 可视化工具实例创建成功")
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=10),
            'view_count': [100, 120, 150, 180, 200, 220, 250, 280, 300, 320],
            'like_count': [10, 12, 15, 18, 20, 22, 25, 28, 30, 32],
            'group': ['group1', 'group2'] * 5
        })
        
        # 测试图表创建
        print("📈 测试图表创建...")
        
        # 测试每日趋势图
        trend_chart = viz.create_daily_trend_chart(test_data, 'view_count', '测试趋势图')
        print("✅ 每日趋势图创建成功")
        
        # 测试分组对比图
        group_data = test_data.groupby('group')['view_count'].sum().reset_index()
        comparison_chart = viz.create_group_comparison_chart(group_data, 'view_count', '测试对比图')
        print("✅ 分组对比图创建成功")
        
        # 测试堆叠面积图
        stacked_chart = viz.create_stacked_area_chart(test_data, 'view_count', '测试堆叠图')
        print("✅ 堆叠面积图创建成功")
        
        # 测试摘要卡片
        summary_data = {
            'total_records': 1000,
            'unique_accounts': 100,
            'unique_groups': 10
        }
        summary_html = viz.create_summary_cards(summary_data)
        print("✅ 摘要卡片创建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强版可视化工具测试失败: {str(e)}")
        return False

def test_link_group_mapping():
    """测试链接分组映射"""
    print("\n🔗 测试链接分组映射...")
    
    try:
        from link_group_mapping import get_group_by_link, get_all_mappings, get_mapping_statistics
        
        # 测试链接映射
        test_urls = [
            'https://insnap.ai/videos',
            'https://insnap.ai/zh/download',
            'https://insnap.ai/influencers',
            'https://example.com/unknown'
        ]
        
        for url in test_urls:
            group = get_group_by_link(url)
            print(f"   链接: {url} → 分组: {group}")
        
        # 测试映射统计
        stats = get_mapping_statistics()
        print(f"✅ 映射统计: {stats}")
        
        # 测试所有映射
        mappings = get_all_mappings()
        print(f"✅ 映射配置: {len(mappings['link_mappings'])} 个链接映射")
        
        return True
        
    except Exception as e:
        print(f"❌ 链接分组映射测试失败: {str(e)}")
        return False

def test_enhanced_app_import():
    """测试增强版应用导入"""
    print("\n🚀 测试增强版应用导入...")
    
    try:
        # 设置路径
        dashboard_dir = os.path.join(parent_dir, 'dashboard')
        sys.path.insert(0, dashboard_dir)
        
        # 尝试导入应用（不运行）
        import enhanced_app
        print("✅ 增强版应用导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强版应用导入失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🧪 开始增强版功能测试...\n")
    
    tests = [
        ("增强版数据处理器", test_enhanced_data_processor),
        ("增强版可视化工具", test_enhanced_visualization),
        ("链接分组映射", test_link_group_mapping),
        ("增强版应用导入", test_enhanced_app_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🔍 测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            results.append((test_name, False))
        print()
    
    # 输出测试结果
    print("📊 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！增强版功能准备就绪。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关配置。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 