"""
全局常量定义文件 - Global Constants

此文件包含无限AI开发系统中使用的所有超时设置和其他常量。
将硬编码的超时值统一管理在此处，便于修改和维护。
"""

# ============================================================================
# OpenCode 超时设置
# ============================================================================


class TimeoutConstants:
    """超时常量类"""

    # OpenCode 执行超时
    OPENCODE_DEFAULT = 3600  # 默认OpenCode超时 (1小时)
    OPENCODE_INITIAL = 180  # Initializer首次运行较短超时 (3分钟)
    OPENCODE_RETRY = 3600  # 重试用满时间 (1小时)
    OPENCODE_COMMUNICATE = 5  # process.communicate超时 (5秒)
    OPENCODE_CONFIG_FALLBACK = 600  # 配置读取失败时的备用超时 (10分钟)

    # OpenCode API 超时
    OPENCODE_API_SESSION = 10  # API创建session超时 (10秒)
    OPENCODE_API_POLL = 30  # API轮询超时 (30秒)

    # 测试相关超时
    TEST_E2E = 300  # 端到端测试超时 (5分钟)
    TEST_BASIC = 300  # 基本测试超时 (5分钟)
    TEST_UNIT = 120  # 单元测试超时 (2分钟)
    TEST_VERIFY = 10  # 服务验证超时 (10秒)

    INIT_SCRIPT = 30  # init.sh脚本执行超时 (30秒)
    # 会话管理超时
    SESSION_SAVE_INTERVAL = 300  # 会话保存间隔 (5分钟)

    # 系统默认超时 (用于测试和诊断)
    SYSTEM_TIMEOUT_SHORT = 30  # 短超时 (30秒，用于简单测试)
    SYSTEM_TIMEOUT_MEDIUM = 60  # 中等超时 (1分钟)
    SYSTEM_TIMEOUT_LONG = 120  # 长超时 (2分钟)


# ============================================================================
# Git 相关常量
# ============================================================================


class GitConstants:
    """Git相关常量"""

    # Git 配置
    GIT_USER_NAME = "Infinite AI Developer"
    GIT_USER_EMAIL = "ai@infinite-developer.local"

    # 提交消息模板
    COMMIT_MSG_INITIAL = "feat: initial project setup"
    COMMIT_MSG_FEATURE_PREFIX = "feat: implement "
    COMMIT_MSG_BUGFIX_PREFIX = "fix: "
    COMMIT_MSG_REFACTOR_PREFIX = "refactor: "
    COMMIT_MSG_TEST_PREFIX = "test: "

    # 分支命名
    BRANCH_MAIN = "main"
    BRANCH_DEVELOP = "develop"
    BRANCH_FEATURE_PREFIX = "feature/"
    BRANCH_BUGFIX_PREFIX = "bugfix/"
    BRANCH_HOTFIX_PREFIX = "hotfix/"


# ============================================================================
# 系统配置常量
# ============================================================================


class SystemConstants:
    """系统配置常量"""

    # 文件路径常量
    FEATURE_LIST_FILE = "feature_list.json"
    PROGRESS_FILE = "claude-progress.txt"
    INIT_SCRIPT_FILE = "init.sh"

    # 目录路径常量
    PROMPTS_DIR = "prompts"
    TESTS_DIR = "tests"
    SRC_DIR = "src"
    CONFIG_DIR = "config"

    # 功能管理常量
    FEATURE_MIN_COUNT = 2
    FEATURE_MAX_COUNT = 50
    FEATURE_MAX_RETRIES = 2

    # Agent 类型
    AGENT_TYPE_INITIALIZER = "initializer"
    AGENT_TYPE_CODING = "coding"

    # 功能状态
    FEATURE_STATUS_PENDING = "pending"
    FEATURE_STATUS_IN_PROGRESS = "in_progress"
    FEATURE_STATUS_COMPLETED = "completed"
    FEATURE_STATUS_SKIPPED = "skipped"

    # 优先级
    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"


# ============================================================================
# 导出常用别名
# ============================================================================

# 超时常量别名
OPENCODE_TIMEOUT = TimeoutConstants.OPENCODE_DEFAULT
OPENCODE_INITIAL_TIMEOUT = TimeoutConstants.OPENCODE_INITIAL
OPENCODE_RETRY_TIMEOUT = TimeoutConstants.OPENCODE_RETRY
TEST_E2E_TIMEOUT = TimeoutConstants.TEST_E2E
TEST_UNIT_TIMEOUT = TimeoutConstants.TEST_UNIT

# Git 常量别名
GIT_DEFAULT_NAME = GitConstants.GIT_USER_NAME
GIT_DEFAULT_EMAIL = GitConstants.GIT_USER_EMAIL
COMMIT_INITIAL = GitConstants.COMMIT_MSG_INITIAL

# 系统常量别名
FEATURE_LIST = SystemConstants.FEATURE_LIST_FILE
PROGRESS_FILE = SystemConstants.PROGRESS_FILE
INIT_FILE = SystemConstants.INIT_SCRIPT_FILE
