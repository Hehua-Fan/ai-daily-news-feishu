# 服务器部署指南

## 关键回答：服务器上不需要单独下载 Playwright！

所有 Playwright 依赖都会在 Docker 容器构建时自动安装。

## 已修复的 Dockerfile 配置

✅ **已添加 Playwright 浏览器支持**
- 自动安装 Chromium 浏览器
- 包含所有必要的系统库依赖
- 在容器内完全解决 Playwright 运行环境

## 部署步骤

### 1. 上传代码到服务器
```bash
# 将整个项目文件夹上传到服务器
scp -r ai_news_bot user@your-server:/path/to/
```

### 2. 在服务器上构建并运行
```bash
# 进入项目目录
cd /path/to/ai_news_bot

# 构建 Docker 镜像
docker-compose -f docker/docker-compose.yml build

# 启动容器
docker-compose -f docker/docker-compose.yml up -d
```

### 3. 验证运行状态
```bash
# 查看容器状态
docker-compose -f docker/docker-compose.yml ps

# 查看日志
docker-compose -f docker/docker-compose.yml logs -f

# 进入容器测试
docker exec -it ai-news-bot bash
python backend/manual_exec.py  # 测试手动执行
```

## 注意事项

⚠️ **镜像大小**：由于包含 Chromium 浏览器，Docker 镜像会比较大（约 500MB+）

🔧 **首次构建**：第一次构建时间较长，因为需要下载浏览器和系统依赖

🚀 **后续更新**：只需重新构建镜像即可，无需在服务器上安装额外软件

## 配置文件

记得在服务器上配置 `backend/config.yml`：
```yaml
# 复制 config.example.yml 为 config.yml 并填入实际配置
cp backend/config.example.yml backend/config.yml
```

## 健康检查

Docker 容器已配置健康检查，会自动监控服务状态。
