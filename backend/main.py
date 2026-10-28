import sqlite3
import math
import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ================= 数据库连接辅助函数 =================
def get_db():
    # row_factory 让返回的数据像字典一样，可以用 row['name'] 访问
    conn = sqlite3.connect('earthquake.db')
    conn.row_factory = sqlite3.Row
    return conn

# SQL 里面的 Haversine 距离公式（计算两点间球面距离，单位：公里）
HAVERSINE_SQL = """
    (6371 * acos(
        cos(radians(?)) * cos(radians(lat)) * cos(radians(lon) - radians(?)) 
        + sin(radians(?)) * sin(radians(lat))
    ))
"""

# ================= 1. 获取台站 =================
@app.get("/stations")
def get_stations():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM stations")
    rows = cursor.fetchall()
    conn.close()
    
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature",
             "properties": {"name": r["name"], "type": r["type"], "instrument": r["instrument"], "ip": r["ip"]},
             "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]}}
            for r in rows
        ]
    }

# ================= 2. 获取/查询地震 =================
@app.get("/events")
def get_events(center_lon: float = None, center_lat: float = None, radius_km: float = None, days: int = None, province: str = None):
    conn = get_db()
    cursor = conn.cursor()
    
    sql = "SELECT * FROM events WHERE 1=1"
    params = []

    if province and province != "全部":
        sql += " AND placeName LIKE ?"
        params.append(f"%{province}%")

    if center_lon is not None and center_lat is not None and radius_km is not None:
        sql += f" AND {HAVERSINE_SQL} <= ?"
        params.extend([center_lat, center_lon, center_lat, radius_km])

    if days is not None:
        sql += " AND time >= datetime('now', 'localtime', ?)"
        params.append(f'-{days} days')

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    features = []
    for r in rows:
        # 【核心修改点】：自动兜底地名
        place = r["placeName"]
        if not place or place in ["未知区域", "undefined", "null"]:
            place = f"东经{r['lon']:.1f}° 北纬{r['lat']:.1f}°"
            
        features.append({
            "type": "Feature",
            "properties": {
                "mag": r["mag"], 
                "time": r["time"], 
                "place": place
            },
            "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]}
        })

    return {"type": "FeatureCollection", "features": features}
# ================= 3. 大模型 AI 查询 =================
client = OpenAI(api_key="sk-a2ce43c06ef84e7e87a4584886f77acb", base_url="https://api.deepseek.com")

tools = [{
    "type": "function",
    "function": {
        "name": "query_events_near_station",
        "description": "查询某个地震台站周边一定半径内、最近若干天的地震事件",
        "parameters": {
            "type": "object",
            "properties": {
                "station_name": {"type": "string", "description": "地震台站名称，必须是给定列表中的一个"},
                "radius_km": {"type": "number", "description": "缓冲半径，单位公里"},
                "days": {"type": "integer", "description": "查询最近多少天"}
            },
            "required": ["station_name", "radius_km", "days"]
        }
    }
}]

@app.post("/ai-query")
async def ai_query(body: dict):
    user_text = body.get("text", "")
    
    # 从数据库动态获取台站名称列表
    conn = get_db()
    stations = conn.execute("SELECT name, lon, lat FROM stations").fetchall()
    conn.close()
    station_names = [s["name"] for s in stations]
    
    try:
        resp = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"你是地震查询助手。可用的台站有：{station_names}。请根据用户输入调用函数。"},
                {"role": "user", "content": user_text}
            ],
            tools=tools,
            temperature=0.1
        )
        
        tool_call = resp.choices[0].message.tool_calls
        if not tool_call:
            return {"error": "模型没有调用工具", "raw": resp.choices[0].message.content}
            
        args = json.loads(tool_call[0].function.arguments)
        
        # 匹配台站经纬度
        station = next((s for s in stations if s["name"] == args["station_name"]), None)
        if not station:
            return {"error": f"找不到台站：{args['station_name']}"}
            
        # 调用上面写好的空间查询接口
        events_geojson = get_events(
            center_lon=station["lon"], 
            center_lat=station["lat"],
            radius_km=args["radius_km"], 
            days=args["days"]
        )
        
        return {"params": args, "events": events_geojson}
        
    except Exception as e:
        return {"error": f"后端大模型调用失败: {str(e)}"}
