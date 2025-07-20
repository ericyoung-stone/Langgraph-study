#!/usr/bin/env python3
"""
测试运行脚本
"""

import os
import subprocess
import sys


def run_tests():
    """运行所有测试"""
    print("🧪 开始运行测试...")
    print("=" * 50)
    
    # 检查是否安装了pytest
    try:
        import pytest
        print("✅ pytest 已安装")
    except ImportError:
        print("❌ pytest 未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)
    
    # 运行测试
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("📊 测试输出:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  警告/错误:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("🎉 所有测试通过!")
        else:
            print("❌ 部分测试失败")
            
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行测试时出错: {e}")
        return False


def run_specific_test():
    """运行特定的测试文件"""
    print("🧪 运行 React Agent 测试...")
    
    test_file = "tests/get_start/test_quick_start_react_agent_demo.py"
    
    if not os.path.exists(test_file):
        print(f"❌ 测试文件不存在: {test_file}")
        return False
    
    cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print("📊 测试输出:")
        print(result.stdout)
        
        if result.returncode == 0:
            print("🎉 React Agent 测试通过!")
        else:
            print("❌ React Agent 测试失败")
            
        return result.returncode == 0
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 运行测试时出错: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="运行项目测试")
    parser.add_argument("--specific", action="store_true", 
                       help="只运行 React Agent 测试")
    
    args = parser.parse_args()
    
    if args.specific:
        success = run_specific_test()
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1) 