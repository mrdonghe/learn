#!/usr/bin/env python3
"""
Test fallback behavior when OpenCode fails.
Uses a dummy command that fails quickly to trigger fallback.
"""

import sys
import os
import tempfile
import shutil
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from infinite_agent import InfiniteAIDeveloper


def create_test_config(config_path: str):
    """Create a test config with dummy OpenCode command that fails fast."""
    config = {
        "opencode": {
            "mode": "cli",
            "command": "/bin/false",  # This command always fails
            "timeout": 2,  # Short timeout
            "model": "deepseek/deepseek-reasoner",
        },
        "feature_generation": {
            "min_features": 2,
            "max_features": 5,
            "max_retries": 0,  # No retries, fail fast
            "retry_timeout": 1,
            "default_features": [
                {
                    "id": "test_feature_001",
                    "category": "functional",
                    "description": "Test feature 1",
                    "priority": "high",
                    "steps": ["Step 1", "Step 2"],
                    "passes": False,
                    "dependencies": [],
                },
                {
                    "id": "test_feature_002",
                    "category": "testing",
                    "description": "Test feature 2",
                    "priority": "medium",
                    "steps": ["Step 1", "Step 2"],
                    "passes": False,
                    "dependencies": ["test_feature_001"],
                },
            ],
        },
        "git": {
            "auto_commit": False,  # Disable git for test
        },
        "testing": {
            "e2e_enabled": False,
        },
    }
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    return config_path


def test_fallback():
    """Test that fallback works when OpenCode fails."""
    test_dir = tempfile.mkdtemp(prefix="test_fallback_")
    config_path = os.path.join(test_dir, "test_config.yaml")
    create_test_config(config_path)

    print(f"Test directory: {test_dir}")
    print(f"Config path: {config_path}")

    try:
        # Create developer with custom config
        developer = InfiniteAIDeveloper(project_path=test_dir, config_path=config_path)

        # Run initializer with simple prompt
        print("Running initializer...")
        result = developer.run_initializer("用go语言实现快速排序")

        print(f"Initializer result: {result}")

        # Check that fallback was triggered
        if result.get("fallback"):
            print("✅ Fallback triggered as expected")
        else:
            print(
                "⚠️  Fallback not triggered, but OpenCode may have succeeded unexpectedly"
            )

        # Check required files were created
        required = ["feature_list.json", "claude-progress.txt", "init.sh"]
        all_exist = True
        for req in required:
            path = os.path.join(test_dir, req)
            exists = os.path.exists(path)
            print(f"{req}: {'✓' if exists else '✗'}")
            if not exists:
                all_exist = False
            elif req == "feature_list.json":
                # Verify it contains our test features
                import json

                with open(path, "r") as f:
                    features = json.load(f)
                    print(f"  Features loaded: {len(features)}")
                    for feat in features:
                        print(f"    - {feat.get('id')}: {feat.get('description')}")

        if all_exist:
            print("✅ All required files created")
        else:
            print("❌ Some files missing")

        return all_exist and result.get("success", False)

    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"Cleaned up test directory: {test_dir}")


if __name__ == "__main__":
    success = test_fallback()
    sys.exit(0 if success else 1)
