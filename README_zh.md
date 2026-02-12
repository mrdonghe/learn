# 第7周

在Week 5基础上稍作增强的全栈入门项目，包含一些后端改进。

- 使用SQLite的FastAPI后端 (SQLAlchemy)
- 静态前端 (无需Node工具链)
- 最小化测试 (pytest)
- 预提交钩子 (black + ruff)
- 相对于Week 5的增强功能：
  - 模型上的时间戳 (`created_at`, `updated_at`)
  - 列表端点的分页和排序
  - 可选过滤器 (例如，按完成状态过滤action items)
  - 用于部分更新的PATCH端点

## 快速开始

1) 创建并激活虚拟环境，然后安装依赖

```bash
cd /Users/mihaileric/Documents/code/modern-software-dev-assignments
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

2) (可选) 安装预提交钩子

```bash
pre-commit install
```

3) 运行应用程序 (从 `week6/` 目录)

```bash
cd week7 && make run
```

打开 `http://localhost:8000` 访问前端，`http://localhost:8000/docs` 访问API文档。

## 项目结构

```
backend/                # FastAPI应用
frontend/               # 由FastAPI服务的静态UI
data/                   # SQLite数据库 + 种子数据
docs/                   # 用于智能体驱动工作流的任务说明
```

## 测试

```bash
cd week7 && make test
```

## 格式化/代码检查

```bash
cd week7 && make format
cd week7 && make lint
```

## 配置

将 `.env.example` 复制到 `.env` (在 `week7/` 目录中) 以覆盖默认配置，如数据库路径。