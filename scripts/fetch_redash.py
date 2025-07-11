# scripts/fetch_redash.py

import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# 从环境变量读取配置（推荐方式）
REDASH_API_KEY = os.getenv("REDASH_API_KEY")
REDASH_URL = os.getenv("REDASH_URL")  # 替换为你自己的 Redash 实例地址
QUERY_ID = os.getenv("REDASH_QUERY_ID")  # 替换为你的 Query ID

def fetch_redash_data():
    """从 Redash 拉取指定 query 的 CSV 数据并保存"""
    if not REDASH_API_KEY:
        raise ValueError("请设置环境变量 REDASH_API_KEY")

    export_url = f"{REDASH_URL}/api/queries/{QUERY_ID}/results.csv"
    headers = {"Authorization": f"Key {REDASH_API_KEY}"}

    response = requests.get(export_url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Redash 请求失败：{response.status_code} - {response.text}")

    # 保存为带时间戳的 CSV
    today = datetime.today().strftime("%Y-%m-%d")
    os.makedirs("data/redash_data", exist_ok=True)
    filepath = f"/Users/insnap/Documents/RedirectDataAnalysis/data/redash_data_{today}.csv"

    with open(filepath, "wb") as f:
        f.write(response.content)

    print(f"✅ 数据已保存至：{filepath}")
    return filepath

# 可直接运行测试
if __name__ == "__main__":
    fetch_redash_data()
