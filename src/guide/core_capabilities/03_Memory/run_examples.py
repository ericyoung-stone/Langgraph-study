#!/usr/bin/env python3
"""
LangGraph 内存功能交互式运行脚本

提供友好的菜单界面，允许用户选择运行特定的内存功能示例
支持运行所有示例或单个示例，包含错误处理机制
"""

import asyncio
import sys
import traceback
from typing import Callable

from memory_examples import MemoryExamples


class InteractiveRunner:
    """交互式运行器类"""
    
    def __init__(self):
        """初始化运行器"""
        self.examples = MemoryExamples()
        self.menu_options = {
            "1": ("基本短期内存演示", self.examples.basic_short_term_memory_demo),
            "2": ("PostgreSQL 内存演示", self.examples.postgres_memory_demo),
            "3": ("MongoDB 内存演示", self.examples.mongodb_memory_demo),
            "4": ("检查点管理演示", self.examples.checkpoint_management_demo),
            "5": ("内存管理演示", self.examples.memory_management_demo),
            "6": ("异步 PostgreSQL 演示", self._run_async_demo),
            "7": ("运行所有演示", self.examples.run_all_demos),
            "0": ("退出", self._exit_program)
        }
    
    def _exit_program(self):
        """退出程序"""
        print("\n感谢使用 LangGraph 内存功能演示！再见！")
        sys.exit(0)
    
    async def _run_async_demo(self):
        """运行异步演示"""
        try:
            await self.examples.async_postgres_memory_demo()
        except Exception as e:
            print(f"异步演示运行失败: {e}")
            if self._should_show_traceback():
                traceback.print_exc()
    
    def _should_show_traceback(self) -> bool:
        """询问是否显示详细错误信息"""
        while True:
            choice = input("\n是否显示详细错误信息？(y/n): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                return True
            elif choice in ['n', 'no', '否']:
                return False
            else:
                print("请输入 y 或 n")
    
    def _display_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("           LangGraph 内存功能演示菜单")
        print("="*60)
        print("请选择要运行的演示:")
        print()
        
        for key, (name, _) in self.menu_options.items():
            print(f"  {key}. {name}")
        
        print("\n" + "-"*60)
        print("提示:")
        print("- 选择 1-6: 运行单个演示")
        print("- 选择 7: 运行所有演示")
        print("- 选择 0: 退出程序")
        print("- 数据库演示需要相应的数据库服务运行")
        print("- 异步演示需要适当的异步环境")
        print("-"*60)
    
    def _get_user_choice(self) -> str:
        """获取用户选择"""
        while True:
            choice = input("\n请输入您的选择 (0-7): ").strip()
            if choice in self.menu_options:
                return choice
            else:
                print("❌ 无效选择！请输入 0-7 之间的数字。")
    
    def _run_demo_with_error_handling(self, demo_func: Callable, demo_name: str):
        """运行演示并处理错误"""
        print(f"\n🚀 开始运行: {demo_name}")
        print("="*50)
        
        try:
            # 检查是否是异步函数
            if asyncio.iscoroutinefunction(demo_func):
                # 运行异步函数
                asyncio.run(demo_func())
            else:
                # 运行同步函数
                result = demo_func()
                return result
                
        except KeyboardInterrupt:
            print(f"\n⚠️  用户中断了 {demo_name} 的运行")
        except ImportError as e:
            print(f"\n❌ 导入错误: {e}")
            print("请确保已安装所需的依赖包")
        except ConnectionError as e:
            print(f"\n❌ 连接错误: {e}")
            print("请检查网络连接或数据库服务状态")
        except Exception as e:
            print(f"\n❌ {demo_name} 运行失败: {e}")
            if self._should_show_traceback():
                traceback.print_exc()
        else:
            print(f"\n✅ {demo_name} 运行完成！")
        
        print("="*50)
    
    def _confirm_run_all(self) -> bool:
        """确认是否运行所有演示"""
        print("\n⚠️  运行所有演示可能需要较长时间")
        print("数据库演示需要相应的数据库服务运行")
        while True:
            choice = input("确定要运行所有演示吗？(y/n): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                return True
            elif choice in ['n', 'no', '否']:
                return False
            else:
                print("请输入 y 或 n")
    
    def run(self):
        """主运行循环"""
        print("欢迎使用 LangGraph 内存功能演示！")
        print("正在初始化...")
        
        try:
            # 测试模型连接
            print("测试模型连接...")
            test_result = self.examples.basic_short_term_memory_demo()
            print("✅ 模型连接成功！")
        except Exception as e:
            print(f"❌ 模型连接失败: {e}")
            print("请检查 LM Studio 是否正在运行，以及网络连接是否正常")
            if self._should_show_traceback():
                traceback.print_exc()
            return
        
        while True:
            try:
                self._display_menu()
                choice = self._get_user_choice()
                
                demo_name, demo_func = self.menu_options[choice]
                
                if choice == "7":  # 运行所有演示
                    if self._confirm_run_all():
                        self._run_demo_with_error_handling(demo_func, demo_name)
                elif choice == "0":  # 退出
                    demo_func()
                else:  # 运行单个演示
                    self._run_demo_with_error_handling(demo_func, demo_name)
                
                # 询问是否继续
                if choice != "0":
                    self._ask_continue()
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  检测到中断信号")
                self._exit_program()
            except Exception as e:
                print(f"\n❌ 程序运行出错: {e}")
                if self._should_show_traceback():
                    traceback.print_exc()
                self._ask_continue()
    
    def _ask_continue(self):
        """询问是否继续运行"""
        while True:
            choice = input("\n是否继续运行其他演示？(y/n): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                break
            elif choice in ['n', 'no', '否']:
                self._exit_program()
            else:
                print("请输入 y 或 n")


def main():
    """主函数"""
    try:
        runner = InteractiveRunner()
        runner.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
