"""
LangGraph 流式输出示例运行脚本

这个脚本允许用户选择运行特定的流式输出示例。
"""

import asyncio

from streaming_examples import (
    demo_agent_progress_streaming,
    demo_llm_token_streaming,
    demo_tool_updates_streaming,
    demo_multiple_stream_modes,
    demo_disable_streaming,
    demo_workflow_basic_streaming,
    demo_graph_state_streaming,
    demo_custom_data_streaming,
    demo_debug_streaming,
    demo_async_llm_manual_config,
    demo_async_custom_streaming,
    demo_arbitrary_llm_streaming,
)


def print_menu():
    """打印菜单选项"""
    print("\n" + "=" * 60)
    print("LangGraph 流式输出示例菜单")
    print("=" * 60)
    print("同步示例:")
    print("  1. 代理进度流式输出")
    print("  2. LLM Token 流式输出")
    print("  3. 工具更新流式输出")
    print("  4. 多模式流式输出")
    print("  5. 禁用流式输出")
    print("  6. 工作流基本流式输出")
    print("  7. 流式输出图状态")
    print("  8. 自定义数据流式输出")
    print("  9. 调试模式流式输出")
    print("\n异步示例:")
    print("  10. 异步 LLM 调用手动配置")
    print("  11. 异步自定义流式输出")
    print("  12. 与任意 LLM 一起使用")
    print("\n其他选项:")
    print("  0. 运行所有示例")
    print("  q. 退出")
    print("=" * 60)


async def run_example(choice):
    """根据用户选择运行相应的示例"""
    examples = {
        "1": demo_agent_progress_streaming,
        "2": demo_llm_token_streaming,
        "3": demo_tool_updates_streaming,
        "4": demo_multiple_stream_modes,
        "5": demo_disable_streaming,
        "6": demo_workflow_basic_streaming,
        "7": demo_graph_state_streaming,
        "8": demo_custom_data_streaming,
        "9": demo_debug_streaming,
        "10": demo_async_llm_manual_config,
        "11": demo_async_custom_streaming,
        "12": demo_arbitrary_llm_streaming,
    }
    
    if choice in examples:
        print(f"\n正在运行示例 {choice}...")
        try:
            if choice in ["10", "11", "12"]:
                # 异步示例
                await examples[choice]()
            else:
                # 同步示例
                examples[choice]()
            print(f"\n示例 {choice} 运行完成！")
        except Exception as e:
            print(f"运行示例 {choice} 时出错: {e}")
    else:
        print("无效的选择，请重新输入。")


async def run_all_examples():
    """运行所有示例"""
    print("\n正在运行所有示例...")
    
    # 同步示例
    sync_examples = [
        demo_agent_progress_streaming,
        demo_llm_token_streaming,
        demo_tool_updates_streaming,
        demo_multiple_stream_modes,
        demo_disable_streaming,
        demo_workflow_basic_streaming,
        demo_graph_state_streaming,
        demo_custom_data_streaming,
        demo_debug_streaming,
    ]
    
    for i, example in enumerate(sync_examples, 1):
        print(f"\n运行同步示例 {i}...")
        try:
            example()
        except Exception as e:
            print(f"同步示例 {i} 运行出错: {e}")
    
    # 异步示例
    async_examples = [
        demo_async_llm_manual_config,
        demo_async_custom_streaming,
        demo_arbitrary_llm_streaming,
    ]
    
    for i, example in enumerate(async_examples, 10):
        print(f"\n运行异步示例 {i}...")
        try:
            await example()
        except Exception as e:
            print(f"异步示例 {i} 运行出错: {e}")
    
    print("\n所有示例运行完成！")


async def main():
    """主函数"""
    print("欢迎使用 LangGraph 流式输出示例！")
    print("请确保您已经安装了所需的依赖包。")
    print("如果遇到导入错误，请运行: pip install langgraph langchain langchain-openai")
    
    while True:
        print_menu()
        choice = input("\n请选择要运行的示例 (输入数字或 'q' 退出): ").strip()
        
        if choice.lower() == 'q':
            print("再见！")
            break
        elif choice == "0":
            await run_all_examples()
        elif choice in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]:
            await run_example(choice)
        else:
            print("无效的选择，请重新输入。")
        
        input("\n按回车键继续...")


if __name__ == "__main__":
    asyncio.run(main())
