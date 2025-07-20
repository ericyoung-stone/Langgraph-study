#!/usr/bin/env python3
"""
测试 React Agent 演示
"""

import os
import sys

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.get_start.react_agent_demo import run_agent_demo


def main():
    """主函数"""
    print("🧪 开始测试 React Agent...")
    print("=" * 50)
    
    try:
        # 运行代理演示
        result = run_agent_demo()
        print("\n✅ 测试成功完成!")
        return result
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return None


if __name__ == "__main__":
    main() 