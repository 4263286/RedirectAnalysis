"""
测试新架构的功能
验证映射配置、数据处理和可视化工具
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))
sys.path.append(os.path.dirname(__file__))

def test_mapping_config():
    """测试映射配置功能"""
    print("🔧 测试映射配置功能...")
    
    try:
        from group_click_map import (
            get_page_type_for_group,
            get_all_mappings,
            get_mapping_statistics,
            add_mapping_rule,
            remove_mapping_rule
        )
        
        # 测试基本映射
        assert get_page_type_for_group("main_avatar") == "videos"
        assert get_page_type_for_group("wan_produce101") == "download"
        assert get_page_type_for_group("unknown_group") == "other"
        
        # 测试获取所有映射
        mappings = get_all_mappings()
        assert 'mappings' in mappings
        assert 'descriptions' in mappings
        assert 'reverse_mappings' in mappings
        
        # 测试统计信息
        stats = get_mapping_statistics()
        assert 'total_mappings' in stats
        assert 'page_types' in stats
        assert 'groups' in stats
        
        # 测试添加新映射
        add_mapping_rule("test_group", "videos", "测试分组")
        assert get_page_type_for_group("test_group") == "videos"
        
        # 测试删除映射
        remove_mapping_rule("test_group")
        assert get_page_type_for_group("test_group") == "other"
        
        print("✅ 映射配置功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 映射配置功能测试失败: {str(e)}")
        return False

def test_data_processor():
    """测试数据处理器功能"""
    print("📊 测试数据处理器功能...")
    
    try:
        from data_processor import TikTokDataProcessor
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5),
            'user_id': ['user1', 'user2', 'user3', 'user4', 'user5'],
            'group': ['main_avatar', 'wan_produce101', 'main_avatar', 'test_group', 'wan_produce101'],
            'view_diff': [100, 200, 150, 80, 300],
            'like_diff': [10, 20, 15, 8, 30],
            'comment_diff': [5, 10, 7, 4, 15],
            'share_diff': [2, 5, 3, 1, 8]
        })
        
        # 测试新方法
        processor = TikTokDataProcessor(
            redash_file_path='data/redash_data/redash_data_2025-07-08.csv',
            accounts_file_path='data/postingManager_data/accounts_detail.xlsx'
        )
        processor.merged_df = test_data
        
        # 测试获取账号排名
        ranking = processor.get_account_performance_ranking(metric='view_diff', top_n=3)
        if ranking is not None:
            assert len(ranking) == 3
            assert ranking.iloc[0]['view_diff'] == 300  # 最大值应该在第一位
        
        # 测试获取分组趋势
        trend = processor.get_group_performance_trend('main_avatar')
        if trend is not None:
            assert len(trend) > 0
            assert 'view_diff' in trend.columns
        
        # 测试获取指标汇总
        summary = processor.get_diff_metrics_summary()
        if summary is not None:
            assert len(summary) > 0
            assert 'group' in summary.columns
        
        print("✅ 数据处理器功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 数据处理器功能测试失败: {str(e)}")
        return False

def test_visualization_utils():
    """测试可视化工具功能"""
    print("📈 测试可视化工具功能...")
    
    try:
        from visualization_utils import (
            plot_diff_metrics_trend,
            plot_correlation_scatter,
            plot_comparison_line,
            plot_account_history,
            plot_group_performance_table,
            plot_top_accounts_ranking,
            create_metric_summary_card
        )
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5),
            'view_diff': [100, 200, 150, 80, 300],
            'like_diff': [10, 20, 15, 8, 30],
            'comment_diff': [5, 10, 7, 4, 15],
            'share_diff': [2, 5, 3, 1, 8]
        })
        
        # 测试趋势图
        fig1 = plot_diff_metrics_trend(test_data)
        assert fig1 is not None
        
        # 测试散点图
        fig2 = plot_correlation_scatter(test_data, 'view_diff', 'like_diff')
        assert fig2 is not None
        
        # 测试对比图
        fig3 = plot_comparison_line(test_data, 'date', 'view_diff', 'like_diff')
        assert fig3 is not None
        
        # 测试账号历史图
        account_data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5),
            'view_diff': [100, 200, 150, 80, 300],
            'like_diff': [10, 20, 15, 8, 30],
            'comment_diff': [5, 10, 7, 4, 15],
            'share_diff': [2, 5, 3, 1, 8]
        })
        fig4 = plot_account_history(account_data, 'test_user')
        assert fig4 is not None
        
        # 测试分组表现表格
        group_data = pd.DataFrame({
            'group': ['group1', 'group2'],
            'view_diff': [1000, 2000],
            'like_diff': [100, 200]
        })
        fig5 = plot_group_performance_table(group_data)
        assert fig5 is not None
        
        # 测试账号排名图
        ranking_data = pd.DataFrame({
            'user_id': ['user1', 'user2', 'user3'],
            'group': ['group1', 'group2', 'group1'],
            'view_diff': [300, 200, 100]
        })
        fig6 = plot_top_accounts_ranking(ranking_data)
        assert fig6 is not None
        
        # 测试指标卡片
        card_html = create_metric_summary_card("测试指标", 1000, 100, "positive")
        assert "测试指标" in card_html
        assert "1,000" in card_html
        
        print("✅ 可视化工具功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 可视化工具功能测试失败: {str(e)}")
        return False

def test_clicks_analyzer():
    """测试 Clicks 分析器功能"""
    print("🔁 测试 Clicks 分析器功能...")
    
    try:
        from clicks_analyzer import ClicksAnalyzer
        
        # 创建测试数据
        clicks_data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5),
            'group': ['main_avatar', 'wan_produce101', 'main_avatar', 'test_group', 'wan_produce101'],
            'page_type': ['videos', 'download', 'videos', 'other', 'download'],
            'click_count': [50, 100, 75, 25, 150]
        })
        
        merged_data = pd.DataFrame({
            'date': pd.date_range('2025-01-01', periods=5),
            'group': ['main_avatar', 'wan_produce101', 'main_avatar', 'test_group', 'wan_produce101'],
            'view_diff': [100, 200, 150, 80, 300]
        })
        
        # 测试分析器
        analyzer = ClicksAnalyzer(
            clicks_file_path='data/clicks/20250708ClicksInsnap.csv',
            merged_data_path='data/merged_tiktok_data.csv'
        )
        analyzer.clicks_df = clicks_data
        analyzer.merged_df = merged_data
        
        # 测试处理功能
        result = analyzer.process_clicks_by_group()
        assert result is True
        
        # 测试获取映射信息
        mapping_info = analyzer.get_mapping_config_info()
        assert mapping_info is not None
        assert 'mappings' in mapping_info
        
        print("✅ Clicks 分析器功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ Clicks 分析器功能测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试新架构功能...")
    print("=" * 50)
    
    tests = [
        test_mapping_config,
        test_data_processor,
        test_visualization_utils,
        test_clicks_analyzer
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！新架构功能正常")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    main() 