#!/usr/bin/env python3
import subprocess
import tempfile
import os
import shutil


def test_simple_prompt():
    # Read simple prompt
    with open(
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "init_prompt_simple.md"),
        "r",
        encoding="utf-8",
    ) as f:
        init_prompt = f.read()

    user_prompt = "用go语言实现快速排序"
    full_prompt = f"{init_prompt}\n\n## User Request\n\n{user_prompt}"

    test_dir = tempfile.mkdtemp(prefix="test_simple_")
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
        "deepseek/deepseek-chat",
        full_prompt,
    ]

    print(f"Running OpenCode...")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, cwd=test_dir, env=env
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout)}")
        print(f"Stderr length: {len(result.stderr)}")

        if result.stdout:
            print("\n=== Stdout (first 1000 chars) ===")
            print(result.stdout[:1000])

        if result.stderr:
            print("\n=== Stderr (first 1000 chars) ===")
            print(result.stderr[:1000])

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

    except subprocess.TimeoutExpired:
        print("TIMEOUT after 30 seconds")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\nCleaned up {test_dir}")


if __name__ == "__main__":
    test_simple_prompt()
