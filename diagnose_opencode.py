#!/usr/bin/env python3
"""
诊断 OpenCode 失败问题
"""

import os
import sys
import json
import tempfile
import time
from pathlib import Path
from datetime import datetime

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from opencode_manager import OpenCodeManager


def test_opencode_direct():
    """直接测试 OpenCodeManager"""
    test_dir = Path(tempfile.mkdtemp(prefix="diagnose_opencode_"))
    print(f"测试目录: {test_dir}")

    # 使用与系统相同的配置
    config = {
        "opencode": {
            "mode": "cli",
            "command": "opencode",
            "timeout": 60,  # 使用 60 秒，与系统第一次尝试相同
            "model": "deepseek/deepseek-reasoner",
        }
    }

    print(f"配置: {json.dumps(config, indent=2)}")

    # 初始化管理器
    manager = OpenCodeManager(test_dir, config)

    # 读取实际的 init_concise.md 提示
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "init_prompt.md")
    with open(prompt_path, "r", encoding="utf-8") as f:
        init_prompt = f.read()

    # 构建完整提示，与系统相同
    user_prompt = "用go语言实现快速排序"
    full_prompt = f"Project: {user_prompt}\n\n{init_prompt}"

    print(f"提示长度: {len(full_prompt)} 字符")
    print(f"提示预览 (前500字符): {full_prompt[:500]}...")

    # 运行 OpenCode
    print(f"[{datetime.now()}] 🚀 开始运行 OpenCode (超时: 60秒)...")
    start_time = time.time()

    result = manager.run(prompt=full_prompt, agent="initializer", timeout=60)

    end_time = time.time()
    elapsed = end_time - start_time
    print(f"[{datetime.now()}] ⏱️ 运行耗时: {elapsed:.2f} 秒")
    print(f"结果: {json.dumps(result, indent=2, ensure_ascii=False)}")

    # 检查文件
    feature_file = test_dir / "feature_list.json"
    file_exists = feature_file.exists()
    print(f"feature_list.json 是否存在: {file_exists}")

    if file_exists:
        try:
            with open(feature_file, "r") as f:
                content = f.read()
                print(f"文件大小: {len(content)} 字符")
                # 尝试解析 JSON
                data = json.loads(content)
                print(f"JSON 有效! 包含 {len(data)} 个功能")
                for i, feat in enumerate(data[:3]):  # 只显示前3个
                    print(
                        f"  功能 {i + 1}: {feat.get('id')} - {feat.get('description')[:80]}..."
                    )
        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
            print(f"文件内容前200字符: {content[:200]}")
        except Exception as e:
            print(f"读取文件错误: {e}")

    # 检查 success 标志和文件存在是否一致
    success = result.get("success", False)
    if success and not file_exists:
        print("⚠️  结果 success=True 但文件不存在!")
    elif not success and file_exists:
        print("⚠️  结果 success=False 但文件存在! (可能是超时但文件已创建)")
    elif success and file_exists:
        print("✅ 成功: success=True 且文件存在")
    else:
        print("❌ 失败: success=False 且文件不存在")

    # 检查错误详情
    if "error" in result:
        print(f"错误: {result['error']}")
    if "stderr" in result and result["stderr"]:
        print(f"STDERR: {result['stderr'][:500]}")
    if "stdout" in result and result["stdout"]:
        print(f"STDOUT 前500字符: {result['stdout'][:500]}")

    return result, test_dir


def test_simple_prompt():
    """测试简单提示以验证 OpenCode 基本功能"""
    test_dir = Path(tempfile.mkdtemp(prefix="diagnose_simple_"))
    print(f"\n{'=' * 60}")
    print("测试简单提示...")
    print(f"测试目录: {test_dir}")

    config = {
        "opencode": {
            "mode": "cli",
            "command": "opencode",
            "timeout": 30,
            "model": "deepseek/deepseek-reasoner",
        }
    }

    manager = OpenCodeManager(test_dir, config)

    # 简单提示
    simple_prompt = "创建一个 hello.txt 文件，内容为 'Hello World'"
    print(f"简单提示: {simple_prompt}")

    start_time = time.time()
    result = manager.run(prompt=simple_prompt, timeout=30)
    end_time = time.time()

    print(f"耗时: {end_time - start_time:.2f} 秒")
    print(f"结果 success: {result.get('success', False)}")

    hello_file = test_dir / "hello.txt"
    if hello_file.exists():
        with open(hello_file, "r") as f:
            print(f"文件内容: {f.read()}")
        print("✅ 简单提示测试成功")
    else:
        print("❌ 简单提示测试失败")
        print(f"结果详情: {json.dumps(result, indent=2, ensure_ascii=False)}")

    return result


if __name__ == "__main__":
    print("开始诊断 OpenCode 失败问题...")

    # 测试简单提示
    simple_result = test_simple_prompt()

    # 测试完整系统提示
    print(f"\n{'=' * 60}")
    print("测试完整系统提示...")
    print(f"{'=' * 60}")

    main_result, test_dir = test_opencode_direct()

    print(f"\n{'=' * 60}")
    print("诊断完成")
    print(f"测试目录保留在: {test_dir}")
    print("请检查上面的输出以确定问题所在。")

    # 总结
    feature_file = test_dir / "feature_list.json"
    if feature_file.exists() and main_result.get("success", False):
        print("✅ 系统测试成功")
        sys.exit(0)
    elif feature_file.exists() and not main_result.get("success", False):
        print("⚠️  文件已创建但 success=False (可能是超时问题)")
        sys.exit(1)
    else:
        print("❌ 系统测试失败")
        sys.exit(1)
