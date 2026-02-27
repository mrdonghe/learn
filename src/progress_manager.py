import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class ProgressManager:
    PROGRESS_FILE = "claude-progress.txt"

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.progress_file = project_path / self.PROGRESS_FILE

    def get_progress(self) -> Dict[str, Any]:
        if not self.progress_file.exists():
            return self._default_progress()

        content = self.progress_file.read_text(encoding="utf-8")
        return self._parse_progress(content)

    def _default_progress(self) -> Dict[str, Any]:
        return {
            "started": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "sessions_completed": 0,
            "features_completed": 0,
            "features_total": 0,
            "current_work": "None (initializing)",
            "history": [],
        }

    def _parse_progress(self, content: str) -> Dict[str, Any]:
        progress = self._default_progress()
        lines = content.split("\n")

        for i, line in enumerate(lines):
            if "Started:" in line:
                progress["started"] = line.split("Started:")[1].strip()
            elif "Last Updated:" in line:
                progress["last_updated"] = line.split("Last Updated:")[1].strip()
            elif "Sessions Completed:" in line:
                count = line.split("Sessions Completed:")[1].strip()
                progress["sessions_completed"] = (
                    int(count.split("/")[0]) if "/" in count else int(count)
                )
            elif "Features Completed:" in line:
                count = line.split("Features Completed:")[1].strip()
                if "/" in count:
                    parts = count.split("/")
                    progress["features_completed"] = int(parts[0])
                    progress["features_total"] = int(parts[1])
                else:
                    progress["features_completed"] = int(count)
            elif "Current Feature:" in line:
                progress["current_work"] = line.split("Current Feature:")[1].strip()

        return progress

    def update(
        self, session_completed: bool = False, feature_completed: Optional[str] = None
    ):
        progress = self.get_progress()

        if session_completed:
            progress["sessions_completed"] += 1

        if feature_completed:
            progress["features_completed"] += 1
            progress["current_work"] = feature_completed

        progress["last_updated"] = datetime.now().isoformat()

        self._save_progress(progress)
    def set_current_feature(self, feature_id: str):
        """设置当前正在处理的功能，但不标记为完成"""
        progress = self.get_progress()
        progress["current_work"] = feature_id
        progress["last_updated"] = datetime.now().isoformat()
        self._save_progress(progress)

    def _save_progress(self, progress: Dict[str, Any]):
        content = f"""# Project Progress

## Status
- Started: {progress["started"]}
- Last Updated: {progress["last_updated"]}
- Sessions Completed: {progress["sessions_completed"]}
- Features Completed: {progress["features_completed"]} / {progress["features_total"]}

## Current Work
- Current Feature: {progress["current_work"]}

## History
{chr(10).join(progress.get("history", []))}
"""
        self.progress_file.write_text(content, encoding="utf-8")

    def add_history_entry(self, entry: str):
        progress = self.get_progress()
        history = progress.get("history", [])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        history.append(f"- [{timestamp}] {entry}")
        progress["history"] = history
        self._save_progress(progress)

    def restore_from_git_history(self, git_manager) -> Dict[str, Any]:
        """从git历史恢复进度

        根据Anthropic文章描述，使用git历史重建进度状态

        参数:
            git_manager: GitManager实例

        返回:
            Dict[str, Any]: 恢复结果，包含进度状态和消息
        """
        try:
            # 1. 从git历史获取进度信息
            git_restore_result = git_manager.restore_progress_from_git()
            if not git_restore_result.get("success", False):
                return {"success": False, "error": git_restore_result.get("error", "Unknown git error")}

            # 2. 如果git中没有进度历史，返回默认进度
            if git_restore_result.get("progress_content") is None:
                return {"success": True, "progress": self._default_progress(), "message": "No progress history in git"}

            # 3. 解析从git获取的进度内容
            progress_content = git_restore_result["progress_content"]
            restored_progress = self._parse_progress(progress_content)

            # 4. 获取功能列表内容（如果存在）
            features_content = git_restore_result.get("features_content")
            features_restored = False
            if features_content:
                # 将功能列表写回磁盘
                features_path = self.project_path / "feature_list.json"
                features_path.write_text(features_content, encoding="utf-8")
                features_restored = True

            # 5. 获取功能完成摘要
            completion_summary = git_manager.get_feature_completion_summary()

            # 6. 验证恢复的进度是否合理
            if self._validate_restored_progress(restored_progress):
                # 保存恢复的进度
                self._save_progress(restored_progress)
                
                return {
                    "success": True,
                    "progress": restored_progress,
                    "features_restored": features_restored,
                    "completion_summary": completion_summary,
                    "message": f"Progress restored from git history: {restored_progress.get('features_completed', 0)} features completed"
                }
            else:
                return {"success": False, "error": "Restored progress failed validation"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _validate_restored_progress(self, progress: Dict[str, Any]) -> bool:
        """验证恢复的进度数据是否合理"""
        # 基本验证
        if not isinstance(progress, dict):
            return False

        # 检查必要字段
        required_fields = ["started", "last_updated", "sessions_completed", "features_completed"]
        for field in required_fields:
            if field not in progress:
                return False

        # 验证数据类型
        try:
            sessions = int(progress.get("sessions_completed", 0))
            features = int(progress.get("features_completed", 0))
            if sessions < 0 or features < 0:
                return False
        except (ValueError, TypeError):
            return False

        return True

    def get_recovery_context(self, git_manager) -> str:
        """生成恢复上下文摘要，用于添加到OpenCode提示词

        根据Anthropic文章描述，每个会话开始时应该：
        1. 运行pwd
        2. 读取git日志和进度文件
        3. 了解最近的工作

        返回:
            str: 格式化的恢复上下文
        """
        if not self.progress_file.exists():
            return "# Recovery Context\n\nNo progress file found. Starting fresh.\n"

        # 获取当前进度
        progress = self.get_progress()
        
        # 获取git历史摘要
        git_summary = ""
        try:
            if git_manager.is_git_repo():
                completion_summary = git_manager.get_feature_completion_summary()
                git_summary = (
                    f"\n## Git History Summary\n"
                    f"- Total commits analyzed: {completion_summary.get('total_commits', 0)}"
                    f"\n- Feature implementations found: {completion_summary.get('feature_implementations', 0)}"
                    f"\n- Recent features:"
                )
                for feature in completion_summary.get("recent_features", [])[:3]:
                    git_summary += f"\n  - {feature.get('feature_description', 'Unknown')}"
        except Exception:
            git_summary = "\n## Git History\nUnable to read git history"

        # 构建恢复上下文
        context = f"""# Recovery Context

## Project Status
- Started: {progress.get('started', 'Unknown')}
- Last Updated: {progress.get('last_updated', 'Unknown')}
- Sessions Completed: {progress.get('sessions_completed', 0)}
- Features Completed: {progress.get('features_completed', 0)} / {progress.get('features_total', 0)}
- Current Work: {progress.get('current_work', 'None')}

{git_summary}

## Next Steps
1. Run pwd to confirm working directory
2. Read git log --oneline -20 to see recent work
3. Check claude-progress.txt for detailed progress
4. Review feature_list.json for pending features
"""
        
        return context
