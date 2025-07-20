"""
LangGraph Agents 教程
基于官方文档 https://langchain-ai.github.io/langgraph/agents/agents/ 的代码封装

本模块展示了 LangGraph 预构建组件的使用方法，包括：
- 创建 React Agent
- 配置语言模型
- 添加自定义提示
- 添加内存功能
- 配置结构化输出
"""

from typing import List

from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from pydantic import BaseModel

from src.common.local_llm import get_lm_studio_llm


def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息
    
    Args:
        city (str): 城市名称
        
    Returns:
        str: 天气信息
    """
    return f"It's always sunny in {city}!"


class WeatherResponse(BaseModel):
    """天气响应结构化模型"""
    conditions: str


def create_basic_agent():
    """
    步骤 2: 创建基础 React Agent
    
    创建一个简单的 React Agent，包含：
    - 语言模型配置
    - 工具函数
    - 系统提示
    
    Returns:
        agent: 配置好的 React Agent
    """
    agent = create_react_agent(
        model=get_lm_studio_llm(),  # 使用本地 LLM Studio 模型
        tools=[get_weather],  # 提供工具列表
        prompt="You are a helpful assistant"  # 系统提示
    )
    return agent


def create_configured_agent():
    """
    步骤 3: 配置语言模型
    
    创建一个配置了特定参数的 React Agent，包括：
    - 温度设置
    - 模型参数配置
    
    Returns:
        agent: 配置好的 React Agent
    """
    # 配置语言模型参数
    # model = init_chat_model(
    #     "deepseek:deepseek-v3",
    #     temperature=0  # 设置温度为 0，使输出更确定性
    # )
    
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
    )
    return agent


def create_static_prompt_agent():
    """
    步骤 4a: 添加静态提示
    
    创建一个使用静态提示的 React Agent
    
    Returns:
        agent: 配置好的 React Agent
    """
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
        # 静态提示，永远不会改变
        prompt="Never answer questions about the weather."
    )
    return agent


def create_dynamic_prompt_agent():
    """
    步骤 4b: 添加动态提示
    
    创建一个使用动态提示的 React Agent，可以根据状态和配置生成消息列表
    
    Returns:
        agent: 配置好的 React Agent
    """
    def prompt(state: AgentState, config: RunnableConfig) -> List[AnyMessage]:
        """
        动态提示函数
        
        Args:
            state: 代理状态
            config: 运行时配置
            
        Returns:
            List[AnyMessage]: 消息列表
        """
        user_name = config["configurable"].get("user_name", "User")
        system_msg = f"You are a helpful assistant. Address the user as {user_name}."
        return [{"role": "system", "content": system_msg}] + state["messages"]
    
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
        prompt=prompt
    )
    return agent


def create_memory_agent():
    """
    步骤 5: 添加内存功能
    
    创建一个支持多轮对话的 React Agent，包含：
    - 内存检查点
    - 会话持久化
    - 线程 ID 管理
    
    Returns:
        agent: 配置好的 React Agent
    """
    # 创建内存检查点
    checkpointer = InMemorySaver()
    
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
        checkpointer=checkpointer  # 启用内存功能
    )
    return agent


def create_structured_output_agent():
    """
    步骤 6: 配置结构化输出
    
    创建一个支持结构化输出的 React Agent，包含：
    - Pydantic 模型定义
    - 结构化响应格式
    - 模式验证
    
    Returns:
        agent: 配置好的 React Agent
    """
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
        response_format=WeatherResponse  # 配置结构化输出
    )
    return agent


def run_basic_agent_demo():
    """
    运行基础代理演示
    """
    print("🚀 步骤 2: 创建基础 React Agent")
    print("=" * 50)
    
    try:
        agent = create_basic_agent()
        
        # 运行代理
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
        )
        
        print("📊 基础代理响应:")
        print(result)
        return result
        
    except Exception as e:
        print(f"❌ 基础代理运行错误: {e}")
        return None


def run_configured_agent_demo():
    """
    运行配置代理演示
    """
    print("\n🚀 步骤 3: 配置语言模型")
    print("=" * 50)
    
    try:
        agent = create_configured_agent()
        
        # 运行代理
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
        )
        
        print("📊 配置代理响应:")
        print(result)
        return result
        
    except Exception as e:
        print(f"❌ 配置代理运行错误: {e}")
        return None


def run_static_prompt_demo():
    """
    运行静态提示代理演示
    """
    print("\n🚀 步骤 4a: 静态提示代理")
    print("=" * 50)
    
    try:
        agent = create_static_prompt_agent()
        
        # 运行代理
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
        )
        
        print("📊 静态提示代理响应:")
        print(result)
        return result
        
    except Exception as e:
        print(f"❌ 静态提示代理运行错误: {e}")
        return None


def run_dynamic_prompt_demo():
    """
    运行动态提示代理演示
    """
    print("\n🚀 步骤 4b: 动态提示代理")
    print("=" * 50)
    
    try:
        agent = create_dynamic_prompt_agent()
        
        # 运行代理，提供用户配置
        config = {"configurable": {"user_name": "John Smith"}}
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
            config
        )
        
        print("📊 动态提示代理响应:")
        print(result)
        return result
        
    except Exception as e:
        print(f"❌ 动态提示代理运行错误: {e}")
        return None


def run_memory_agent_demo():
    """
    运行内存代理演示
    """
    print("\n🚀 步骤 5: 内存代理演示")
    print("=" * 50)
    
    try:
        agent = create_memory_agent()
        
        # 配置会话
        config = {"configurable": {"thread_id": "1"}}
        
        # 第一次对话
        print("📝 第一次对话: what is the weather in sf")
        sf_response = agent.invoke(
            {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
            config
        )
        print("📊 第一次响应:")
        print(sf_response)
        
        # 第二次对话（应该记住之前的对话）
        print("\n📝 第二次对话: what about new york?")
        ny_response = agent.invoke(
            {"messages": [{"role": "user", "content": "what about new york?"}]},
            config
        )
        print("📊 第二次响应:")
        print(ny_response)
        
        return {"sf": sf_response, "ny": ny_response}
        
    except Exception as e:
        print(f"❌ 内存代理运行错误: {e}")
        return None


def run_structured_output_demo():
    """
    运行结构化输出代理演示
    """
    print("\n🚀 步骤 6: 结构化输出代理")
    print("=" * 50)
    
    try:
        agent = create_structured_output_agent()
        
        # 运行代理
        response = agent.invoke(
            {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
        )
        
        print("📊 结构化输出响应:")
        print(response)
        
        # 访问结构化响应
        if "structured_response" in response:
            print("\n📋 结构化响应:")
            print(response["structured_response"])
        
        return response
        
    except Exception as e:
        print(f"❌ 结构化输出代理运行错误: {e}")
        return None


def run_complete_tutorial():
    """
    运行完整的 LangGraph Agents 教程
    """
    print("🎓 LangGraph Agents 完整教程")
    print("=" * 60)
    
    results = {}
    
    # 步骤 2: 基础代理
    results["basic"] = run_basic_agent_demo()
    
    # 步骤 3: 配置代理
    results["configured"] = run_configured_agent_demo()
    
    # 步骤 4a: 静态提示
    results["static_prompt"] = run_static_prompt_demo()
    
    # 步骤 4b: 动态提示
    results["dynamic_prompt"] = run_dynamic_prompt_demo()
    
    # 步骤 5: 内存代理
    results["memory"] = run_memory_agent_demo()
    
    # 步骤 6: 结构化输出
    results["structured"] = run_structured_output_demo()
    
    print("\n🎉 教程完成!")
    return results


if __name__ == "__main__":
    # 当直接运行此文件时执行完整教程
    results = run_complete_tutorial()
    for k, v in results.items():
        print(f"{k}: {v}")