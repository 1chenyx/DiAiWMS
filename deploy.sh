#!/bin/bash

set -e

echo "========================================"
echo "WMS 智能仓储系统 - 部署脚本"
echo "========================================"

ENV_FILE=".env"

if [ ! -f "$ENV_FILE" ]; then
    echo "错误: 未找到 .env 文件"
    echo "请复制 .env.example 为 .env 并配置相关参数"
    exit 1
fi

source $ENV_FILE

echo "环境配置:"
echo "  - Image Tag: ${IMAGE_TAG:-latest}"
echo ""

# 检查 PostgreSQL 和 Redis 容器是否已存在
DB_CONTAINER_EXISTS=false
REDIS_CONTAINER_EXISTS=false

if docker ps -a --format '{{.Names}}' | grep -q '^wms-db-1$\|^wms_db_1$\|^db$'; then
    DB_CONTAINER_EXISTS=true
    echo "PostgreSQL 容器已存在，跳过重建"
fi

if docker ps -a --format '{{.Names}}' | grep -q '^wms-redis-1$\|^wms_redis_1$\|^redis$'; then
    REDIS_CONTAINER_EXISTS=true
    echo "Redis 容器已存在，跳过重建"
fi

# 如果数据库容器不存在，才拉取镜像
if [ "$DB_CONTAINER_EXISTS" = false ] || [ "$REDIS_CONTAINER_EXISTS" = false ]; then
    echo "拉取数据库镜像..."
    if [ "$DB_CONTAINER_EXISTS" = false ]; then
        docker pull docker.m.daocloud.io/library/postgres:16-alpine || true
    fi
    if [ "$REDIS_CONTAINER_EXISTS" = false ]; then
        docker pull docker.m.daocloud.io/library/redis:7-alpine || true
    fi
fi

# 检查是否需要构建镜像
BUILD_IMAGES=${BUILD_IMAGES:-true}

if [ "$BUILD_IMAGES" = "true" ]; then
    echo "构建后端镜像..."
    docker build -t wms-backend:${IMAGE_TAG:-latest} ./webapi
    
    echo "构建前端镜像..."
    docker build -t wms-frontend:${IMAGE_TAG:-latest} ./webui
fi

echo "停止旧应用容器（保留数据库容器）..."
docker compose -f docker-compose.prod.yaml stop backend frontend 2>/dev/null || true
docker compose -f docker-compose.prod.yaml rm -f backend frontend 2>/dev/null || true

echo "启动新容器..."
docker compose -f docker-compose.prod.yaml up -d

echo "等待服务启动..."
sleep 10

echo "服务状态:"
docker compose -f docker-compose.prod.yaml ps

echo ""
echo "健康检查..."
for i in {1..30}; do
    if curl -sf http://localhost:8010/api/ping > /dev/null 2>&1; then
        echo "✓ 后端服务正常"
        break
    fi
    echo "等待后端服务启动... ($i/30)"
    sleep 2
done

if curl -sf http://localhost:8011/health > /dev/null 2>&1; then
    echo "✓ 前端服务正常"
else
    echo "✗ 前端服务异常"
fi

echo ""
echo "清理无用镜像..."
docker image prune -f

echo ""
echo "========================================"
echo "部署完成！"
echo "========================================"
echo "访问地址: http://localhost:8011"
echo ""
