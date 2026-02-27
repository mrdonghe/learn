from . import constants

from datetime import datetime
import subprocess
import json
import time
import os
import requests
from pathlib import Path
from typing import Dict, Any, Optional


class OpenCodeManager:
    """
    OpenCode 集成管理器
    支持 CLI 和 Server API 两种模式
    """

    def __init__(self, project_path: Path, config: Dict[str, Any]):
        self.project_path = project_path
        self.config = config.get("opencode", {})
        self.mode = self.config.get("mode", "cli")
        self.server_process: Optional[subprocess.Popen] = None

    def run(self, prompt: str, agent: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """运行 OpenCode"""
        if self.mode == "server":
            return self._run_via_server(prompt, agent, timeout)
        else:
            print(f"======================================== _run_via_cli")
            return self._run_via_cli(prompt, agent, timeout)

    def _run_via_cli(self, prompt: str, agent: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """通过 CLI 运行"""
        cmd = self.config.get("command", "opencode")
        config_timeout = self.config.get("timeout", constants.TimeoutConstants.OPENCODE_DEFAULT)
        actual_timeout = timeout if timeout is not None else config_timeout
        model = self.config.get("model", None)

        args = [
            cmd, "run",
            # "--dir", str(self.project_path),
        ]

        # Note: OpenCode may not support custom agent names
        # We use different prompts instead of different agents
        # if agent:
        #     args.extend(["--agent", agent])

        if model:
            args.extend(["--model", model])

        # Prompt as positional argument (not --prompt)
        # args.append(prompt)
        
        # prompt = "你好"
        args.append(prompt)
        # args.extend(["--prompt", prompt])

        print(f"[{datetime.now()}] [OpenCode CLI] 开始执行: {cmd} run ... [{agent or 'default'}] 超时: {actual_timeout}秒")

        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        env["TERM"] = "dumb"
        # Ensure UTF-8 locale for Chinese characters
        env["LANG"] = "en_US.UTF-8"
        env["LC_ALL"] = "en_US.UTF-8"

        print(f"======================================== args {args}")

        try:
            # 使用 Popen 以便实时读取输出
            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(self.project_path),
                env=env,
            )

            stdout_lines = []
            stderr_lines = []

            # 实时读取输出
            print(f"[{datetime.now()}] [OpenCode CLI] 开始执行，超时: {actual_timeout}秒")
            print("=" * 50)

            try:
                # 使用线程或异步读取 stdout 和 stderr
                # 简单方法：使用 communicate 但设置超时
                start_time = time.time()
                while True:
                    # 检查超时
                    if time.time() - start_time > actual_timeout:
                        process.kill()
                        raise subprocess.TimeoutExpired(cmd, actual_timeout)

                    # 检查进程是否结束
                    returncode = process.poll()
                    if returncode is not None:
                        break

                    # 尝试读取一些输出
                    try:
                        # 非阻塞读取
                        import select
                        import fcntl

                        # 设置非阻塞读取
                        def set_nonblocking(fd):
                            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
                            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

                        set_nonblocking(process.stdout.fileno())
                        set_nonblocking(process.stderr.fileno())

                        # 检查是否有数据可读
                        readable, _, _ = select.select([process.stdout, process.stderr], [], [], 0.1)
                        for stream in readable:
                            if stream == process.stdout:
                                line = process.stdout.readline()
                                if line:
                                    print(f"[OpenCode {datetime.now()}] {line.rstrip()}")
                                    stdout_lines.append(line)
                            elif stream == process.stderr:
                                line = process.stderr.readline()
                                if line:
                                    print(f"[OpenCode {datetime.now()}] {line.rstrip()}")
                                    stderr_lines.append(line)
                    except (IOError, OSError):
                        # 非阻塞读取可能失败，继续
                        time.sleep(0.1)

                # 进程已结束，读取剩余输出
                remaining_stdout, remaining_stderr = process.communicate(timeout=constants.TimeoutConstants.OPENCODE_COMMUNICATE)
                if remaining_stdout:
                    for line in remaining_stdout.split('\n'):
                        if line.strip():
                            print(f"[OpenCode {datetime.now()}] {line}")
                            stdout_lines.append(line + '\n')
                if remaining_stderr:
                    for line in remaining_stderr.split('\n'):
                        if line.strip():
                            print(f"[OpenCode {datetime.now()}] {line}")
                            stderr_lines.append(line + '\n')

                stdout = ''.join(stdout_lines)
                stderr = ''.join(stderr_lines)
                returncode = process.returncode

            except subprocess.TimeoutExpired as e:
                process.kill()
                stdout, stderr = process.communicate()
                print(f"[{datetime.now()}] [OpenCode CLI] 超时: {e}")
                return {"success": False, "error": "Timeout", "timeout": actual_timeout, "stdout": stdout, "stderr": stderr}

            print("=" * 50)
            print(f"[{datetime.now()}] [OpenCode CLI] 执行完成，返回码: {returncode}")

            output = stdout + stderr

            return {
                "success": returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "returncode": returncode,
                "output": output,
            }

        except subprocess.TimeoutExpired as e:
            print(f"[{datetime.now()}] [OpenCode CLI] TimeoutExpired: {e}")
            return {"success": False, "error": "Timeout", "timeout": actual_timeout}
        except Exception as e:
            print(f"[{datetime.now()}] [OpenCode CLI] Exception: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def _run_via_server(self, prompt: str, agent: Optional[str] = None, timeout: Optional[int] = None) -> Dict[str, Any]:
        """通过 Server API 运行"""
        server_url = self.config.get("server_url", "http://localhost:4096")
        password = self.config.get("server_password", "")
        config_timeout = self.config.get("timeout", constants.TimeoutConstants.OPENCODE_DEFAULT)
        actual_timeout = timeout if timeout is not None else config_timeout

        headers = {"Content-Type": "application/json"}
        if password:
            headers["Authorization"] = f"Bearer {password}"

        try:
            # 创建 session
            session_resp = requests.post(
                f"{server_url}/session",
                headers=headers,
                json={"title": f"Infinite AI Developer Session"},
                timeout=constants.TimeoutConstants.OPENCODE_API_SESSION
            )
            session_resp.raise_for_status()
            session_id = session_resp.json()["id"]

            # 发送消息
            message_resp = requests.post(
                f"{server_url}/session/{session_id}/message",
                headers=headers,
                json={
                    "parts": [{"type": "text", "text": prompt}]
                },
                timeout=actual_timeout
            )
            message_resp.raise_for_status()

            result = message_resp.json()

            return {
                "success": True,
                "session_id": session_id,
                "message": result,
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def _parse_json_output(self, stdout: str) -> Dict[str, Any]:
        """解析 JSON 输出"""
        try:
            for line in stdout.strip().split("\n"):
                if line.strip():
                    data = json.loads(line)
                    if data.get("type") == "finish":
                        return {
                            "finished": True,
                            "message": data.get("message", ""),
                            "data": data,
                        }
            return {"finished": False, "raw": stdout[:500]}
        except json.JSONDecodeError:
            return {"finished": False, "raw": stdout[:500]}

    def start_server(self) -> bool:
        """启动 OpenCode Server"""
        if self.mode != "server":
            return True

        cmd = [
            self.config.get("command", "opencode"),
            "serve",
            "--port", str(self.config.get("server_url", "4096").split(":")[-1]),
        ]

        print(f"[OpenCode {datetime.now()}] Starting server: {' '.join(cmd)}")

        try:
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.project_path),
            )
            time.sleep(3)
            return True
        except Exception as e:
            print(f"[OpenCode {datetime.now()}] Failed to start server: {e}")
            return False

    def stop_server(self):
        """停止 OpenCode Server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
