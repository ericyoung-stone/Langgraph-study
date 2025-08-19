"""
人在回路（Human-in-the-loop, HITL）示例集合

说明：
- 本文件根据 `overview.md` 与 `human_in_the_loop.md` 中的所有要点与示例代码改写而来。
- 每个示例封装为类方法，具备独立可运行性、中文注释与基础错误处理。
- 示例中凡涉及模型的地方，统一通过 `src.common.local_llm.get_lm_studio_llm()` 获取本地模型。
- 由于不同环境下 `langgraph`/`langchain` 版本差异较大，示例均以 try/except 包裹，
  当依赖缺失或 API 不兼容时不会抛出异常导致脚本整体终止，而是输出友好提示。
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

try:
    # LangGraph 基础能力
    from langgraph.types import interrupt, Command
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.constants import START, END
    from langgraph.graph import StateGraph
    from langgraph.prebuilt import create_react_agent
    from langgraph.prebuilt.interrupt import HumanInterruptConfig, HumanInterrupt  # type: ignore
    from langchain_core.runnables import RunnableConfig
except Exception:  # 允许在缺少依赖时降级
    interrupt = None  # type: ignore
    Command = None  # type: ignore
    InMemorySaver = None  # type: ignore
    START = object()  # type: ignore
    END = object()  # type: ignore
    StateGraph = None  # type: ignore
    create_react_agent = None  # type: ignore
    HumanInterruptConfig = dict  # type: ignore
    HumanInterrupt = dict  # type: ignore
    RunnableConfig = Dict[str, Any]  # type: ignore

try:
    # LangChain 工具
    from langchain_core.tools import tool as create_tool
    from langchain_core.tools import BaseTool
except Exception:
    create_tool = None  # type: ignore
    BaseTool = object  # type: ignore

try:
    # 本地模型
    from src.common.local_llm import get_lm_studio_llm
except Exception:  # 兼容在不同执行目录下的导入
    from common.local_llm import get_lm_studio_llm  # type: ignore


class HumanInTheLoopExamples:
    """HITL 示例集合。每个方法都是独立可执行的 demo。"""

    # =========================
    # 基础 interrupt 示例
    # =========================
    def demo_interrupt_minimal(self) -> Optional[Dict[str, Any]]:
        """最小可用 interrupt 示例。

        对应文档 "Pause using interrupt" 中的最小片段：
        - 构建一个包含单节点的图，在节点中调用 interrupt 暂停
        - 使用 Command(resume=...) 恢复
        """
        try:
            if any(x is None for x in [interrupt, Command, InMemorySaver, StateGraph]):
                print("[提示] 依赖未就绪（langgraph 相关）。跳过 demo_interrupt_minimal。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                some_text: str

            def human_node(state: State):
                value = interrupt({"text_to_revise": state["some_text"]})
                return {"some_text": value}

            # 构建图
            builder = StateGraph(State)
            builder.add_node("human_node", human_node)
            builder.add_edge(START, "human_node")
            checkpointer = InMemorySaver()
            graph = builder.compile(checkpointer=checkpointer)

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            # 首次运行，命中中断
            result = graph.invoke({"some_text": "original text"}, config=config)
            print("中断信息:", result.get("__interrupt__"))

            # 恢复
            final = graph.invoke(Command(resume="Edited text"), config=config)
            print("恢复结果:", final)
            return final
        except Exception as exc:
            print("[错误] demo_interrupt_minimal 运行失败:", exc)
            return None

    def demo_interrupt_extended(self) -> Optional[Dict[str, Any]]:
        """扩展示例：与 minimal 相同，但展示更多打印与注释。"""
        try:
            if any(x is None for x in [interrupt, Command, InMemorySaver, StateGraph]):
                print("[提示] 依赖未就绪。跳过 demo_interrupt_extended。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                some_text: str

            def human_node(state: State):
                value = interrupt({"text_to_revise": state["some_text"]})
                return {"some_text": value}

            builder = StateGraph(State)
            builder.add_node("human_node", human_node)
            builder.add_edge(START, "human_node")
            checkpointer = InMemorySaver()
            graph = builder.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": str(uuid.uuid4())}}

            result = graph.invoke({"some_text": "original text"}, config=config)
            print("中断:", result.get("__interrupt__"))

            final = graph.invoke(Command(resume="Edited text"), config=config)
            print("最终状态:", final)
            return final
        except Exception as exc:
            print("[错误] demo_interrupt_extended 运行失败:", exc)
            return None

    # =========================
    # 多中断一次恢复
    # =========================
    def demo_resume_multiple_interrupts(self) -> Optional[Dict[str, Any]]:
        """并行两个节点分别中断，使用一个 Command 一次性恢复。"""
        try:
            if any(x is None for x in [interrupt, Command, InMemorySaver, StateGraph]):
                print("[提示] 依赖未就绪。跳过 demo_resume_multiple_interrupts。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                text_1: str
                text_2: str

            def human_node_1(state: State):
                value = interrupt({"text_to_revise": state["text_1"]})
                return {"text_1": value}

            def human_node_2(state: State):
                value = interrupt({"text_to_revise": state["text_2"]})
                return {"text_2": value}

            builder = StateGraph(State)
            builder.add_node("human_node_1", human_node_1)
            builder.add_node("human_node_2", human_node_2)
            builder.add_edge(START, "human_node_1")
            builder.add_edge(START, "human_node_2")
            checkpointer = InMemorySaver()
            graph = builder.compile(checkpointer=checkpointer)

            thread_id = str(uuid.uuid4())
            config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
            result = graph.invoke({"text_1": "t1", "text_2": "t2"}, config=config)
            interrupts = result.get("__interrupt__", [])
            print("中断数量:", len(interrupts))

            # 读取 state 中的 interrupts id → resume 值映射
            state = graph.get_state(config)
            resume_map = {i.interrupt_id: f"edited for {i.value}" for i in state.interrupts}  # type: ignore
            final = graph.invoke(Command(resume=resume_map), config=config)
            print("恢复后的状态:", final)
            return final
        except Exception as exc:
            print("[错误] demo_resume_multiple_interrupts 运行失败:", exc)
            return None

    # =========================
    # 审批（Approve / Reject）
    # =========================
    def demo_approve_or_reject_minimal(self) -> Optional[Dict[str, Any]]:
        """最小审批路由示例。"""
        try:
            if any(x is None for x in [interrupt, Command, InMemorySaver, StateGraph, START, END]):
                print("[提示] 依赖未就绪。跳过 demo_approve_or_reject_minimal。")
                return None

            from typing import Literal, TypedDict

            class State(TypedDict):
                llm_output: str

            def human_approval(state: State) -> Command[Literal["some_node", "another_node"]]:  # type: ignore
                is_approved = interrupt({"question": "Is this correct?", "llm_output": state["llm_output"]})
                return Command(goto="some_node" if is_approved else "another_node")

            def some_node(state: State) -> State:
                print("走已批准路径")
                return state

            def another_node(state: State) -> State:
                print("走拒绝后的替代路径")
                return state

            builder = StateGraph(State)
            builder.add_node("human_approval", human_approval)
            builder.add_node("some_node", some_node)
            builder.add_node("another_node", another_node)
            builder.set_entry_point("human_approval")
            builder.add_edge("some_node", END)
            builder.add_edge("another_node", END)
            graph = builder.compile(checkpointer=InMemorySaver())

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = graph.invoke({"llm_output": "demo"}, config=config)
            print("中断:", result.get("__interrupt__"))

            final = graph.invoke(Command(resume=True), config=config)
            print("最终:", final)
            return final
        except Exception as exc:
            print("[错误] demo_approve_or_reject_minimal 运行失败:", exc)
            return None

    def demo_approve_or_reject_extended(self) -> Optional[Dict[str, Any]]:
        """扩展示例：批准/拒绝并带状态更新与分支。"""
        try:
            if any(x is None for x in [interrupt, Command, InMemorySaver, StateGraph, START, END]):
                print("[提示] 依赖未就绪。跳过 demo_approve_or_reject_extended。")
                return None

            from typing import Literal, TypedDict

            class State(TypedDict):
                llm_output: str
                decision: str

            def generate_llm_output(state: State) -> State:
                return {"llm_output": "This is the generated output."}

            def human_approval(state: State) -> Command[Literal["approved_path", "rejected_path"]]:  # type: ignore
                decision = interrupt({
                    "question": "Do you approve the following output?",
                    "llm_output": state["llm_output"],
                })
                if decision == "approve":
                    return Command(goto="approved_path", update={"decision": "approved"})
                else:
                    return Command(goto="rejected_path", update={"decision": "rejected"})

            def approved_node(state: State) -> State:
                print("✅ Approved path taken.")
                return state

            def rejected_node(state: State) -> State:
                print("❌ Rejected path taken.")
                return state

            builder = StateGraph(State)
            builder.add_node("generate_llm_output", generate_llm_output)
            builder.add_node("human_approval", human_approval)
            builder.add_node("approved_path", approved_node)
            builder.add_node("rejected_path", rejected_node)
            builder.set_entry_point("generate_llm_output")
            builder.add_edge("generate_llm_output", "human_approval")
            builder.add_edge("approved_path", END)
            builder.add_edge("rejected_path", END)
            graph = builder.compile(checkpointer=InMemorySaver())

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = graph.invoke({}, config=config)
            print("中断:", result.get("__interrupt__"))

            final = graph.invoke(Command(resume="approve"), config=config)
            print("最终:", final)
            return final
        except Exception as exc:
            print("[错误] demo_approve_or_reject_extended 运行失败:", exc)
            return None

    # =========================
    # 编辑状态（Edit State）
    # =========================
    def demo_edit_state_minimal(self) -> Optional[Dict[str, Any]]:
        """最小编辑状态示例。"""
        try:
            if any(x is None for x in [interrupt, Command, InMemorySaver, StateGraph]):
                print("[提示] 依赖未就绪。跳过 demo_edit_state_minimal。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                llm_generated_summary: str

            def human_editing(state: State):
                result = interrupt({
                    "task": "Review the output from the LLM and make any necessary edits.",
                    "llm_generated_summary": state["llm_generated_summary"],
                })
                return {"llm_generated_summary": result["edited_text"]}

            builder = StateGraph(State)
            builder.add_node("human_editing", human_editing)
            builder.add_edge(START, "human_editing")
            graph = builder.compile(checkpointer=InMemorySaver())

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = graph.invoke({"llm_generated_summary": "cats on the mat"}, config=config)
            print("中断:", result.get("__interrupt__"))
            final = graph.invoke(Command(resume={"edited_text": "edited"}), config=config)
            print("最终:", final)
            return final
        except Exception as exc:
            print("[错误] demo_edit_state_minimal 运行失败:", exc)
            return None

    def demo_edit_state_extended(self) -> Optional[Dict[str, Any]]:
        """扩展示例：编辑后进入下游节点使用。"""
        try:
            if any(x is None for x in [interrupt, Command, InMemorySaver, StateGraph, START, END]):
                print("[提示] 依赖未就绪。跳过 demo_edit_state_extended。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                summary: str

            def generate_summary(state: State) -> State:
                return {"summary": "The cat sat on the mat and looked at the stars."}

            def human_review_edit(state: State) -> State:
                result = interrupt({
                    "task": "Please review and edit the generated summary if necessary.",
                    "generated_summary": state["summary"],
                })
                return {"summary": result["edited_summary"]}

            def downstream_use(state: State) -> State:
                print(f"✅ Using edited summary: {state['summary']}")
                return state

            builder = StateGraph(State)
            builder.add_node("generate_summary", generate_summary)
            builder.add_node("human_review_edit", human_review_edit)
            builder.add_node("downstream_use", downstream_use)
            builder.set_entry_point("generate_summary")
            builder.add_edge("generate_summary", "human_review_edit")
            builder.add_edge("human_review_edit", "downstream_use")
            builder.add_edge("downstream_use", END)
            graph = builder.compile(checkpointer=InMemorySaver())

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = graph.invoke({}, config=config)
            print("中断:", result.get("__interrupt__"))
            final = graph.invoke(Command(resume={"edited_summary": "edited"}), config=config)
            print("最终:", final)
            return final
        except Exception as exc:
            print("[错误] demo_edit_state_extended 运行失败:", exc)
            return None

    # =========================
    # 工具调用审阅（在工具内部 interrupt）
    # =========================
    def demo_tool_call_review_direct_interrupt(self) -> Optional[None]:
        """在工具内部调用 interrupt 的审阅流程示例。

        统一替换模型来源为 get_lm_studio_llm()。
        注意：实际运行依赖 create_react_agent、langchain 等组件，若缺失将提示并跳过。
        """
        try:
            if any(x is None for x in [interrupt, InMemorySaver, create_react_agent]):
                print("[提示] 依赖未就绪（需要 langgraph.prebuilt.create_react_agent 等）。跳过该示例。")
                return None

            def book_hotel(hotel_name: str):
                response = interrupt(
                    f"Trying to call `book_hotel` with args {{'hotel_name': {hotel_name}}}. Please approve or suggest edits."
                )
                if response["type"] == "accept":
                    pass
                elif response["type"] == "edit":
                    hotel_name = response["args"]["hotel_name"]
                else:
                    raise ValueError(f"Unknown response type: {response['type']}")
                return f"Successfully booked a stay at {hotel_name}."

            checkpointer = InMemorySaver()
            model = get_lm_studio_llm()
            agent = create_react_agent(model=model, tools=[book_hotel], checkpointer=checkpointer)

            config = {"configurable": {"thread_id": "1"}}
            # 首次流式运行会在工具内部 interrupt 处暂停
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": "book a stay at McKittrick hotel"}]},
                config,
            ):
                print(chunk)

            # 使用 Command 恢复
            for chunk in agent.stream(Command(resume={"type": "accept"}), config):
                print(chunk)
            return None
        except Exception as exc:
            print("[错误] demo_tool_call_review_direct_interrupt 运行失败:", exc)
            return None

    # =========================
    # 工具调用审阅（封装器为任意工具外挂 HITL）
    # =========================
    def demo_tool_call_review_wrapper(self) -> Optional[None]:
        """使用包装器为任意工具增加人审支持，并运行代理。"""
        try:
            if any(x is None for x in [interrupt, InMemorySaver, create_react_agent]):
                print("[提示] 依赖未就绪。跳过 demo_tool_call_review_wrapper。")
                return None

            if create_tool is None:
                print("[提示] 缺少 langchain_core.tools.create_tool，跳过该示例。")
                return None

            def add_human_in_the_loop(tool, *, interrupt_config: Optional[HumanInterruptConfig] = None):
                if create_tool is None:
                    raise RuntimeError("工具封装需要 langchain_core 工具装饰器")

                if interrupt_config is None:
                    interrupt_config = {"allow_accept": True, "allow_edit": True, "allow_respond": True}

                # 统一转换为 BaseTool
                base_tool = tool if isinstance(tool, BaseTool) else create_tool(tool)

                @create_tool(base_tool.name, description=base_tool.description, args_schema=base_tool.args_schema)
                def call_tool_with_interrupt(config: RunnableConfig, **tool_input):  # type: ignore
                    request: HumanInterrupt = {
                        "action_request": {"action": base_tool.name, "args": tool_input},
                        "config": interrupt_config,  # type: ignore
                        "description": "Please review the tool call",
                    }
                    response = interrupt([request])[0]
                    if response["type"] == "accept":
                        tool_response = base_tool.invoke(tool_input, config)
                    elif response["type"] == "edit":
                        tool_input = response["args"]["args"]
                        tool_response = base_tool.invoke(tool_input, config)
                    elif response["type"] == "response":
                        tool_response = response["args"]
                    else:
                        raise ValueError(f"Unsupported interrupt response type: {response['type']}")
                    return tool_response

                return call_tool_with_interrupt

            def book_hotel(hotel_name: str):
                return f"Successfully booked a stay at {hotel_name}."

            checkpointer = InMemorySaver()
            model = get_lm_studio_llm()
            agent = create_react_agent(
                model=model,
                tools=[add_human_in_the_loop(book_hotel)],
                checkpointer=checkpointer,
            )

            config = {"configurable": {"thread_id": "1"}}
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": "book a stay at McKittrick hotel"}]},
                config,
            ):
                print(chunk)

            for chunk in agent.stream(Command(resume=[{"type": "accept"}]), config):
                print(chunk)
            return None
        except Exception as exc:
            print("[错误] demo_tool_call_review_wrapper 运行失败:", exc)
            return None

    # =========================
    # 校验人类输入（多次 interrupt 循环）
    # =========================
    def demo_validate_input_minimal(self) -> Optional[Dict[str, Any]]:
        """最小的输入校验循环示例。"""
        try:
            if any(x is None for x in [interrupt, InMemorySaver, StateGraph]):
                print("[提示] 依赖未就绪。跳过 demo_validate_input_minimal。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                age: int

            def human_node(state: State):
                question = "What is your age?"
                while True:
                    answer = interrupt(question)
                    if not isinstance(answer, int) or answer < 0:
                        question = f"'{answer} is not a valid age. What is your age?"
                        continue
                    break
                print(f"The human in the loop is {answer} years old.")
                return {"age": answer}

            builder = StateGraph(State)
            builder.add_node("human_node", human_node)
            builder.add_edge(START, "human_node")
            graph = builder.compile(checkpointer=InMemorySaver())

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = graph.invoke({}, config=config)
            print("中断:", result.get("__interrupt__"))
            # 模拟恢复三次（两次无效输入，再一次有效）
            result = graph.invoke(Command(resume="not a number"), config=config)
            print("二次中断:", result.get("__interrupt__"))
            result = graph.invoke(Command(resume="-10"), config=config)
            print("三次中断:", result.get("__interrupt__"))
            final = graph.invoke(Command(resume=25), config=config)
            print("最终:", final)
            return final
        except Exception as exc:
            print("[错误] demo_validate_input_minimal 运行失败:", exc)
            return None

    def demo_validate_input_extended(self) -> Optional[Dict[str, Any]]:
        """扩展的输入校验示例（更贴近文档的完整代码）。"""
        try:
            if any(x is None for x in [interrupt, Command, InMemorySaver, StateGraph, START, END]):
                print("[提示] 依赖未就绪。跳过 demo_validate_input_extended。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                age: int

            def get_valid_age(state: State) -> State:
                prompt = "Please enter your age (must be a non-negative integer)."
                while True:
                    user_input = interrupt(prompt)
                    try:
                        age = int(str(user_input))
                        if age < 0:
                            raise ValueError("Age must be non-negative.")
                        break
                    except (ValueError, TypeError):
                        prompt = f"'{user_input}' is not valid. Please enter a non-negative integer for age."
                return {"age": age}

            def report_age(state: State) -> State:
                print(f"✅ Human is {state['age']} years old.")
                return state

            builder = StateGraph(State)
            builder.add_node("get_valid_age", get_valid_age)
            builder.add_node("report_age", report_age)
            builder.set_entry_point("get_valid_age")
            builder.add_edge("get_valid_age", "report_age")
            builder.add_edge("report_age", END)
            graph = builder.compile(checkpointer=InMemorySaver())

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = graph.invoke({}, config=config)
            print(result.get("__interrupt__"))
            result = graph.invoke(Command(resume="not a number"), config=config)
            print(result.get("__interrupt__"))
            result = graph.invoke(Command(resume="-10"), config=config)
            print(result.get("__interrupt__"))
            final = graph.invoke(Command(resume="25"), config=config)
            print(final)
            return final
        except Exception as exc:
            print("[错误] demo_validate_input_extended 运行失败:", exc)
            return None

    # =========================
    # 静态中断（断点调试）
    # =========================
    def demo_static_interrupt_compile_time(self) -> Optional[None]:
        """在编译期设置 interrupt_before/after。"""
        try:
            if any(x is None for x in [InMemorySaver, StateGraph, START, END]):
                print("[提示] 依赖未就绪。跳过 demo_static_interrupt_compile_time。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                input: str

            def step_1(state):
                print("---Step 1---")
                return state

            def step_2(state):
                print("---Step 2---")
                return state

            def step_3(state):
                print("---Step 3---")
                return state

            builder = StateGraph(State)
            builder.add_node("step_1", step_1)
            builder.add_node("step_2", step_2)
            builder.add_node("step_3", step_3)
            builder.add_edge(START, "step_1")
            builder.add_edge("step_1", "step_2")
            builder.add_edge("step_2", "step_3")
            builder.add_edge("step_3", END)

            checkpointer = InMemorySaver()
            graph = builder.compile(checkpointer=checkpointer, interrupt_before=["step_3"])  # type: ignore

            config = {"configurable": {"thread_id": "some_thread"}}
            graph.invoke({"input": "hello"}, config=config)
            # 继续执行到下一个断点
            graph.invoke(None, config=config)
            return None
        except Exception as exc:
            print("[错误] demo_static_interrupt_compile_time 运行失败:", exc)
            return None

    def demo_static_interrupt_runtime(self) -> Optional[None]:
        """在运行期设置 interrupt_before/after（注：子图不支持运行时设置）。"""
        try:
            if any(x is None for x in [InMemorySaver, StateGraph, START, END]):
                print("[提示] 依赖未就绪。跳过 demo_static_interrupt_runtime。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                input: str

            def step_1(state):
                print("---Step 1---")
                return state

            def step_2(state):
                print("---Step 2---")
                return state

            builder = StateGraph(State)
            builder.add_node("step_1", step_1)
            builder.add_node("step_2", step_2)
            builder.add_edge(START, "step_1")
            builder.add_edge("step_1", "step_2")
            builder.add_edge("step_2", END)

            graph = builder.compile(checkpointer=InMemorySaver())
            config = {"configurable": {"thread_id": "some_thread"}}

            # 运行时传入断点配置（部分版本可能不支持此参数签名，已 try/except）
            try:
                graph.invoke(
                    {"input": "hello"},
                    interrupt_before=["step_1"],  # type: ignore
                    interrupt_after=["step_2"],  # type: ignore
                    config=config,
                )
            except TypeError:
                print("[提示] 当前版本不支持在 invoke 时传入 interrupt_* 参数，演示到此为止。")
            return None
        except Exception as exc:
            print("[错误] demo_static_interrupt_runtime 运行失败:", exc)
            return None

    # =========================
    # 副作用放置位置的考虑
    # =========================
    def demo_side_effects_after_interrupt(self) -> Optional[Dict[str, Any]]:
        """在 interrupt 之后执行有副作用的调用，避免重复恢复时重复触发。"""
        try:
            if any(x is None for x in [interrupt, InMemorySaver, StateGraph]):
                print("[提示] 依赖未就绪。跳过 demo_side_effects_after_interrupt。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                answer: str

            def api_call(ans: str):
                print(f"[API 调用] 使用参数: {ans}")
                return {"ok": True}

            def human_node(state: State):
                answer = interrupt("what is your name?")
                api_call(str(answer))  # interrupt 之后再调用
                return {"answer": str(answer)}

            builder = StateGraph(State)
            builder.add_node("human_node", human_node)
            builder.add_edge(START, "human_node")
            graph = builder.compile(checkpointer=InMemorySaver())

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = graph.invoke({}, config=config)
            print("中断:", result.get("__interrupt__"))
            final = graph.invoke(Command(resume="Alice"), config=config)
            print("最终:", final)
            return final
        except Exception as exc:
            print("[错误] demo_side_effects_after_interrupt 运行失败:", exc)
            return None

    def demo_side_effects_separate_node(self) -> Optional[Dict[str, Any]]:
        """将副作用操作拆分到单独节点，避免恢复时重复副作用。"""
        try:
            if any(x is None for x in [interrupt, InMemorySaver, StateGraph, START, END]):
                print("[提示] 依赖未就绪。跳过 demo_side_effects_separate_node。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                answer: str

            def human_node(state: State):
                answer = interrupt("what is your name?")
                return {"answer": str(answer)}

            def api_call_node(state: State):
                print(f"[API 调用] 使用参数: {state['answer']}")
                return state

            builder = StateGraph(State)
            builder.add_node("human_node", human_node)
            builder.add_node("api_call_node", api_call_node)
            builder.add_edge(START, "human_node")
            builder.add_edge("human_node", "api_call_node")
            builder.add_edge("api_call_node", END)
            graph = builder.compile(checkpointer=InMemorySaver())

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            result = graph.invoke({}, config=config)
            print("中断:", result.get("__interrupt__"))
            final = graph.invoke(Command(resume="Bob"), config=config)
            print("最终:", final)
            return final
        except Exception as exc:
            print("[错误] demo_side_effects_separate_node 运行失败:", exc)
            return None

    # =========================
    # 子图与父图的恢复语义
    # =========================
    def demo_parent_subgraph_interrupt(self) -> Optional[Dict[str, Any]]:
        """展示父图节点调用子图，子图内 interrupt 时的恢复行为。"""
        try:
            if any(x is None for x in [interrupt, Command, InMemorySaver, StateGraph, START]):
                print("[提示] 依赖未就绪。跳过 demo_parent_subgraph_interrupt。")
                return None

            from typing import TypedDict

            class State(TypedDict):
                state_counter: int

            counter_node_in_subgraph = {"count": 0}
            counter_human_node = {"count": 0}
            counter_parent_node = {"count": 0}

            def node_in_subgraph(state: State):
                counter_node_in_subgraph["count"] += 1
                print(f"Entered `node_in_subgraph` a total of {counter_node_in_subgraph['count']} times")
                return state

            def human_node(state: State):
                counter_human_node["count"] += 1
                print(f"Entered human_node in sub-graph a total of {counter_human_node['count']} times")
                answer = interrupt("what is your name?")
                print(f"Got an answer of {answer}")
                return state

            checkpointer = InMemorySaver()

            sub_builder = StateGraph(State)
            sub_builder.add_node("some_node", node_in_subgraph)
            sub_builder.add_node("human_node", human_node)
            sub_builder.add_edge(START, "some_node")
            sub_builder.add_edge("some_node", "human_node")
            subgraph = sub_builder.compile(checkpointer=checkpointer)

            def parent_node(state: State):
                counter_parent_node["count"] += 1
                print(f"Entered `parent_node` a total of {counter_parent_node['count']} times")
                subgraph_state = subgraph.invoke(state)
                return subgraph_state

            builder = StateGraph(State)
            builder.add_node("parent_node", parent_node)
            builder.add_edge(START, "parent_node")
            graph = builder.compile(checkpointer=checkpointer)

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            for chunk in graph.stream({"state_counter": 1}, config):  # type: ignore
                print(chunk)

            print('--- Resuming ---')
            for chunk in graph.stream(Command(resume="Alice"), config):  # type: ignore
                print(chunk)
            return {"ok": True}
        except Exception as exc:
            print("[错误] demo_parent_subgraph_interrupt 运行失败:", exc)
            return None

    # =========================
    # 多次 interrupt 同节点的注意事项（演示潜在非确定行为）
    # =========================
    def demo_multiple_interrupts_in_one_node_caution(self) -> Optional[Dict[str, Any]]:
        """演示在同一节点里多次 interrupt 可能导致的索引错配问题（尽量避免）。"""
        try:
            if any(x is None for x in [interrupt, InMemorySaver, StateGraph, START]):
                print("[提示] 依赖未就绪。跳过 demo_multiple_interrupts_in_one_node_caution。")
                return None

            from typing import TypedDict, Optional as TOptional

            class State(TypedDict):
                age: TOptional[str]
                name: TOptional[str]

            def human_node(state: State):
                if not state.get('name'):
                    name = interrupt("what is your name?")
                else:
                    name = "N/A"

                if not state.get('age'):
                    age = interrupt("what is your age?")
                else:
                    age = "N/A"

                print(f"Name: {name}. Age: {age}")
                return {"age": age, "name": name}

            builder = StateGraph(State)
            builder.add_node("human_node", human_node)
            builder.add_edge(START, "human_node")
            graph = builder.compile(checkpointer=InMemorySaver())

            config = {"configurable": {"thread_id": str(uuid.uuid4())}}
            for chunk in graph.stream({"age": None, "name": None}, config):  # type: ignore
                print(chunk)

            for chunk in graph.stream(Command(resume="John", update={"name": "foo"}), config):  # type: ignore
                print(chunk)
            return {"ok": True}
        except Exception as exc:
            print("[错误] demo_multiple_interrupts_in_one_node_caution 运行失败:", exc)
            return None


if __name__ == "__main__":
    # 简单自测入口：运行部分示例（建议用 run_examples.py 交互式运行）
    demos = HumanInTheLoopExamples()
    demos.demo_interrupt_minimal()

