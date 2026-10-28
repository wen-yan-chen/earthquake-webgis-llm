import sqlite3
import requests

print("正在获取最新数据，并智能提取中文地名...")
resp = requests.get("https://api.wolfx.jp/cenc_eqlist.json", timeout=30)
raw = resp.json()

entries = [val for key, val in raw.items() if isinstance(val, dict) and key.startswith("No")]

conn = sqlite3.connect('earthquake.db')
cursor = conn.cursor()

# 清空旧数据重新插入
cursor.execute('DELETE FROM events')

inserted = 0
for item in entries:
    try:
        lon = float(item["longitude"])
        lat = float(item["latitude"])
        mag = float(item["magnitude"])
        time_str = item["time"]
        
        # 【暴力破解】：遍历这条地震数据里的所有字段，找包含中文字符的字符串！
        place = "未知区域"
        for key, val in item.items():
            if isinstance(val, str):
                # 如果这个字符串里有中文，并且不是时间格式（不含冒号）
                if any('\u4e00' <= char <= '\u9fff' for char in val) and ":" not in val:
                    place = val
                    break
                    
    except (KeyError, TypeError, ValueError):
        continue

    cursor.execute(
        'INSERT INTO events (lon, lat, mag, time, placeName) VALUES (?, ?, ?, ?, ?)',
        (lon, lat, mag, time_str, place)
    )
    inserted += 1

conn.commit()
conn.close()
print(f"✅ 执行完毕！已更新 {inserted} 条数据。")