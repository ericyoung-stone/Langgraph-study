# 测试指南

本项目采用标准的 Python 测试结构，使用 pytest 作为测试框架。

## 项目结构

```
Langgraph-study/
├── src/                          # 源代码
│   └── get_start/               # get_start 模块
│       ├── __init__.py
│       ├── react_agent_demo.py  # React Agent 演示
│       └── README.md
├── tests/                        # 测试代码
│   ├── __init__.py
│   ├── README.md                # 测试说明
│   └── get_start/               # get_start 模块测试
│       ├── __init__.py
│       └── test_react_agent_demo.py
├── run_tests.py                 # 测试运行脚本
├── pytest.ini                   # pytest 配置
├── pyproject.toml               # 项目配置（包含测试依赖）
└── TESTING.md                   # 本文件
```

## 快速开始

### 1. 安装测试依赖

```bash
# 使用 uv 安装测试依赖
uv add --dev pytest pytest-cov pytest-mock

# 或者使用 pip
pip install pytest pytest-cov pytest-mock
```

### 2. 运行测试

```bash
# 运行所有测试
python run_tests.py

# 运行特定模块测试
python run_tests.py --specific

# 使用 pytest 直接运行
pytest

# 运行特定测试文件
pytest tests/get_start/test_quick_start_react_agent_demo.py -v
```

## 测试类型

### 单元测试
- **位置**: `tests/get_start/test_react_agent_demo.py`
- **特点**: 测试单个函数，使用 mock 隔离依赖
- **运行**: `pytest tests/get_start/ -m "not integration"`

### 集成测试
- **标记**: `@pytest.mark.integration`
- **特点**: 测试组件间交互，可能需要外部依赖
- **运行**: `pytest -m integration`

### 慢速测试
- **标记**: `@pytest.mark.slow`
- **特点**: 执行时间较长的测试
- **跳过**: `pytest -m "not slow"`

## 测试覆盖率

### 生成覆盖率报告

```bash
# 基本覆盖率
pytest --cov=src tests/

# 生成 HTML 报告
pytest --cov=src --cov-report=html tests/

# 生成 XML 报告（用于 CI/CD）
pytest --cov=src --cov-report=xml tests/
```

### 覆盖率目标

- 单元测试覆盖率: > 80%
- 集成测试覆盖率: > 60%
- 总体覆盖率: > 70%

## 测试最佳实践

### 1. 测试文件组织
- 测试文件与源代码文件对应
- 测试文件以 `test_` 开头
- 测试类以 `Test` 开头
- 测试方法以 `test_` 开头

### 2. 测试方法
- 使用描述性的测试方法名
- 每个测试只测试一个功能点
- 使用 `assert` 进行断言
- 测试正常情况、异常情况和边界情况

### 3. Mock 使用
- 对于外部依赖使用 mock
- 对于 API 调用使用 mock
- 对于文件系统操作使用 mock

### 4. 测试数据
- 使用固定的测试数据
- 避免测试间的数据依赖
- 使用 `setUp` 和 `tearDown` 方法

## 示例测试

```python
import pytest
from unittest.mock import patch, MagicMock

class TestMyFunction:
    def test_basic_functionality(self):
        """测试基本功能"""
        result = my_function("input")
        assert result == "expected_output"
    
    @patch('module.external_api')
    def test_with_mock(self, mock_api):
        """测试使用 mock 的功能"""
        mock_api.return_value = "mocked_response"
        result = my_function("input")
        assert result == "expected_output"
    
    def test_error_handling(self):
        """测试错误处理"""
        with pytest.raises(ValueError):
            my_function("invalid_input")
```

## CI/CD 集成

### GitHub Actions 示例

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.13'
    - name: Install dependencies
      run: |
        pip install -e ".[test]"
    - name: Run tests
      run: |
        pytest --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## 故障排除

### 常见问题

1. **ImportError**: 确保测试文件路径正确
2. **ModuleNotFoundError**: 检查 `sys.path` 设置
3. **AssertionError**: 检查测试数据和期望结果
4. **Mock 不工作**: 确保 mock 路径正确

### 调试技巧

```bash
# 详细输出
pytest -v -s

# 只运行失败的测试
pytest --lf

# 在失败时停止
pytest -x

# 显示局部变量
pytest -l
```

## 贡献指南

1. 为新功能编写测试
2. 确保所有测试通过
3. 保持测试覆盖率
4. 遵循测试命名规范
5. 添加适当的文档字符串 