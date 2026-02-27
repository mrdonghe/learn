from . import constants

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


class TestRunner:
    def __init__(self, project_path: Path):
        self.project_path = project_path

    def run_e2e_tests(self) -> Dict[str, Any]:
        playwright_available = self._check_playwright()

        if playwright_available:
            return self._run_playwright_tests()
        else:
            return self._run_basic_tests()

    def _check_playwright(self) -> bool:
        result = subprocess.run(
            ["python", "-c", "import playwright"], capture_output=True
        )
        return result.returncode == 0

    def _run_playwright_tests(self) -> Dict[str, Any]:
        test_script = self.project_path / "e2e_test.py"

        if not test_script.exists():
            return {"success": False, "error": "No e2e_test.py found", "tests_run": 0}

        result = subprocess.run(
            ["python", str(test_script)],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
            timeout=constants.TimeoutConstants.TEST_E2E,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    def _run_basic_tests(self) -> Dict[str, Any]:
        result = subprocess.run(
            ["python", "-m", "pytest", "-v", "--tb=short"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
            timeout=constants.TimeoutConstants.TEST_BASIC,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "tests_run": "unknown",
        }

    def run_unit_tests(self) -> Dict[str, Any]:
        result = subprocess.run(
            ["python", "-m", "pytest", "-v"],
            cwd=str(self.project_path),
            capture_output=True,
            text=True,
            timeout=constants.TimeoutConstants.TEST_UNIT,
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def verify_server_running(self, url: str = "http://localhost:3000") -> bool:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
            capture_output=True,
            text=True,
            timeout=constants.TimeoutConstants.TEST_VERIFY,
        )
        return result.stdout.strip() == "200"
