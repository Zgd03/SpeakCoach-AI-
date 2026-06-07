# SpeakCoach AI — 英语口语练习工具

七牛云第三期比赛题目1
demo视频介绍：https://www.bilibili.com/video/BV1CVEh6zEGv/
基于 AI 的英语口语对话练习工具，支持多种真实场景的语音交互训练，提供实时纠错、评分分析和课后总结。

## 功能特性

### 🎯 场景练习
- **3 个内置场景**：面试、餐厅点餐、商务会议，覆盖不同难度级别
- **自定义场景**：用户可创建自己的口语练习场景，自定义 AI 角色设定
- 每个场景预设开场白，进入即练

### 🎤 语音交互
- **按住说话**：长按录音，松开发送，模拟真实对话节奏
- **连续语音识别**：基于浏览器 Web Speech API，支持多人对话场景
- **AI 语音回复**：使用 edge-tts 将 AI 回复转为自然语音播放
- **音频队列**：顺序播放防止音频重叠，支持重新播放

### 🤖 AI 教练 (DeepSeek)
- **实时对话**：WebSocket 全双工通信，毫秒级延迟
- **智能纠错**：每次回复附带语法/表达/用词/发音纠错（中文解释）
- **实时评分**：语法、流利度、词汇三维度评分
- **场景感知**：AI 根据场景角色设定（面试官/服务员/同事）扮演对应角色

### 📊 学习分析
- **课后总结**：AI 自动生成综合评分、优劣势分析、改进建议
- **对话校正**：逐句对比原文与修正，附带详细解释
- **导出报告**：一键导出 Markdown 格式学习报告

### 📋 历史管理
- 分页浏览历史练习记录
- 一键删除不需要的记录
- 随时查看历史总结报告

## 项目截图

| 功能 | 描述 |
|------|------|
| 🏠 **首页** | 场景选择列表 + 自定义场景创建 |
| 💬 **对话页** | 实时语音对话 + 纠错面板 + 评分条 |
| 📊 **总结页** | 综合评分 + 维度分析 + 导出报告 |
| 📋 **历史页** | 练习记录列表 + 分页加载 + 删除 |

## 技术栈

### 前端

| 技术 | 用途 |
|------|------|
| **Vue 3** (Composition API + `<script setup>`) | 前端框架 |
| **Vite** | 构建工具 |
| **Vue Router 4** | 路由管理 (4 个页面) |
| **Axios** | HTTP 请求 |
| **Web Speech API** | 语音识别（英文 en-US） |
| **WebSocket** | 实时通信 |
| **edge-tts**（后端调用） | 语音合成 |

### 后端

| 技术 | 用途 |
|------|------|
| **Python FastAPI** | Web 框架 + WebSocket |
| **SQLAlchemy 2.0** | ORM |
| **SQLite** | 数据库 |
| **httpx** | 异步 HTTP 客户端（调用 DeepSeek API） |
| **DeepSeek API** | AI 对话 + 纠错 + 评分 + 总结 |
| **edge-tts** | 文字转语音 |

## 快速开始

### 前置要求

- Python 3.10+
- Node.js 18+
- DeepSeek API Key

### 1. 克隆项目

```bash
git clone https://github.com/your-username/SpeakCoach-AI.git
cd SpeakCoach-AI
```

### 2. 后端配置

```bash
cd backend

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 DeepSeek API Key
#    DEEPSEEK_API_KEY=sk-your-key-here
#    DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
#    DEEPSEEK_MODEL=deepseek-chat

# 安装依赖
pip install -r requirements.txt

# 初始化场景数据（3 个内置场景）
python -m app.seed

# 启动后端
uvicorn app.main:app --reload
```

后端运行在 http://localhost:8000

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173

### 4. 使用

1. 打开浏览器访问 http://localhost:5173
2. 选择一个场景（面试/餐厅/会议）或创建自定义场景
3. 按住 🎤 按钮开始说话，松开发送
4. AI 自动回复、纠错并评分
5. 点击「结束练习」查看课后总结报告

## 项目结构

```
SpeakCoach-AI/
├── frontend/                          # Vue 3 前端
│   ├── src/
│   │   ├── views/                     # 页面组件
│   │   │   ├── HomeView.vue           # 首页（场景选择 + 自定义场景）
│   │   │   ├── ChatView.vue           # 对话页（语音 + 文字输入）
│   │   │   ├── SummaryView.vue        # 总结页（评分 + 导出）
│   │   │   └── HistoryView.vue        # 历史页（分页 + 删除）
│   │   ├── components/                # 通用组件
│   │   │   ├── SceneCard.vue          # 场景卡片
│   │   │   ├── VoiceRecorder.vue      # 语音录音按钮
│   │   │   ├── ChatBubble.vue         # 对话气泡
│   │   │   └── CorrectionPanel.vue    # 纠错面板
│   │   ├── composables/               # 组合式函数
│   │   │   ├── useSpeechRecognition.js # 语音识别（连续模式）
│   │   │   └── useWebSocket.js        # WebSocket（自动重连+音频队列）
│   │   ├── services/
│   │   │   └── api.js                 # API 封装
│   │   ├── router/
│   │   │   └── index.js               # 路由配置
│   │   ├── assets/
│   │   │   └── main.css               # 全局样式
│   │   ├── App.vue                    # 根组件
│   │   └── main.js                    # 入口
│   ├── index.html
│   ├── vite.config.js                 # Vite 配置（含 API 代理）
│   └── package.json
│
├── backend/                           # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py                    # 应用入口 + 路由注册
│   │   ├── config.py                  # 环境配置（Pydantic Settings）
│   │   ├── database.py                # SQLAlchemy 引擎 + 会话
│   │   ├── seed.py                    # 种子数据（3 个内置场景）
│   │   ├── models/
│   │   │   └── db_models.py           # 数据模型（Scenario/Session/Message/Correction）
│   │   ├── schemas/
│   │   │   └── schemas.py             # Pydantic Schema
│   │   ├── routers/
│   │   │   ├── scenarios.py           # 场景 CRUD（GET/POST/DELETE）
│   │   │   ├── sessions.py            # 会话管理 + 总结生成
│   │   │   └── ws.py                  # WebSocket 实时对话
│   │   └── services/
│   │       ├── llm_service.py         # DeepSeek API 调用（对话+纠错+评分）
│   │       ├── summary_service.py     # DeepSeek API 调用（课后总结）
│   │       └── tts_service.py         # edge-tts 语音合成
│   ├── requirements.txt
│   └── .env.example
│
├── .env.example                       # 环境变量模板
└── README.md
```

