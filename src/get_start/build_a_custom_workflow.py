"""
LangGraph 自定义工作流教程

本文件封装了 LangGraph 基础教程系列的全部关键步骤，适合自定义和扩展。
每个步骤均有独立函数和详细注释，遵循标准 Python 开发规范。
"""
import json
import os
from typing import Annotated, Any, Dict

from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt
from typing_extensions import TypedDict

from src.common.local_llm import get_lm_studio_llm
from src.common.utils import set_env_if_undefined
from src.get_start import get_start_dir


# 1. 定义基础 State
class ChatState(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

# 2. 构建基础聊天机器人
def build_basic_chatbot(llm) -> Any:
    """
    步骤1：构建基础聊天机器人
    """
    graph_builder = StateGraph(ChatState)

    def chatbot_node(state: ChatState):
        return {"messages": [llm.invoke(state["messages"])]}

    graph_builder.add_node("chatbot", chatbot_node)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile()


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        return {"messages": outputs}

# 3. 集成工具（如 Web 搜索 + 自定义BasicToolNode）
def build_tool_chatbot(llm) -> Any:
    """
    步骤2：集成工具
    """
    graph_builder = StateGraph(ChatState)
    tool = TavilySearch(max_results=2)
    tools = [tool]
    llm_with_tools = llm.bind_tools(tools)

    def chatbot_node(state: ChatState):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    def route_tools(
            state: ChatState,
    ):
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get("messages", []):
            ai_message = messages[-1]
        else:
            raise ValueError(f"No messages found in input state to tool_edge: {state}")
        if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
            return "tools"
        return END

    graph_builder.add_node("chatbot", chatbot_node)
    # tool_node = ToolNode(tools=tools) # (1)内置ToolNode
    tool_node = BasicToolNode(tools=tools) # (2)自定义BasicToolNode
    graph_builder.add_node("tools", tool_node)
    # graph_builder.add_conditional_edges("chatbot", tools_condition)  # (1)配套内置ToolNode
    # (2)配套自定义BasicToolNode,定义条件边:如果聊天机器人请求使用工具，`tools_condition` 函数返回 "tools"；如果可以直接回复，则返回 "END"。这种条件路由定义了主智能体循环。
    graph_builder.add_conditional_edges(
        "chatbot",
        route_tools,
        # 以下字典可让您告知图将条件的输出解释为特定节点, 它默认为恒等函数，但如果您想使用除“tools”之外的其他名称的节点，
        # 您可以将字典的值更新为其他内容,例如，"tools": "my_tools"(字典的value是真实要执行的node)
        {"tools": "tools", END: END},
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile()

# 4. 添加记忆能力(使用内置的ToolNode)
def build_memory_chatbot(llm) -> Any:
    """
    步骤3：添加记忆能力
    """
    graph_builder = StateGraph(ChatState)
    tool = TavilySearch(max_results=2)
    tools = [tool]
    llm_with_tools = llm.bind_tools(tools)

    def chatbot_node(state: ChatState):
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    graph_builder.add_node("chatbot", chatbot_node)
    tool_node = ToolNode(tools=tools) # (1)内置ToolNode
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("chatbot", tools_condition)  # (1) 配套内置ToolNode, 条件返回的为"tools"或"__end__"节点
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.set_entry_point("chatbot") # 设置流程入口为 "chatbot" 节点，即对话从 AI 处理消息开始。等价于下方两行代码
    # graph_builder.add_edge(START, "chatbot")
    # graph_builder.add_edge("chatbot", END)
    memory = MemorySaver()
    return graph_builder.compile(checkpointer=memory)

# 5. 引入人类参与
def build_human_in_loop_chatbot(llm) -> Any:
    """
    步骤4：引入人类参与
    """
    graph_builder = StateGraph(ChatState)
    tool1 = TavilySearch(max_results=2)

    @tool
    def human_assistance(query: str) -> str:
        """请求人工协助"""
        human_response = interrupt({"query": query})
        return human_response["data"]

    tools = [tool1, human_assistance]
    llm_with_tools = llm.bind_tools(tools)
    
    def chatbot_node(state: ChatState):
        message = llm_with_tools.invoke(state["messages"])
        # 因为我们将在工具执行期间进行中断操作，所以我们禁用并行工具调用，以避免在恢复时重复任何工具调用。
        assert len(message.tool_calls) <= 1
        return {"messages": [message]}

    graph_builder.add_node("chatbot", chatbot_node)
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    memory = MemorySaver()
    return graph_builder.compile(checkpointer=memory)

# 6. 自定义状态结构
def build_custom_state_chatbot(llm) -> Any:
    """
    步骤5：自定义状态
    """
    class CustomState(TypedDict):
        messages: Annotated[list, add_messages]
        name: str
        birthday: str

    graph_builder = StateGraph(CustomState)
    tool1 = TavilySearch(max_results=2)

    # 请注意，由于我们正在为状态更新生成一条工具消息（ToolMessage），所以我们通常需要相应工具调用的ID。
    # 我们可以使用LangChain的InjectedToolCallId来表明，在工具的模式中，这个参数不应该向模型透露。
    @tool
    def human_assistance(
        name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> str | Command:
        """请求人工协助"""
        human_response = interrupt({
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        })
        # 如果信息正确，按原样更新状态。
        if human_response.get("correct", "").lower().startswith("y"):
            verified_name = name
            verified_birthday = birthday
            response = "Correct"
        # 否则，从人工审核人员处获取信息。
        else:
            verified_name = human_response.get("name", name)
            verified_birthday = human_response.get("birthday", birthday)
            response = f"Made a correction: {human_response}"
        # 这次我们在工具内部使用ToolMessage显式更新状态。
        state_update = {
            "name": verified_name,
            "birthday": verified_birthday,
            "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
        }
        # 我们在工具中返回一个Command对象来更新我们的状态。
        return Command(update=state_update)

    tools = [tool1, human_assistance]
    llm_with_tools = llm.bind_tools(tools)

    def chatbot_node(state: CustomState):
        message = llm_with_tools.invoke(state["messages"])
        assert len(message.tool_calls) <= 1
        return {"messages": [message]}

    graph_builder.add_node("chatbot", chatbot_node)
    tool_node = ToolNode(tools=tools)
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    memory = MemorySaver()
    return graph_builder.compile(checkpointer=memory)

# 7. 时光回溯能力
def get_state_history(graph, config: Dict) -> Any:
    """
    步骤6：时光回溯
    获取某一会话的所有历史状态快照
    """
    return graph.get_state_history(config)

# 8. 演示主入口
def run_all_demos():
    """
    依次演示所有步骤
    """
    set_env_if_undefined("TAVILY_API_KEY", "your-api-key")
    llm = get_lm_studio_llm()
    img_dir = os.path.join(get_start_dir, "graph_img")
    print("\n===== 步骤1：基础聊天机器人 =====")
    # basic_graph = build_basic_chatbot(llm)
    # display_graph_nodes(basic_graph, img_path=os.path.join(img_dir, "basic_graph.png"))
    # result1 = basic_graph.invoke({"messages": [{"role": "user", "content": "你好！"}]})
    # print_agent_invoke_result(result1)

    print("\n===== 步骤2：集成工具 =====")
    # tool_graph = build_tool_chatbot(llm)
    # display_graph_nodes(tool_graph, img_path=os.path.join(img_dir, "tool_graph.png"))
    # result2 = tool_graph.invoke({"messages": [{"role": "user", "content": "LangGraph 是什么？"}]})
    # print_agent_invoke_result(result2)

    print("\n===== 步骤3.1：添加记忆能力 =====")
    # memory_graph = build_memory_chatbot(llm)
    # display_graph_nodes(memory_graph, img_path=os.path.join(img_dir, "memory_graph.png"))
    # config = {"configurable": {"thread_id": "1"}}
    # result3a = memory_graph.invoke({"messages": [{"role": "user", "content": "我叫小明。"}]}, config)
    # result3b = memory_graph.invoke({"messages": [{"role": "user", "content": "你还记得我是谁吗？"}]}, config)
    # print_agent_invoke_result(result3a)
    # print_agent_invoke_result(result3b)

    print("\n===== 步骤3.2：添加记忆能力(stream) =====")
    # config = {"configurable": {"thread_id": "2"}}
    # # The config is the **second positional argument** to stream() or invoke()!
    # events1 = memory_graph.stream({"messages": [{"role": "user", "content": "Hi there! My name is Will."}]}, config, stream_mode="values")
    # for event in events1:
    #     event["messages"][-1].pretty_print()
    # events2 = memory_graph.stream({"messages": [{"role": "user", "content": "Remember my name?"}]}, config, stream_mode="values")
    # for event in events2:
    #     event["messages"][-1].pretty_print()
    # snapshot = memory_graph.get_state(config)
    # print("snapshot:", snapshot) # 空()
    # print("snapshot.next:", snapshot.next)

    print("\n===== 步骤4：引入人类参与 =====")
    # 需人工交互环境下演示
    # human_graph = build_human_in_loop_chatbot(llm)
    # display_graph_nodes(human_graph, img_path=os.path.join(img_dir, "human_graph.png"))
    # user_input = "I need some expert guidance for building an AI agent. Could you request assistance for me?"
    # config = {"configurable": {"thread_id": "1"}}
    # events1 = human_graph.stream({"messages": [{"role": "user", "content": user_input}]}, config, stream_mode="values")
    # for event in events1:
    #     event["messages"][-1].pretty_print()
    # snapshot = human_graph.get_state(config)
    # # print("snapshot:", snapshot)
    # print("snapshot.next:", snapshot.next) # (tools,)
    # # 人工介入+恢复
    # human_response = (
    #     "We, the experts are here to help! We'd recommend you check out LangGraph to build your agent."
    #     " It's much more reliable and extensible than simple autonomous agents."
    # )
    # human_command = Command(resume={"data": human_response})
    # events2 = human_graph.stream(human_command, config, stream_mode="values")
    # for event in events2:
    #     if "messages" in event:
    #         event["messages"][-1].pretty_print()

    print("\n===== 步骤5：自定义状态 =====")
    # custom_graph = build_custom_state_chatbot(llm)
    # display_graph_nodes(custom_graph, img_path=os.path.join(img_dir, "custom_graph.png"))
    # user_input = (
    #     "Can you look up when LangGraph was released? "
    #     "When you have the answer, use the human_assistance tool for review."
    # )
    # config = {"configurable": {"thread_id": "1"}}
    # # 触发human_assistance 工具中的中断
    # events = custom_graph.stream({"messages": [{"role": "user", "content": user_input}]}, config, stream_mode="values")
    # for event in events:
    #     if "messages" in event:
    #         event["messages"][-1].pretty_print()
    #
    # # 添加人工协助
    # human_command = Command(
    #     resume={
    #         "name": "LangGraph",
    #         "birthday": "Jan 17, 2024",
    #     },
    # )
    # events = custom_graph.stream(human_command, config, stream_mode="values")
    # for event in events:
    #     if "messages" in event:
    #         event["messages"][-1].pretty_print()
    # snapshot = custom_graph.get_state(config)
    # print("snapshot:", snapshot)
    # m = {k: v for k, v in snapshot.values.items() if k in ("name", "birthday")}
    # print("m:", m)
    # # 手动更新状态(可选), 但是通常建议使用中断功能，因为它允许数据在人在环交互中传输，而与状态更新无关。
    # custom_graph.update_state(config, {"name": "LangGraph (library)"})
    # snapshot2 = custom_graph.get_state(config)
    # print("snapshot2:", snapshot2)
    # m2 = {k: v for k, v in snapshot.values.items() if k in ("name", "birthday")}
    # print("m2:", m2)

    print("\n===== 步骤6：时光回溯 =====")
    # 1)构建图
    memory_graph = build_memory_chatbot(llm)
    # 2.1)添加对话
    config = {"configurable": {"thread_id": "1"}}
    events = memory_graph.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "I'm learning LangGraph. "
                        "Could you do some research on it for me?"
                    ),
                },
            ],
        },
        config,
        stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    # 2.2)添加对话
    events = memory_graph.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Ya that's helpful. Maybe I'll "
                        "build an autonomous agent with it!"
                    ),
                },
            ],
        },
        config,
        stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
    # 3)回放完整的状态历史记录
    history = get_state_history(memory_graph, config)
    to_replay = None
    for state in history:
        print("Num Messages: ", len(state.values["messages"]), "Next: ", state.next)
        print("-" * 80)
        if len(state.values["messages"]) == 6:
            # We are somewhat arbitrarily selecting a specific state based on the number of chat messages in the state.
            to_replay = state
    # 从检查点恢复
    print(to_replay.next)
    print(to_replay.config)

    # 4)从某个时刻(to_replay)加载状态
    # 检查点的 to_replay.config 包含一个 checkpoint_id 时间戳。提供这个 checkpoint_id 值告诉 LangGraph 的检查指针加载从那个时刻开始的状态。
    for event in memory_graph.stream(None, to_replay.config, stream_mode="values"):
        if "messages" in event:
            event["messages"][-1].pretty_print()

if __name__ == "__main__":
    # 需根据实际环境初始化 LLM
    # from langchain.chat_models import init_chat_model
    # import os
    # os.environ["OPENAI_API_KEY"] = "your-openai-key"
    # llm = init_chat_model("openai:gpt-4.1")
    run_all_demos()
