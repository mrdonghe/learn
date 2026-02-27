#!/usr/bin/env python3
"""Simple test of OpenCodeManager integration."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from opencode_manager import OpenCodeManager


def test_opencode_manager():
    """Test OpenCodeManager with a simple prompt."""
    test_dir = Path("/tmp/test_opencode_integration")
    test_dir.mkdir(exist_ok=True)

    # Minimal config (CLI mode defaults)
    config = {
        "opencode": {
            "mode": "cli",
            "command": "opencode",
            "timeout": 30,  # Short timeout for test
            "model": "deepseek/deepseek-reasoner",
        }
    }

    print(f"Testing OpenCodeManager in directory: {test_dir}")
    print(f"Config: {config}")

    manager = OpenCodeManager(test_dir, config)

    # Very simple prompt - just ask for a greeting
    prompt = "Create a file called hello.txt with the text 'Hello World'"

    try:
        print(f"Running OpenCode with prompt: {prompt}")
        result = manager.run(prompt=prompt, timeout=30)
        print(f"Result: {result}")

        # Check if hello.txt was created
        hello_file = test_dir / "hello.txt"
        if hello_file.exists():
            content = hello_file.read_text()
            print(f"Success! hello.txt created with content: {content}")
            return True
        else:
            print("Warning: hello.txt not created")
            # Check what files were created
            files = list(test_dir.glob("*"))
            print(f"Files in directory: {files}")
            return False

    except Exception as e:
        print(f"Error running OpenCode: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_opencode_manager()
    sys.exit(0 if success else 1)
