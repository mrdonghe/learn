#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from infinite_agent import InfiniteAIDeveloper


def test_init():
    test_dir = "/tmp/test_system_init"
    os.makedirs(test_dir, exist_ok=True)

    developer = InfiniteAIDeveloper(project_path=test_dir)

    print(f"Project path: {test_dir}")
    print(f"Is initialized? {developer.is_initialized()}")

    # Run initializer with simple prompt
    result = developer.run_initializer("用go语言实现快速排序")

    print(f"Initializer result: {result}")

    # Check files
    required = ["feature_list.json", "claude-progress.txt", "init.sh"]
    for req in required:
        path = os.path.join(test_dir, req)
        exists = os.path.exists(path)
        print(f"{req}: {'✓' if exists else '✗'}")
        if exists:
            try:
                with open(path, "r") as f:
                    content = f.read()
                    print(f"  Content preview: {content[:200]}")
            except Exception as e:
                print(f"  Error reading: {e}")

    # Cleanup
    import shutil

    shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    test_init()
