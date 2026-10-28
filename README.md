\# 🌍 基于 WebGIS 与大语言模型的地震可视化与智能分析平台



本项目是对《基于WebGIS的新疆地震台站与地震事件可视化智能分析平台构建》一文的轻量化复现与扩展。结合了 WebGIS 空间可视化与 LLM（大语言模型）的意图识别能力，实现了地震台站与真实地震目录的多维展示及智能交互。



\## ✨ 核心特性

\- \*\*真实数据驱动\*\*：抓取中国地震台网（CENC）真实地震数据落库 SQLite。

\- \*\*空间计算下推\*\*：利用 SQL 原生 Haversine 公式，直接在数据库层完成球面距离计算。

\- \*\*大模型智能交互\*\*：接入 DeepSeek API (Function Calling)，将自然语言解析为 SQL 查询参数。

\- \*\*高颜值 WebGIS\*\*：基于 Leaflet 构建，支持省份联动、震级分级渲染、点聚合与毛玻璃 UI。



\## 🛠️ 技术栈

\- \*\*前端\*\*：HTML5, Leaflet.js, MarkerCluster

\- \*\*后端\*\*：Python, FastAPI, SQLite3

\- \*\*AI\*\*：DeepSeek API



\## 🚀 快速运行

1\. 安装依赖：`pip install -r requirements.txt`

2\. 进入后端目录并初始化数据库：`cd backend \&\& python init\_db.py \&\& python fetch\_cenc\_data.py`

3\. 启动后端服务：`uvicorn main:app --reload`

4\. 用浏览器打开 `frontend/index.html` 即可体验。



\## 📸 系统截图

\*(把截图放进 docs/figures 里，并像下面这样引用)\*

!\[全局概览](docs/figures/figure1.png)

!\[AI智能查询](docs/figures/figure2.png)

