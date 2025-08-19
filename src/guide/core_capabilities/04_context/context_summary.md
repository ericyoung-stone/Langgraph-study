# LangGraph 上下文（Context）要点总结

来源参考：`https://langchain-ai.github.io/langgraph/agents/context/`

## 核心概念

- **Context Engineering**：为 AI 应用动态提供“合适的信息和工具”以完成任务的工程实践。
- **两大维度**：
  - **可变性（Mutability）**：
    - 静态上下文（Static）：运行期间不变，如用户元数据、数据库连接、工具集合。
    - 动态上下文（Dynamic）：在一次运行中会变化，如对话历史、中间结果、工具输出等。
  - **生命周期（Lifetime）**：
    - 运行时（Runtime）：仅作用于单次调用/运行。
    - 跨会话（Cross-conversation）：跨多次会话持久存在。

## LangGraph 提供的三类上下文

| 类型 | 描述 | 可变性 | 生命周期 | 访问方式 |
| --- | --- | --- | --- | --- |
| 静态运行时上下文（Static runtime context） | 启动时传入的用户元数据、工具、连接等 | 静态 | 单次运行 | `invoke`/`stream` 的 `context` 参数 |
| 动态运行时上下文（State） | 一次运行中可变的状态（对话、工具结果等） | 动态 | 单次运行 | LangGraph State 对象 |
| 动态跨会话上下文（Store） | 多次会话共享的持久数据（偏好、资料等） | 动态 | 跨会话 | LangGraph Store |

提示：运行时上下文（Runtime context）不同于 LLM 的上下文窗口。运行时上下文是代码执行需要的本地依赖/数据；可以用它来决定放入 LLM 提示词的数据，从而优化上下文窗口的使用。

## 关键变更（v0.6）

- 使用 `context=` 参数传入运行时上下文（替代旧的 `config['configurable']`）。

## 示例要点总览

### 1. 静态运行时上下文（Static runtime context）

- 在 Agent 提示词中访问：通过 `get_runtime(ContextSchema)` 获取运行时，再从 `runtime.context` 读取静态数据（如 `user_name`）。
- 在工作流节点中访问：在节点签名中接收 `config: Runtime[ContextSchema]`，从 `config.context` 中读取。
- 在工具中访问：在 `@tool` 方法内使用 `get_runtime(ContextSchema)` 读取 `runtime.context`。

### 2. 动态运行时上下文（State）

- 在 Agent 中使用：扩展 `AgentState`（或 `MessagesState`）定义自定义状态结构，把动态信息（如 `user_name`）放入 state；在 `prompt(state)` 中读取。
- 在工作流中使用：自定义 `TypedDict` 状态结构；节点函数返回“状态更新字典”以请求状态合并更新。

提示：如需将状态跨会话持久化，请结合内存功能（参见 Memory 指南）。

### 3. 动态跨会话上下文（Store）

- 用于跨会话的长期记忆（用户档案、偏好、历史事实等）。
- 可在运行时对象中获取 Store 并进行读写，用于长期语境注入。

## 与示例代码实现的映射

- 静态运行时上下文
  - Agent 提示词示例 → `example_static_runtime_context_agent_prompt()`
  - 工作流节点示例 → `example_static_runtime_context_workflow_node()`
  - 工具中访问示例 → `example_static_runtime_context_in_tool()`
- 动态运行时上下文（State）
  - Agent 中示例 → `example_dynamic_runtime_context_in_agent()`
  - 工作流中示例 → `example_dynamic_runtime_context_in_workflow()`
- 动态跨会话上下文（Store）
  - 文档未提供直接代码片段，本仓库示例提供运行时可探测的占位演示。


