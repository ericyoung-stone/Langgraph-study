# LangGraph Agents 教程

这个模块基于 [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/agents/agents/) 创建，展示了如何使用 LangGraph 的预构建组件来快速构建智能代理系统。

## 文件结构

```
src/get_start/
├── langgraph_agents_tutorial.py  # 主要教程代码
├── LANGGRAPH_AGENTS_TUTORIAL.md  # 本文件
└── ...
```

## 教程步骤

### 步骤 2: 创建基础 React Agent

```python
def create_basic_agent():
    """创建基础 React Agent"""
    agent = create_react_agent(
        model=get_lm_studio_llm(),  # 使用本地 LLM Studio 模型
        tools=[get_weather],        # 提供工具列表
        prompt="You are a helpful assistant"  # 系统提示
    )
    return agent
```

**功能说明：**
- 使用 `create_react_agent` 创建基础代理
- 配置语言模型（使用本地 LLM Studio）
- 添加工具函数（天气查询）
- 设置系统提示

### 步骤 3: 配置语言模型

```python
def create_configured_agent():
    """配置语言模型参数"""
    model = init_chat_model(
        "anthropic:claude-3-7-sonnet-latest",
        temperature=0  # 设置温度为 0，使输出更确定性
    )
    
    agent = create_react_agent(
        model=model,
        tools=[get_weather],
    )
    return agent
```

**功能说明：**
- 使用 `init_chat_model` 配置模型参数
- 设置温度参数控制输出随机性
- 支持自定义模型配置

### 步骤 4a: 添加静态提示

```python
def create_static_prompt_agent():
    """创建使用静态提示的代理"""
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
        prompt="Never answer questions about the weather."  # 静态提示
    )
    return agent
```

**功能说明：**
- 使用固定的系统提示
- 提示内容永远不会改变
- 适合简单的指令控制

### 步骤 4b: 添加动态提示

```python
def create_dynamic_prompt_agent():
    """创建使用动态提示的代理"""
    def prompt(state: AgentState, config: RunnableConfig) -> List[AnyMessage]:
        """动态提示函数"""
        user_name = config["configurable"].get("user_name", "User")
        system_msg = f"You are a helpful assistant. Address the user as {user_name}."
        return [{"role": "system", "content": system_msg}] + state["messages"]
    
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
        prompt=prompt
    )
    return agent
```

**功能说明：**
- 根据运行时状态和配置生成提示
- 支持用户个性化设置
- 可以访问代理状态和配置信息

### 步骤 5: 添加内存功能

```python
def create_memory_agent():
    """创建支持多轮对话的代理"""
    checkpointer = InMemorySaver()  # 创建内存检查点
    
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
        checkpointer=checkpointer  # 启用内存功能
    )
    return agent
```

**功能说明：**
- 使用 `InMemorySaver` 实现会话持久化
- 支持多轮对话记忆
- 通过 `thread_id` 管理不同会话

### 步骤 6: 配置结构化输出

```python
class WeatherResponse(BaseModel):
    """天气响应结构化模型"""
    conditions: str

def create_structured_output_agent():
    """创建支持结构化输出的代理"""
    agent = create_react_agent(
        model=get_lm_studio_llm(),
        tools=[get_weather],
        response_format=WeatherResponse  # 配置结构化输出
    )
    return agent
```

**功能说明：**
- 使用 Pydantic 模型定义输出结构
- 自动验证和格式化响应
- 支持类型安全的输出

## 使用方法

### 1. 运行完整教程

```python
from src.get_start.langgraph_agents_tutorial import run_complete_tutorial

# 运行所有步骤的演示
results = run_complete_tutorial()
```

### 2. 运行单个步骤

```python
from src.get_start.langgraph_agents_tutorial import (
    run_basic_agent_demo,
    run_configured_agent_demo,
    run_static_prompt_demo,
    run_dynamic_prompt_demo,
    run_memory_agent_demo,
    run_structured_output_demo
)

# 运行特定步骤
result = run_basic_agent_demo()
```

### 3. 创建自定义代理

```python
from src.get_start.langgraph_agents_tutorial import create_basic_agent

# 创建代理
agent = create_basic_agent()

# 使用代理
result = agent.invoke({
    "messages": [{"role": "user", "content": "what is the weather in sf"}]
})
```

## 演示函数

### `run_basic_agent_demo()`
运行步骤 2 的演示，展示基础 React Agent 的创建和使用。

### `run_configured_agent_demo()`
运行步骤 3 的演示，展示如何配置语言模型参数。

### `run_static_prompt_demo()`
运行步骤 4a 的演示，展示静态提示的使用。

### `run_dynamic_prompt_demo()`
运行步骤 4b 的演示，展示动态提示的使用。

### `run_memory_agent_demo()`
运行步骤 5 的演示，展示内存功能和多轮对话。

### `run_structured_output_demo()`
运行步骤 6 的演示，展示结构化输出的使用。

## 工具函数

### `get_weather(city: str) -> str`
简单的天气查询工具函数，返回指定城市的天气信息。

### `WeatherResponse`
Pydantic 模型，用于定义天气响应的结构化格式。

## 配置说明

### 语言模型配置
- 默认使用本地 LLM Studio 模型
- 支持自定义模型参数（温度、最大令牌数等）
- 可以配置不同的模型提供商

### 内存配置
- 使用 `InMemorySaver` 进行内存管理
- 支持会话持久化
- 通过 `thread_id` 区分不同会话

### 提示配置
- 支持静态和动态提示
- 可以访问代理状态和运行时配置
- 支持用户个性化设置

## 错误处理

所有演示函数都包含完整的错误处理：
- 捕获并记录异常
- 提供友好的错误信息
- 确保程序不会因错误而崩溃

## 测试

运行测试：

```bash
# 运行基本测试
python test_tutorial_demo.py

# 运行完整测试套件
python -m pytest tests/get_start/test_langgraph_agents_tutorial.py -v
```

## 依赖项

- langgraph >= 0.5.3
- langchain >= 0.3.26
- langchain-openai >= 0.3.28
- pydantic >= 2.0.0

这些依赖项已在 `pyproject.toml` 中配置。

## 扩展建议

1. **添加更多工具**：可以添加更多工具函数来扩展代理功能
2. **自定义模型**：可以配置不同的语言模型提供商
3. **持久化存储**：可以使用数据库替代内存存储
4. **API 集成**：可以集成真实的天气 API 服务
5. **用户界面**：可以添加 Web 界面或聊天界面

## 参考资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/agents/agents/)
- [LangChain 文档](https://python.langchain.com/)
- [Pydantic 文档](https://docs.pydantic.dev/) 