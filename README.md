# 🤖 AI新闻机器人

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-green.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个智能的AI新闻推送机器人，自动抓取TechCrunch、The Verge的最新AI资讯以及GitHub热门仓库，通过AutoAgents AI进行中文翻译和总结，并发送精美的交互式卡片到飞书群聊。

## ✨ 核心特性

- 🚀 **智能抓取**: 自动从TechCrunch、The Verge获取最新AI资讯
- 🔥 **热门仓库**: 抓取GitHub Trending热门开源项目
- 🧠 **AI驱动**: 使用AutoAgents AI进行智能翻译和内容总结
- 📱 **美观推送**: 发送精美的飞书交互式卡片，支持一键跳转
- ⏰ **定时推送**: 每天早上9点自动推送，无需人工干预
- 💾 **云端存储**: 基于Supabase的可靠数据存储，自动去重
- 🐳 **一键部署**: Docker容器化部署，环境隔离，开箱即用
- 🎯 **模块化设计**: 清晰的代码架构，易于扩展和维护

## 📁 项目结构

```
ai_news_bot/
├── backend/                    # 🏗️ 后端核心代码
│   ├── agents/                 # 🤖 智能代理
│   │   ├── feishu_sender.py   # 📱 飞书消息发送 + 定时任务
│   │   └── news_handler.py    # 📰 新闻处理和AI集成
│   ├── config/                 # ⚙️ 配置管理
│   │   ├── config_manager.py  # 📋 配置文件管理
│   │   └── database.py        # 💾 Supabase数据库操作
│   ├── scraper/               # 🕷️ 新闻爬虫
│   │   ├── techcrunch_scraper.py    # TechCrunch爬虫
│   │   ├── verge_scraper.py         # The Verge爬虫
│   │   └── github_trending_scraper.py  # GitHub热门仓库爬虫
│   ├── config.yml             # ⚙️ 配置文件
│   ├── config.example.yml     # 📄 配置模板
│   ├── manual_exec.py         # 🔧 手动执行脚本
│   └── requirements.txt       # 📦 Python依赖
├── docker/                    # 🐳 Docker部署
│   ├── Dockerfile             # 🏗️ 镜像构建
│   ├── docker-compose.yml     # 🚀 容器编排
│   ├── .dockerignore          # 🚫 Docker忽略文件
│   └── README.md              # 📖 Docker部署说明
├── playground/                # 🧪 测试和文档
│   ├── test_*.py              # 🧪 测试脚本
│   └── *.md                   # 📚 技术文档
├── logs/                      # 📊 日志文件
├── .gitignore                 # 🚫 Git忽略文件
└── README.md                  # 📖 项目说明
```

## 🚀 快速开始

### 前置要求

- Python 3.11+
- 飞书机器人 (企业内部机器人)
- AutoAgents AI 账号
- Supabase 数据库

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd ai_news_bot
```

### 2. 配置设置

```bash
# 复制配置模板
cp backend/config.example.yml backend/config.yml

# 编辑配置文件
nano backend/config.yml
```

配置文件说明：

```yaml
# 飞书机器人配置
lark:
  api_url: "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_BOT_HOOK_ID"
  api_secret: "your_lark_api_secret_here"

# API 配置
apis:
  autoagentsai:
    agent_id: "your_agent_id_here"
    personal_auth_key: "your_personal_auth_key_here"
    personal_auth_secret: "your_personal_auth_secret_here"

# Supabase 数据库配置
supabase:
  url: "https://your-project-id.supabase.co"
  anon_key: "your_supabase_anon_key_here"

# 数据库表配置
database:
  table_name: "ai_news"
```

### 3. 本地开发

```bash
# 安装依赖
cd backend
pip install -r requirements.txt

# 手动执行一次 (测试配置)
python manual_exec.py

# 启动定时任务
python agents/feishu_sender.py
```

## 🐳 快速部署 (推荐)

### 使用 Docker Compose (一键部署)

```bash
# 1. 确保配置文件已设置
cp backend/config.example.yml backend/config.yml
# 编辑 backend/config.yml 填写实际配置

# 2. 启动服务
cd docker
docker-compose up -d

# 3. 查看日志
docker-compose logs -f ai-news-bot

# 4. 停止服务
docker-compose down
```

### 使用 Docker (手动部署)

```bash
# 构建镜像
docker build -t ai-news-bot -f docker/Dockerfile .

