#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Build the prompt as the system does
prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "init_prompt.md")
with open(prompt_path, "r", encoding="utf-8") as f:
    init_prompt = f.read()

user_prompt = "用go语言实现快速排序"
full_prompt = f"{init_prompt}\n\n## 用户需求\n\n{user_prompt}"

print("=== Prompt length ===")
print(f"{len(full_prompt)} characters")

print("\n=== First 500 chars ===")
print(full_prompt[:500])

print("\n=== Last 500 chars ===")
print(full_prompt[-500:])

# Write to file for inspection
with open("/tmp/debug_prompt.txt", "w", encoding="utf-8") as f:
    f.write(full_prompt)
print(f"\nPrompt written to /tmp/debug_prompt.txt")

# Now test with OpenCode
import subprocess
import tempfile
import shutil

test_dir = tempfile.mkdtemp(prefix="debug_opencode_")
print(f"\n=== Testing OpenCode in {test_dir} ===")

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

print(f"Command: {' '.join(cmd[:6])} [prompt...]")

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

except subprocess.TimeoutExpired:
    print("TIMEOUT after 30 seconds")
except Exception as e:
    print(f"Error: {e}")
finally:
    shutil.rmtree(test_dir, ignore_errors=True)
    print(f"\nCleaned up {test_dir}")
