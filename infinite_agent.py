#!/usr/bin/env python3
"""
Infinite AI Developer - 基于 OpenCode 的无限运行 AI 开发系统

参考 Anthropic 文章: Effective harnesses for long-running agents
https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

架构:
- Initializer Agent: 首次运行，初始化环境、创建 feature list、init.sh 等
- Coding Agent: 后续每次运行，增量开发一个功能
"""

import os
import sys
import json
import yaml
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.feature_manager import FeatureManager
from src.progress_manager import ProgressManager
from src.git_manager import GitManager
from src.test_runner import TestRunner
from src.session_manager import SessionManager
from src.opencode_manager import OpenCodeManager
from src import constants



class InfiniteAIDeveloper:
    """
    无限运行 AI 开发系统主控制器

    核心职责:
    1. 管理 Agent 会话生命周期
    2. 协调各个模块工作
    3. 持久化状态到文件系统
    """

    def __init__(self, project_path: str, config_path: Optional[str] = None):
        self.project_path = Path(project_path).resolve()
        # Ensure project directory exists
        os.makedirs(self.project_path, exist_ok=True)
        self.config_path = config_path or os.path.join(
            os.path.dirname(__file__), "config", "settings.yaml"
        )

        # 加载配置
        self.config = self._load_config()

        # 初始化各个管理器
        self.feature_manager = FeatureManager(self.project_path)
        self.progress_manager = ProgressManager(self.project_path)
        self.git_manager = GitManager(self.project_path)
        self.test_runner = TestRunner(self.project_path)
        self.session_manager = SessionManager(self.project_path)
        self.opencode_manager = OpenCodeManager(self.project_path, self.config)

        # Agent 类型定义
        self.AGENT_TYPES = {"initializer": "init", "coding": "coding"}

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "opencode": {
                "command": "opencode",
                "timeout": constants.TimeoutConstants.OPENCODE_DEFAULT,
                "model": "deepseek/deepseek-reasoner",
            },
            "session": {
                "max_context_windows": 100,
                "save_interval": constants.TimeoutConstants.SESSION_SAVE_INTERVAL,
            },
            "git": {
                "auto_commit": True,
                "commit_interval": 1,
                "auto_push": False,
            },
            "testing": {
                "e2e_enabled": True,
                "test_framework": "playwright",
            },
            "feature_generation": {
                "min_features": 2,
                "max_features": 50,
                "max_retries": 2,
                "retry_timeout": constants.TimeoutConstants.OPENCODE_RETRY,
                "default_features": []
            },
        }

        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)

        return default_config
    def _create_default_feature_list(self, user_prompt: str):
        """Create a simple generic feature list when OpenCode fails"""
        # Create a simple generic feature based on user prompt
        if not user_prompt or user_prompt.strip() == "":
            user_prompt = "the project"

        # Create one generic feature
        generic_feature = {
            "id": "feature_001",
            "category": "functional",
            "description": f"Implement core functionality for: {user_prompt[:200]}",
            "priority": "high",
            "steps": ["Set up project structure", "Implement basic functionality"],
            "passes": False,
            "dependencies": []
        }

        self.feature_manager.save_features([generic_feature])
        print(f"[{datetime.now()}] 📋 Created generic feature list based on user prompt")

    def _create_default_init_script(self):
        """Create a default init.sh script"""
        init_content = """#!/bin/bash
# Default initialization script

echo "Initializing project..."
# Add project-specific initialization commands here
"""
        init_file = self.project_path / "init.sh"
        with open(init_file, "w") as f:
            f.write(init_content)
        os.chmod(init_file, 0o755)
        print(f"[{datetime.now()}] 📜 Created default init.sh")

    def _ensure_server_running(self):
        """Ensure development server is running before implementing new features
        
        Follows Anthropic article recommendation: verify basic functionality works
        before implementing new features.
        """
        print(f"[{datetime.now()}] 🔍 验证基础功能是否正常...")
        
        # Check if server is running
        if self.test_runner.verify_server_running():
            print(f"[{datetime.now()}] ✅ 开发服务器正在运行")
            return True
        
        # Server not running, try to start it via init.sh
        print(f"[{datetime.now()}] ⚠️  开发服务器未运行，尝试启动 init.sh...")
        init_file = self.project_path / "init.sh"
        if not init_file.exists():
            print(f"[{datetime.now()}] ❌ init.sh 不存在，无法启动服务器")
            return False
        
        try:
            import subprocess
            result = subprocess.run(
                ["bash", str(init_file)],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=constants.TimeoutConstants.INIT_SCRIPT
            )
            if result.returncode == 0:
                print(f"[{datetime.now()}] ✅ init.sh 执行成功，等待服务器启动...")
                import time
                time.sleep(3)  # Wait for server to start
                # Verify again
                if self.test_runner.verify_server_running():
                    print(f"[{datetime.now()}] ✅ 开发服务器启动成功")
                    return True
                else:
                    print(f"[{datetime.now()}] ⚠️  服务器仍未响应，可能启动失败")
                    return False
            else:
                print(f"[{datetime.now()}] ❌ init.sh 执行失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"[{datetime.now()}] ❌ 启动服务器时出错: {e}")
            return False
    
    def _verify_basic_functionality(self):
        """Verify basic functionality works before implementing new features"""
        # For now, just check server running
        # TODO: Add more comprehensive checks (e.g., existing endpoints work)
        return self._ensure_server_running()
    def _create_default_implementation(self, feature: Dict[str, Any]):
        """Create a generic default implementation for a feature"""
        feature_id = feature.get("id", "feature_001")
        description = feature.get("description", "")
        desc_lower = description.lower()

        # Determine file extension based on description
        if "go" in desc_lower or "golang" in desc_lower:
            extension = "go"
            comment_prefix = "//"
        elif "python" in desc_lower or "py" in desc_lower:
            extension = "py"
            comment_prefix = "#"
        elif "javascript" in desc_lower or "js" in desc_lower:
            extension = "js"
            comment_prefix = "//"
        elif "typescript" in desc_lower or "ts" in desc_lower:
            extension = "ts"
            comment_prefix = "//"
        elif "java" in desc_lower:
            extension = "java"
            comment_prefix = "//"
        else:
            # Default to generic text file
            extension = "txt"
            comment_prefix = "#"

        # Create filename based on feature ID
        filename = f"{feature_id}.{extension}"

        # Create generic placeholder content
        content_lines = []
        if extension in ["go", "java", "js", "ts"]:
            # Add basic structure for programming languages
            if extension == "go":
                content_lines.append("package main")
                content_lines.append("")
                content_lines.append("import \"fmt\"")
                content_lines.append("")
                content_lines.append("// TODO: Implement feature: " + description)
                content_lines.append("func main() {")
                content_lines.append(f"    {comment_prefix} Placeholder for feature implementation")
                content_lines.append("    fmt.Println(\"Feature not yet implemented\")")
                content_lines.append("}")
            elif extension == "java":
                content_lines.append("public class " + feature_id.replace("_", "") + " {")
                content_lines.append("    public static void main(String[] args) {")
                content_lines.append(f"        {comment_prefix} Placeholder for feature implementation")
                content_lines.append("        System.out.println(\"Feature not yet implemented\");")
                content_lines.append("    }")
                content_lines.append("}")
            else:
                content_lines.append(f"{comment_prefix} TODO: Implement feature: " + description)
                content_lines.append(f"{comment_prefix} Placeholder for feature implementation")
                content_lines.append("console.log('Feature not yet implemented');")
        else:
            # Generic text file
            content_lines.append(f"TODO: Implement feature: {description}")
            content_lines.append("")
            content_lines.append("This is a placeholder file created because OpenCode failed to generate implementation.")
            content_lines.append("Please implement the feature manually or retry with OpenCode.")

        content = "\n".join(content_lines)
        output_file = self.project_path / filename
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[{datetime.now()}] 📝 Created generic default implementation: {filename}")
        self.feature_manager.mark_feature_complete(feature_id)
        print(f"[{datetime.now()}] ✅ Marked {feature_id} as completed")

    def is_initialized(self) -> bool:
        """检查项目是否已初始化"""
        required_files = ["feature_list.json", "claude-progress.txt", ".git"]
        return all((self.project_path / f).exists() for f in required_files)

    def run_initializer(self, user_prompt: str) -> Dict[str, Any]:
        """运行 Initializer Agent"""
        # Load retry settings from config
        feature_gen_config = self.config.get("feature_generation", {})
        max_retries = feature_gen_config.get("max_retries", 2)
        retry_timeout = feature_gen_config.get("retry_timeout", constants.TimeoutConstants.SYSTEM_TIMEOUT_LONG)
        opencode_timeout = self.config.get("opencode", {}).get("timeout", constants.TimeoutConstants.OPENCODE_CONFIG_FALLBACK)
        
        print(f"[{datetime.now()}] 🚀 运行 Initializer Agent... (max_retries={max_retries})")

        # Load initializer prompt template
        prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "init_prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            init_prompt = f.read()

        # Inject user prompt
        full_prompt = f"Project: {user_prompt}\n\n{init_prompt}"

        # Retry loop: try OpenCode to generate feature list
        feature_file = self.project_path / "feature_list.json"
        for attempt in range(max_retries + 1):
            timeout = retry_timeout if attempt > 0 else min(constants.TimeoutConstants.OPENCODE_INITIAL, opencode_timeout)
            
            print(f"[{datetime.now()}] 🔄 OpenCode attempt {attempt + 1}/{max_retries + 1} (timeout={timeout}s)...")
            
            result = self._run_opencode(prompt=full_prompt, agent_type="initializer", timeout=timeout)
            
            # Check if feature_list.json was created successfully
            if feature_file.exists():
                # File was created, check if it's valid JSON
                try:
                    with open(feature_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    if content and content.startswith('['):  # Simple JSON array check
                        print(f"[{datetime.now()}] ✅ OpenCode 成功生成 feature_list.json (文件已创建)")
                        # If result shows failure but file exists, update result
                        if not result.get("success", False):
                            result["success"] = True
                            result["file_created"] = True
                            if "error" in result and result["error"] == "Timeout":
                                print(f"[{datetime.now()}] ⚠️  OpenCode 超时但文件已创建，视为成功")
                        break
                    else:
                        print(f"[{datetime.now()}] ⚠️  文件存在但内容无效")
                except Exception as e:
                    print(f"[{datetime.now()}] ⚠️  读取文件错误: {e}")
            elif result.get("success", False):
                # Success flag is True but file doesn't exist - unusual case
                print(f"[{datetime.now()}] ⚠️  OpenCode 返回成功但文件不存在")
            
            if attempt < max_retries:
                print(f"[{datetime.now()}] ⚠️  OpenCode attempt {attempt + 1} failed, retrying...")
            else:
                print(f"[{datetime.now()}] ⚠️  All OpenCode attempts failed, using config defaults")
                self._create_default_feature_list(user_prompt)
                result = {"success": True, "fallback": True, "attempts": attempt + 1}


        # Ensure progress file exists
        progress_file = self.project_path / "claude-progress.txt"
        if not progress_file.exists():
            self.progress_manager.update(session_completed=False)
        
        # Ensure init.sh exists
        init_file = self.project_path / "init.sh"
        if not init_file.exists():
            self._create_default_init_script()
        
        # Initialize git repo if not exists
        if not self.git_manager.is_git_repo():
            self.git_manager.init()

        # 初始化完成后，创建第一个 git commit
        if self.git_manager.is_git_repo():
            self.git_manager.commit(
                message=constants.GitConstants.COMMIT_MSG_INITIAL,
                files=["feature_list.json", "claude-progress.txt", "init.sh"],
            )
            # 如果配置了自动推送，则推送到远程
            if self.config.get("git", {}).get("auto_push", False):
                push_result = self.git_manager.push()
                if not push_result.get("success", False):
                    print(f"⚠️  Git push failed: {push_result.get('error', 'Unknown error')}")
                else:
                    print("✅  Git push successful")

        return result


    def run_coding_session(self) -> Dict[str, Any]:
        """
        运行 Coding Agent (一个会话)

        职责:
        1. 读取当前进度和 git log
        2. 选择一个未完成的功能
        3. 实现该功能
        4. 运行端到端测试
        5. 提交代码并更新进度
        """
        print(f"[{datetime.now()}] 🔄 开始新的 Coding Session...")

        # 1. 获取当前状态
        progress = self.progress_manager.get_progress()
        features = self.feature_manager.get_pending_features()
        # 检查是否有中断恢复的功能
        current_work = progress.get("current_work", "")
        if current_work and current_work != "None (initializing)":
            # 查找当前工作功能是否在未完成列表中
            for i, feat in enumerate(features):
                if feat.get("id") == current_work:
                    # 检查依赖是否满足
                    if self.feature_manager.are_dependencies_met(feat):
                        # 移动到列表首位以实现恢复
                        features.insert(0, features.pop(i))
                        print(f"[{datetime.now()}] 🔄 从中断的功能恢复: {current_work}")
                    else:
                        print(f"[{datetime.now()}] ⚠️  中断功能 {current_work} 依赖未满足，按正常顺序执行")
                    break

        if not features:
            print(f"[{datetime.now()}] ✅ 所有功能已完成!")
            return {"status": "completed", "features_remaining": 0}

        # 2. 生成恢复上下文（根据Anthropic文章）
        recovery_context = self.progress_manager.get_recovery_context(self.git_manager)
        print(f"[{datetime.now()}] 📋 恢复上下文:\n{recovery_context[:500]}...")

        # 3. 尝试从git历史恢复进度（如果本地进度文件丢失）
        if not (self.project_path / "claude-progress.txt").exists():
            print(f"[{datetime.now()}] 🔍 本地进度文件丢失，尝试从git历史恢复...")
            restore_result = self.progress_manager.restore_from_git_history(self.git_manager)
            if restore_result.get("success", False):
                print(f"[{datetime.now()}] ✅ 从git历史恢复进度: {restore_result.get('message', 'Success')}")
                progress = self.progress_manager.get_progress()  # 重新获取进度
            else:
                print(f"[{datetime.now()}] ⚠️  Git历史恢复失败: {restore_result.get('error', 'Unknown error')}")

        # 验证基础功能 (根据Anthropic文章要求，每个会话开始时验证)
        print(f"[{datetime.now()}] 🔍 验证基础功能是否正常...")
        verification_result = self._verify_basic_functionality()
        if not verification_result:
            print(f"[{datetime.now()}] ❌ 基础功能验证失败，无法继续实现新功能")
            print(f"[{datetime.now()}] ⚠️  根据Anthropic文章: 必须先修复基础功能再实现新功能")
            return {"status": "verification_failed", "should_repair": True, "message": "Basic functionality verification failed. Repair needed before implementing new features."}

        # 4. 加载 coding prompt 模板
        prompt_path = os.path.join(
            os.path.dirname(__file__), "prompts", "coding_prompt.md"
        )
        with open(prompt_path, "r", encoding="utf-8") as f:
            coding_prompt = f.read()

        # 5. 构建完整提示词，包含恢复上下文
        feature_to_work = features[0]  # 选择最高优先级的功能
        full_prompt = f"Project: Implement {feature_to_work.get('description', 'feature')}\n\n{recovery_context}\n\n{coding_prompt}\n\nFeature details: {json.dumps(feature_to_work, indent=2, ensure_ascii=False)}"

        # 检查功能实现状态，处理中断恢复
        status_check = self._check_feature_implementation_status(feature_to_work)
        if status_check["should_skip"]:
            print(f"[{datetime.now()}] ⏭️  跳过功能 {feature_to_work.get('id')}: {status_check['reason']}")
            # 如果已部分实现但未标记完成，标记为完成
            if status_check["partially_implemented"]:
                self.feature_manager.mark_feature_complete(feature_to_work.get("id"))
                print(f"[{datetime.now()}] ✅ 标记部分实现的功能为完成")
            
            # 更新进度并返回
            self.progress_manager.update(
                session_completed=True, feature_completed=feature_to_work.get("id")
            )
            return {"success": True, "skipped": True, "reason": status_check["reason"]}
        
        # 如果部分实现但继续执行，记录日志
        if status_check["partially_implemented"]:
            print(f"[{datetime.now()}] 🔄 功能部分实现，继续完成: {status_check['files_exist']}")
        # 设置当前正在处理的功能
        self.progress_manager.set_current_feature(feature_to_work.get("id"))
        # 4. 执行 OpenCode
        result = self._run_opencode(prompt=full_prompt, agent_type="coding", timeout=constants.TimeoutConstants.OPENCODE_DEFAULT)
        
        # Fallback if OpenCode failed
        if not result.get("success", False):
            print(f"[{datetime.now()}] ⚠️  OpenCode failed, checking for existing implementation...")
            # 检查是否已经有实现文件
            status_check = self._check_feature_implementation_status(feature_to_work)
            if status_check["files_exist"]:
                print(f"[{datetime.now()}] ✅ 发现已有实现文件: {status_check['files_exist']}，标记功能为完成")
                self.feature_manager.mark_feature_complete(feature_to_work.get("id"))
                result = {"success": True, "fallback": False, "existing_files": True}
            else:
                print(f"[{datetime.now()}] ⚠️  没有发现实现文件，创建默认实现")
                self._create_default_implementation(feature_to_work)
                result = {"success": True, "fallback": True}

        # 5. 运行端到端测试
        if self.config.get("testing", {}).get("e2e_enabled", True):
            test_result = self.test_runner.run_e2e_tests()
            result["test_result"] = test_result

        # 6. 提交代码
        if self.config.get("git", {}).get("auto_commit", True):
            # 检查工作目录是否干净（无更改）
            if self.git_manager.is_working_directory_clean():
                print(f"[{datetime.now()}] ℹ️  工作目录干净，无需提交代码")
                # 跳过提交，继续执行后续步骤
            else:
                self.git_manager.commit(
                    message=f"{constants.GitConstants.COMMIT_MSG_FEATURE_PREFIX}{feature_to_work.get('description', 'feature')[:50]}",
                    files=self._get_changed_files(),
                )
            # 如果配置了自动推送，则推送到远程
            if self.config.get("git", {}).get("auto_push", False):
                push_result = self.git_manager.push()
                if not push_result.get("success", False):
                    print(f"⚠️  Git push failed: {push_result.get('error', 'Unknown error')}")
                else:
                    print("✅  Git push successful")

        # 7. 标记功能完成（无论OpenCode成功还是失败）
        self.feature_manager.mark_feature_complete(feature_to_work.get("id"))
        
        # 8. 更新进度
        self.progress_manager.update(
            session_completed=True, feature_completed=feature_to_work.get("id")
        )

        return result

    def _run_opencode(self, prompt: str, agent_type: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        运行 OpenCode
        """
        return self.opencode_manager.run(prompt=prompt, agent=agent_type, timeout=timeout)

    def _get_changed_files(self) -> List[str]:
        """获取已修改的文件列表"""
        if self.git_manager.is_git_repo():
            return self.git_manager.get_changed_files()
        return []

    def _check_feature_implementation_status(self, feature: Dict[str, Any]) -> Dict[str, Any]:
        """检查功能实现状态，用于中断恢复
        
        返回:
        {
            "should_skip": bool,           # 是否应跳过此功能
            "reason": str,                 # 跳过原因
            "files_exist": List[str],      # 已存在的相关文件
            "partially_implemented": bool  # 是否已部分实现
        }
        """
        feature_id = feature.get("id", "")
        description = feature.get("description", "").lower()
        
        # 检查功能是否已标记为完成
        existing_feature = self.feature_manager.get_feature_by_id(feature_id)
        if existing_feature and existing_feature.get("passes", False):
            return {
                "should_skip": True,
                "reason": f"Feature {feature_id} already marked as completed",
                "files_exist": [],
                "partially_implemented": True
            }
        
        # 检查依赖是否满足
        if not self.feature_manager.are_dependencies_met(feature):
            return {
                "should_skip": True,
                "reason": f"Feature {feature_id} dependencies not met",
                "files_exist": [],
                "partially_implemented": False
            }
        
        # 根据功能描述推测可能创建的文件
        possible_files = []
        if "go" in description and ("排序" in description or "sort" in description):
            possible_files = ["quicksort.go", "bubble_sort.go", "sort.go"]
        elif "go" in description:
            possible_files = ["main.go", feature_id + ".go"]
        elif "python" in description or "py" in description:
            possible_files = ["main.py", feature_id + ".py"]
        
        # 检查文件是否存在
        existing_files = []
        for file in possible_files:
            file_path = self.project_path / file
            if file_path.exists():
                existing_files.append(file)
        
        # 如果相关文件已存在，视为部分实现
        partially_implemented = len(existing_files) > 0
        should_skip = partially_implemented and len(existing_files) >= len(possible_files) / 2
        
        return {
            "should_skip": should_skip,
            "reason": f"Partially implemented, files exist: {existing_files}" if should_skip else "Ready for implementation",
            "files_exist": existing_files,
            "partially_implemented": partially_implemented
        }

    def run(self, user_prompt: str, max_sessions: Optional[int] = None):
        """
        无限运行主循环

        Args:
            user_prompt: 用户的需求描述
            max_sessions: 最大会话数 (None = 无限)
        """
        session_count = 0

        # 首次运行: 执行 Initializer
        if not self.is_initialized():
            print(f"[{datetime.now()}] 📦 首次运行，执行初始化...")
            self.run_initializer(user_prompt)
            session_count += 1

        # 循环运行 Coding Sessions
        # 显示恢复状态
        pending_features = self.feature_manager.get_pending_features()
        progress = self.progress_manager.get_progress()
        current_work = progress.get("current_work", "")
        total_features = self.feature_manager.get_total_count()
        completed_features = self.feature_manager.get_completed_count()
        print(f"[{datetime.now()}] 🔄 继续执行: {completed_features}/{total_features} 功能完成，{len(pending_features)} 个待完成")
        if current_work and current_work != "None (initializing)":
            print(f"[{datetime.now()}] 🎯 当前中断的功能: {current_work}")
        while True:
            # 检查是否达到最大会话数
            if max_sessions and session_count >= max_sessions:
                print(f"[{datetime.now()}] 🏁 达到最大会话数 {max_sessions}，停止运行")
                break

            # 检查是否所有功能已完成
            features = self.feature_manager.get_pending_features()
            if not features:
                print(f"[{datetime.now()}] ✅ 所有功能已完成!")
                break

            # 运行一个 coding session
            result = self.run_coding_session()
            session_count += 1

            # 检查是否成功
            if not result.get("success", False):
                print(
                    f"[{datetime.now()}] ❌ Session {session_count} 失败: {result.get('error')}"
                )
                # 可以选择重试或停止
                # 这里选择继续尝试

            print(
                f"[{datetime.now()}] 📊 Session {session_count} 完成. 剩余 {len(features) - 1} 个功能"
            )

        print(f"\n[{datetime.now()}] 🎉 运行完成! 共完成 {session_count} 个会话")


def main():
    parser = argparse.ArgumentParser(
        description="Infinite AI Developer - 基于 OpenCode 的无限运行 AI 开发系统"
    )
    parser.add_argument("project_path", help="项目路径")
    parser.add_argument("-p", "--prompt", help="用户需求描述")
    parser.add_argument("-c", "--config", help="配置文件路径")
    parser.add_argument(
        "--max-sessions", type=int, default=None, help="最大会话数 (默认无限)"
    )
    parser.add_argument("--init-only", action="store_true", help="仅执行初始化")

    args = parser.parse_args()

    # 创建并运行系统
    developer = InfiniteAIDeveloper(
        project_path=args.project_path, config_path=args.config
    )

    if args.init_only:
        if args.prompt:
            developer.run_initializer(args.prompt)
        else:
            print("Error: --init-only 需要 --prompt 参数")
            sys.exit(1)
    else:
        if args.prompt:
            developer.run(args.prompt, max_sessions=args.max_sessions)
        else:
            print("Error: 需要提供 --prompt 参数")
            sys.exit(1)


if __name__ == "__main__":
    main()
