#!/usr/bin/env python3
"""
LangGraph Agents Tutorial 测试模块
"""

import os
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.get_start.langgraph_agents_tutorial import (
    get_weather,
    WeatherResponse,
    create_basic_agent,
    create_configured_agent,
    create_static_prompt_agent,
    create_dynamic_prompt_agent,
    create_memory_agent,
    create_structured_output_agent,
    run_basic_agent_demo,
    run_memory_agent_demo,
    run_structured_output_demo,
    run_complete_tutorial
)


class TestGetWeather:
    """测试 get_weather 函数"""
    
    def test_get_weather_basic(self):
        """测试基本的天气查询功能"""
        result = get_weather("北京")
        assert result == "It's always sunny in 北京!"
    
    def test_get_weather_empty_city(self):
        """测试空城市名称"""
        result = get_weather("")
        assert result == "It's always sunny in !"
    
    def test_get_weather_special_chars(self):
        """测试特殊字符城市名称"""
        result = get_weather("New York")
        assert result == "It's always sunny in New York!"


class TestWeatherResponse:
    """测试 WeatherResponse 模型"""
    
    def test_weather_response_creation(self):
        """测试创建 WeatherResponse 实例"""
        response = WeatherResponse(conditions="sunny")
        assert response.conditions == "sunny"
    
    def test_weather_response_validation(self):
        """测试 WeatherResponse 验证"""
        # 应该成功创建
        response = WeatherResponse(conditions="cloudy")
        assert response.conditions == "cloudy"


class TestAgentCreation:
    """测试代理创建函数"""
    
    @patch('src.get_start.langgraph_agents_tutorial.get_lm_studio_llm')
    @patch('src.get_start.langgraph_agents_tutorial.create_react_agent')
    def test_create_basic_agent(self, mock_create_agent, mock_get_llm):
        """测试创建基础代理"""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_basic_agent()
        
        assert agent == mock_agent
        mock_create_agent.assert_called_once_with(
            model=mock_llm,
            tools=[get_weather],
            prompt="You are a helpful assistant"
        )
    
    @patch('src.get_start.langgraph_agents_tutorial.init_chat_model')
    @patch('src.get_start.langgraph_agents_tutorial.create_react_agent')
    def test_create_configured_agent(self, mock_create_agent, mock_init_model):
        """测试创建配置代理"""
        mock_model = MagicMock()
        mock_init_model.return_value = mock_model
        
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_configured_agent()
        
        assert agent == mock_agent
        mock_init_model.assert_called_once_with(
            "anthropic:claude-3-7-sonnet-latest",
            temperature=0
        )
    
    @patch('src.get_start.langgraph_agents_tutorial.get_lm_studio_llm')
    @patch('src.get_start.langgraph_agents_tutorial.create_react_agent')
    def test_create_static_prompt_agent(self, mock_create_agent, mock_get_llm):
        """测试创建静态提示代理"""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_static_prompt_agent()
        
        assert agent == mock_agent
        mock_create_agent.assert_called_once_with(
            model=mock_llm,
            tools=[get_weather],
            prompt="Never answer questions about the weather."
        )
    
    @patch('src.get_start.langgraph_agents_tutorial.get_lm_studio_llm')
    @patch('src.get_start.langgraph_agents_tutorial.create_react_agent')
    def test_create_dynamic_prompt_agent(self, mock_create_agent, mock_get_llm):
        """测试创建动态提示代理"""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_dynamic_prompt_agent()
        
        assert agent == mock_agent
        # 验证调用参数包含 prompt 函数
        call_args = mock_create_agent.call_args
        assert call_args[1]['model'] == mock_llm
        assert call_args[1]['tools'] == [get_weather]
        assert callable(call_args[1]['prompt'])
    
    @patch('src.get_start.langgraph_agents_tutorial.get_lm_studio_llm')
    @patch('src.get_start.langgraph_agents_tutorial.create_react_agent')
    @patch('src.get_start.langgraph_agents_tutorial.InMemorySaver')
    def test_create_memory_agent(self, mock_saver, mock_create_agent, mock_get_llm):
        """测试创建内存代理"""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        mock_checkpointer = MagicMock()
        mock_saver.return_value = mock_checkpointer
        
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_memory_agent()
        
        assert agent == mock_agent
        mock_create_agent.assert_called_once_with(
            model=mock_llm,
            tools=[get_weather],
            checkpointer=mock_checkpointer
        )
    
    @patch('src.get_start.langgraph_agents_tutorial.get_lm_studio_llm')
    @patch('src.get_start.langgraph_agents_tutorial.create_react_agent')
    def test_create_structured_output_agent(self, mock_create_agent, mock_get_llm):
        """测试创建结构化输出代理"""
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_structured_output_agent()
        
        assert agent == mock_agent
        mock_create_agent.assert_called_once_with(
            model=mock_llm,
            tools=[get_weather],
            response_format=WeatherResponse
        )


