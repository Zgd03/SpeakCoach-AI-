# SpeakCoach AI — 英语口语练习工具

基于 AI 的英语口语练习工具，支持多种场景下的实时语音对话训练。

## 功能

- 🎯 **场景选择**：面试、点餐、会议等多种真实场景
- 🎤 **语音对话**：通过浏览器语音识别进行实时对话
- 🤖 **AI 教练**：基于 DeepSeek API 的智能对话伙伴
- 📝 **实时纠错**：语法、表达、用词的实时纠正
- 📊 **课后总结**：评分、优劣势分析、改进建议

## 技术栈

- **前端**：Vue 3 + Vite
- **后端**：Python FastAPI
- **数据库**：SQLite (SQLAlchemy)
- **语音合成**：edge-tts
- **语音识别**：浏览器 Web Speech API
- **AI 模型**：DeepSeek API

## 快速开始

### 1. 克隆项目

```bash
git clone <repo-url>
cd SpeakCoach-AI
```

### 2. 后端配置

```bash
cd backend
cp ../.env.example ../.env
# 编辑 .env 填入 DeepSeek API Key
pip install -r requirements.txt
python -m app.seed   # 初始化场景数据
uvicorn app.main:app --reload   # 启动后端 (http://localhost:8000)
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev   # 启动前端 (http://localhost:5173)
```

### 4. 使用

打开浏览器访问 http://localhost:5173，选择一个场景开始练习。

## PR 规范

本项目遵循以下 PR 规范：

- **单一职责**：每个 PR 只实现或修改一个功能
- **小而精**：鼓励尽可能小、粒度尽可能细的 PR
- **清晰标题**：`feat: 功能名称` / `fix: 修复问题` / `style: 样式修改`
- **完整描述**：包含功能描述、实现思路、测试方式

## 项目结构

```
SpeakCoach-AI/
├── frontend/          # Vue3 前端
├── backend/           # FastAPI 后端
├── .env.example       # 环境变量模板
└── README.md
```
