#!/bin/bash

set -e

DEPLOY_PATH="${DEPLOY_PATH:-/opt/wms}"
COMPOSE_FILE="docker-compose.prod.yaml"
BACKEND_PORT="${BACKEND_PORT:-8010}"
FRONTEND_PORT="${FRONTEND_PORT:-8011}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_command() {
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        log_error "docker-compose 未安装"
        exit 1
    fi
    log_info "使用: $COMPOSE_CMD"
}

configure_docker_mirror() {
    log_info "配置 Docker 镜像加速器..."
    sudo mkdir -p /etc/docker
    
    if [ ! -f /etc/docker/daemon.json.bak ]; then
        sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.bak 2>/dev/null || true
    fi
    
    sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev"
  ]
}
EOF
    
    if ! sudo diff -q /etc/docker/daemon.json /etc/docker/daemon.json.current 2>/dev/null; then
        log_info "重启 Docker 服务..."
        sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.current
        sudo systemctl daemon-reload
        sudo systemctl restart docker || sudo service docker restart || true
        sleep 5
    fi
}

pull_base_images() {
    log_info "拉取基础镜像..."
    
    if ! sudo docker ps -a --format '{{.Names}}' | grep -q 'wms-db'; then
        log_info "拉取 PostgreSQL 镜像..."
        sudo docker pull docker.m.daocloud.io/library/postgres:16-alpine
    fi
    
    if ! sudo docker ps -a --format '{{.Names}}' | grep -q 'wms-redis'; then
        log_info "拉取 Redis 镜像..."
        sudo docker pull docker.m.daocloud.io/library/redis:7-alpine
    fi
}

build_images() {
    log_info "构建后端镜像..."
    sudo docker build -t wms-backend:latest ./webapi
    
    log_info "构建前端镜像..."
    sudo docker build -t wms-frontend:latest ./webui
}

ensure_env_file() {
    if [ ! -f .env ]; then
        log_warn ".env 文件不存在，请手动创建"
        log_info "示例配置:"
        cat << 'EOF'
DB_HOST=db
DB_PORT=5432
DB_DATABASE=wms
DB_USERNAME=postgres
DB_PASSWORD=your_password
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
IMAGE_BACKEND=wms-backend:latest
IMAGE_FRONTEND=wms-frontend:latest
EOF
        exit 1
    fi
    log_info ".env 文件已存在"
}

deploy() {
    log_info "=========================================="
    log_info "WMS 智能仓储系统 - 部署"
    log_info "=========================================="
    
    cd "$DEPLOY_PATH"
    
    check_command
    configure_docker_mirror
    ensure_env_file
    pull_base_images
    
    if [ "$SKIP_BUILD" != "true" ]; then
        build_images
    else
        log_info "跳过镜像构建"
    fi
    
    log_info "启动服务..."
    $COMPOSE_CMD -f $COMPOSE_FILE up -d
    
    log_info "等待服务启动..."
    sleep 15
    
    log_info "服务状态:"
    $COMPOSE_CMD -f $COMPOSE_FILE ps
    
    log_info "=========================================="
    log_info "部署完成！"
    log_info "后端地址: http://localhost:$BACKEND_PORT"
    log_info "前端地址: http://localhost:$FRONTEND_PORT"
    log_info "=========================================="
}

rollback() {
    log_info "执行回滚..."
    
    cd "$DEPLOY_PATH"
    check_command
    
    if sudo docker inspect wms-backend:previous &> /dev/null; then
        log_info "回滚后端镜像..."
        sudo docker tag wms-backend:previous wms-backend:current
        export IMAGE_BACKEND=wms-backend:current
    fi
    
    if sudo docker inspect wms-frontend:previous &> /dev/null; then
        log_info "回滚前端镜像..."
        sudo docker tag wms-frontend:previous wms-frontend:current
        export IMAGE_FRONTEND=wms-frontend:current
    fi
    
    $COMPOSE_CMD -f $COMPOSE_FILE up -d --no-deps backend frontend
    
    log_info "回滚完成"
}

stop() {
    log_info "停止服务..."
    cd "$DEPLOY_PATH"
    check_command
    $COMPOSE_CMD -f $COMPOSE_FILE down
    log_info "服务已停止"
}

logs() {
    cd "$DEPLOY_PATH"
    check_command
    $COMPOSE_CMD -f $COMPOSE_FILE logs -f --tail=100 "$@"
}

status() {
    cd "$DEPLOY_PATH"
    check_command
    $COMPOSE_CMD -f $COMPOSE_FILE ps
}

cleanup() {
    log_info "清理无用镜像和容器..."
    sudo docker system prune -af --filter "until=168h"
    log_info "清理完成"
}

show_help() {
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  deploy    部署服务（默认命令）"
    echo "  rollback  回滚到上一版本"
    echo "  stop      停止服务"
    echo "  logs      查看日志（可选参数：服务名）"
    echo "  status    查看服务状态"
    echo "  cleanup   清理无用镜像"
    echo "  help      显示帮助信息"
    echo ""
    echo "环境变量:"
    echo "  DEPLOY_PATH    部署目录（默认: /opt/wms）"
    echo "  SKIP_BUILD     跳过镜像构建（true/false）"
    echo "  BACKEND_PORT   后端端口（默认: 8010）"
    echo "  FRONTEND_PORT  前端端口（默认: 8011）"
}

case "${1:-deploy}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    stop)
        stop
        ;;
    logs)
        shift
        logs "$@"
        ;;
    status)
        status
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "未知命令: $1"
        show_help
        exit 1
        ;;
esac
