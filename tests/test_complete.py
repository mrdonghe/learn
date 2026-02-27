#!/usr/bin/env python3
import sys
import os
import tempfile
import json
import shutil
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from infinite_agent import InfiniteAIDeveloper


def test_complete_workflow():
    """测试完整的初始化 -> 编码会话工作流"""
    test_dir = tempfile.mkdtemp(prefix="test_complete_workflow_")
    print(f"Test directory: {test_dir}")

    # Step 1: 初始化
    dev = InfiniteAIDeveloper(test_dir)
    print("Step 1: Initializing project...")

    # 模拟 OpenCode 生成功能列表（使用 mock）
    def mock_run_opencode(prompt, agent_type, timeout=None):
        print(f"[Mock OpenCode] Called with agent_type={agent_type}, timeout={timeout}")

        if agent_type == "initializer":
            # 模拟创建有效的 feature_list.json
            features = [
                {
                    "id": "feature_001",
                    "category": "functional",
                    "description": "Implement basic quicksort algorithm for integer slices",
                    "priority": "high",
                    "steps": [
                        "Create Go module with 'go mod init quicksort'",
                        "Write quicksort.go with function: func QuickSort(arr []int) []int",
                        "Implement partitioning logic",
                        "Add main.go to test with sample array",
                    ],
                    "passes": False,
                    "dependencies": [],
                },
                {
                    "id": "feature_002",
                    "category": "testing",
                    "description": "Create comprehensive unit tests for quicksort implementation",
                    "priority": "high",
                    "steps": [
                        "Create test file for quicksort function",
                        "Test various input cases: empty slice, already sorted, reverse sorted, random",
                        "Verify correctness of sorted output compared to standard library sort",
                    ],
                    "passes": False,
                    "dependencies": ["feature_001"],
                },
            ]

            feature_file = os.path.join(test_dir, "feature_list.json")
            with open(feature_file, "w") as f:
                json.dump(features, f, indent=2)

            return {"success": True, "created_files": ["feature_list.json"]}
        elif agent_type == "coding":
            # 模拟创建 Go 代码文件
            quicksort_file = os.path.join(test_dir, "quicksort.go")
            with open(quicksort_file, "w") as f:
                f.write("""package main

import "fmt"

func QuickSort(arr []int) []int {
    if len(arr) < 2 {
        return arr
    }
    
    pivot := arr[0]
    var left, right []int
    
    for _, v := range arr[1:] {
        if v <= pivot {
            left = append(left, v)
        } else {
            right = append(right, v)
        }
    }
    
    left = QuickSort(left)
    right = QuickSort(right)
    
    return append(append(left, pivot), right...)
}

func main() {
    arr := []int{5, 2, 8, 1, 9, 3}
    sorted := QuickSort(arr)
    fmt.Printf("Original: %v\\n", arr)
    fmt.Printf("Sorted: %v\\n", sorted)
}""")

            main_file = os.path.join(test_dir, "main.go")
            with open(main_file, "w") as f:
                f.write("""package main

func main() {
    // Main entry point
}""")

            # 更新 feature_list.json
            feature_file = os.path.join(test_dir, "feature_list.json")
            if os.path.exists(feature_file):
                with open(feature_file, "r") as f:
                    features = json.load(f)

                for feature in features:
                    if feature["id"] == "feature_001":
                        feature["passes"] = True

                with open(feature_file, "w") as f:
                    json.dump(features, f, indent=2)

            return {"success": True, "created_files": ["quicksort.go", "main.go"]}
        else:
            return {"success": False, "error": "Unknown agent type"}

    # 替换 _run_opencode 方法
    dev._run_opencode = mock_run_opencode

    # 运行初始化
    init_result = dev.run_initializer("用go语言实现快速排序")
    print(f"Initializer result: {init_result}")

    # 检查文件
    print("\nChecking files after initialization:")
    for f in ["feature_list.json", "claude-progress.txt", "init.sh"]:
        path = os.path.join(test_dir, f)
        print(f"  {f}: {'✅' if os.path.exists(path) else '❌'}")

    # 检查 git
    git_dir = os.path.join(test_dir, ".git")
    print(f"  .git: {'✅' if os.path.exists(git_dir) else '❌'}")

    # Step 2: 运行编码会话
    print("\nStep 2: Running coding session...")
    start = time.time()
    coding_result = dev.run_coding_session()
    elapsed = time.time() - start

    print(f"Coding session completed in {elapsed:.1f}s")
    print(f"Coding result: {json.dumps(coding_result, indent=2, default=str)}")

    # 检查生成的代码文件
    print("\nChecking files after coding session:")
    go_files = [f for f in os.listdir(test_dir) if f.endswith(".go")]
    for f in go_files:
        path = os.path.join(test_dir, f)
        size = os.path.getsize(path)
        print(f"  {f}: {size} bytes")

    # 检查 feature 是否被标记为完成
    feature_file = os.path.join(test_dir, "feature_list.json")
    if os.path.exists(feature_file):
        with open(feature_file, "r") as f:
            features = json.load(f)

        print("\nFeature status:")
        for feature in features:
            print(f"  {feature['id']}: passes={feature.get('passes')}")

    # 清理
    shutil.rmtree(test_dir)
    print(f"\nCleaned up test directory")

    return True


if __name__ == "__main__":
    success = test_complete_workflow()
    sys.exit(0 if success else 1)
