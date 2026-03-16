FROM python:3.12-slim AS builder

WORKDIR /backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/backend \
    TZ=Asia/Shanghai \
    app_env=prod \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

WORKDIR /backend

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY config ./config
COPY app ./app
COPY alembic.ini ./

RUN mkdir -p /backend/logs && chmod 777 /backend/logs

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/ping || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--log-level", "info"]
