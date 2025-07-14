#!/usr/bin/env python3
"""
数据更新脚本
用于自动替换数据文件并重启看板
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
import time

def update_redash_data(new_file_path: str):
    """更新 Redash 数据"""
    target_dir = "data/redash_data"
    os.makedirs(target_dir, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y-%m-%d")
    target_file = os.path.join(target_dir, f"redash_data_{timestamp}.csv")
    
    # 复制文件
    shutil.copy2(new_file_path, target_file)
    print(f"✅ Redash 数据已更新: {target_file}")
    return target_file

def update_clicks_data(new_file_path: str):
    """更新 Clicks 数据"""
    target_dir = "data/clicks"
    os.makedirs(target_dir, exist_ok=True)
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d")
    target_file = os.path.join(target_dir, f"{timestamp}ClicksInsnap.csv")
    
    # 复制文件
    shutil.copy2(new_file_path, target_file)
    print(f"✅ Clicks 数据已更新: {target_file}")
    return target_file

def update_accounts_data(new_file_path: str):
    """更新 Accounts 数据"""
    target_dir = "data/postingManager_data"
    os.makedirs(target_dir, exist_ok=True)
    
    target_file = os.path.join(target_dir, "accounts_detail.xlsx")
    
    # 复制文件
    shutil.copy2(new_file_path, target_file)
    print(f"✅ Accounts 数据已更新: {target_file}")
    return target_file

def restart_dashboard():
    """重启看板应用"""
    print("🔄 重启看板应用...")
    
    # 检查是否有正在运行的 Streamlit 进程
    try:
        result = subprocess.run(['pgrep', '-f', 'streamlit'], capture_output=True, text=True)
        if result.stdout:
            print("⏹️  停止现有 Streamlit 进程...")
            subprocess.run(['pkill', '-f', 'streamlit'])
            time.sleep(2)
    except:
        pass
    
    # 启动新的应用
    try:
        os.chdir("dashboard")
        subprocess.Popen(['streamlit', 'run', 'enhanced_app.py', '--server.port', '8501'])
        print("✅ 看板应用已重启")
        print("🌐 访问地址: http://localhost:8501")
    except Exception as e:
        print(f"❌ 重启失败: {e}")

def main():
    """主函数"""
    print("🔄 TikTok 数据分析看板 - 数据更新工具")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python update_data.py --redash <redash_file>")
        print("  python update_data.py --clicks <clicks_file>")
        print("  python update_data.py --accounts <accounts_file>")
        print("  python update_data.py --all <redash_file> <clicks_file> <accounts_file>")
        print("  python update_data.py --restart")
        return
    
    command = sys.argv[1]
    
    if command == "--redash" and len(sys.argv) >= 3:
        update_redash_data(sys.argv[2])
        
    elif command == "--clicks" and len(sys.argv) >= 3:
        update_clicks_data(sys.argv[2])
        
    elif command == "--accounts" and len(sys.argv) >= 3:
        update_accounts_data(sys.argv[2])
        
    elif command == "--all" and len(sys.argv) >= 5:
        update_redash_data(sys.argv[2])
        update_clicks_data(sys.argv[3])
        update_accounts_data(sys.argv[4])
        
    elif command == "--restart":
        restart_dashboard()
        
    else:
        print("❌ 参数错误，请检查使用方法")
        return
    
    print("\n✅ 数据更新完成！")
    print("💡 提示: 如果看板正在运行，请刷新页面或重启应用以查看最新数据")

if __name__ == "__main__":
    main() 