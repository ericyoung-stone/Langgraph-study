# 测试目录

这个目录包含了项目的所有测试文件，按照标准的 Python 项目结构组织。

## 目录结构

```
tests/
├── __init__.py                    # 测试模块初始化
├── README.md                      # 本文件
└── get_start/                     # get_start 模块的测试
    ├── __init__.py               # 子模块初始化
    └── test_react_agent_demo.py  # React Agent 演示测试
```

## 测试文件命名规范

- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头
- 测试方法以 `test_` 开头

## 运行测试

### 方法一：使用 pytest 直接运行

```bash
# 运行所有测试
pytest

# 运行特定模块的测试
pytest tests/get_start/

# 运行特定测试文件
pytest tests/get_start/test_react_agent_demo.py

# 运行特定测试方法
pytest tests/get_start/test_react_agent_demo.py::TestGetWeather::test_get_weather_basic
```

### 方法二：使用项目提供的测试脚本

```bash
# 运行所有测试
python run_tests.py

# 只运行 React Agent 测试
python run_tests.py --specific
```

### 方法三：使用 Python 模块方式

```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/get_start/test_react_agent_demo.py -v
```

## 测试类型

### 单元测试 (Unit Tests)
- 测试单个函数或方法的功能
- 使用 mock 对象隔离依赖
- 快速执行，不依赖外部服务

### 集成测试 (Integration Tests)
- 测试多个组件之间的交互
- 可能需要外部依赖（如 API 密钥）
- 标记为 `@pytest.mark.integration`

### 慢速测试 (Slow Tests)
- 执行时间较长的测试
- 标记为 `@pytest.mark.slow`
- 可以使用 `-m "not slow"` 跳过

## 测试覆盖率

运行测试覆盖率检查：

```bash
pytest --cov=src tests/
```

生成覆盖率报告：

```bash
pytest --cov=src --cov-report=html tests/
```

## 测试最佳实践

1. **测试隔离**：每个测试应该独立运行，不依赖其他测试的状态
2. **使用 Mock**：对于外部依赖（如 API 调用），使用 mock 对象
3. **测试边界条件**：包括正常情况、异常情况和边界情况
4. **描述性命名**：测试方法名应该清楚地描述测试的内容
5. **断言明确**：每个测试应该有一个明确的断言

## 添加新测试

1. 在相应的测试目录中创建新的测试文件
2. 文件名以 `test_` 开头
3. 测试类继承自 `unittest.TestCase` 或使用 pytest 风格
4. 测试方法以 `test_` 开头
5. 添加适当的文档字符串

## 示例

```python
import pytest
from unittest.mock import patch

class TestMyFunction:
    def test_my_function_basic(self):
        """测试基本功能"""
        result = my_function("test")
        assert result == "expected_result"
    
    @patch('module.external_dependency')
    def test_my_function_with_mock(self, mock_dependency):
        """测试使用 mock 的功能"""
        mock_dependency.return_value = "mocked_value"
        result = my_function("test")
        assert result == "expected_result"
``` 