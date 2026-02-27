#!/usr/bin/env python3
import subprocess
import tempfile
import os
import shutil
import json


def test_concise():
    test_dir = tempfile.mkdtemp(prefix="test_concise_")
    print(f"Test directory: {test_dir}")

    # Create feature list similar to what we have
    feature = {
        "id": "feature_001",
        "category": "functional",
        "description": "Implement basic quicksort algorithm for integer slices",
        "priority": "high",
        "steps": ["Step 1: Create Go module", "Step 2: Write quicksort function"],
        "passes": False,
        "dependencies": [],
    }

    with open(os.path.join(test_dir, "feature_list.json"), "w") as f:
        json.dump([feature], f, indent=2)

    # Read concise prompt
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "coding_concise.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        coding_prompt = f.read()

    full_prompt = f"Project: Implement {feature['description']}\n\n{coding_prompt}\n\nFeature details: {json.dumps(feature, indent=2, ensure_ascii=False)}"

    print(f"Prompt length: {len(full_prompt)} chars")
    print(f"First 300 chars:\n{full_prompt[:300]}")

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

    print(f"Running OpenCode with timeout 120s...")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, cwd=test_dir, env=env
        )

        print(f"Return code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout)}")
        print(f"Stderr length: {len(result.stderr)}")

        if result.stdout:
            print("\n=== Stdout (first 1000 chars) ===")
            print(result.stdout[:1000])

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

    except subprocess.TimeoutExpired:
        print("TIMEOUT after 120 seconds")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
        print(f"\nCleaned up {test_dir}")


if __name__ == "__main__":
    test_concise()
