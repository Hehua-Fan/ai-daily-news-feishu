# 使用Python 3.11作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置时区为北京时间
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 安装系统依赖（包括 Playwright 所需的浏览器依赖）
RUN apt-get update && apt-get install -y \
    gcc \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 复制后端代码和配置
COPY ./backend /app/backend

# 设置pip镜像源为国内源，并安装依赖
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r /app/backend/requirements.txt

# 安装 Playwright 浏览器和系统依赖（需要在 root 用户下执行）
RUN python -m playwright install chromium
RUN python -m playwright install-deps

# 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 创建日志目录
RUN mkdir -p /app/logs

# 设置适当的权限
RUN chown -R appuser:appuser /app

# 切换到非root用户
USER appuser

# 设置Python路径
ENV PYTHONPATH="/app/backend:$PYTHONPATH"

# 健康检查
HEALTHCHECK --interval=300s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('https://www.baidu.com', timeout=10)" || exit 1

# 运行定时任务
CMD ["python", "-u", "/app/backend/agents/feishu_sender.py"] 