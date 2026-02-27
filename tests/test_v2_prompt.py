#!/usr/bin/env python3
import subprocess
import tempfile
import os
import shutil
import json


def test_v2_prompt():
    # Read v2 prompt
    with open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "init_prompt_v2.md"),
        "r",
        encoding="utf-8",
    ) as f:
        prompt_template = f.read()

    user_request = "用go语言实现快速排序"
    full_prompt = prompt_template.replace("{USER_REQUEST}", user_request)

    test_dir = tempfile.mkdtemp(prefix="test_v2_")
    print(f"Test directory: {test_dir}")

    env = os.environ.copy()
    env["NO_COLOR"] = "1"
    env["TERM"] = "dumb"

    cmd = [
        "opencode",
        "run",
        "--dir",
        test_dir,
        "--model",
        "deepseek/deepseek-reasoner",
        full_prompt,
    ]

    print(f"Running OpenCode (timeout 60s)...")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, cwd=test_dir, env=env
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout)}")
        print(f"Stderr length: {len(result.stderr)}")

        if result.stdout:
            print("\n=== Stdout (first 1500 chars) ===")
            print(result.stdout[:1500])

        if result.stderr:
            print("\n=== Stderr (first 500 chars) ===")
            print(result.stderr[:500])

        # List files
        print(f"\n=== Files in {test_dir} ===")
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                path = os.path.join(root, file)
                rel = os.path.relpath(path, test_dir)
                print(f"  {rel}")
                if file == "feature_list.json":
                    with open(path, "r") as f:
                        content = f.read()
                        print(f"    Content:\n{content}")
                        # Validate JSON
                        try:
                            data = json.loads(content)
                            print(f"    JSON valid, type: {type(data)}")
                            if isinstance(data, list):
                                print(f"    Array length: {len(data)}")
                                for i, feat in enumerate(data[:3]):
                                    print(
                                        f"    Feature {i}: id={feat.get('id')}, passes={feat.get('passes')}"
                                    )
                        except json.JSONDecodeError as e:
                            print(f"    JSON invalid: {e}")

    except subprocess.TimeoutExpired:
        print("TIMEOUT after 60 seconds")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\nCleaned up {test_dir}")


if __name__ == "__main__":
    test_v2_prompt()
