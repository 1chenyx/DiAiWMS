# DiAiWMS - 智能仓储管理系统

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.12+-green.svg)
![Vue](https://img.shields.io/badge/Vue-3.5+-brightgreen.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**一个现代化、智能化的仓储管理系统，集成 AI 能力**

[功能特性](#功能特性) • [技术架构](#技术架构) • [快速开始](#快速开始) • [部署指南](#部署指南)

</div>

---

## 📋 项目简介

DiAiWMS 是一个基于 **FastAPI + Vue 3** 构建的企业级智能仓储管理系统。系统采用前后端分离架构，支持多租户模式，集成了 LangChain AI 能力，提供智能化的仓储作业辅助功能。

### 核心亮点

- 🏢 **多租户架构** - 完整的多租户数据隔离，每个租户独立数据库
- 🤖 **AI 智能助手** - 集成 LangChain，支持多种 LLM 提供商（OpenAI、Anthropic 等）
- 📦 **全流程管理** - 覆盖入库、出库、库存、盘点等完整仓储业务
- 🔐 **权限控制** - 基于角色的访问控制（RBAC）
- 🚀 **高性能** - 异步架构，Redis 缓存，支持高并发
- 🐳 **容器化部署** - 完整的 Docker 支持，一键部署

---

## ✨ 功能特性

### 基础数据管理

| 模块 | 功能 |
|------|------|
| 商品管理 | SPU/SKU 管理、商品分类、条码管理 |
| 仓库管理 | 仓库、库区、库位管理 |
| 合作伙伴 | 客户、供应商、货主管理 |
| 系统配置 | 用户、角色、菜单权限管理 |

### 入库管理

- 📥 **入库单管理** - 创建入库计划、跟踪入库状态
- 📋 **收货确认** - 实际收货数量确认、质检管理
- 📍 **上架作业** - 智能推荐上架库位、上架任务管理

### 出库管理

- 📤 **出库单管理** - 创建出库计划、波次管理
- 🛒 **拣货作业** - 智能拣货路径规划、拣货任务分配
- ✅ **出库确认** - 出库复核、发货管理

### 库存管理

- 📊 **库存查询** - 实时库存、批次管理
- 🔄 **库存移动** - 移库、补货作业
- ❄️ **库存冻结** - 冻结/解冻管理
- 📝 **库存盘点** - 盘点计划、盘点差异处理
- ⚖️ **库存调整** - 盘盈盘亏处理

### AI 智能功能

- 💬 **智能对话** - 自然语言交互，辅助仓储作业
- 🔧 **工具调用** - 可扩展的 AI 工具系统
- 📐 **规则引擎** - 可配置的业务规则
- 🎯 **技能系统** - 可定制的 AI 技能

---

## 🏗️ 技术架构

### 后端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.12+ | 编程语言 |
| FastAPI | 0.129+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM 框架 |
| PostgreSQL | 16 | 主数据库 |
| Redis | 7 | 缓存/会话 |
| LangChain | 0.3+ | AI 框架 |
| Alembic | 1.18+ | 数据库迁移 |

### 前端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | 3.5+ | 前端框架 |
| TypeScript | 5.9+ | 类型支持 |
| Element Plus | 2.13+ | UI 组件库 |
| Pinia | 3.0+ | 状态管理 |
| Vue Router | 5.0+ | 路由管理 |
| Vite | 8.0+ | 构建工具 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端 (Vue 3)                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ 入库管理 │ │ 出库管理 │ │ 库存管理 │ │ AI 助手  │           │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
└───────┼──────────┼──────────┼──────────┼───────────────────┘
        │          │          │          │
        └──────────┴──────────┴──────────┘
                       │
              ┌────────┴────────┐
              │   API Gateway   │
              │   (Nginx)       │
              └────────┬────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                    后端 (FastAPI)                            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ API 层  │ │Service层│ │Repository│ │  AI层   │           │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘           │
│       │          │          │          │                    │
│       └──────────┴──────────┴──────────┘                    │
│                       │                                     │
│              ┌────────┴────────┐                           │
│              │    数据访问层    │                           │
│              └────────┬────────┘                           │
└───────────────────────┼─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
  ┌─────┴─────┐   ┌─────┴─────┐   ┌─────┴─────┐
  │PostgreSQL │   │   Redis   │   │  LLM API  │
  │ (主数据库) │   │  (缓存)   │   │ (AI服务)  │
  └───────────┘   └───────────┘   └───────────┘
```

---

## 🚀 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- （可选）Node.js 20+ 用于本地前端开发
- （可选）Python 3.12+ 用于本地后端开发

### 方式一：Docker 部署（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/1chenyx/DiAiWMS.git
cd DiAiWMS

# 2. 创建环境配置文件
cat > .env << EOF
DB_HOST=db
DB_PORT=5432
DB_DATABASE=wms
DB_USERNAME=postgres
DB_PASSWORD=your_secure_password
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
EOF

# 3. 启动服务
docker compose -f docker-compose.prod.yaml up -d

# 4. 查看服务状态
docker compose -f docker-compose.prod.yaml ps

# 5. 访问应用
# 前端: http://localhost:8011
# 后端 API 文档: http://localhost:8010/docs
```

### 方式二：本地开发

#### 后端开发

```bash
cd webapi

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

# 配置环境
cp config/app_dev.yaml.example config/app_dev.yaml
# 编辑配置文件，设置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
python runserver.py
```

#### 前端开发

```bash
cd webui

# 安装依赖
npm install --registry=https://registry.npmmirror.com

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

---

## 📦 部署指南

### 生产环境部署

项目提供了完整的 CI/CD 流程，支持自动构建和部署。

#### GitHub Actions 自动部署

1. **配置 GitHub Secrets**

| Secret 名称 | 说明 |
|------------|------|
| `DEPLOY_HOST` | 部署服务器地址 |
| `DEPLOY_PORT` | SSH 端口（默认 22） |
| `DEPLOY_USER` | SSH 用户名 |
| `DEPLOY_SSH_KEY` | SSH 私钥 |
| `DEPLOY_PATH` | 部署路径（默认 /opt/wms） |
| `DB_PASSWORD` | 数据库密码 |
| `REDIS_PASSWORD` | Redis 密码 |

2. **触发部署**

```bash
# 推送到 main 分支自动触发
git push origin main

# 或在 GitHub Actions 页面手动触发
```

#### 手动部署

```bash
# 在服务器上执行
cd /opt/wms
./scripts/deploy.sh deploy    # 部署
./scripts/deploy.sh rollback  # 回滚
./scripts/deploy.sh logs      # 查看日志
./scripts/deploy.sh status    # 查看状态
```

### Docker 镜像

项目使用 GitHub Container Registry 存储镜像：

- 后端镜像: `ghcr.io/1chenyx/diaiwms/backend:latest`
- 前端镜像: `ghcr.io/1chenyx/diaiwms/frontend:latest`

---

## 📁 项目结构

```
DiAiWMS/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD 配置
├── scripts/
│   └── deploy.sh               # 部署脚本
├── webapi/                     # 后端项目
│   ├── app/
│   │   ├── api/                # API 路由
│   │   ├── models/             # 数据模型
│   │   ├── schemas/            # Pydantic 模型
│   │   ├── services/           # 业务逻辑
│   │   ├── repositories/       # 数据访问
│   │   ├── ai/                 # AI 相关模块
│   │   └── utils/              # 工具函数
│   ├── config/                 # 配置文件
│   ├── migrations/             # 数据库迁移
│   └── tests/                  # 测试文件
├── webui/                      # 前端项目
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   ├── components/         # 通用组件
│   │   ├── services/           # API 服务
│   │   ├── composables/        # 组合式函数
│   │   ├── store/              # 状态管理
│   │   └── router/             # 路由配置
│   └── public/                 # 静态资源
├── docker-compose.prod.yaml    # 生产环境编排
└── .env.example                # 环境变量示例
```

---

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DB_HOST` | 数据库主机 | db |
| `DB_PORT` | 数据库端口 | 5432 |
| `DB_DATABASE` | 数据库名称 | wms |
| `DB_USERNAME` | 数据库用户名 | postgres |
| `DB_PASSWORD` | 数据库密码 | - |
| `REDIS_HOST` | Redis 主机 | redis |
| `REDIS_PORT` | Redis 端口 | 6379 |
| `REDIS_PASSWORD` | Redis 密码 | - |
| `IMAGE_BACKEND` | 后端镜像名 | wms-backend:latest |
| `IMAGE_FRONTEND` | 前端镜像名 | wms-frontend:latest |

### AI 配置

系统支持多种 LLM 提供商，通过管理界面配置：

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- 自定义 OpenAI 兼容 API

---

## 🤝 参与贡献

欢迎参与项目开发！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 代码规范

- Python 代码遵循 PEP 8 规范
- 使用类型注解
- 编写单元测试
- 更新相关文档

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系方式

- 项目地址: [https://github.com/1chenyx/DiAiWMS](https://github.com/1chenyx/DiAiWMS)
- 问题反馈: [Issues](https://github.com/1chenyx/DiAiWMS/issues)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star ⭐**

</div>
