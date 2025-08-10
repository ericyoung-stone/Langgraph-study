# LangGraph 内存功能

本目录包含 LangGraph 内存功能的完整指南和示例代码。

## 文件说明

- `memory_guide.md` - LangGraph 内存功能的详细指南，解析了官方文档的要点
- `memory_examples.py` - 包含所有内存功能示例代码的 Python 文件
- `run_examples.py` - 交互式运行脚本，提供友好的菜单界面
- `README.md` - 本文件，使用说明

## 功能概述

LangGraph 提供了两种类型的内存：

1. **短期内存** - 用于多轮对话的上下文保持
2. **长期内存** - 用于跨会话的数据存储

## 快速开始

### 方法一：交互式运行（推荐）

使用交互式运行脚本，提供友好的菜单界面：

```bash
python run_examples.py
```

这将启动一个交互式菜单，您可以：
- 选择运行特定的演示
- 运行所有演示
- 查看详细的错误信息
- 优雅地退出程序

### 方法二：直接运行示例

#### 1. 基本短期内存演示

```python
from memory_examples import MemoryExamples

examples = MemoryExamples()
examples.basic_short_term_memory_demo()
```

#### 2. 检查点管理演示

```python
examples.checkpoint_management_demo()
```

#### 3. 内存管理演示

```python
examples.memory_management_demo()
```

#### 4. 运行所有演示

```python
examples.run_all_demos()
```

## 数据库支持

### PostgreSQL

要使用 PostgreSQL 检查点器，需要安装：

```bash
pip install langgraph-checkpoint-postgres
```

### MongoDB

要使用 MongoDB 检查点器，需要安装：

```bash
pip install langgraph-checkpoint-mongodb
```

## 主要功能

### 短期内存
- 多轮对话支持
- 状态持久化
- 线程管理

### 长期内存
- 跨会话数据存储
- 语义搜索
- 用户偏好存储

### 内存管理
- 消息修剪
- 检查点管理
- 历史记录查看

## 最佳实践

1. **开发阶段**：使用 `InMemorySaver` 进行快速原型开发
2. **生产环境**：使用数据库支持的检查点器
3. **内存策略**：根据应用需求选择合适的记忆类型
4. **定期清理**：实现适当的内存清理策略

## 交互式运行脚本功能

`run_examples.py` 提供了以下功能：

### 菜单选项
1. **基本短期内存演示** - 演示基本的多轮对话功能
2. **PostgreSQL 内存演示** - 演示生产环境的数据库存储
3. **MongoDB 内存演示** - 演示文档型数据库存储
4. **检查点管理演示** - 演示检查点的创建、查看和删除
5. **内存管理演示** - 演示内存的修剪和管理
6. **异步 PostgreSQL 演示** - 演示异步数据库操作
7. **运行所有演示** - 依次运行所有演示
0. **退出** - 优雅地退出程序

### 错误处理机制
- **模型连接测试** - 启动时自动测试模型连接
- **异常捕获** - 捕获并处理各种异常
- **详细错误信息** - 可选择显示详细的错误堆栈
- **用户中断处理** - 优雅处理 Ctrl+C 中断
- **连接错误提示** - 针对数据库连接错误的友好提示

### 用户体验
- **友好的菜单界面** - 清晰的选项展示
- **输入验证** - 验证用户输入的有效性
- **确认机制** - 运行所有演示前的确认
- **继续运行选项** - 每次演示后询问是否继续
- **状态反馈** - 清晰的成功/失败状态提示

## 注意事项

- **模型配置**: 所有示例都使用本地 LM Studio 中的 `qwen3-4b` 模型
- **数据库示例**: 需要相应的数据库服务运行
- **异步功能**: 需要适当的异步环境
- **生产环境**: 需要考虑性能和存储成本
- **首次运行**: 会测试模型连接，确保 LM Studio 正在运行
- **网络连接**: 确保可以访问 `http://192.168.1.22:1234/v1`
- **检查点管理**: 使用正确的 API 方法 `get_tuple()` 和 `list_checkpoints()`

## 相关链接

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [内存功能文档](https://langchain-ai.github.io/langgraph/how-tos/memory/add-memory/)
