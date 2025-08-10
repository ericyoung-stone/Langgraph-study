#!/usr/bin/env python3
"""
测试检查点管理修复的脚本
"""

from memory_examples import MemoryExamples


def test_checkpoint_management():
    """测试检查点管理功能"""
    print("🧪 测试检查点管理功能...")
    
    try:
        examples = MemoryExamples()
        examples.checkpoint_management_demo()
        print("✅ 检查点管理功能测试通过！")
    except Exception as e:
        print(f"❌ 检查点管理功能测试失败: {e}")
        raise


def test_memory_management():
    """测试内存管理功能"""
    print("🧪 测试内存管理功能...")
    
    try:
        examples = MemoryExamples()
        examples.memory_management_demo()
        print("✅ 内存管理功能测试通过！")
    except Exception as e:
        print(f"❌ 内存管理功能测试失败: {e}")
        raise


def main():
    """主测试函数"""
    print("开始测试检查点管理修复...\n")
    
    # 测试检查点管理
    test_checkpoint_management()
    print()
    
    # 测试内存管理
    test_memory_management()
    print()
    
    print("🎉 所有测试完成！")


if __name__ == "__main__":
    main()
