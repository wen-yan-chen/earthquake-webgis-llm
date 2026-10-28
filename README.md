# 基于 WebGIS 与大语言模型的地震台站与事件可视化智能分析平台

![Python](https://img.shields.io/badge/Python-3.12-blue)
![WebGIS](https://img.shields.io/badge/WebGIS-Leaflet-green)
![Backend](https://img.shields.io/badge/Backend-FastAPI-teal)
![LLM](https://img.shields.io/badge/LLM-DeepSeek-orange)
![Domain](https://img.shields.io/badge/Domain-Seismic-red)

这是一个基于 WebGIS 与大语言模型（LLM）的地震数据可视化与智能查询小科研实践项目。本项目复现并验证了李栋等（2026）《基于WebGIS的新疆地震台站与地震事件可视化智能分析平台构建》一文中的核心思想，实现了一个 **“真实数据抓取 + SQL空间计算下推 + LLM意图解析”** 的全栈轻量级闭环系统。

## 项目背景

在现代地震监测网络中，产生了海量、实时、空间分散的观测数据。现有业务软件多侧重于单台波形分析，缺乏对区域宏观态势的直观展示；同时，复杂的空间查询（如“查询某台站周边 X 公里内的地震”）对非专业运维人员门槛较高。本项目通过轻量级技术栈，复现了从 **“前端地图渲染”** 到 **“大模型自然语言转空间 SQL”** 的完整数据流。

## 核心特性

*   **真实数据驱动**：自动抓取中国地震台网（CENC）的真实地震目录数据，并持久化至 SQLite 数据库。
*   **空间计算下推（SQL Haversine）**：抛弃传统的内存循环计算，直接在 SQL 语句中编写球面距离公式，让数据库引擎完成“周边范围”的高效空间过滤，完美复刻 PostGIS 的 `ST_DWithin` 功能。
*   **大模型自然语言交互**：接入 DeepSeek API（Function Calling），将用户输入的自然语言指令精准提取为结构化参数（台站名、半径、天数），自动生成查询结果并在地图上联动渲染。
*   **高颜值可视化大屏**：基于 Leaflet 构建，支持毛玻璃悬浮面板拖拽、省份下拉联动过滤、震级分级颜色渲染（红/橙/绿）及海量点的 MarkerCluster 聚合。

## 目录结构

```text
├── backend/                 # 后端代码目录
│   ├── main.py              # FastAPI 主程序 (包含 AI 接口与空间查询接口)
│   ├── init_db.py           # 初始化 SQLite 数据库与台站表
│   ├── fetch_cenc_data.py   # 爬取中国地震台网真实数据并清洗落库
│   └── fix_name_final.py    # 地名缺失修复/兜底处理脚本
├── frontend/                # 前端代码目录
│   └── index.html           # 地图渲染、交互 UI 与 ECharts/Leaflet 逻辑
├── docs/                    # 文档与素材目录
│   ├── figures/             # README 及报告截图
│   └── document.pdf         # LaTeX 实验报告源码及编译 PDF
├── requirements.txt         # Python 依赖包列表
└── README.md                # 项目说明文档
```

## 快速开始

### 1. 环境准备

安装所需的 Python 依赖：

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

本项目默认使用 DeepSeek API。请务必使用环境变量，不要在代码中硬编码真实的 API Key！

Windows (PowerShell):

```powershell
$env:DEEPSEEK_API_KEY="sk-你的真实API密钥"
```

Mac/Linux:

```bash
export DEEPSEEK_API_KEY="sk-你的真实API密钥"
```

> 注：请确保 `main.py` 中读取的是 `os.getenv("DEEPSEEK_API_KEY")`。

### 3. 初始化数据与启动

```bash
# 进入后端目录
cd backend

# 初始化数据库
python init_db.py

# 抓取真实地震数据
python fetch_cenc_data.py

# 启动后端服务
uvicorn main:app --reload
```

### 4. 前端运行

后端启动成功后，直接用浏览器打开 `frontend/index.html` 即可看到地图与交互大屏。

## 实验结果与效果

通过引入 DeepSeek 的 Function Calling 能力，系统成功突破了传统 WebGIS 只能依赖表单查询的局限。

| 查询方式 | 响应速度 | 用户操作门槛 | 空间计算性能 |
| --- | --- | --- | --- |
| 传统表单查询 | 依赖 SQL 优化 | 需手动输入经纬度或选择行政区 | 依赖 PostGIS 空间索引 |
| 纯 LLM 对话 (无工具) | 较慢（易幻觉） | 极低 | 无法直接执行空间计算 |
| 本系统 (LLM+SQL下推) | < 2秒 (含AI推理) | 极低 (一句话) | 极优 (SQL引擎直接过滤) |

> 注：AI 的具体意图识别表现受模型版本和温度参数影响。测试中如遇地名缺失，系统自动兜底显示为“东经XX° 北纬XX°”。

## 科研反思与局限（Critical Thinking）

在复现和实验过程中，我们发现了一些值得进一步研究的痛点：

1.  **数据库性能瓶颈**：小规模数据下，SQLite + 内存计算 Haversine 表现优异；但若数据量达到论文中的千万级，轻量级方案将遇到瓶颈，必须迁移至 PostgreSQL + PostGIS。

2.  **AI 意图理解的边界**：大模型偶尔会将模糊词（如“附近”）解析为固定数值（如 50km），这在一定程度上引入了不可控性，需要对 Prompt 进行严格的边界约束。

3.  **地理坐标系偏移**：前端使用的高德/极简瓦片底图属于 GCJ-02 坐标系，而后端数据库使用的是 WGS84 坐标系。为实现精准匹配，实际工程中往往需要引入坐标纠偏算法。

## 参考文献

李栋, 邓耀华, 王欣, 等. (2026). 基于WebGIS的新疆地震台站与地震事件可视化智能分析平台构建. 内陆地震.

Chen C, Ma W L, Gao C L, et al. (2025). GaussDB-AISQL: a composable cloud-native SQL system with AI capabilities. Frontiers of Computer Science.

## 许可证

本项目采用 MIT License。代码与 LaTeX 报告仅供学习和科研交流使用。
