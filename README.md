# 排课组（group2）

本仓库负责**排课逻辑**，在创建课程表时需要从 group1 查询教师信息。

## 架构

```
frontend (Vue + Vite)  :5174
        ↓ proxy /api/course/*
backend (Flask)        :8082
        ↓ （不经过 Nginx）
group1 backend         BASE_INFO_API_URL
        ↓
MySQL                  :3307   逻辑库 db_course
```

---

## 快速开始

### 1. 初始化配置

```bash
cp .env.example .env
```

`.env` 里有两个变量需要填写：

```
DB_PASS=dev456                           # 本地 MySQL 密码，随意设
BASE_INFO_API_URL=http://127.0.0.1:8081  # group1 的地址（见下方场景说明）
```

### 2. 选择联调场景

**场景 A：group1 正在本地运行**

确认 group1 已通过 `make dev` 启动（后端跑在 8081 端口），`.env` 保持默认即可。

```bash
curl http://127.0.0.1:8081/api/base/teacher/1001
# 确认 group1 在线后再启动本组服务
```

> 如果是在 Docker 容器内调用宿主机的 group1，`BASE_INFO_API_URL` 需要改为 `http://host.docker.internal:8081`（Mac/Windows 原生支持；Linux 已在 `docker-compose.dev.yml` 中配置）。

**场景 B：group1 不可用，用 Apifox Mock 代替**

1. 在 Apifox 新建接口：`GET /api/base/teacher/{id}`，响应体填 `{"id": 1001, "name": "张三(MOCK)"}`
2. 开启「本地 Mock」，复制基础 URL（格式如 `https://mock.apifox.com/xxxxxxxx`）
3. 把 `.env` 里的 `BASE_INFO_API_URL` 改为这个 URL

验证 Mock 可访问：

```bash
BASE_URL=$(grep BASE_INFO_API_URL .env | cut -d= -f2)
curl "${BASE_URL}/api/base/teacher/1001"
```

两个场景切换只改 `.env` 里的`BASE_INFO_API_URL`。

### 3. 启动开发环境

```bash
make dev
```

就绪标志：

```
backend-course-dev | [DB] 排课表初始化完成
frontend-course-dev |   ➜  Local: http://localhost:5174/
```

### 4. 验证

```bash
curl http://localhost:8082/api/course/health
curl http://localhost:8082/api/course/schedule/1001
# 期望：{"teacher_name": "张三", "course": "软件工程导论", ...}
```

浏览器访问 `http://localhost:5174`，点击「为教师 #1001 排课」。

### 5. 停止

```bash
make down
```

---

## 开发规范

### api调用只依赖接口约定

```python
# ✅ 正确——BASE_INFO_API_URL 由外部注入
BASE_URL = os.environ.get("BASE_INFO_API_URL")
resp = requests.get(f"{BASE_URL}/api/base/teacher/{teacher_id}")

# ❌ 错误——硬编码 IP
resp = requests.get("http://172.17.0.3:8081/api/base/teacher/1")
```

接口契约（路径、参数、响应结构）由双方约定，文档化。约定后双方可以完全独立开发。

### 本组只连自己的数据库

```python
# DB_NAME 由环境变量注入，本组值为 db_course
DB_NAME = os.environ.get("DB_NAME")
```

大盘中两组共用同一个 MySQL 实例，靠逻辑库名隔离。

---

## 交付物

推送 `main` 分支后，GitHub Actions 自动构建：

| 镜像 | 说明 |
|------|------|
| `ghcr.io/uppi7/zjuse-backend-course:latest` | Flask 服务 |
| `ghcr.io/uppi7/zjuse-frontend-course:latest` | 仅含 `/dist`，无启动进程 |


