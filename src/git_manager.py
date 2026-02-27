import subprocess
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from . import constants



class GitManager:
    def __init__(self, project_path: Path):
        self.project_path = project_path

    def is_git_repo(self) -> bool:
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    def init(self):
        # Set default user if not configured
        try:
            subprocess.run(
                ["git", "config", "user.email"],
                cwd=str(self.project_path),
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError:
            subprocess.run(
                ["git", "config", "user.email", constants.GitConstants.GIT_USER_EMAIL],
                cwd=str(self.project_path),
                check=False
            )
        try:
            subprocess.run(
                ["git", "config", "user.name"],
                cwd=str(self.project_path),
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError:
            subprocess.run(
                ["git", "config", "user.name", constants.GitConstants.GIT_USER_NAME],
                cwd=str(self.project_path),
                check=False
            )
        subprocess.run(["git", "init"], cwd=str(self.project_path), check=True)
    def get_changed_files(self) -> List[str]:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []
        files = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            # Parse git status line
            # git status --porcelain format:
            #   XY filename
            #   XY "filename with spaces"
            # Where X and Y are status codes, space after 2 chars
            # Examples:
            #   " M filename"  - modified (space before M means not staged)
            #   "M  filename"  - staged for commit
            #   "?? filename"  - untracked
            #   "A  filename"  - added
            #   "D  filename"  - deleted
            #   "R  old -> new" - renamed
            
            # Filter: only include unstaged changes (first char space) or untracked ("??")
            status = line[:2]
            if status[0] != ' ' and status[0] != '?':
                # Staged change, skip
                continue
            # For simple cases, take everything after first 3 characters
            if len(line) >= 4:
                filepath = line[3:].strip()
                # Handle quoted filenames
                if filepath.startswith('"'):
                    # Find closing quote
                    end_quote = filepath.find('"', 1)
                    if end_quote != -1:
                        filepath = filepath[1:end_quote]
                # Handle rename format: "old -> new"
                if ' -> ' in filepath:
                    # For renamed files, git status shows both names
                    # We should only add the new name
                    parts = filepath.split(' -> ')
                    if len(parts) == 2:
                        filepath = parts[1].strip('"')
                if filepath:
                    files.append(filepath)
        return files
    def get_staged_files(self) -> List[str]:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.strip().split("\n") if f]

    def is_working_directory_clean(self) -> bool:
        """Check if working directory is clean (no staged or unstaged changes)"""
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
        )
        # Empty output means clean working directory
        return result.stdout.strip() == ""

    def add(self, files: List[str]):
        if not files:
            return
        subprocess.run(["git", "add"] + files, cwd=str(self.project_path), check=True)

    def commit(self, message: str, files: Optional[List[str]] = None):
        if not self.is_git_repo():
            self.init()
            subprocess.run(["git", "add", "-A"], cwd=str(self.project_path), check=True)
        elif files is not None:
            self.add(files)
        # Set git environment variables to avoid author errors
        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = constants.GitConstants.GIT_USER_NAME
        env["GIT_AUTHOR_EMAIL"] = constants.GitConstants.GIT_USER_EMAIL
        env["GIT_COMMITTER_NAME"] = env["GIT_AUTHOR_NAME"]
        env["GIT_COMMITTER_EMAIL"] = env["GIT_AUTHOR_EMAIL"]
        
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                check=True,
                env=env
            )
        except subprocess.CalledProcessError as e:
            # Check if error is "nothing to commit"
            if e.stderr and ("nothing to commit" in e.stderr.lower() or "nothing added to commit" in e.stderr.lower()):
                print(f"ℹ️  No changes to commit (working directory clean)")
                return
            # Log but don't crash - allow system to continue
            print(f"⚠️  Git commit failed: {e}")
            if e.stderr:
                print(f"   Stderr: {e.stderr[:200]}")
            # Try to set config and retry once
            try:
                subprocess.run(
                    ["git", "config", "user.email", constants.GitConstants.GIT_USER_EMAIL],
                    cwd=str(self.project_path),
                    check=False
                )
                subprocess.run(
                    ["git", "config", "user.name", constants.GitConstants.GIT_USER_NAME],
                    cwd=str(self.project_path),
                    check=False
                )
                # Retry commit
                retry_result = subprocess.run(
                    ["git", "commit", "-m", message],
                    cwd=str(self.project_path),
                    capture_output=True,
                    text=True,
                    check=False,
                    env=env
                )
                if retry_result.returncode == 0:
                    print("✅  Git commit successful after setting config")
                else:
                    # Check if retry also failed with "nothing to commit"
                    if retry_result.stderr and ("nothing to commit" in retry_result.stderr.lower() or "nothing added to commit" in retry_result.stderr.lower()):
                        print(f"ℹ️  No changes to commit (working directory clean)")
                    else:
                        print(f"⚠️  Git commit still failed after setting config")
                        if retry_result.stderr:
                            print(f"   Stderr: {retry_result.stderr[:200]}")
            except Exception:
                pass

    def push(self, remote: str = "origin", branch: Optional[str] = None) -> Dict[str, Any]:
        """Push commits to remote repository

        参数:
            remote: 远程仓库名称 (默认: "origin")
            branch: 分支名称 (默认: 当前分支)

        返回:
            {"success": bool, "stdout": str, "stderr": str, "error": Optional[str]}
        """
        if not self.is_git_repo():
            return {"success": False, "error": "Not a git repository", "stdout": "", "stderr": ""}

        # 获取当前分支
        current_branch = self.get_current_branch()
        target_branch = branch or current_branch

        # 检查是否有远程仓库
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", remote],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=constants.TimeoutConstants.SYSTEM_TIMEOUT_SHORT
            )
            if result.returncode != 0:
                return {"success": False, "error": f"Remote '{remote}' not configured", "stdout": result.stdout, "stderr": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout checking remote", "stdout": "", "stderr": ""}

        # 执行push
        try:
            push_result = subprocess.run(
                ["git", "push", remote, target_branch],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=constants.TimeoutConstants.SYSTEM_TIMEOUT_LONG
            )

            return {
                "success": push_result.returncode == 0,
                "stdout": push_result.stdout,
                "stderr": push_result.stderr,
                "error": None if push_result.returncode == 0 else f"Push failed with code {push_result.returncode}"
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Push timeout", "stdout": "", "stderr": ""}
        except Exception as e:
            return {"success": False, "error": str(e), "stdout": "", "stderr": ""}


    def get_recent_commits(self, count: int = 10) -> List[str]:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--oneline"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return []
        return result.stdout.strip().split("\n")

    def get_current_branch(self) -> str:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return "main"
        return result.stdout.strip() or "main"

    def revert_to_commit(self, commit_hash: str):
        subprocess.run(
            ["git", "revert", "--no-commit", commit_hash],
            cwd=str(self.project_path),
            check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"revert: revert to {commit_hash}"],
            cwd=str(self.project_path),
            check=True,
        )

    def checkout_files(self, files: List[str]):
        subprocess.run(
            ["git", "checkout", "--"] + files, cwd=str(self.project_path), check=True
        )

    def get_file_history(self, filepath: str) -> List[Dict[str, Any]]:
        """获取文件的git提交历史

        参数:
            filepath: 文件路径

        返回:
            List[Dict[str, Any]]: 提交历史列表，包含提交哈希、作者、日期、消息
        """
        if not self.is_git_repo():
            return []

        try:
            # 使用git log获取文件的详细历史
            result = subprocess.run(
                [
                    "git", "log", "--all", "--follow",
                    "--pretty=format:%H|%an|%ad|%s",
                    "--date=iso",
                    "--", filepath
                ],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=constants.TimeoutConstants.SYSTEM_TIMEOUT_MEDIUM
            )
            if result.returncode != 0:
                return []

            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 3)
                if len(parts) >= 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3],
                    })
            return commits

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return []

    def restore_progress_from_git(self) -> Dict[str, Any]:
        """从git历史恢复进度信息

        分析git提交历史，重建进度状态，包括:
        - 最新的进度文件内容 (claude-progress.txt)
        - 最新的功能列表 (feature_list.json)
        - 已完成的功能列表
        - 项目启动时间

        返回:
            Dict[str, Any]: 恢复的进度信息
        """
        if not self.is_git_repo():
            return {"success": False, "error": "Not a git repository"}

        try:
            # 1. 获取进度文件历史
            progress_history = self.get_file_history("claude-progress.txt")
            feature_history = self.get_file_history("feature_list.json")

            # 2. 如果找不到文件历史，返回空进度
            if not progress_history and not feature_history:
                return {"success": True, "progress": None, "features": None, "message": "No history found"}

            # 3. 获取最新的进度文件内容
            latest_progress = None
            if progress_history:
                latest_progress = self._get_file_content_at_commit(
                    "claude-progress.txt", progress_history[0]["hash"]
                )

            # 4. 获取最新的功能列表内容
            latest_features = None
            if feature_history:
                latest_features = self._get_file_content_at_commit(
                    "feature_list.json", feature_history[0]["hash"]
                )

            # 5. 分析提交消息，提取功能完成历史
            feature_completion_history = self._analyze_feature_completions()

            return {
                "success": True,
                "progress_content": latest_progress,
                "features_content": latest_features,
                "progress_history": progress_history,
                "feature_history": feature_history,
                "feature_completions": feature_completion_history,
                "message": "Progress restored from git history"
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_file_content_at_commit(self, filepath: str, commit_hash: str) -> Optional[str]:
        """获取特定提交中的文件内容"""
        try:
            result = subprocess.run(
                ["git", "show", f"{commit_hash}:{filepath}"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=constants.TimeoutConstants.SYSTEM_TIMEOUT_SHORT
            )
            if result.returncode == 0:
                return result.stdout
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
        return None

    def _analyze_feature_completions(self) -> List[Dict[str, Any]]:
        """分析提交消息，提取功能完成历史

        从提交消息中识别:
        - feat: implement ... 提交 (功能实现)
        - chore: update progress files 提交 (进度更新)

        返回:
            List[Dict[str, Any]]: 功能完成历史
        """
        try:
            # 获取所有提交
            result = subprocess.run(
                ["git", "log", "--all", "--pretty=format:%H|%s", "--date=iso"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=constants.TimeoutConstants.SYSTEM_TIMEOUT_MEDIUM
            )
            if result.returncode != 0:
                return []

            completions = []
            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue
                parts = line.split("|", 1)
                if len(parts) >= 2:
                    commit_hash = parts[0]
                    message = parts[1]

                    # 分析提交消息类型
                    if message.startswith(constants.GitConstants.COMMIT_MSG_FEATURE_PREFIX):
                        # 功能实现提交
                        feature_desc = message[len(constants.GitConstants.COMMIT_MSG_FEATURE_PREFIX):].strip()
                        completions.append({
                            "type": "feature_implementation",
                            "commit": commit_hash,
                            "message": message,
                            "feature_description": feature_desc[:100],  # 限制长度
                            "timestamp": None  # 需要从其他命令获取
                        })
                    elif message == "chore: update progress files":
                        # 进度更新提交
                        completions.append({
                            "type": "progress_update",
                            "commit": commit_hash,
                            "message": message,
                            "timestamp": None
                        })
                    elif message == constants.GitConstants.COMMIT_MSG_INITIAL:
                        # 初始化提交
                        completions.append({
                            "type": "initialization",
                            "commit": commit_hash,
                            "message": message,
                            "timestamp": None
                        })

            return completions

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return []

    def get_feature_completion_summary(self) -> Dict[str, Any]:
        """获取功能完成摘要

        返回已完成功能的数量统计和最近活动
        """
        completions = self._analyze_feature_completions()

        # 统计
        feature_impl_count = sum(1 for c in completions if c["type"] == "feature_implementation")
        progress_update_count = sum(1 for c in completions if c["type"] == "progress_update")
        initialization_count = sum(1 for c in completions if c["type"] == "initialization")

        # 最近的功能实现
        recent_features = [
            c for c in completions
            if c["type"] == "feature_implementation"
        ][:5]  # 最近5个

        return {
            "total_commits": len(completions),
            "feature_implementations": feature_impl_count,
            "progress_updates": progress_update_count,
            "initializations": initialization_count,
            "recent_features": recent_features,
            "message": f"Found {feature_impl_count} feature implementations in git history"
        }
