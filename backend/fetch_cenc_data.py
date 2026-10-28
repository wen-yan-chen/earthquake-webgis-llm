import sqlite3
import requests
from datetime import datetime

URL = "https://api.wolfx.jp/cenc_eqlist.json"
print("正在从 Wolfx 获取 CENC 地震目录...")
resp = requests.get(URL, timeout=30)
raw = resp.json()

entries = [val for key, val in raw.items() if isinstance(val, dict) and key.startswith("No")]
print(f"获取到 {len(entries)} 条 CENC 地震记录。")

conn = sqlite3.connect('earthquake.db')
cursor = conn.cursor()

# 【修改点1】：尝试给表加一个 placeName 字段（如果没加过会报错，忽略即可）
try:
    cursor.execute('ALTER TABLE events ADD COLUMN placeName TEXT')
except sqlite3.OperationalError:
    pass # 字段已存在，跳过

# 清空旧数据
cursor.execute('DELETE FROM events')

inserted = 0
for item in entries:
    try:
        lon = float(item["longitude"])
        lat = float(item["latitude"])
        mag = float(item["magnitude"])
        time_str = item["time"]
        place = item.get("placeName", "未知区域") # 获取地名（如：新疆喀什地区）
    except (KeyError, TypeError, ValueError):
        continue

    cursor.execute(
        'INSERT INTO events (lon, lat, mag, time, placeName) VALUES (?, ?, ?, ?, ?)',
        (lon, lat, mag, time_str, place)
    )
    inserted += 1

conn.commit()
conn.close()
print(f"✅ 已将 {inserted} 条真实数据写入数据库，并包含省份/地名信息！")