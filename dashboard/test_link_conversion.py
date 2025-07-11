#!/usr/bin/env python3
"""
测试链接点击量 & 转化率分析功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from enhanced_data_processor import EnhancedTikTokDataProcessor

def test_link_conversion_analysis():
    """测试链接转化率分析功能"""
    print("🧪 测试链接点击量 & 转化率分析功能")
    
    # 初始化数据处理器
    processor = EnhancedTikTokDataProcessor()
    
    # 合并数据
    if not processor.merge_data():
        print("❌ 数据合并失败")
        return
    
    # 测试链接转化率分析
    print("\n📊 测试链接转化率分析...")
    link_conversion_data = processor.get_link_conversion_analysis()
    
    if link_conversion_data:
        print(f"✅ 成功获取 {len(link_conversion_data)} 个链接的分析数据")
        
        for link_url, analysis_data in link_conversion_data.items():
            print(f"\n🔗 链接: {link_url}")
            print(f"   目标分组: {analysis_data['target_group']}")
            print(f"   总点击量: {analysis_data['total_clicks']:,}")
            print(f"   总浏览量: {analysis_data['total_views']:,}")
            print(f"   平均转化率: {analysis_data['avg_conversion_rate']:.2%}")
            print(f"   最高转化率: {analysis_data['max_conversion_rate']:.2%}")
            print(f"   最低转化率: {analysis_data['min_conversion_rate']:.2%}")
            
            # 显示数据样本
            data = analysis_data['data']
            if not data.empty:
                print(f"   数据行数: {len(data)}")
                print(f"   日期范围: {data['date'].min()} 到 {data['date'].max()}")
                print(f"   数据样本:")
                print(data.head(3).to_string(index=False))
            else:
                print("   ⚠️ 无数据")
    else:
        print("❌ 未获取到链接转化率分析数据")

if __name__ == "__main__":
    test_link_conversion_analysis() 