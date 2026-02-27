# Infinite AI Developer

基于 OpenCode 的无限运行 AI 开发系统，参考 [Anthropic 文章](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 实现。

## 概述

本系统实现了 Anthropic 文章《Effective harnesses for long-running agents》中描述的长期运行 AI 代理最佳实践，基于 OpenCode 构建一个可以无限运行的 AI 开发系统。核心思想是通过状态恢复、增量开发和严格验证，使 AI 代理能够跨越多个上下文窗口进行长期、稳定的软件开发。

### 主要思想

1. **状态持久化与恢复**：通过 git 提交历史重建进度，即使系统中断也能从上次停止的地方继续
2. **增量式开发**：每次只实现一个功能，避免一次性构建整个应用
3. **严格的测试保护**：遵循"绝不删除或修改测试"原则，确保代码质量
4. **基础功能验证**：每次会话开始前验证基本功能是否正常，优先修复而非添加新功能
5. **双代理架构**：Initializer Agent 负责初始化环境，Coding Agent 负责增量开发
6. **全局配置管理**：所有超时和配置集中管理，便于维护和修改


## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    InfiniteAIDeveloper                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Initializer │  │   Coding     │  │    Test      │    │
│  │    Agent     │  │    Agent     │  │    Runner    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Feature    │  │  Progress    │  │     Git      │    │
│  │   Manager    │  │   Manager    │  │   Manager    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 核心概念

### 1. 双 Agent 架构

- **Initializer Agent**: 首次运行时执行，创建 feature list、init.sh、进度文件等
- **Coding Agent**: 后续每次会话执行，增量实现一个功能

### 2. Feature List

详细的功能列表，JSON 格式，每个功能包含：
- 描述
- 测试步骤
- 通过状态
- 优先级
- 依赖

### 3. Progress 追踪

记录每个会话的工作：
- 会话数
- 完成的功能数
- 当前工作
- 历史记录

### 4. Git 集成

- 每次功能完成后自动 commit
- 可以回滚到任意版本

### 5. Git 历史恢复

基于 Anthropic 文章的核心思想：即使本地进度文件丢失，也能从 git 提交历史重建开发进度。

- **进度恢复**：从 `claude-progress.txt` 和 `feature_list.json` 的历史版本重建状态
- **功能完成分析**：分析 git 提交消息，自动识别已实现的功能
- **恢复上下文生成**：为 OpenCode 提供完整的项目上下文，包括历史工作记录

### 6. 基础功能验证

遵循 Anthropic 文章要求：每次 Coding Session 开始前验证基础功能是否正常工作。

- **服务器状态检查**：通过 curl 验证开发服务器是否运行
- **init.sh 执行**：如果服务器未运行，自动执行 init.sh 启动脚本
- **验证失败处理**：如果基础功能损坏，停止新功能实现，返回修复需求

### 7. 测试保护机制

严格执行 Anthropic 文章要求："绝不能删除或修改测试"。

- **测试保护措辞**：在 Coding Prompt 中使用 Anthropic 原文："It is unacceptable to remove or edit tests because this could lead to missing or buggy functionality."
- **测试优先原则**：如果测试失败，修复实现代码而非修改测试
- **JSON 格式保护**：使用 JSON 格式的 feature list，减少误修改风险

### 8. 全局常量管理

所有超时设置和配置项集中管理，便于维护和修改。

- **超时常量**：OpenCode 执行、测试运行、脚本执行等超时统一管理
- **Git 常量**：提交消息模板、分支命名规范等
- **系统常量**：文件路径、功能状态、优先级定义

### 9. 增量开发与状态管理

- **单功能原则**：每次只实现一个功能，避免 one-shot 开发
- **依赖检查**：只有依赖功能全部完成才执行当前功能
- **中断恢复**：支持从上次中断的功能继续开发
- **进度持久化**：每次会话后更新进度文件和 git 提交


## 与 Anthropic 文章的一致性

本系统严格遵循 Anthropic 文章《Effective harnesses for long-running agents》的最佳实践，实现了文章中描述的所有关键机制：

### ✅ 完全符合的要求

| 要求 | 文章原文 | 本系统实现 |
|------|----------|-----------|
| **双代理架构** | "Initializer agent for first run, Coding agent for subsequent sessions" | `run_initializer()` 和 `run_coding_session()` 分离 |
| **测试保护** | "It is unacceptable to remove or edit tests" | 在 `coding_prompt.md` 中使用原文，并添加额外保护措辞 |
| **Git 历史恢复** | "Use git to revert bad code changes and recover working states" | `restore_from_git_history()`、`get_recovery_context()` |
| **增量开发** | "One feature at a time. Never one-shot the app." | 每次只选择最高优先级功能，prompt 中明确禁止 one-shot |
| **基础功能验证** | "Run basic end-to-end test before implementing a new feature" | `_verify_basic_functionality()` 在每个 Coding Session 开始时调用 |
| **进度追踪** | "Write summaries of its progress in a progress file" | `claude-progress.txt` 记录每个会话工作 |
| **Git 提交** | "Commit with descriptive messages after each session" | 自动 commit 功能实现，支持 push 到远程仓库 |

### 📋 实现的核心机制

1. **状态恢复机制**：从 git 提交历史重建 `claude-progress.txt` 和 `feature_list.json`
2. **验证优先原则**：基础功能验证失败时停止新功能开发，优先修复
3. **测试完整性保护**：使用 JSON 格式和强措辞防止测试被修改
4. **超时全局管理**：所有超时设置集中在 `src/constants.py`，便于调整
5. **完整 git 流程**：add → commit → push，支持从任意提交点恢复

### 🧪 已验证的功能

- ✅ Git 历史恢复测试通过 (`tests/test_git_history_recovery.py`)
- ✅ 基础功能验证测试通过
- ✅ 测试保护措辞包含 Anthropic 原文
- ✅ 全局常量替换所有硬编码超时
- ✅ 完整的 git add → commit → push 流程

### ⚠️ 注意事项

- 默认配置 `auto_push: false`，需要手动启用远程推送
- 基础功能验证目前仅检查服务器运行状态，可扩展更多检查
- 修复会话需要外部调度器触发（返回 `should_repair: true` 状态）

## 使用方法

### 1. 安装依赖

```bash
pip install pyyaml requests
```

### 2. 运行系统

```bash
python infinite_agent.py /path/to/project -p "你的需求描述"
```

### 3. 配置

编辑 `config/settings.yaml` 自定义配置。

## 文件结构

```
infinite_ai_developer/
├── infinite_agent.py      # 主控制器
├── prompts/
│   ├── init_prompt.md    # Initializer prompt (主)
│   ├── init_concise.md   # 简洁版 Initializer prompt
│   ├── init_prompt_simple.md # 简化版 Initializer prompt
│   ├── init_prompt_v2.md # Version 2 Initializer prompt
│   ├── coding_prompt.md  # Coding prompt (主)
│   └── coding_concise.md # 简洁版 Coding prompt
├── src/
│   ├── __init__.py
│   ├── constants.py          # 全局常量定义 (超时、Git配置等)
│   ├── opencode_manager.py   # OpenCode CLI/Server 集成
│   ├── feature_manager.py    # 功能列表管理
│   ├── progress_manager.py   # 进度追踪
│   ├── session_manager.py    # 会话管理
│   ├── git_manager.py        # Git 集成
│   └── test_runner.py        # 测试运行器
├── config/
│   └── settings.yaml    # 配置文件
├── tests/               # 测试代码目录
│   ├── test_complete.py     # 完整工作流测试
│   ├── test_opencode_simple.py # OpenCode 集成测试
│   ├── test_git_history_recovery.py # Git历史恢复测试
└── README.md
```

## 参考

- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)
