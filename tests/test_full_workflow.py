#!/usr/bin/env python3
import sys
import os
import tempfile
import shutil
import signal
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from infinite_agent import InfiniteAIDeveloper


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("Test timeout")


def test_workflow():
    # Use existing directory or create new
    test_dir = "/tmp/test_git_fix_fc3143h_"
    if not os.path.exists(test_dir):
        print("Creating new test directory")
        test_dir = tempfile.mkdtemp(prefix="test_full_")
        dev = InfiniteAIDeveloper(test_dir)
        print("Running initializer...")
        init_result = dev.run_initializer("用go语言实现快速排序")
        print(f"Initializer result: {init_result.get('success')}")
    else:
        print(f"Using existing directory: {test_dir}")
        dev = InfiniteAIDeveloper(test_dir)

    print(f"Project initialized: {dev.is_initialized()}")
    print(f"Pending features: {len(dev.feature_manager.get_pending_features())}")

    # Set timeout for coding session (8 minutes)
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(480)

    try:
        print("\n" + "=" * 60)
        print("Starting coding session...")
        print("=" * 60)

        result = dev.run_coding_session()
        print(f"\nCoding session result keys: {list(result.keys())}")
        print(f"Success: {result.get('success')}")
        print(f"Fallback: {result.get('fallback', False)}")

        # Check if any files were created
        import subprocess

        changed = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=test_dir,
            capture_output=True,
            text=True,
        )
        print(f"\nGit status:\n{changed.stdout if changed.stdout else 'No changes'}")

        # Check git log
        log = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=test_dir,
            capture_output=True,
            text=True,
        )
        print(f"\nGit log (last 5):\n{log.stdout if log.stdout else 'No commits'}")

        # Check if feature passes updated
        features = dev.feature_manager.load_features()
        print(f"\nFeatures status:")
        for f in features:
            print(
                f"  {f['id']}: passes={f.get('passes')}, desc={f.get('description', '')[:40]}"
            )

        # List created files
        print(f"\nFiles in project:")
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.startswith(".") and file != ".gitignore":
                    continue
                path = os.path.join(root, file)
                rel = os.path.relpath(path, test_dir)
                print(f"  {rel}")

        return True
    except TimeoutException:
        print("\n❌ Coding session timed out after 8 minutes")
        return False
    except Exception as e:
        print(f"\n❌ Error during coding session: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        signal.alarm(0)
        # Keep directory for inspection
        print(f"\nTest directory kept at {test_dir}")


if __name__ == "__main__":
    success = test_workflow()
    sys.exit(0 if success else 1)
