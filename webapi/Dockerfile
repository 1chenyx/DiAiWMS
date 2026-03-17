ARG PYTHON_IMAGE=docker.m.daocloud.io/library/python:3.12-slim

FROM ${PYTHON_IMAGE} AS builder

WORKDIR /backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --user --no-cache-dir --no-warn-script-location \
    -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

FROM ${PYTHON_IMAGE} AS runtime

ARG BUILD_DATE
ARG VCS_REF

LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.title="WMS Backend" \
      org.opencontainers.image.description="WMS 智能仓储系统后端服务"

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/backend \
    TZ=Asia/Shanghai \
    app_env=prod \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

WORKDIR /backend

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY config ./config
COPY app ./app

RUN mkdir -p /backend/logs \
    && chown -R 1000:1000 /backend/logs \
    && chmod -R 777 /backend/logs

EXPOSE 8010

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8010/api/ping || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010", "--workers", "4", "--log-level", "info"]
