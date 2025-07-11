#!/usr/bin/env python3
"""
简化的功能测试脚本
"""

import sys
import os
import pandas as pd

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_data_loading():
    """测试基本数据加载功能"""
    print("🚀 测试基本数据加载功能...")
    
    # 测试 CSV 数据加载
    try:
        df = pd.read_csv("data/merged_tiktok_data.csv")
        print(f"✅ CSV 数据加载成功: {df.shape}")
        print(f"   - 列名: {list(df.columns)}")
        print(f"   - 日期范围: {df['date'].min()} 到 {df['date'].max()}")
        print(f"   - 分组数量: {df['group'].nunique()}")
        return df
    except Exception as e:
        print(f"❌ CSV 数据加载失败: {e}")
        return None

def test_accounts_data():
    """测试账号数据加载"""
    print("\n📊 测试账号数据加载...")
    
    try:
        accounts_df = pd.read_excel("data/postingManager_data/accounts_detail.xlsx")
        print(f"✅ 账号数据加载成功: {accounts_df.shape}")
        print(f"   - 关键列: {[col for col in accounts_df.columns if 'Tiktok' in col or 'Followers' in col or 'Like' in col]}")
        return accounts_df
    except Exception as e:
        print(f"❌ 账号数据加载失败: {e}")
        return None

def test_clicks_data():
    """测试 Clicks 数据加载"""
    print("\n🖱️ 测试 Clicks 数据加载...")
    
    try:
        clicks_df = pd.read_csv("data/clicks/20250708ClicksInsnap.csv")
        print(f"✅ Clicks 数据加载成功: {clicks_df.shape}")
        print(f"   - 列名: {list(clicks_df.columns)}")
        print(f"   - 页面类型: {clicks_df['page_type'].unique()}")
        print(f"   - 独立访客: {clicks_df['visitor_id'].nunique()}")
        print(f"   - 会话数: {clicks_df['session_id'].nunique()}")
        return clicks_df
    except Exception as e:
        print(f"❌ Clicks 数据加载失败: {e}")
        return None

def test_enhanced_features():
    """测试增强功能"""
    print("\n🔧 测试增强功能...")
    
    # 加载数据
    df = test_basic_data_loading()
    accounts_df = test_accounts_data()
    clicks_df = test_clicks_data()
    
    if df is None or accounts_df is None or clicks_df is None:
        print("❌ 基础数据加载失败，无法测试增强功能")
        return False
    
    # 测试账号详情功能
    print("\n👤 测试账号详情功能...")
    try:
        # 获取一些用户ID
        user_ids = df['user_id'].unique()[:5]
        print(f"   - 测试用户ID: {user_ids}")
        
        # 从账号数据中查找这些用户
        account_details = accounts_df[accounts_df['KOL ID'].astype(str).isin([str(uid) for uid in user_ids])]
        print(f"   - 找到 {len(account_details)} 个匹配的账号")
        
        if not account_details.empty:
            print(f"   - 包含 TikTok 用户名: {'Tiktok Username' in account_details.columns}")
            print(f"   - 包含粉丝数: {'Total Followers' in account_details.columns}")
    except Exception as e:
        print(f"   ❌ 账号详情功能测试失败: {e}")
    
    # 测试 Clicks 关键指标
    print("\n📈 测试 Clicks 关键指标...")
    try:
        metrics = {
            'total_clicks': len(clicks_df),
            'unique_visits': clicks_df['visitor_id'].nunique(),
            'page_visits': clicks_df['session_id'].nunique(),
            'unique_pages': clicks_df['page_type'].nunique()
        }
        print(f"   - 总点击量: {metrics['total_clicks']:,}")
        print(f"   - 独立访客: {metrics['unique_visits']:,}")
        print(f"   - 页面访问: {metrics['page_visits']:,}")
        print(f"   - 页面类型: {metrics['unique_pages']}")
    except Exception as e:
        print(f"   ❌ Clicks 关键指标测试失败: {e}")
    
    # 测试每日汇总指标
    print("\n📊 测试每日汇总指标...")
    try:
        latest_date = df['date'].max()
        daily_data = df[df['date'] == latest_date]
        
        summary = {
            'total_posts': daily_data['post_diff'].sum(),
            'total_views': daily_data['view_diff'].sum(),
            'total_likes': daily_data['like_diff'].sum(),
            'total_comments': daily_data['comment_diff'].sum(),
            'total_shares': daily_data['share_diff'].sum(),
            'active_accounts': len(daily_data['user_id'].unique())
        }
        
        print(f"   - 日期: {latest_date}")
        print(f"   - 总发帖数: {summary['total_posts']:,}")
        print(f"   - 总浏览量: {summary['total_views']:,}")
        print(f"   - 活跃账号: {summary['active_accounts']:,}")
    except Exception as e:
        print(f"   ❌ 每日汇总指标测试失败: {e}")
    
    # 测试效率分布
    print("\n🎯 测试效率分布...")
    try:
        daily_data = df[df['date'] == latest_date].copy()
        daily_data['efficiency'] = daily_data['view_diff'] / daily_data['post_diff'].replace(0, 1)
        
        efficiency_by_group = daily_data.groupby('group')['efficiency'].agg(['mean', 'median', 'count']).reset_index()
        print(f"   - 效率分布计算成功，包含 {len(efficiency_by_group)} 个分组")
        print(f"   - 最佳效率分组: {efficiency_by_group.loc[efficiency_by_group['mean'].idxmax(), 'group']}")
    except Exception as e:
        print(f"   ❌ 效率分布测试失败: {e}")
    
    # 测试 CVR 分析
    print("\n🔄 测试 CVR 分析...")
    try:
        # 按分组聚合 TikTok 数据
        tiktok_by_group = daily_data.groupby('group').agg({
            'view_diff': 'sum',
            'user_id': 'nunique'
        }).reset_index()
        
        # 按页面类型聚合 clicks 数据
        clicks_by_page = clicks_df.groupby('page_type').size().reset_index(name='click_count')
        
        print(f"   - TikTok 分组数据: {len(tiktok_by_group)} 个分组")
        print(f"   - Clicks 页面数据: {len(clicks_by_page)} 个页面类型")
    except Exception as e:
        print(f"   ❌ CVR 分析测试失败: {e}")
    
    print("\n🎉 增强功能测试完成！")
    return True

if __name__ == "__main__":
    test_enhanced_features() 