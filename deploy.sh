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
echo "  - Docker Username: ${DOCKER_USERNAME}"
echo "  - Image Tag: ${IMAGE_TAG:-latest}"
echo ""

echo "登录 Docker Hub..."
echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin

echo "拉取最新镜像..."
docker compose -f docker-compose.prod.yaml pull

echo "停止旧容器..."
docker compose -f docker-compose.prod.yaml down

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