# 运行容器
docker run -d \
  --name ai-news-bot \
  --restart unless-stopped \
  -e TZ=Asia/Shanghai \
  -v $(pwd)/logs:/app/logs \
  ai-news-bot
```

## ⚙️ 配置获取指南

### 1. 飞书机器人配置

1. 进入 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 启用机器人功能
4. 获取 Webhook URL 和 Secret
5. 将机器人添加到目标群聊

### 2. AutoAgents AI 配置

1. 注册 [AutoAgents AI](https://autoagents.ai/) 账号
2. 获取 agent_id, personal_auth_key, personal_auth_secret
3. 确保账号有足够的API调用额度

### 3. Supabase 数据库配置

1. 注册 [Supabase](https://supabase.com/) 账号
2. 创建新项目
3. 在 SQL Editor 中执行以下命令创建表：

```sql
CREATE TABLE ai_news (
    id SERIAL PRIMARY KEY,
    date TEXT NOT NULL,
    tag TEXT NOT NULL,
    title TEXT NOT NULL,
    zh_title TEXT NOT NULL,
    link TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

4. 获取项目 URL 和 anon key

## 🎯 使用方式

### 自动运行
Docker部署后，机器人将自动在每天早上9:00推送AI新闻

### 手动执行
```bash
cd backend
python manual_exec.py
```

### 测试功能
```bash
cd playground

# 测试卡片样式
python test_card_style.py

# 测试AI翻译功能
python test_autoagentsai.py

# 测试GitHub Trending集成
python test_github_trending.py
```

## 📱 消息样式

机器人发送的飞书卡片包含：

- 🎯 **彩色标题栏**: 青绿色主题，日期标识
- 📊 **统计信息**: 显示新闻和仓库总数
- 🏷️ **来源标签**: TechCrunch 🚀 / The Verge ⚡ / GitHub 🔥
- 📝 **智能摘要**: AI生成的中文总结
- 🔘 **阅读按钮**: 一键跳转到原文或仓库
- 🤖 **更新标识**: 自动播报时间戳

## 🔧 开发指南

### 添加新的新闻源

1. 在 `backend/scraper/` 创建新的爬虫文件
2. 实现 `get_news_list()` 方法
3. 在 `backend/agents/news_handler.py` 中添加爬虫

### 修改推送时间

编辑 `backend/agents/feishu_sender.py` 第278行：
```python
# 修改为其他时间，如下午6点
schedule.every().day.at("18:00").do(request_feishu)
```

### 自定义卡片样式

修改 `backend/agents/feishu_sender.py` 中的 `create_news_card()` 方法

## 🚨 故障排除

### 常见问题

**1. 配置文件错误**
```bash
# 检查YAML格式
python -c "import yaml; yaml.safe_load(open('backend/config.yml'))"
```

**2. 网络连接问题**
```bash
# 测试新闻源连接
curl -s https://techcrunch.com >/dev/null && echo "TechCrunch OK"
curl -s https://www.theverge.com >/dev/null && echo "Verge OK"
```

**3. Docker问题**
```bash
# 查看容器日志
docker-compose logs -f ai-news-bot

# 重启容器
docker-compose restart ai-news-bot

# 重新构建
docker-compose build --no-cache
```

**4. 数据库连接问题**
- 检查 Supabase URL 和 Key 是否正确
- 确认数据库表已创建
- 验证网络可以访问 Supabase

### 调试模式

```bash
# 手动执行查看详细输出
cd backend
python manual_exec.py

# 测试单个模块
python -m agents.news_handler
python -m scraper.techcrunch_scraper
```

## 📊 监控和日志

- **Docker日志**: `docker-compose logs -f ai-news-bot`
- **文件日志**: `logs/` 目录
- **健康检查**: Docker自动监控服务状态
- **错误通知**: 飞书卡片会显示错误信息

## 🛠️ 技术栈

- **语言**: Python 3.11+
- **AI服务**: AutoAgents AI (翻译+总结)
- **数据库**: Supabase (PostgreSQL)
- **消息推送**: 飞书机器人 API
- **网页抓取**: requests + BeautifulSoup
- **定时任务**: Python Schedule
- **部署**: Docker + Docker Compose

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🌟 支持

如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！

有问题或建议？欢迎提交 [Issue](../../issues) 或 [Pull Request](../../pulls)。

---

**📧 联系方式**: 如有商业合作或技术咨询，请通过 [Issues](../../issues) 联系。