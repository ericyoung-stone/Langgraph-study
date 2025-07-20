"""
Get Started 模块
包含 LangGraph 入门示例
"""

from .langgraph_agents_tutorial import (
    # 基础函数
    get_weather as tutorial_get_weather,
    WeatherResponse,

    # 代理创建函数
    create_basic_agent,
    create_configured_agent,
    create_static_prompt_agent,
    create_dynamic_prompt_agent,
    create_memory_agent,
    create_structured_output_agent,

    # 演示函数
    run_basic_agent_demo,
    run_configured_agent_demo,
    run_static_prompt_demo,
    run_dynamic_prompt_demo,
    run_memory_agent_demo,
    run_structured_output_demo,
    run_complete_tutorial
)
from .react_agent_demo import (
    get_weather,
    create_weather_agent,
    run_agent_demo
)

__all__ = [
    # React Agent Demo
    "get_weather",
    "create_weather_agent", 
    "run_agent_demo",
    
    # LangGraph Agents Tutorial
    "tutorial_get_weather",
    "WeatherResponse",
    "create_basic_agent",
    "create_configured_agent", 
    "create_static_prompt_agent",
    "create_dynamic_prompt_agent",
    "create_memory_agent",
    "create_structured_output_agent",
    "run_basic_agent_demo",
    "run_configured_agent_demo",
    "run_static_prompt_demo",
    "run_dynamic_prompt_demo",
    "run_memory_agent_demo",
    "run_structured_output_demo",
    "run_complete_tutorial"
]