## API 文档

### REST API

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/health` | 健康检查 |
| `GET` | `/api/scenarios` | 获取所有场景 |
| `GET` | `/api/scenarios/{id}` | 获取单个场景 |
| `POST` | `/api/scenarios` | 创建自定义场景 |
| `DELETE` | `/api/scenarios/{id}` | 删除场景（级联删除关联数据） |
| `POST` | `/api/sessions` | 创建新会话 |
| `GET` | `/api/sessions` | 获取会话列表（支持 `skip`/`limit` 分页） |
| `GET` | `/api/sessions/{id}` | 获取会话详情 |
| `POST` | `/api/sessions/{id}/end` | 结束会话 |
| `DELETE` | `/api/sessions/{id}` | 删除会话（级联删除消息和纠错） |
| `GET` | `/api/sessions/{id}/summary` | 获取课后总结（含缓存） |

### WebSocket

| 端点 | 说明 |
|------|------|
| `ws://host/api/ws/{session_id}` | 实时对话（文本 + 语音 + 纠错 + 评分） |

#### WebSocket 消息类型

**发送：**
```json
{ "type": "user_message", "text": "Hello, how are you?" }
```

**接收：**
```json
{ "type": "ai_reply", "text": "I'm great!", "audio": "<base64 mp3>" }
{ "type": "correction", "data": [{ "original": "...", "corrected": "...", ... }] }
{ "type": "score_update", "data": { "grammar": 85, "fluency": 78, "vocabulary": 90 } }
```

## 数据模型

### Scenario（场景）
- 内置 3 个预设场景 + 用户自定义场景
- 自定义场景含 `system_prompt` 控制 AI 角色行为
- 支持图标、难度等级（初级/中级/高级）

### Session（会话）
- 一次练习对话的完整记录
- 含开始/结束时间、综合评分、AI 总结缓存

### Message（消息）
- 用户和 AI 的对话消息
- 每条 AI 回复附带语法/流利度/词汇评分

### Correction（纠错）
- 用户消息的纠错记录
- 支持类型：语法(grammar)、发音(pronunciation)、表达(expression)、用词(word_choice)
- 严重程度：minor(轻微) / major(严重)

## 核心实现细节

### 语音识别（连续模式）
- `useSpeechRecognition.js` 使用 `continuous: true` 连续识别
- 分离 final（最终结果）和 interim（中间结果），免手动拼接
- `stop()` 返回 Promise，在 `onend` 事件中 resolve，保证拿到完整识别文本

### WebSocket 自动重连
- `useWebSocket.js` 实现指数退避重连：1s → 2s → 4s → 8s → 10s（封顶）
- 最多重试 5 次，`intentionalClose` 机制避免正常断开后重连
- 前端显示「重连中…」黄色状态标识

### 音频播放（队列机制）
- 使用 Promise 链（`audioQueue = audioQueue.then(…)`）顺序播放
- 独立 `replayAudio()` 支持单条重新播放，不阻塞主队列
- base64 → Blob → ObjectURL → Audio 播放链路

### 纠错体验
- 实时纠错：AI 回复时附带的 corrections 立即显示在纠错面板
- 对话气泡内同步显示每条用户消息的纠错详情
- 纠错标签按类型着色（语法=黄、发音=蓝、表达=粉、用词=绿）

### 课后总结缓存
- 首次生成后保存 `session.summary` JSON 字段
- 后续访问直接返回缓存，避免重复调用 DeepSeek API
- 缓存损坏自动检测并重新生成

## 环境变量

参见 `.env.example`：

```env
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

## 开发指南

### 提交规范

```bash
feat: 新功能
fix: 修复问题
refactor: 重构
style: 样式
chore: 杂项
docs: 文档
```

### 开发要点

- 前端开发时后端需同时在运行（API 代理通过 Vite 自动转发到 :8000）
- WebSocket 代理需 `ws: true`（`vite.config.js` 已配置）
- 修改数据库模型后需重启后端（SQLite 自动创建/更新表）
- 新增场景后需刷新页面（前端通过 API 动态加载场景列表）

## License

MIT
