"""
LangGraph 内存功能示例代码

本文件包含 LangGraph 内存功能的完整示例，涵盖：
1. 短期内存基本使用
2. 生产环境配置
3. 检查点管理
4. 内存管理功能
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, MessagesState, START

from src.common.local_llm import get_lm_studio_llm


class MemoryExamples:
    """LangGraph 内存功能示例类"""
    
    def __init__(self):
        """初始化示例类"""
        self.model = get_lm_studio_llm()
        
    def basic_short_term_memory_demo(self):
        """
        演示基本的短期内存功能
        使用 InMemorySaver 实现多轮对话
        """
        print("=== 基本短期内存演示 ===")
        
        # 创建检查点器
        checkpointer = InMemorySaver()
        
        # 定义模型调用函数
        def call_model(state: MessagesState):
            response = self.model.invoke(state["messages"])
            return {"messages": response}
        
        # 构建状态图
        builder = StateGraph(MessagesState)
        builder.add_node("call_model", call_model)
        builder.add_edge(START, "call_model")
        graph = builder.compile(checkpointer=checkpointer)
        
        # 配置
        config = {"configurable": {"thread_id": "demo_thread_1"}}
        
        # 第一轮对话
        print("第一轮对话:")
        result1 = graph.invoke(
            {"messages": [{"role": "user", "content": "你好！我是张三"}]},
            config
        )
        print(f"AI回复: {result1['messages'][-1].content}")
        
        # 第二轮对话（保持上下文）
        print("\n第二轮对话:")
        result2 = graph.invoke(
            {"messages": [{"role": "user", "content": "我的名字是什么？"}]},
            config
        )
        print(f"AI回复: {result2['messages'][-1].content}")
        
        return result1, result2
    
    def postgres_memory_demo(self):
        """
        演示使用 PostgreSQL 的生产环境内存配置
        注意：需要先设置 PostgreSQL 数据库
        """
        print("=== PostgreSQL 内存演示 ===")
        print("注意：此示例需要 PostgreSQL 数据库支持")
        
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            
            # PostgreSQL 连接配置
            DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
            
            with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
                # 首次使用需要设置
                # checkpointer.setup()
                
                def call_model(state: MessagesState):
                    response = self.model.invoke(state["messages"])
                    return {"messages": response}
                
                builder = StateGraph(MessagesState)
                builder.add_node("call_model", call_model)
                builder.add_edge(START, "call_model")
                graph = builder.compile(checkpointer=checkpointer)
                
                config = {"configurable": {"thread_id": "postgres_demo"}}
                
                # 流式处理示例
                print("流式对话演示:")
                for chunk in graph.stream(
                    {"messages": [{"role": "user", "content": "你好！"}]},
                    config,
                    stream_mode="values"
                ):
                    if chunk["messages"]:
                        print(f"流式回复: {chunk['messages'][-1].content}")
                        
        except ImportError:
            print("PostgreSQL 支持未安装，请运行: pip install langgraph-checkpoint-postgres")
        except Exception as e:
            print(f"PostgreSQL 连接失败: {e}")
            print("请确保 PostgreSQL 数据库已启动并配置正确")
    
    async def async_postgres_memory_demo(self):
        """
        演示异步 PostgreSQL 内存配置
        """
        print("=== 异步 PostgreSQL 内存演示 ===")
        
        try:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            
            DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
            
            async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:
                # await checkpointer.setup()
                
                async def call_model(state: MessagesState):
                    response = await self.model.ainvoke(state["messages"])
                    return {"messages": response}
                
                builder = StateGraph(MessagesState)
                builder.add_node("call_model", call_model)
                builder.add_edge(START, "call_model")
                graph = builder.compile(checkpointer=checkpointer)
                
                config = {"configurable": {"thread_id": "async_postgres_demo"}}
                
                print("异步流式对话演示:")
                async for chunk in graph.astream(
                    {"messages": [{"role": "user", "content": "异步你好！"}]},
                    config,
                    stream_mode="values"
                ):
                    if chunk["messages"]:
                        print(f"异步流式回复: {chunk['messages'][-1].content}")
                        
        except ImportError:
            print("异步 PostgreSQL 支持未安装，请运行: pip install langgraph-checkpoint-postgres")
        except Exception as e:
            print(f"异步 PostgreSQL 连接失败: {e}")
    
    def mongodb_memory_demo(self):
        """
        演示使用 MongoDB 的内存配置
        """
        print("=== MongoDB 内存演示 ===")
        print("注意：此示例需要 MongoDB 数据库支持")
        
        try:
            from langgraph.checkpoint.mongodb import MongoDBSaver
            
            # MongoDB 连接配置
            connection_string = "mongodb://localhost:27017"
            db_name = "langgraph_memory"
            collection_name = "checkpoints"
            
            with MongoDBSaver.from_conn_string(
                connection_string, 
                db_name, 
                collection_name
            ) as checkpointer:
                def call_model(state: MessagesState):
                    response = self.model.invoke(state["messages"])
                    return {"messages": response}
                
                builder = StateGraph(MessagesState)
                builder.add_node("call_model", call_model)
                builder.add_edge(START, "call_model")
                graph = builder.compile(checkpointer=checkpointer)
                
                config = {"configurable": {"thread_id": "mongodb_demo"}}
                
                result = graph.invoke(
                    {"messages": [{"role": "user", "content": "MongoDB 测试消息"}]},
                    config
                )
                print(f"MongoDB 回复: {result['messages'][-1].content}")
                
        except ImportError:
            print("MongoDB 支持未安装，请运行: pip install langgraph-checkpoint-mongodb")
        except Exception as e:
            print(f"MongoDB 连接失败: {e}")
            print("请确保 MongoDB 数据库已启动并配置正确")
    
    def checkpoint_management_demo(self):
        """
        演示检查点管理功能
        """
        print("=== 检查点管理演示 ===")
        
        checkpointer = InMemorySaver()
        
        def call_model(state: MessagesState):
            response = self.model.invoke(state["messages"])
            return {"messages": response}
        
        builder = StateGraph(MessagesState)
        builder.add_node("call_model", call_model)
        builder.add_edge(START, "call_model")
        graph = builder.compile(checkpointer=checkpointer)
        
        thread_id = "checkpoint_demo"
        config = {"configurable": {"thread_id": thread_id}}
        
        # 创建一些对话历史
        for i in range(3):
            result = graph.invoke(
                {"messages": [{"role": "user", "content": f"这是第 {i+1} 条消息"}]},
                config
            )
            print(f"消息 {i+1}: {result['messages'][-1].content}")
        
        # 查看线程状态
        print("\n=== 查看线程状态 ===")
        config = {"configurable": {"thread_id": thread_id}}
        try:
            checkpoint_tuple = checkpointer.get_tuple(config)
            if checkpoint_tuple:
                print(f"线程 {thread_id} 的当前状态:")
                print(f"检查点 ID: {checkpoint_tuple.checkpoint['id']}")
                print(f"时间戳: {checkpoint_tuple.checkpoint['ts']}")
                print(f"消息数量: {len(checkpoint_tuple.checkpoint['channel_values']['messages'])}")
            else:
                print(f"线程 {thread_id} 没有找到检查点")
        except Exception as e:
            print(f"获取线程状态失败: {e}")
            checkpoint_tuple = None
        
        # 查看线程历史
        print("\n=== 查看线程历史 ===")
        try:
            history = checkpointer.list(config)
            print(f"线程 {thread_id} 的检查点历史:")
            for checkpoint_tuple in history:
                print(f"  - 检查点 ID: {checkpoint_tuple.checkpoint['id']}")
                print(f"    时间戳: {checkpoint_tuple.checkpoint['ts']}")
                if checkpoint_tuple.checkpoint['channel_values'].get("__start__"):
                    print(f"    __start__消息数量: {len(checkpoint_tuple.checkpoint['channel_values']['__start__'])}")
                elif checkpoint_tuple.checkpoint['channel_values'].get("messages"):
                    print(f"    messages消息数量: {len(checkpoint_tuple.checkpoint['channel_values']['messages'])}")
        except Exception as e:
            print(f"获取线程历史失败: {e}")
            history = []
        
        # 删除线程（清理）
        print("\n=== 删除线程 ===")
        checkpointer.delete_thread(thread_id)
        print(f"线程 {thread_id} 已删除")
        
        return checkpoint_tuple, history
    
    def memory_management_demo(self):
        """
        演示内存管理功能
        """
        print("=== 内存管理演示 ===")
        
        checkpointer = InMemorySaver()
        
        def call_model(state: MessagesState):
            response = self.model.invoke(state["messages"])
            return {"messages": response}
        
        builder = StateGraph(MessagesState)
        builder.add_node("call_model", call_model)
        builder.add_edge(START, "call_model")
        graph = builder.compile(checkpointer=checkpointer)
        
        thread_id = "memory_management_demo"
        config = {"configurable": {"thread_id": thread_id}}
        
        # 创建长对话历史
        print("创建长对话历史...")
        for i in range(5):
            result = graph.invoke(
                {"messages": [{"role": "user", "content": f"这是第 {i+1} 轮对话"}]},
                config
            )
            print(f"第 {i+1} 轮: {result['messages'][-1].content}")
        
        # 查看当前状态
        config = {"configurable": {"thread_id": thread_id}}
        try:
            checkpoint_tuple = checkpointer.get_tuple(config)
            if checkpoint_tuple:
                messages = checkpoint_tuple.checkpoint['channel_values']['messages']
                print(f"\n当前消息数量: {len(messages)}")
                
                # 模拟消息修剪（保留最后3条）
                if len(messages) > 6:  # 3轮对话 = 6条消息
                    trimmed_messages = messages[-6:]
                    print(f"修剪后消息数量: {len(trimmed_messages)}")
                    print("修剪功能演示完成")
        except Exception as e:
            print(f"获取当前状态失败: {e}")
        
        # 清理
        checkpointer.delete_thread(thread_id)
        print("内存管理演示完成")
    
    def run_all_demos(self):
        """
        运行所有演示
        """
        print("开始运行 LangGraph 内存功能演示...\n")
        
        # 1. 基本短期内存演示
        self.basic_short_term_memory_demo()
        print("\n" + "="*50 + "\n")
        
        # 2. PostgreSQL 演示（需要数据库）
        self.postgres_memory_demo()
        print("\n" + "="*50 + "\n")
        
        # 3. MongoDB 演示（需要数据库）
        self.mongodb_memory_demo()
        print("\n" + "="*50 + "\n")
        
        # 4. 检查点管理演示
        self.checkpoint_management_demo()
        print("\n" + "="*50 + "\n")
        
        # 5. 内存管理演示
        self.memory_management_demo()
        print("\n" + "="*50 + "\n")
        
        print("所有演示完成！")


async def run_async_demos():
    """
    运行异步演示
    """
    examples = MemoryExamples()
    await examples.async_postgres_memory_demo()


def main():
    """
    主函数 - 运行所有演示
    """
    examples = MemoryExamples()
    examples.run_all_demos()


if __name__ == "__main__":
    # 运行同步演示
    main()
    
    # 运行异步演示（可选）
    # asyncio.run(run_async_demos())
