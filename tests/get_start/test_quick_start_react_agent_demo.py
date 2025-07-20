#!/usr/bin/env python3
"""
React Agent Demo 测试模块
"""

import os
import sys
from unittest.mock import patch, MagicMock

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.get_start.quick_start_react_agent_demo import (
    get_weather,
    create_weather_agent,
    run_agent_demo
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


class TestCreateWeatherAgent:
    """测试 create_weather_agent 函数"""
    
    # def test_create_weather_agent_no_api_key(self):
    #     """测试没有API密钥时的错误处理"""
    #     with pytest.raises(ValueError) as exc_info:
    #         create_weather_agent()
    #
    #     assert "ANTHROPIC_API_KEY" in str(exc_info.value)
    
    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    @patch('src.get_start.quick_start_react_agent_demo.create_react_agent')
    def test_create_weather_agent_with_api_key(self, mock_create_agent):
        """测试有API密钥时的正常创建"""
        mock_agent = MagicMock()
        mock_create_agent.return_value = mock_agent
        
        agent = create_weather_agent()
        
        assert agent == mock_agent
        mock_create_agent.assert_called_once()


class TestRunAgentDemo:
    """测试 run_agent_demo 函数"""
    
    @patch('src.get_start.quick_start_react_agent_demo.create_weather_agent')
    @patch('builtins.print')
    def test_run_agent_demo_success(self, mock_print, mock_create_agent):
        """测试成功运行代理演示"""
        # 模拟代理
        mock_agent = MagicMock()
        mock_result = {"messages": [{"role": "assistant", "content": "测试响应"}]}
        mock_agent.invoke.return_value = mock_result
        mock_create_agent.return_value = mock_agent
        
        result = run_agent_demo()
        
        assert result == mock_result
        mock_agent.invoke.assert_called_once()
    
    @patch('src.get_start.quick_start_react_agent_demo.create_weather_agent')
    @patch('builtins.print')
    def test_run_agent_demo_value_error(self, mock_print, mock_create_agent):
        """测试配置错误时的处理"""
        mock_create_agent.side_effect = ValueError("API密钥错误")
        
        result = run_agent_demo()
        
        assert result is None
    
    @patch('src.get_start.quick_start_react_agent_demo.create_weather_agent')
    @patch('builtins.print')
    def test_run_agent_demo_general_error(self, mock_print, mock_create_agent):
        """测试一般错误时的处理"""
        mock_create_agent.side_effect = Exception("未知错误")
        
        result = run_agent_demo()
        
        assert result is None


def test_integration():
    """集成测试 - 测试整个流程"""
    # 测试天气函数
    weather_result = get_weather("上海")
    assert "上海" in weather_result
    
    # 测试没有API密钥时的错误处理
    # with pytest.raises(ValueError):
    #     create_weather_agent()


if __name__ == "__main__":
    # 当直接运行此文件时执行基本测试
    print("🧪 开始运行 React Agent 测试...")
    
    # 运行基本测试
    test_get_weather = TestGetWeather()
    test_get_weather.test_get_weather_basic()
    print("✅ get_weather 函数测试通过")
    
    # 测试错误处理
    test_create_agent = TestCreateWeatherAgent()
    test_create_agent.test_create_weather_agent_no_api_key()
    print("✅ create_weather_agent 错误处理测试通过")
    
    print("🎉 所有测试完成!") 