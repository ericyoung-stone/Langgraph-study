# LangGraph 流式输出指南

本目录包含 LangGraph 流式输出的完整指南和示例代码。

## 文件说明

- `streaming_guide.md` - 详细的流式输出指南文档
- `streaming_examples.py` - 包含所有流式输出示例的 Python 文件
- `run_examples.py` - 交互式运行脚本，可以选择运行特定示例
- `README.md` - 本文件，使用说明

## 快速开始

### 1. 安装依赖

确保您已经安装了必要的依赖包：

```bash
pip install langgraph langchain langchain-openai
```

### 2. 配置本地 LM Studio

本示例使用本地 LM Studio 模型，请确保：

1. LM Studio 已启动并运行在 `http://192.168.1.22:1234/v1`
2. 已加载 `qwen3-4b` 模型
3. 如果需要修改配置，请编辑 `src/common/local_llm.py` 文件

### 2. 运行示例

#### 方式一：交互式运行（推荐）

```bash
python run_examples.py
```

这将启动一个交互式菜单，您可以选择运行特定的示例。

#### 方式二：直接运行所有示例

```bash
python streaming_examples.py
```

这将按顺序运行所有示例。

#### 方式三：运行特定示例

您也可以直接导入并运行特定的示例函数：

```python
from streaming_examples import demo_agent_progress_streaming

# 运行代理进度流式输出示例
demo_agent_progress_streaming()
```

## 示例概览

### 同步示例

1. **代理进度流式输出** - 演示如何流式输出代理的执行进度
2. **LLM Token 流式输出** - 演示如何流式输出 LLM 产生的 token
3. **工具更新流式输出** - 演示如何从工具中流式输出更新信息
4. **多模式流式输出** - 演示如何同时使用多种流式模式
5. **禁用流式输出** - 演示如何禁用特定模型的流式输出
6. **工作流基本流式输出** - 演示工作流的基本流式输出
7. **流式输出图状态** - 演示如何流式输出图的状态变化
8. **自定义数据流式输出** - 演示如何流式输出自定义数据
9. **调试模式流式输出** - 演示调试模式的详细输出

### 异步示例

10. **异步 LLM 调用手动配置** - 演示异步 LLM 调用的手动配置
11. **异步自定义流式输出** - 演示异步自定义流式输出
12. **与任意 LLM 一起使用** - 演示如何与任意 LLM API 一起使用流式输出

## 流式模式说明

| 模式 | 描述 |
|------|------|
| `values` | 流式输出图中每个步骤后的完整状态值 |
| `updates` | 流式输出图中每个步骤后的状态更新 |
| `custom` | 从图节点内部流式输出自定义数据 |
| `messages` | 从任何调用 LLM 的图节点流式输出 token |
| `debug` | 流式输出图中执行过程中的尽可能多的信息 |

## 注意事项

1. **本地 LM Studio**：示例使用本地 LM Studio 模型，请确保 LM Studio 已启动并正确配置
2. **网络连接**：需要确保能够访问 LM Studio 服务（默认地址：http://192.168.1.22:1234/v1）
3. **Python 版本**：异步示例在 Python < 3.11 中有一些限制
4. **错误处理**：示例包含基本的错误处理，但在生产环境中需要更完善的错误处理
5. **模型配置**：如需修改模型配置，请编辑 `src/common/local_llm.py` 文件

## 自定义和扩展

您可以基于这些示例创建自己的流式输出应用：

1. 修改工具函数以包含您自己的业务逻辑
2. 调整状态定义以适应您的数据模型
3. 组合不同的流式模式以满足您的需求
4. 添加更多的错误处理和日志记录

## 参考资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [流式输出官方指南](https://langchain-ai.github.io/langgraph/how-tos/streaming/#stream-graph-state)
- [LangChain 文档](https://python.langchain.com/)

## 问题反馈

如果您在使用过程中遇到问题，请检查：

1. 依赖包是否正确安装
2. API 密钥是否正确配置
3. 网络连接是否正常
4. Python 版本是否兼容

对于其他问题，请参考官方文档或提交 issue。
