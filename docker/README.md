# 🐳 Docker 部署指南

本目录包含 AI 新闻机器人的 Docker 部署配置文件。

## 📁 文件说明

- `Dockerfile` - Docker 镜像构建文件
- `docker-compose.yml` - Docker Compose 编排文件
- `.dockerignore` - Docker 构建忽略文件
- `README.md` - 本文件

## 🚀 快速部署

### 方法1: Docker Compose (推荐)

```bash
# 1. 确保已配置 backend/config.yml
cd .. && cp backend/config.example.yml backend/config.yml
# 编辑 backend/config.yml 填写实际配置

# 2. 启动服务
cd docker
docker-compose up -d

# 3. 查看日志
docker-compose logs -f ai-news-bot

# 4. 停止服务
docker-compose down
```

### 方法2: 手动 Docker

```bash
# 构建镜像 (从项目根目录)
cd ..
docker build -t ai-news-bot -f docker/Dockerfile .

# 运行容器
docker run -d \
  --name ai-news-bot \
  --restart unless-stopped \
  -e TZ=Asia/Shanghai \
  -e PYTHONPATH=/app/backend \
  -v $(pwd)/logs:/app/logs \
  ai-news-bot
```

## ⚙️ 配置说明

### 环境变量

- `TZ=Asia/Shanghai` - 设置北京时间
- `PYTHONPATH=/app/backend` - Python 模块路径

### 卷挂载

- `../logs:/app/logs` - 日志文件持久化
- 可选: `../backend/config.yml:/app/backend/config.yml:ro` - 配置文件挂载

### 网络配置

- 容器网络: `ai-news-network`
- 类型: bridge

## 🔧 高级配置

### 自定义构建

```bash
# 使用自定义标签
docker build -t my-ai-news-bot:v1.0 -f docker/Dockerfile ..

# 多平台构建 (如 ARM64)
docker buildx build --platform linux/amd64,linux/arm64 -t ai-news-bot -f docker/Dockerfile ..
```

### 生产环境配置

```yaml
# docker-compose.prod.yml
services:
  ai-news-bot:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    restart: always
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "5"
    healthcheck:
      interval: 2m
      timeout: 30s
      retries: 3
```

## 📊 监控和维护

### 日志管理

```bash
# 查看实时日志
docker-compose logs -f ai-news-bot

# 查看最近的日志
docker-compose logs --tail=100 ai-news-bot

# 查看日志文件
tail -f ../logs/*.log
```

### 健康检查

```bash
# 检查容器状态
docker-compose ps

# 查看健康状态
docker inspect ai-news-bot | grep Health -A 10
```

### 容器维护

```bash
# 重启服务
docker-compose restart ai-news-bot

# 更新镜像
docker-compose pull
docker-compose up -d

# 清理旧镜像
docker image prune -f
```

## 🐛 故障排除

### 常见问题

**1. 容器启动失败**
```bash
# 查看启动日志
docker-compose logs ai-news-bot

# 检查配置文件
docker-compose config
```

**2. 配置文件问题**
```bash
# 验证配置文件挂载
docker-compose exec ai-news-bot ls -la /app/backend/config.yml

# 检查配置内容
docker-compose exec ai-news-bot cat /app/backend/config.yml
```

**3. 网络连接问题**
```bash
# 测试容器网络
docker-compose exec ai-news-bot ping -c 3 www.baidu.com

# 检查DNS解析
docker-compose exec ai-news-bot nslookup techcrunch.com
```

**4. 权限问题**
```bash
# 检查日志目录权限
ls -la ../logs/

# 修复权限 (如果需要)
sudo chown -R $(id -u):$(id -g) ../logs/
```

### 调试模式

```bash
# 交互式运行容器
docker-compose run --rm ai-news-bot bash

# 手动执行脚本
docker-compose exec ai-news-bot python manual_exec.py

# 查看Python模块路径
docker-compose exec ai-news-bot python -c "import sys; print('\n'.join(sys.path))"
```

## 🔄 更新和备份

### 更新服务

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建并启动
docker-compose up -d --build

# 3. 清理旧镜像
docker image prune -f
```

### 数据备份

```bash
# 备份日志文件
tar -czf logs-backup-$(date +%Y%m%d).tar.gz ../logs/

# 备份配置文件
cp ../backend/config.yml config-backup-$(date +%Y%m%d).yml
```

## 📈 性能优化

### 资源限制

```yaml
deploy:
  resources:
    limits:
      memory: 256M      # 内存限制
      cpus: '0.25'      # CPU限制
    reservations:
      memory: 128M      # 内存预留
      cpus: '0.1'       # CPU预留
```

### 镜像优化

- 使用 `.dockerignore` 减少构建上下文
- 多阶段构建减少镜像大小
- 使用 `python:3.11-slim` 基础镜像

## 🛡️ 安全考虑

1. **敏感信息**: 不要在镜像中包含配置文件
2. **用户权限**: 容器内使用非 root 用户运行
3. **网络隔离**: 使用自定义网络
4. **日志安全**: 避免在日志中记录敏感信息

---

**💡 提示**: 如需更多帮助，请查看主目录的 [README.md](../README.md) 或提交 Issue。