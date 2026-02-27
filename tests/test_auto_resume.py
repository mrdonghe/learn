#!/usr/bin/env python3
import sys
import os
import tempfile
import json
import shutil
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from infinite_agent import InfiniteAIDeveloper


def test_auto_resume_after_interruption():
    """测试中断后自动继续执行功能

    场景: 5个功能，完成3个后中断，重新启动系统应自动继续执行剩余2个
    """
    test_dir = tempfile.mkdtemp(prefix="test_auto_resume_")
    print(f"Test directory: {test_dir}")

    # 创建5个功能的 feature_list.json
    features = [
        {
            "id": "feature_001",
            "category": "functional",
            "description": "Implement basic module structure",
            "priority": "high",
            "steps": ["Create main.py"],
            "passes": False,
            "dependencies": [],
        },
        {
            "id": "feature_002",
            "category": "functional",
            "description": "Add utility functions",
            "priority": "high",
            "steps": ["Create utils.py"],
            "passes": False,
            "dependencies": ["feature_001"],
        },
        {
            "id": "feature_003",
            "category": "functional",
            "description": "Implement data processing",
            "priority": "medium",
            "steps": ["Create processor.py"],
            "passes": False,
            "dependencies": ["feature_002"],
        },
        {
            "id": "feature_004",
            "category": "testing",
            "description": "Add unit tests",
            "priority": "medium",
            "steps": ["Create test_main.py"],
            "passes": False,
            "dependencies": ["feature_003"],
        },
        {
            "id": "feature_005",
            "category": "documentation",
            "description": "Add documentation",
            "priority": "low",
            "steps": ["Create README.md"],
            "passes": False,
            "dependencies": ["feature_004"],
        },
    ]

    feature_file = os.path.join(test_dir, "feature_list.json")
    with open(feature_file, "w") as f:
        json.dump(features, f, indent=2)

    # 创建进度文件，模拟已完成3个功能，当前正在处理第4个
    progress_file = os.path.join(test_dir, "claude-progress.txt")
    with open(progress_file, "w") as f:
        f.write(f"""# Project Progress

## Status
- Started: {datetime.now().isoformat()}
- Last Updated: {datetime.now().isoformat()}
- Sessions Completed: 3
- Features Completed: 3 / 5

## Current Work
- Current Feature: feature_004

## History
- [{datetime.now().strftime("%Y-%m-%d %H:%M")}] Completed feature_001
- [{datetime.now().strftime("%Y-%m-%d %H:%M")}] Completed feature_002
- [{datetime.now().strftime("%Y-%m-%d %H:%M")}] Completed feature_003
""")

    # 创建初始化脚本
    init_file = os.path.join(test_dir, "init.sh")
    with open(init_file, "w") as f:
        f.write("#!/bin/bash\necho 'Initialized'\n")
    os.chmod(init_file, 0o755)

    # 初始化git仓库
    import subprocess

    subprocess.run(["git", "init"], cwd=test_dir, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=test_dir,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=test_dir, capture_output=True
    )

    # 创建模拟的已完成功能的文件
    os.makedirs(os.path.join(test_dir, "src"), exist_ok=True)
    for i in range(1, 4):
        filename = os.path.join(test_dir, f"feature_{i:03d}.py")
        with open(filename, "w") as f:
            f.write(f"# Feature {i} implementation\n")
        subprocess.run(["git", "add", "."], cwd=test_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"feat: implement feature_{i:03d}"],
            cwd=test_dir,
            capture_output=True,
        )

    # 更新feature_list.json，标记前3个为完成
    with open(feature_file, "r") as f:
        features = json.load(f)

    for feature in features:
        if feature["id"] in ["feature_001", "feature_002", "feature_003"]:
            feature["passes"] = True

    with open(feature_file, "w") as f:
        json.dump(features, f, indent=2)

    # 创建 InfiniteAIDeveloper 实例
    dev = InfiniteAIDeveloper(test_dir)

    # 模拟 OpenCode 行为
    call_count = {"coding": 0, "initializer": 0}

    def mock_run_opencode(prompt, agent_type, timeout=None):
        call_count[agent_type] = call_count.get(agent_type, 0) + 1

        if agent_type == "coding":
            # 获取当前未完成的功能
            pending_features = dev.feature_manager.get_pending_features()
            if not pending_features:
                return {"success": True, "no_more_features": True}

            # 模拟实现当前功能
            current_feature = pending_features[0]  # 应该已经是 feature_004
            feature_id = current_feature["id"]

            # 创建对应的文件
            if feature_id == "feature_004":
                filename = os.path.join(test_dir, "test_main.py")
                with open(filename, "w") as f:
                    f.write("import unittest\n# Tests for the project\n")
            elif feature_id == "feature_005":
                filename = os.path.join(test_dir, "README.md")
                with open(filename, "w") as f:
                    f.write("# Project Documentation\n")

            # 标记功能为完成
            dev.feature_manager.mark_feature_complete(feature_id)

            # 模拟git提交
            subprocess.run(["git", "add", "."], cwd=test_dir, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", f"feat: implement {feature_id}"],
                cwd=test_dir,
                capture_output=True,
            )

            return {"success": True, "feature_completed": feature_id}

        elif agent_type == "initializer":
            # 初始化代理 - 不应该被调用，因为项目已初始化
            return {"success": True, "already_initialized": True}

        return {"success": False, "error": "Unknown agent type"}

    # 替换 _run_opencode 方法
    original_run_opencode = dev._run_opencode
    dev._run_opencode = mock_run_opencode

    print("\n=== 步骤1: 验证恢复状态检测 ===")
    # 检查进度读取
    progress = dev.progress_manager.get_progress()
    print(
        f"进度读取: 完成 {progress['features_completed']}/{progress['features_total']} 功能"
    )
    print(f"当前工作: {progress['current_work']}")

    # 检查未完成功能
    pending = dev.feature_manager.get_pending_features()
    print(f"未完成功能: {[f['id'] for f in pending]}")

    # 验证当前工作是否正确检测为 feature_004
    assert progress["current_work"] == "feature_004", (
        f"Expected current_work=feature_004, got {progress['current_work']}"
    )
    assert len(pending) == 2, f"Expected 2 pending features, got {len(pending)}"
    assert pending[0]["id"] == "feature_004", (
        f"Expected first pending feature to be feature_004, got {pending[0]['id']}"
    )

    print("✅ 恢复状态检测通过")

    print("\n=== 步骤2: 运行系统自动继续 ===")
    # 运行系统，限制最大会话数为2（完成剩余2个功能）
    # 注意：run() 方法需要 user_prompt，但这里只是继续执行
    # 我们可以直接调用 run_coding_session 两次，但更好的方法是测试整个流程

    # 由于 run() 需要 user_prompt，我们直接模拟循环
    completed_features_before = dev.feature_manager.get_completed_count()
    print(f"开始前完成的功能数: {completed_features_before}/5")

    # 运行两个coding session来完成剩余功能
    print("\n执行第一个coding session (应该完成 feature_004)...")
    result1 = dev.run_coding_session()
    print(f"结果: {result1}")

    # 检查 feature_004 是否完成
    feature_004 = dev.feature_manager.get_feature_by_id("feature_004")
    assert feature_004["passes"] == True, (
        f"Feature 004 should be completed, but passes={feature_004.get('passes')}"
    )

    print("\n执行第二个coding session (应该完成 feature_005)...")
    result2 = dev.run_coding_session()
    print(f"结果: {result2}")

    # 检查 feature_005 是否完成
    feature_005 = dev.feature_manager.get_feature_by_id("feature_005")
    assert feature_005["passes"] == True, (
        f"Feature 005 should be completed, but passes={feature_005.get('passes')}"
    )

    completed_features_after = dev.feature_manager.get_completed_count()
    print(f"完成后完成的功能数: {completed_features_after}/5")

    assert completed_features_after == 5, (
        f"Expected 5 completed features, got {completed_features_after}"
    )

    print("✅ 自动继续执行通过")

    print("\n=== 步骤3: 验证日志输出包含恢复提示 ===")
    # 由于我们直接调用了 run_coding_session，没有看到 run() 中的恢复日志
    # 我们可以测试进度管理器是否更新了当前工作

    # 恢复原始方法
    dev._run_opencode = original_run_opencode

    # 清理
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory")

    return True


