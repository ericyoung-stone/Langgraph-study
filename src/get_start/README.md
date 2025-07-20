# React Agent 示例

这个示例展示了如何使用 LangGraph 的 `create_react_agent` 创建一个简单的天气查询代理。

## 文件结构

```
src/get_start/
├── __init__.py              # 模块初始化文件
├── react_agent_demo.py      # React Agent 演示代码
└── README.md               # 本文件
```

## 功能说明

### `get_weather(city: str) -> str`
一个简单的天气查询工具函数，返回指定城市的天气信息。

### `create_weather_agent()`
创建一个配置好的 React Agent，使用 Claude-3-7-Sonnet 模型和天气查询工具。

### `run_agent_demo()`
运行完整的代理演示，包括创建代理、发送测试查询和显示结果。

## 使用方法

### 1. 设置环境变量

首先需要设置 Anthropic API 密钥：

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

您可以在 [Anthropic Console](https://console.anthropic.com/) 获取 API 密钥。

### 2. 运行演示

#### 方法一：直接运行模块文件

```bash
python src/get_start/react_agent_demo.py
```

#### 方法二：使用测试脚本

```bash
python test_react_agent.py
```

#### 方法三：在 Python 中导入使用

```python
from src.get_start.react_agent_demo import run_agent_demo

# 运行演示
result = run_agent_demo()
```

## 预期输出

成功运行时，您将看到类似以下的输出：

```
🚀 启动 React Agent 演示...
📝 测试查询: what is the weather in sf
📊 代理响应:
[代理的响应内容]
```

## 错误处理

如果遇到 API 密钥未设置的错误，程序会提供详细的解决方案说明。

## 依赖项

- langgraph >= 0.5.3
- langchain >= 0.3.26

这些依赖项已在 `pyproject.toml` 中配置。 