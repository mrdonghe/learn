#!/usr/bin/env python3
"""
Verify all module imports work after test reorganization.
"""

import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

modules_to_import = [
    # src modules
    ("feature_manager", "FeatureManager"),
    ("progress_manager", "ProgressManager"),
    ("git_manager", "GitManager"),
    ("test_runner", "TestRunner"),
    ("session_manager", "SessionManager"),
    ("opencode_manager", "OpenCodeManager"),
    # main agent
    ("infinite_agent", "InfiniteAIDeveloper"),
]


def test_imports():
    errors = []
    for module_name, class_name in modules_to_import:
        try:
            module = __import__(module_name, fromlist=[class_name])
            print(f"✅ {module_name} imported successfully")
            if class_name:
                cls = getattr(module, class_name)
                print(f"   → {class_name} accessible")
        except Exception as e:
            errors.append((module_name, class_name, e))
            print(f"❌ {module_name} import failed: {e}")
            traceback.print_exc()

    # Also test that test files can import infinite_agent
    print("\nTesting test file imports...")
    test_files = [
        "test_coding_session.py",
        "test_complete.py",
        "test_concise_prompt.py",
        "test_fallback.py",
        "test_full_workflow.py",
        "test_git_fix.py",
        "test_init_debug.py",
        "test_opencode_simple.py",
        "test_simple_prompt.py",
        "test_system.py",
        "test_timeout.py",
        "test_v2_prompt.py",
        "test_workflow.py",
    ]
    for test_file in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if not os.path.exists(test_path):
            print(f"⚠️  {test_file} not found")
            continue
        try:
            # Simple check: can we compile the file?
            with open(test_path, "r") as f:
                source = f.read()
            compile(source, test_file, "exec")
            print(f"✅ {test_file} compiles")
        except Exception as e:
            errors.append((test_file, "compile", e))
            print(f"❌ {test_file} compile error: {e}")

    if errors:
        print(f"\n❌ Found {len(errors)} import/compile errors:")
        for err in errors:
            print(f"   - {err[0]}.{err[1]}: {err[2]}")
        return False
    else:
        print("\n✅ All imports and compilations successful!")
        return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