def test_resume_with_failed_feature():
    """测试中断在失败功能后的恢复"""
    test_dir = tempfile.mkdtemp(prefix="test_resume_failed_")
    print(f"\n=== 失败功能恢复测试目录: {test_dir} ===")

    features = [
        {
            "id": "feature_a",
            "category": "functional",
            "description": "Basic functionality",
            "priority": "high",
            "steps": ["Create basic.py"],
            "passes": False,
            "dependencies": [],
        },
        {
            "id": "feature_b",
            "category": "functional",
            "description": "Advanced functionality",
            "priority": "high",
            "steps": ["Create advanced.py"],
            "passes": False,
            "dependencies": ["feature_a"],
        },
    ]

    feature_file = os.path.join(test_dir, "feature_list.json")
    with open(feature_file, "w") as f:
        json.dump(features, f, indent=2)

    # 设置当前工作为 feature_b，但 feature_a 未完成（依赖未满足）
    progress_file = os.path.join(test_dir, "claude-progress.txt")
    with open(progress_file, "w") as f:
        f.write(f"""# Project Progress

## Status
- Started: {datetime.now().isoformat()}
- Last Updated: {datetime.now().isoformat()}
- Sessions Completed: 1
- Features Completed: 0 / 2

## Current Work
- Current Feature: feature_b

## History
- [{datetime.now().strftime("%Y-%m-%d %H:%M")}] Started project
""")

    # 其他必要文件
    init_file = os.path.join(test_dir, "init.sh")
    with open(init_file, "w") as f:
        f.write("#!/bin/bash\necho 'Initialized'\n")
    os.chmod(init_file, 0o755)

    import subprocess

    subprocess.run(["git", "init"], cwd=test_dir, capture_output=True)

    dev = InfiniteAIDeveloper(test_dir)

    # 验证恢复逻辑应该跳过 feature_b（依赖未满足），选择 feature_a
    pending = dev.feature_manager.get_pending_features()
    progress = dev.progress_manager.get_progress()

    print(f"当前工作: {progress['current_work']}")
    print(f"未完成功能: {[f['id'] for f in pending]}")

    # 由于依赖检查，feature_b 应该被跳过，feature_a 应该被优先处理
    # 但我们的恢复逻辑会检查依赖，如果依赖不满足会打印警告并按正常顺序执行

    # 运行 coding session 应该处理 feature_a
    # 模拟 OpenCode
    def mock_run_opencode(prompt, agent_type, timeout=None):
        if agent_type == "coding":
            # 检查prompt中是否包含feature_a
            if "feature_a" in prompt or "Basic functionality" in prompt:
                # 创建文件
                with open(os.path.join(test_dir, "basic.py"), "w") as f:
                    f.write("# Basic functionality\n")
                dev.feature_manager.mark_feature_complete("feature_a")
                return {"success": True, "feature_completed": "feature_a"}
        return {"success": False, "error": "Unexpected call"}

    dev._run_opencode = mock_run_opencode

    result = dev.run_coding_session()
    print(f"Coding session result: {result}")

    # 验证 feature_a 完成
    feature_a = dev.feature_manager.get_feature_by_id("feature_a")
    assert feature_a["passes"] == True, (
        f"Feature a should be completed after dependency resolution"
    )

    print("✅ 依赖未满足时的恢复逻辑通过")

    shutil.rmtree(test_dir)
    print("Cleaned up test directory")

    return True


if __name__ == "__main__":
    print("Running auto-resume tests...")
    try:
        success1 = test_auto_resume_after_interruption()
        success2 = test_resume_with_failed_feature()

        if success1 and success2:
            print("\n🎉 所有自动继续测试通过!")
            sys.exit(0)
        else:
            print("\n❌ 部分测试失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
