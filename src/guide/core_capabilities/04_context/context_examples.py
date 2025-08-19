"""
基于 `context.md` 的上下文管理示例集合。

约定：
- 所有示例均为可独立调用的函数，并包含中文注释与基础错误处理。
- 如示例中需要模型，统一使用 `src.common.local_llm.get_lm_studio_llm()` 获取。
  - 需确保本机/局域网有可用的 LM Studio/OpenAI 兼容服务，或根据需要修改 base_url。
- 工具函数尽量采用本地可运行的逻辑，避免外部依赖。

注意：
- 文档中提到的部分 API 在 LangGraph 版本上可能存在差异；示例里通过 try/except 做了兼容性保护，
  当所需 API 不可用时会给出友好提示而不中断整个脚本运行。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from typing_extensions import TypedDict

try:
    # LangGraph 相关导入（不同版本 API 可能有差异）
    from langgraph.prebuilt import create_react_agent
    from langgraph.prebuilt.chat_agent_executor import AgentState
    from langgraph.graph import StateGraph
    from langgraph.runtime import get_runtime
    from langgraph.runtime import Runtime as LGRuntime  # 用于类型标注
except Exception as e:  # noqa: F841 - 记录但不抛出，示例中会动态检查
    create_react_agent = None  # type: ignore
    AgentState = object  # type: ignore
    StateGraph = None  # type: ignore
    get_runtime = None  # type: ignore
    LGRuntime = object  # type: ignore

try:
    # LangChain 工具装饰器
    from langchain_core.tools import tool
except Exception:
    tool = None  # type: ignore

try:
    # 消息类型
    from langchain_core.messages import AnyMessage
except Exception:
    AnyMessage = Any  # type: ignore

try:
    # 本地模型获取函数
    from src.common.local_llm import get_lm_studio_llm
except Exception:  # 允许相对路径失败时使用 fallback 导入
    from common.local_llm import get_lm_studio_llm  # type: ignore


# ========== 通用工具 ========== #

if tool is not None:

    @tool
    def get_weather(city: str) -> str:
        """演示用工具：返回本地虚构的天气信息，避免外部依赖。"""
        fake_db = {
            "san francisco": "晴，21℃",
            "beijing": "多云，26℃",
            "shanghai": "小雨，24℃",
        }
        city_key = city.strip().lower()
        return fake_db.get(city_key, f"{city} 天气数据暂不可用（示例数据）")

else:

    def get_weather(city: str) -> str:  # type: ignore
        """当未安装 langchain_core 时的降级工具。"""
        return "无法使用工具（缺少 langchain_core）。"


# ========== 1) 静态运行时上下文：Agent 提示词中访问 ========== #
def example_static_runtime_context_agent_prompt() -> None:
    """示例：在 Agent 的提示词中访问静态运行时上下文。

    对应文档：Static runtime context → Agent prompt 示例。
    关键点：通过 get_runtime(ContextSchema) 读取 runtime.context.user_name。
    """

    if create_react_agent is None or get_runtime is None:
        print("[跳过] 缺少 LangGraph 相关 API，无法运行该示例。")
        return

    @dataclass
    class ContextSchema:
        user_name: str

    # 自定义提示词函数：从运行时上下文读取 user_name
    def prompt(state: AgentState) -> List[AnyMessage]:  # type: ignore[valid-type]
        try:
            runtime = get_runtime(ContextSchema)  # type: ignore
            system_msg = f"You are a helpful assistant. Address the user as {runtime.context.user_name}."
        except Exception as exc:
            print(f"[错误] 无法获取运行时上下文: {exc}")
            system_msg = "You are a helpful assistant. (runtime context not available)"
        # 这里直接将系统消息与输入消息合并
        try:
            messages = state["messages"]  # type: ignore[index]
        except Exception:
            messages = []
        return [{"role": "system", "content": system_msg}] + list(messages)

    try:
        model = get_lm_studio_llm()
        agent = create_react_agent(
            model=model,
            tools=[get_weather],
            prompt=prompt,
            context_schema=ContextSchema,  # 允许在调用时传入 context
        )
        result = agent.invoke(
            input={"messages": [{"role": "user", "content": "what is the weather in San Francisco?"}]},
            context={"user_name": "John Smith"},  # 静态运行时上下文
        )
        print("[输出]", result)
    except Exception as exc:
        print(f"[错误] 运行示例失败: {exc}")


# ========== 2) 静态运行时上下文：工作流节点中访问 ========== #
def example_static_runtime_context_workflow_node() -> None:
    """示例：在工作流节点中访问静态运行时上下文。

    对应文档：Static runtime context → Workflow node 示例。
    关键点：节点签名可接受 config: Runtime[ContextSchema]，从 config.context 读取数据。
    """

    if StateGraph is None or get_runtime is None:
        print("[跳过] 缺少 LangGraph 相关 API，无法运行该示例。")
        return

    @dataclass
    class ContextSchema:
        user_name: str

    class SimpleState(TypedDict):
        messages: List[AnyMessage]

    # 兼容性更强：仅接收 state，在函数内通过 get_runtime 获取运行时
    def node(state: SimpleState) -> Dict[str, Any]:  # type: ignore[valid-type]
        try:
            runtime = get_runtime(ContextSchema)  # type: ignore
            user_name = runtime.context.user_name  # type: ignore[attr-defined]
            print(f"[节点] 读取到用户: {user_name}")
        except Exception as exc:
            print(f"[节点] 无法读取运行时上下文: {exc}")
        # 本节点不更新状态
        return {}

    try:
        builder = StateGraph(SimpleState)
        builder.add_node("node", node)
        builder.set_entry_point("node")
        graph = builder.compile()

        result = graph.invoke(
            {"messages": [{"role": "user", "content": "hi"}]},
            context={"user_name": "Alice"},
        )
        print("[输出]", result)
    except Exception as exc:
        print(f"[错误] 运行示例失败: {exc}")


# ========== 3) 静态运行时上下文：在工具中访问 ========== #
def example_static_runtime_context_in_tool() -> None:
    """示例：在工具函数中访问静态运行时上下文以读取用户信息。

    对应文档：Static runtime context → In a tool 示例。
    关键点：工具内部使用 get_runtime(ContextSchema) 读取 runtime.context。
    """

    if create_react_agent is None or get_runtime is None:
        print("[跳过] 缺少 LangGraph 相关 API，无法运行该示例。")
        return

    @dataclass
    class ContextSchema:
        user_name: str

    # 这里定义一个工具，它会从运行时上下文读取 user_name，并返回一个假的邮箱
    if tool is not None:
        @tool
        def get_user_email() -> str:
            """根据运行时上下文中的 user_name 返回演示邮箱地址。"""
            try:
                runtime = get_runtime(ContextSchema)  # type: ignore
                email = f"{runtime.context.user_name.replace(' ','.').lower()}@example.com"
                return email
            except Exception as exc:
                return f"无法获取用户邮箱（运行时上下文不可用）：{exc}"
        tools = [get_user_email]
    else:
        def get_user_email() -> str:  # type: ignore
            return "无法使用工具（缺少 langchain_core）。"

        tools = [get_user_email]

    def prompt(state: AgentState) -> List[AnyMessage]:  # type: ignore[valid-type]
        return [{"role": "system", "content": "你是一个可以查询用户邮箱的助手。"}] + list(state.get("messages", []))  # type: ignore[attr-defined]

    try:
        model = get_lm_studio_llm()
        agent = create_react_agent(
            model=model,
            tools=tools,
            prompt=prompt,
            context_schema=ContextSchema,
        )
        result = agent.invoke(
            {"messages": [{"role": "user", "content": "请查询我的邮箱"}]},
            context={"user_name": "John Smith"},
        )
        print("[输出]", result)
    except Exception as exc:
        print(f"[错误] 运行示例失败: {exc}")


# ========== 4) 动态运行时上下文（State）：Agent 中使用 ========== #
def example_dynamic_runtime_context_in_agent() -> None:
    """示例：在 Agent 中使用自定义 State 以携带动态数据（如 user_name）。

    对应文档：Dynamic runtime context（state）→ In an agent 示例。
    关键点：扩展 AgentState，定义自有字段，并在 prompt(state) 中读取。
    """

    if create_react_agent is None:
        print("[跳过] 缺少 LangGraph 相关 API，无法运行该示例。")
        return

    class CustomState(AgentState):  # type: ignore[misc, valid-type]
        user_name: str

    def prompt(state: CustomState) -> List[AnyMessage]:  # type: ignore[valid-type]
        user_name = state.get("user_name", "用户")  # type: ignore[attr-defined]
        system_msg = f"You are a helpful assistant. User's name is {user_name}"
        return [{"role": "system", "content": system_msg}] + list(state.get("messages", []))  # type: ignore[attr-defined]

    try:
        model = get_lm_studio_llm()
        agent = create_react_agent(
            model=model,
            tools=[get_weather],
            state_schema=CustomState,
            prompt=prompt,
        )
        result = agent.invoke({
            "messages": [{"role": "user", "content": "hi!"}],
            "user_name": "John Smith",
        })
        print("[输出]", result)
    except Exception as exc:
        print(f"[错误] 运行示例失败: {exc}")


# ========== 5) 动态运行时上下文（State）：工作流中使用 ========== #
def example_dynamic_runtime_context_in_workflow() -> None:
    """示例：在工作流中使用自定义 TypedDict 状态，并通过节点返回“增量更新”。

    对应文档：Dynamic runtime context（state）→ In a workflow 示例。
    关键点：节点返回的 dict 表示对 State 的更新请求。
    """

    if StateGraph is None:
        print("[跳过] 缺少 LangGraph 相关 API，无法运行该示例。")
        return

    class CustomState(TypedDict):
        messages: List[AnyMessage]
        extra_field: int

    def node(state: CustomState) -> Dict[str, Any]:
        # 读取现有状态并做简单更新
        extra_field_value = int(state.get("extra_field", 0))
        return {"extra_field": extra_field_value + 1}

    try:
        builder = StateGraph(CustomState)
        builder.add_node("node", node)
        builder.set_entry_point("node")
        graph = builder.compile()

        result = graph.invoke({
            "messages": [{"role": "user", "content": "hello"}],
            "extra_field": 1,
        })
        print("[输出]", result)
    except Exception as exc:
        print(f"[错误] 运行示例失败: {exc}")


# ========== 6) 动态跨会话上下文（Store）：占位演示 ========== #


def example_dynamic_cross_conversation_context_store() -> None:
    """示例：演示如何探测/访问运行时的持久化 Store（若已在应用中配置）。

    文档强调 Store 用于跨会话的长期记忆。此处不强依赖具体后端，仅做探测与演示写入/读取流程。
    实际生产中应配置具体的 Store（如 SQLite/PG/自定义）并在运行中启用。
    """

    if get_runtime is None:
        print("[跳过] 缺少运行时 API，无法演示 Store。")
        return

    @dataclass
    class ContextSchema:
        user_name: str

    try:
        runtime = get_runtime(ContextSchema)  # type: ignore
    except Exception as exc:
        print(f"[错误] 无法获取运行时以访问 Store：{exc}")
        return

    store = getattr(runtime, "store", None)
    if store is None:
        print("[信息] 当前未启用持久化 Store。可参考 Memory 指南进行配置后再试。")
        return

    try:
        # 以下仅为伪代码/演示流程，具体 API 以实际 Store 对象为准
        # 例如：store.put(namespace, key, value) / store.get(namespace, key)
        namespace = "user_profile"
        key = "preferred_name"
        value = getattr(runtime.context, "user_name", "User")  # type: ignore[attr-defined]

        # 伪接口调用（不同 Store 实现接口不同，这里仅演示异常保护）
        if hasattr(store, "put"):
            store.put(namespace, key, value)  # type: ignore[attr-defined]
        print("[Store] 已尝试写入用户偏好名称。")

        fetched = None
        if hasattr(store, "get"):
            fetched = store.get(namespace, key)  # type: ignore[attr-defined]
        print("[Store] 读取结果：", fetched)
    except Exception as exc:
        print(f"[错误] 访问 Store 失败（根据实际 Store 实现调整示例）：{exc}")


# ========== 工具：列出可运行的示例函数 ========== #
def list_examples() -> Dict[str, Any]:
    """返回示例名称到可调用对象的映射。"""
    return {
        "静态上下文-在Agent提示词中访问": example_static_runtime_context_agent_prompt,
        "静态上下文-在工作流节点中访问": example_static_runtime_context_workflow_node,
        "静态上下文-在工具中访问": example_static_runtime_context_in_tool,
        "动态上下文State-在Agent中使用": example_dynamic_runtime_context_in_agent,
        "动态上下文State-在工作流中使用": example_dynamic_runtime_context_in_workflow,
        "动态跨会话上下文Store-占位演示": example_dynamic_cross_conversation_context_store,
    }


__all__ = [
    "example_static_runtime_context_agent_prompt",
    "example_static_runtime_context_workflow_node",
    "example_static_runtime_context_in_tool",
    "example_dynamic_runtime_context_in_agent",
    "example_dynamic_runtime_context_in_workflow",
    "example_dynamic_cross_conversation_context_store",
    "list_examples",
]


