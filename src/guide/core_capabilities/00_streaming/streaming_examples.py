"""
LangGraph 流式输出示例

本文件包含 LangGraph 流式输出的各种示例，每个示例都是独立的可执行方法。
"""

import asyncio
import operator
from typing import TypedDict

from langchain_core.tools import tool
from langgraph.config import get_stream_writer
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import create_react_agent
from langgraph.types import StreamWriter
from typing_extensions import Annotated

from src.common.local_llm import get_lm_studio_llm


# ============================================================================
# 基础工具定义
# ============================================================================

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。"""
    writer = get_stream_writer()
    # 流式输出任意数据
    writer(f"正在查找城市数据: {city}")
    return f"{city} 的天气总是晴朗的！"


@tool
def query_database(query: str) -> str:
    """查询数据库。"""
    writer = get_stream_writer()
    writer({"data": "已检索 0/100 条记录", "type": "progress"})
    # 模拟数据库查询
    import time
    time.sleep(0.1)
    writer({"data": "已检索 100/100 条记录", "type": "progress"})
    return "查询结果：数据库中有 100 条记录"


# ============================================================================
# 状态定义
# ============================================================================

class State(TypedDict):
    """基础状态定义"""
    messages: Annotated[list[dict], operator.add]


class JokeState(TypedDict):
    """笑话生成状态"""
    topic: str
    joke: str


# ============================================================================
# 示例 1: 代理进度流式输出
# ============================================================================

def demo_agent_progress_streaming():
    """演示代理进度流式输出"""
    print("=== 示例 1: 代理进度流式输出 ===")
    
    # 创建 React 代理
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
    )
    
    print("开始流式输出代理进度...")
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]},
        stream_mode="updates"
    ):
        print(f"更新: {chunk}")
        print()


# ============================================================================
# 示例 2: LLM Token 流式输出
# ============================================================================

def demo_llm_token_streaming():
    """演示 LLM Token 流式输出"""
    print("=== 示例 2: LLM Token 流式输出 ===")
    
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
    )
    
    print("开始流式输出 LLM tokens...")
    for token, metadata in agent.stream(
        {"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]},
        stream_mode="messages"
    ):
        print(f"Token: {token}")
        print(f"Metadata: {metadata}")
        print()


# ============================================================================
# 示例 3: 工具更新流式输出
# ============================================================================

def demo_tool_updates_streaming():
    """演示工具更新流式输出"""
    print("=== 示例 3: 工具更新流式输出 ===")
    
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
    )
    
    print("开始流式输出工具更新...")
    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]},
        stream_mode="custom"
    ):
        print(f"自定义数据: {chunk}")
        print()


# ============================================================================
# 示例 4: 多模式流式输出
# ============================================================================

def demo_multiple_stream_modes():
    """演示多模式流式输出"""
    print("=== 示例 4: 多模式流式输出 ===")
    
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
    )
    
    print("开始多模式流式输出...")
    for stream_mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]},
        stream_mode=["updates", "messages", "custom"]
    ):
        print(f"模式: {stream_mode}")
        print(f"数据: {chunk}")
        print()


# ============================================================================
# 示例 5: 禁用流式输出
# ============================================================================

def demo_disable_streaming():
    """演示禁用流式输出"""
    print("=== 示例 5: 禁用流式输出 ===")
    
    # 创建禁用流式输出的模型
    model = get_lm_studio_llm()
    model.disable_streaming = True
    
    print("已禁用流式输出")
    print(f"模型配置: {model}")


# ============================================================================
# 示例 6: 工作流基本流式输出
# ============================================================================

def demo_workflow_basic_streaming():
    """演示工作流基本流式输出"""
    print("=== 示例 6: 工作流基本流式输出 ===")
    
    def node(state):
        writer = get_stream_writer()
        writer({"progress": "正在处理..."})
        return {"result": "完成"}
    
    graph = (
        StateGraph(State)
        .add_node(node)
        .add_edge(START, "node")
        .compile()
    )
    
    inputs = {"messages": [{"role": "user", "content": "测试消息"}]}
    
    print("开始工作流流式输出...")
    for chunk in graph.stream(inputs, stream_mode="custom"):
        print(f"工作流数据: {chunk}")


# ============================================================================
# 示例 7: 流式输出图状态
# ============================================================================

def demo_graph_state_streaming():
    """演示流式输出图状态"""
    print("=== 示例 7: 流式输出图状态 ===")
    
    def node1(state):
        return {"messages": [{"role": "assistant", "content": "第一步完成"}]}
    
    def node2(state):
        return {"messages": [{"role": "assistant", "content": "第二步完成"}]}
    
    graph = (
        StateGraph(State)
        .add_node("node1", node1)
        .add_node("node2", node2)
        .add_edge(START, "node1")
        .add_edge("node1", "node2")
        .compile()
    )
    
    inputs = {"messages": [{"role": "user", "content": "开始处理"}]}
    
    print("开始流式输出图状态...")
    for chunk in graph.stream(inputs, stream_mode="values"):
        print(f"完整状态: {chunk}")
    
    print("\n开始流式输出状态更新...")
    for chunk in graph.stream(inputs, stream_mode="updates"):
        print(f"状态更新: {chunk}")


# ============================================================================
# 示例 8: 自定义数据流式输出
# ============================================================================

def demo_custom_data_streaming():
    """演示自定义数据流式输出"""
    print("=== 示例 8: 自定义数据流式输出 ===")
    
    def custom_node(state):
        writer = get_stream_writer()
        writer({"data": "检索到 0/100 条记录", "type": "progress"})
        # 模拟处理
        import time
        time.sleep(0.1)
        writer({"data": "检索到 100/100 条记录", "type": "progress"})
        return {"result": "处理完成"}
    
    graph = (
        StateGraph(State)
        .add_node(custom_node)
        .add_edge(START, "custom_node")
        .compile()
    )
    
    inputs = {"messages": [{"role": "user", "content": "查询数据"}]}
    
    print("开始自定义数据流式输出...")
    for chunk in graph.stream(inputs, stream_mode="custom"):
        print(f"自定义数据: {chunk}")


# ============================================================================
# 示例 9: 异步 LLM 调用手动配置
# ============================================================================

async def demo_async_llm_manual_config():
    """演示异步 LLM 调用的手动配置"""
    print("=== 示例 9: 异步 LLM 调用手动配置 ===")
    
    llm = get_lm_studio_llm()
    
    async def call_model(state, config):
        topic = state["topic"]
        print("正在生成笑话...")
        joke_response = await llm.ainvoke(
            [{"role": "user", "content": f"写一个关于 {topic} 的笑话"}],
            config,  # 传递配置以确保正确的上下文传播
        )
        return {"joke": joke_response.content}
    
    graph = (
        StateGraph(JokeState)
        .add_node(call_model)
        .add_edge(START, "call_model")
        .compile()
    )
    
    print("开始异步 LLM 流式输出...")
    async for chunk, metadata in graph.astream(
        {"topic": "冰淇淋"},
        stream_mode="messages",
    ):
        if chunk.content:
            print(chunk.content, end="|", flush=True)
    print()


# ============================================================================
# 示例 10: 异步自定义流式输出
# ============================================================================

async def demo_async_custom_streaming():
    """演示异步自定义流式输出"""
    print("=== 示例 10: 异步自定义流式输出 ===")
    
    async def generate_joke(state: JokeState, writer: StreamWriter):
        writer({"custom_key": "在生成笑话时流式输出自定义数据"})
        return {"joke": f"这是关于 {state['topic']} 的笑话"}
    
    graph = (
        StateGraph(JokeState)
        .add_node(generate_joke)
        .add_edge(START, "generate_joke")
        .compile()
    )
    
    print("开始异步自定义流式输出...")
    async for chunk in graph.astream(
        {"topic": "冰淇淋"},
        stream_mode="custom",
    ):
        print(f"异步自定义数据: {chunk}")


# ============================================================================
# 示例 11: 与任意 LLM 一起使用
# ============================================================================

async def demo_arbitrary_llm_streaming():
    """演示与任意 LLM 一起使用流式输出"""
    print("=== 示例 11: 与任意 LLM 一起使用 ===")
    
    async def call_arbitrary_model(state):
        """调用任意模型并流式输出结果的示例节点"""
        writer = get_stream_writer()
        
        # 模拟自定义流式客户端
        async def your_custom_streaming_client(topic):
            responses = [
                f"关于 {topic} 的第一个想法",
                f"关于 {topic} 的第二个想法", 
                f"关于 {topic} 的最终结论"
            ]
            for response in responses:
                await asyncio.sleep(0.1)
                yield response
        
        # 使用自定义流式客户端
        async for chunk in your_custom_streaming_client(state["topic"]):
            writer({"custom_llm_chunk": chunk})
        
        return {"result": "完成"}
    
    graph = (
        StateGraph(JokeState)
        .add_node(call_arbitrary_model)
        .add_edge(START, "call_arbitrary_model")
        .compile()
    )
    
    print("开始任意 LLM 流式输出...")
    async for chunk in graph.astream(
        {"topic": "人工智能"},
        stream_mode="custom",
    ):
        print(f"任意 LLM 数据: {chunk}")


# ============================================================================
# 示例 12: 调试模式流式输出
# ============================================================================

def demo_debug_streaming():
    """演示调试模式流式输出"""
    print("=== 示例 12: 调试模式流式输出 ===")
    
    def debug_node(state):
        return {"messages": [{"role": "assistant", "content": "调试信息"}]}
    
    graph = (
        StateGraph(State)
        .add_node(debug_node)
        .add_edge(START, "debug_node")
        .compile()
    )
    
    inputs = {"messages": [{"role": "user", "content": "调试测试"}]}
    
    print("开始调试模式流式输出...")
    for chunk in graph.stream(inputs, stream_mode="debug"):
        print(f"调试信息: {chunk}")


# ============================================================================
# 主函数 - 运行所有示例
# ============================================================================

def run_all_sync_examples():
    """运行所有同步示例"""
    print("开始运行 LangGraph 流式输出示例...\n")
    
    # 同步示例
    demo_agent_progress_streaming()
    demo_llm_token_streaming()
    demo_tool_updates_streaming()
    demo_multiple_stream_modes()
    demo_disable_streaming()
    demo_workflow_basic_streaming()
    demo_graph_state_streaming()
    demo_custom_data_streaming()
    demo_debug_streaming()


async def run_all_async_examples():
    """运行所有异步示例"""
    print("开始运行异步示例...\n")
    
    # 异步示例
    await demo_async_llm_manual_config()
    await demo_async_custom_streaming()
    await demo_arbitrary_llm_streaming()


async def main():
    """主函数"""
    print("LangGraph 流式输出完整示例")
    print("=" * 50)
    
    # 运行同步示例
    run_all_sync_examples()
    
    print("\n" + "=" * 50)
    
    # 运行异步示例
    await run_all_async_examples()
    
    print("\n所有示例运行完成！")


if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main())
