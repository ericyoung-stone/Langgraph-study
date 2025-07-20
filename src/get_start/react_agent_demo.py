"""
React Agent Demo
使用 LangGraph 的 create_react_agent 创建一个简单的天气查询代理
"""

import os

from langgraph.prebuilt import create_react_agent


def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息
    
    Args:
        city (str): 城市名称
        
    Returns:
        str: 天气信息
    """
    return f"It's always sunny in {city}!"


def create_weather_agent():
    """
    创建一个天气查询代理
    
    Returns:
        agent: 配置好的React Agent
    """
    # 检查API密钥
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "请设置 ANTHROPIC_API_KEY 环境变量。\n"
            "您可以在 https://console.anthropic.com/ 获取API密钥"
        )
    
    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_weather],
        prompt="You are a helpful assistant"
    )
    return agent


def run_agent_demo():
    """
    运行代理演示
    """
    print("🚀 启动 React Agent 演示...")
    
    try:
        # 创建代理
        agent = create_weather_agent()
        
        # 测试查询
        test_query = "what is the weather in sf"
        print(f"📝 测试查询: {test_query}")
        
        # 运行代理
        result = agent.invoke(
            {"messages": [{"role": "user", "content": test_query}]}
        )
        
        print("📊 代理响应:")
        print(result)
        
        return result
        
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("\n💡 解决方案:")
        print("1. 在 https://console.anthropic.com/ 获取API密钥")
        print("2. 设置环境变量: export ANTHROPIC_API_KEY='your-api-key'")
        return None
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        return None


if __name__ == "__main__":
    # 当直接运行此文件时执行演示
    run_agent_demo() 