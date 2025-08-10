# LangGraph 流式输出指南

## 概述

LangGraph 支持从代理（agent）或工作流（workflow）中流式输出数据，提供实时的执行反馈。

**注意**：本指南中的示例使用本地 LM Studio 模型（`qwen3-4b`），运行在 `http://192.168.1.22:1234/v1`。如需修改配置，请编辑 `src/common/local_llm.py` 文件。

## 支持的流式模式

| 模式 | 描述 |
|------|------|
| `values` | 流式输出图中每个步骤后的完整状态值 |
| `updates` | 流式输出图中每个步骤后的状态更新。如果同一步骤中有多个更新（例如多个节点运行），这些更新会分别流式输出 |
| `custom` | 从图节点内部流式输出自定义数据 |
| `messages` | 从任何调用 LLM 的图节点流式输出 2-元组 (LLM token, metadata) |
| `debug` | 流式输出图中执行过程中的尽可能多的信息 |

## 从代理流式输出

### 代理进度

使用 `stream_mode="updates"` 来流式输出代理进度，在每个代理步骤后发出事件。

对于调用一次工具的代理，您应该看到以下更新：
- **LLM 节点**：包含工具调用请求的 AI 消息
- **工具节点**：包含执行结果的工具消息  
- **LLM 节点**：最终的 AI 响应

### LLM Token 流式输出

使用 `stream_mode="messages"` 来流式输出 LLM 产生的 token：

```python
for token, metadata in agent.stream(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    stream_mode="messages"
):
    print("Token", token)
    print("Metadata", metadata)
```

### 工具更新流式输出

使用 `get_stream_writer()` 来流式输出工具执行过程中的更新：

```python
from langgraph.config import get_stream_writer

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    writer = get_stream_writer()
    # 流式输出任意数据
    writer(f"Looking up data for city: {city}")
    return f"It's always sunny in {city}!"
```

### 多模式流式输出

可以指定多个流式模式：`stream_mode=["updates", "messages", "custom"]`

### 禁用流式输出

对于不支持流式输出的模型，可以设置 `disable_streaming=True`：

```python
from src.common.local_llm import get_lm_studio_llm

model = get_lm_studio_llm()
model.disable_streaming = True
```

## 从工作流流式输出

### 基本用法示例

```python
from langgraph.config import get_stream_writer

def node(state):
    writer = get_stream_writer()
    writer({"progress": "Processing..."})
    return {"result": "completed"}

graph = (
    StateGraph(State)
    .add_node(node)
    .add_edge(START, "node")
    .compile()
)

for chunk in graph.stream(inputs, stream_mode="custom"):
    print(chunk)
```

### 流式输出图状态

使用 `stream_mode="values"` 或 `stream_mode="updates"` 来流式输出图的状态变化。

### 流式输出子图输出

支持从子图中流式输出数据。

### 调试

使用 `stream_mode="debug"` 获取最详细的执行信息。

### LLM Token 流式输出

#### 按 LLM 调用过滤

可以过滤特定 LLM 调用的 token 流式输出。

#### 按节点过滤

可以过滤特定节点的 token 流式输出。

### 流式输出自定义数据

使用 `get_stream_writer()` 从图节点内部流式输出自定义数据：

```python
@tool
def query_database(query: str) -> str:
    """Query the database."""
    writer = get_stream_writer()
    writer({"data": "Retrieved 0/100 records", "type": "progress"})
    # 执行查询
    writer({"data": "Retrieved 100/100 records", "type": "progress"})
    return "some-answer"
```

### 与任意 LLM 一起使用

`stream_mode="custom"` 可以与任何 LLM API 一起使用，即使该 API 没有实现 LangChain 聊天模型接口。

这允许您集成原始 LLM 客户端或提供自己流式接口的外部服务，使 LangGraph 对于自定义设置高度灵活。

### 禁用特定聊天模型的流式输出

```python
from src.common.local_llm import get_lm_studio_llm

llm = get_lm_studio_llm()
llm.disable_streaming = True
```

## Python < 3.11 的异步支持

在 Python < 3.11 版本中，asyncio 任务不支持 `context` 参数，这限制了 LangGraph 自动传播上下文的能力，影响流式机制：

1. 必须显式将 `RunnableConfig` 传递给异步 LLM 调用
2. 不能在异步节点或工具中使用 `get_stream_writer()`，必须直接传递 `writer` 参数

### 异步 LLM 调用的手动配置示例

```python
from src.common.local_llm import get_lm_studio_llm

llm = get_lm_studio_llm()

async def call_model(state, config):
    topic = state["topic"]
    joke_response = await llm.ainvoke(
        [{"role": "user", "content": f"Write a joke about {topic}"}],
        config,  # 传递配置以确保正确的上下文传播
    )
    return {"joke": joke_response.content}
```

### 异步自定义流式输出示例

```python
async def generate_joke(state: State, writer: StreamWriter):
    writer({"custom_key": "Streaming custom data while generating a joke"})
    return {"joke": f"This is a joke about {state['topic']}"}
```

## 最佳实践

1. **选择合适的流式模式**：根据您的需求选择合适的流式模式组合
2. **错误处理**：在流式输出过程中妥善处理错误
3. **性能考虑**：流式输出可能会影响性能，特别是在高并发场景下
4. **调试**：使用 `debug` 模式来诊断流式输出问题
5. **兼容性**：注意不同 Python 版本的异步支持差异

## 参考链接

- [LangGraph 流式输出官方文档](https://langchain-ai.github.io/langgraph/how-tos/streaming/#stream-graph-state)
