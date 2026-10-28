import sqlite3
import os
from datetime import datetime

# 👇 【物理删除大法】：不管文件在不在，直接干掉，保证是全新的！
if os.path.exists('earthquake.db'):
    try:
        os.remove('earthquake.db')
        print("🗑️ 检测到旧数据库，已从硬盘上物理删除！")
    except PermissionError:
        print("❌ 删除失败！说明数据库还被占用。请务必确认终端里没有在跑 uvicorn，也没有其他 Python 脚本在运行！")
        exit()

# 重新连接（因为文件刚被删，这里会自动建一个全新的空库）
conn = sqlite3.connect('earthquake.db')
cursor = conn.cursor()

# 创建台站表（8列）
cursor.execute('''
CREATE TABLE stations (
    id INTEGER PRIMARY KEY,
    name TEXT,
    lon REAL,
    lat REAL,
    type TEXT,
    instrument TEXT,
    ip TEXT,
    province TEXT
)
''')

# 插入台站数据
stations = [
    (1, "喀什基准台", 75.99, 39.47, "基准站", "STS-2", "10.0.1.11", "新疆"),
    (2, "乌鲁木齐台", 87.62, 43.82, "一般站", "CMG-3T", "10.0.1.12", "新疆"),
    (3, "和田台", 79.92, 37.11, "一般站", "FSS-3DBH", "10.0.1.13", "新疆"),
    (4, "库尔勒台", 86.15, 41.76, "基本站", "STS-2", "10.0.1.14", "新疆"),
    (5, "伊宁台", 81.32, 43.92, "一般站", "CMG-3T", "10.0.1.15", "新疆"),
    (6, "成都基准台", 104.06, 30.67, "基准站", "STS-2", "10.0.2.11", "四川"),
    (7, "西昌台", 102.26, 27.89, "一般站", "CMG-3T", "10.0.2.12", "四川"),
    (8, "昆明基准台", 102.71, 25.04, "基准站", "STS-2", "10.0.3.11", "云南"),
    (9, "大理台", 100.23, 25.59, "一般站", "FSS-3DBH", "10.0.3.12", "云南"),
    (10, "拉萨基准台", 91.13, 29.65, "基准站", "STS-2", "10.0.4.11", "西藏"),
    (11, "西宁台", 101.77, 36.62, "一般站", "CMG-3T", "10.0.5.11", "青海"),
    (12, "兰州台", 103.83, 36.06, "基本站", "STS-2", "10.0.6.11", "甘肃")
]
cursor.executemany('INSERT INTO stations VALUES (?, ?, ?, ?, ?, ?, ?, ?)', stations)

# 顺便建好地震表（为了防呆，虽然 fetch 脚本里也会建）
cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lon REAL,
    lat REAL,
    mag REAL,
    time TEXT,
    placeName TEXT
)
''')

conn.commit()
conn.close()
print("✅ 全新数据库创建成功！台站数据已写入！")