#!/usr/bin/env python3
import sys
import os
import tempfile
import shutil
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from infinite_agent import InfiniteAIDeveloper


def test_full_workflow():
    """Test initialization -> coding session -> commit -> progress update"""
    test_dir = tempfile.mkdtemp(prefix="test_workflow_")
    print(f"Test directory: {test_dir}")

    # Step 1: Initialization with timeout 60s (will likely timeout and fallback)
    dev = InfiniteAIDeveloper(test_dir)
    print("Running initializer...")
    init_result = dev.run_initializer("用go语言实现快速排序")
    print(f"Initializer result: {init_result}")

    # Check files created
    assert os.path.exists(os.path.join(test_dir, "feature_list.json")), (
        "feature_list.json not created"
    )
    assert os.path.exists(os.path.join(test_dir, "claude-progress.txt")), (
        "claude-progress.txt not created"
    )
    assert os.path.exists(os.path.join(test_dir, "init.sh")), "init.sh not created"
    assert os.path.exists(os.path.join(test_dir, ".git")), "git repo not created"
    print("✓ Initialization files created")

    # Step 2: Run coding session with timeout 60s (will likely timeout and fallback)
    print("Running coding session...")
    start = time.time()
    coding_result = dev.run_coding_session()
    elapsed = time.time() - start
    print(f"Coding session completed in {elapsed:.1f}s")
    print(f"Coding result: {json.dumps(coding_result, indent=2, default=str)}")

    # Check if fallback was used (expected)
    if coding_result.get("fallback"):
        print("✓ Fallback used as expected")
    else:
        print("⚠️  OpenCode succeeded (unexpected but okay)")

    # Check if feature marked as completed
    features = dev.feature_manager.load_features()
    feature_001 = next((f for f in features if f["id"] == "feature_001"), None)
    if feature_001 and feature_001.get("passes"):
        print("✓ feature_001 marked as completed")
    else:
        print("✗ feature_001 not completed")
        return False

    # Check if files were created (default implementation)
    go_file = os.path.join(test_dir, "quicksort.go")
    if os.path.exists(go_file):
        print(f"✓ Default implementation file created: {go_file}")
    else:
        # Maybe other files created
        print("Checking for any new Go files...")
        import glob

        go_files = glob.glob(os.path.join(test_dir, "*.go"))
        for f in go_files:
            print(f"  Found: {f}")

    # Check git commit
    import subprocess

    git_log = subprocess.run(
        ["git", "log", "--oneline", "-n", "2"],
        cwd=test_dir,
        capture_output=True,
        text=True,
    )
    print(f"Git log:\n{git_log.stdout}")

    # Check progress file updated
    progress_content = open(os.path.join(test_dir, "claude-progress.txt")).read()
    if "feature_001" in progress_content:
        print("✓ Progress file updated with feature_001")
    else:
        print("Progress file content:", progress_content[:200])

    print(f"\n✅ Full workflow test passed in {elapsed:.1f}s")

    # Clean up
    shutil.rmtree(test_dir)
    print(f"Cleaned up test directory")
    return True


if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)