class TestDemoFunctions:
    """测试演示函数"""
    
    @patch('src.get_start.langgraph_agents_tutorial.create_basic_agent')
    @patch('builtins.print')
    def test_run_basic_agent_demo_success(self, mock_print, mock_create_agent):
        """测试基础代理演示成功"""
        mock_agent = MagicMock()
        mock_result = {"messages": [{"role": "assistant", "content": "测试响应"}]}
        mock_agent.invoke.return_value = mock_result
        mock_create_agent.return_value = mock_agent
        
        result = run_basic_agent_demo()
        
        assert result == mock_result
        mock_agent.invoke.assert_called_once()
    
    @patch('src.get_start.langgraph_agents_tutorial.create_basic_agent')
    @patch('builtins.print')
    def test_run_basic_agent_demo_error(self, mock_print, mock_create_agent):
        """测试基础代理演示错误处理"""
        mock_create_agent.side_effect = Exception("测试错误")
        
        result = run_basic_agent_demo()
        
        assert result is None
    
    @patch('src.get_start.langgraph_agents_tutorial.create_memory_agent')
    @patch('builtins.print')
    def test_run_memory_agent_demo(self, mock_print, mock_create_agent):
        """测试内存代理演示"""
        mock_agent = MagicMock()
        mock_sf_result = {"messages": [{"role": "assistant", "content": "SF天气"}]}
        mock_ny_result = {"messages": [{"role": "assistant", "content": "NY天气"}]}
        mock_agent.invoke.side_effect = [mock_sf_result, mock_ny_result]
        mock_create_agent.return_value = mock_agent
        
        result = run_memory_agent_demo()
        
        assert result == {"sf": mock_sf_result, "ny": mock_ny_result}
        assert mock_agent.invoke.call_count == 2
    
    @patch('src.get_start.langgraph_agents_tutorial.create_structured_output_agent')
    @patch('builtins.print')
    def test_run_structured_output_demo(self, mock_print, mock_create_agent):
        """测试结构化输出演示"""
        mock_agent = MagicMock()
        mock_result = {
            "messages": [{"role": "assistant", "content": "测试响应"}],
            "structured_response": WeatherResponse(conditions="sunny")
        }
        mock_agent.invoke.return_value = mock_result
        mock_create_agent.return_value = mock_agent
        
        result = run_structured_output_demo()
        
        assert result == mock_result


class TestCompleteTutorial:
    """测试完整教程"""
    
    @patch('src.get_start.langgraph_agents_tutorial.run_basic_agent_demo')
    @patch('src.get_start.langgraph_agents_tutorial.run_configured_agent_demo')
    @patch('src.get_start.langgraph_agents_tutorial.run_static_prompt_demo')
    @patch('src.get_start.langgraph_agents_tutorial.run_dynamic_prompt_demo')
    @patch('src.get_start.langgraph_agents_tutorial.run_memory_agent_demo')
    @patch('src.get_start.langgraph_agents_tutorial.run_structured_output_demo')
    @patch('builtins.print')
    def test_run_complete_tutorial(self, mock_print, mock_structured, mock_memory, 
                                  mock_dynamic, mock_static, mock_configured, mock_basic):
        """测试完整教程运行"""
        # 设置模拟返回值
        mock_basic.return_value = {"basic": "result"}
        mock_configured.return_value = {"configured": "result"}
        mock_static.return_value = {"static": "result"}
        mock_dynamic.return_value = {"dynamic": "result"}
        mock_memory.return_value = {"memory": "result"}
        mock_structured.return_value = {"structured": "result"}
        
        result = run_complete_tutorial()
        
        # 验证所有演示函数都被调用
        mock_basic.assert_called_once()
        mock_configured.assert_called_once()
        mock_static.assert_called_once()
        mock_dynamic.assert_called_once()
        mock_memory.assert_called_once()
        mock_structured.assert_called_once()
        
        # 验证返回结果
        expected_result = {
            "basic": {"basic": "result"},
            "configured": {"configured": "result"},
            "static_prompt": {"static": "result"},
            "dynamic_prompt": {"dynamic": "result"},
            "memory": {"memory": "result"},
            "structured": {"structured": "result"}
        }
        assert result == expected_result


def test_integration():
    """集成测试 - 测试整个流程"""
    # 测试天气函数
    weather_result = get_weather("上海")
    assert "上海" in weather_result
    
    # 测试 WeatherResponse 模型
    response = WeatherResponse(conditions="cloudy")
    assert response.conditions == "cloudy"


if __name__ == "__main__":
    # 当直接运行此文件时执行基本测试
    print("🧪 开始运行 LangGraph Agents Tutorial 测试...")
    
    # 运行基本测试
    test_get_weather = TestGetWeather()
    test_get_weather.test_get_weather_basic()
    print("✅ get_weather 函数测试通过")
    
    # 测试模型
    test_weather_response = TestWeatherResponse()
    test_weather_response.test_weather_response_creation()
    print("✅ WeatherResponse 模型测试通过")
    
    print("🎉 所有测试完成!") 