#!/usr/bin/env python3
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from infinite_agent import InfiniteAIDeveloper


def test():
    test_dir = tempfile.mkdtemp(prefix="test_git_fix_")
    print(f"Test directory: {test_dir}")

    try:
        dev = InfiniteAIDeveloper(test_dir)
        result = dev.run_initializer("用go语言实现快速排序")
        print(f"Result: {result}")

        # Check git log
        import subprocess

        log = subprocess.run(
            ["git", "log", "--oneline"], cwd=test_dir, capture_output=True, text=True
        )
        print(f"Git log exit code: {log.returncode}")
        if log.stdout:
            print(f"Git log:\n{log.stdout}")

        return True
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Keep directory for inspection
        print(f"Test directory kept at {test_dir}")
        # shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)
