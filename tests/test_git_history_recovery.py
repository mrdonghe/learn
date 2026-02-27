#!/usr/bin/env python3
"""
测试Git历史恢复功能

根据Anthropic文章《Effective harnesses for long-running agents》的要求，
测试系统是否能从git历史提交重建进度。
"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from src.git_manager import GitManager
    from src.progress_manager import ProgressManager
    from src.feature_manager import FeatureManager

    print("=" * 70)
    print("测试 Git 历史恢复功能 - 与Anthropic文章要求保持一致")
    print("=" * 70)

    def create_test_project() -> Path:
        """创建测试项目，模拟真实开发场景"""
        test_dir = Path(tempfile.mkdtemp(prefix="test_git_recovery_"))
        print(f"创建测试目录: {test_dir}")

        # 初始化git仓库
        import subprocess

        subprocess.run(["git", "init"], cwd=test_dir, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=test_dir,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=test_dir,
            capture_output=True,
        )

        # 创建初始进度文件
        progress_content = f"""# Project Progress

## Status
- Started: {datetime.now().isoformat()}
- Last Updated: {datetime.now().isoformat()}
- Sessions Completed: 0
- Features Completed: 0 / 3

## Current Work
- Current Feature: feature_001

## History
- [{datetime.now().strftime("%Y-%m-%d %H:%M")}] Initial project setup
"""

        (test_dir / "claude-progress.txt").write_text(
            progress_content, encoding="utf-8"
        )

        # 创建功能列表
        feature_list = [
            {
                "id": "feature_001",
                "category": "functional",
                "description": "Implement basic data structure",
                "priority": "high",
                "steps": ["Step 1: Define struct", "Step 2: Implement methods"],
                "passes": False,
                "dependencies": [],
            },
            {
                "id": "feature_002",
                "category": "testing",
                "description": "Add unit tests for data structure",
                "priority": "medium",
                "passes": False,
                "dependencies": ["feature_001"],
            },
            {
                "id": "feature_003",
                "category": "functional",
                "description": "Add CLI interface",
                "priority": "low",
                "passes": False,
                "dependencies": ["feature_001"],
            },
        ]

        (test_dir / "feature_list.json").write_text(
            json.dumps(feature_list, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # 初始提交
        subprocess.run(["git", "add", "-A"], cwd=test_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: initial project setup"],
            cwd=test_dir,
            capture_output=True,
        )

        return test_dir

    def simulate_feature_completion(test_dir: Path, feature_id: str, description: str):
        """模拟完成一个功能"""
        import subprocess

        # 创建一些代码文件
        code_file = test_dir / f"{feature_id}.go"
        code_file.write_text(
            f'// Implementation of {description}\npackage main\n\nfunc main() {{\n\tprintln("Feature {feature_id} implemented")\n}}',
            encoding="utf-8",
        )

        # 更新功能列表
        feature_list_path = test_dir / "feature_list.json"
        if feature_list_path.exists():
            features = json.loads(feature_list_path.read_text(encoding="utf-8"))
            for feature in features:
                if feature["id"] == feature_id:
                    feature["passes"] = True
            feature_list_path.write_text(
                json.dumps(features, indent=2, ensure_ascii=False), encoding="utf-8"
            )

        # 更新进度文件
        progress_path = test_dir / "claude-progress.txt"
        if progress_path.exists():
            content = progress_path.read_text(encoding="utf-8")
            # 更新进度
            lines = content.split("\n")
            for i, line in enumerate(lines):
                if "Features Completed:" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        current = parts[1].strip().split("/")[0]
                        try:
                            lines[i] = f"- Features Completed: {int(current) + 1} / 3"
                        except ValueError:
                            lines[i] = f"- Features Completed: 1 / 3"
                elif "Current Feature:" in line:
                    # 设置下一个功能
                    if feature_id == "feature_001":
                        next_feature = "feature_002"
                    elif feature_id == "feature_002":
                        next_feature = "feature_003"
                    else:
                        next_feature = "feature_001"
                    lines[i] = f"- Current Feature: {next_feature}"
            
            # 添加历史记录
            history_start = -1
            for i, line in enumerate(lines):
                if "## History" in line:
                    history_start = i + 1
                    break
            
            if history_start > 0:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 添加秒数以确保每次不同
                history_entry = f"- [{timestamp}] Completed feature {feature_id}: {description}"
                lines.insert(history_start, history_entry)
            
            progress_path.write_text("\n".join(lines), encoding="utf-8")

        # 提交代码（只提交代码文件）
        subprocess.run(["git", "add", f"{feature_id}.go"], cwd=test_dir, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", f"feat: implement {description[:50]}"],
            cwd=test_dir,
            capture_output=True,
        )

        # 进度更新提交（只提交进度文件）
        subprocess.run(
            ["git", "add", "claude-progress.txt", "feature_list.json"],
            cwd=test_dir,
            capture_output=True,
        )
        # 检查是否有文件需要提交
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=test_dir,
            capture_output=True,
            text=True
        )
        if status_result.stdout.strip():  # 如果有变更，则提交
            subprocess.run(
                ["git", "commit", "-m", "chore: update progress files"],
                cwd=test_dir,
                capture_output=True,
            )
            print(f"   进度更新提交已创建")
        else:
            print(f"   进度文件无变化，跳过提交")

    def test_git_history_recovery():
        """主测试函数"""
        test_dir = None
        try:
            # 1. 创建测试项目
            test_dir = create_test_project()

            # 2. 模拟完成一些功能
            print(f"\n{'=' * 70}")
            print("阶段1: 模拟开发过程")
            print(f"{'=' * 70}")

            simulate_feature_completion(
                test_dir, "feature_001", "Implement basic data structure"
            )
            print("✅ 模拟完成 feature_001")

            simulate_feature_completion(
                test_dir, "feature_002", "Add unit tests for data structure"
            )
            print("✅ 模拟完成 feature_002")

            # 3. 检查git历史
            import subprocess

            git_log = subprocess.run(
                ["git", "log", "--oneline", "-10"],
                cwd=test_dir,
                capture_output=True,
                text=True,
            )
            print(f"\nGit提交历史:")
            print(git_log.stdout)

            # 4. 删除本地进度文件，模拟文件丢失
            print(f"\n{'=' * 70}")
            print("阶段2: 模拟进度文件丢失")
            print(f"{'=' * 70}")

            (test_dir / "claude-progress.txt").unlink(missing_ok=True)
            (test_dir / "feature_list.json").unlink(missing_ok=True)
            print("✅ 删除本地进度文件，模拟中断/丢失场景")

            # 5. 测试从git历史恢复
            print(f"\n{'=' * 70}")
            print("阶段3: 测试从git历史恢复")
            print(f"{'=' * 70}")

            git_manager = GitManager(test_dir)
            progress_manager = ProgressManager(test_dir)

            # 5.1 测试get_file_history
            progress_history = git_manager.get_file_history("claude-progress.txt")
            print(f"claude-progress.txt历史提交数: {len(progress_history)}")
            assert len(progress_history) > 0, "应该能找到进度文件的历史"

            # 5.2 测试restore_progress_from_git
            restore_result = git_manager.restore_progress_from_git()
            print(f"Git恢复结果: {restore_result.get('success', False)}")
            assert restore_result.get("success", False), "Git恢复应该成功"

            progress_content = restore_result.get("progress_content")
            features_content = restore_result.get("features_content")
            assert progress_content is not None, "应该能恢复进度内容"
            assert features_content is not None, "应该能恢复功能列表"

            print(f"✅ 成功从git恢复进度内容 ({len(progress_content)} 字符)")
            print(f"✅ 成功从git恢复功能列表 ({len(features_content)} 字符)")

            # 5.3 测试ProgressManager恢复
            pm_restore_result = progress_manager.restore_from_git_history(git_manager)
            print(f"ProgressManager恢复结果: {pm_restore_result.get('success', False)}")
            assert pm_restore_result.get("success", False), (
                "ProgressManager恢复应该成功"
            )

            restored_progress = pm_restore_result.get("progress", {})
            print(f"恢复的进度状态:")
            print(
                f"  Features Completed: {restored_progress.get('features_completed', 0)}"
            )
            print(f"  Current Work: {restored_progress.get('current_work', 'None')}")

            # 验证恢复的进度正确性
            assert restored_progress.get("features_completed", 0) >= 2, (
                "应该显示至少2个功能已完成"
            )
            print("✅ 恢复的进度数据验证通过")

            # 5.4 测试恢复上下文生成
            print(f"\n{'=' * 70}")
            print("阶段4: 测试恢复上下文生成")
            print(f"{'=' * 70}")

            recovery_context = progress_manager.get_recovery_context(git_manager)
            print(f"恢复上下文长度: {len(recovery_context)} 字符")

            # 验证恢复上下文包含Anthropic文章要求的内容
            required_sections = [
                "Recovery Context",
                "Project Status",
                "Git History",
                "Next Steps",
            ]

            for section in required_sections:
                assert section in recovery_context, f"恢复上下文应包含 '{section}'"

            required_steps = [
                "Run pwd",
                "Read git log",
                "Check claude-progress.txt",
                "Review feature_list.json",
            ]

            for step in required_steps:
                assert step in recovery_context, f"恢复上下文应包含步骤 '{step}'"

            print("✅ 恢复上下文符合Anthropic文章要求")

            # 5.5 测试功能完成分析
            print(f"\n{'=' * 70}")
            print("阶段5: 测试功能完成分析")
            print(f"{'=' * 70}")

            completions = git_manager._analyze_feature_completions()
            print(f"分析到的提交类型数量: {len(completions)}")

            feature_impl_count = sum(
                1 for c in completions if c["type"] == "feature_implementation"
            )
            progress_update_count = sum(
                1 for c in completions if c["type"] == "progress_update"
            )

            print(f"  Feature implementations: {feature_impl_count}")
            print(f"  Progress updates: {progress_update_count}")

            assert feature_impl_count >= 2, "应该分析到至少2个功能实现提交"
            assert progress_update_count >= 2, "应该分析到至少2个进度更新提交"
            print("✅ 功能完成分析验证通过")

            # 6. 验证恢复后的系统状态
            print(f"\n{'=' * 70}")
            print("阶段6: 验证恢复后的系统状态")
            print(f"{'=' * 70}")

            # 检查是否成功恢复了文件
            assert (test_dir / "claude-progress.txt").exists(), "进度文件应该被恢复"
            assert (test_dir / "feature_list.json").exists(), "功能列表文件应该被恢复"

            # 读取恢复后的文件
            restored_features = json.loads(
                (test_dir / "feature_list.json").read_text(encoding="utf-8")
            )
            completed_count = sum(
                1 for f in restored_features if f.get("passes", False)
            )
            print(f"恢复后的功能完成状态: {completed_count}/{len(restored_features)}")

            assert completed_count >= 2, "应该显示至少2个功能已完成"
            print("✅ 文件恢复验证通过")

            print(f"\n{'=' * 70}")
            print("✅ 所有测试通过! Git历史恢复功能正常工作")
            print(f"{'=' * 70}")

            return True

        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback

            traceback.print_exc()
            return False

        finally:
            # 清理测试目录
            if test_dir and test_dir.exists():
                print(f"\n清理测试目录: {test_dir}")
                shutil.rmtree(test_dir, ignore_errors=True)

    # 运行测试
    if test_git_history_recovery():
        sys.exit(0)
    else:
        sys.exit(1)

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 测试初始化失败: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
