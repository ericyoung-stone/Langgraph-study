"""
交互式运行脚本：提供菜单选择运行 `context_examples.py` 中的各个示例。

特性：
- 列出所有示例并支持单个或全部运行；
- 对运行过程中的异常进行捕获并打印友好提示；
- 中文交互提示。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Callable, Dict


def _ensure_project_root_on_syspath(current_dir: Path) -> None:
    """向 sys.path 注入项目根目录，使得 `import src.*` 可用。

    通过向上查找带有 `pyproject.toml` 的目录来确定项目根。
    """
    for parent in [current_dir, *current_dir.parents]:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            if str(parent) not in sys.path:
                sys.path.insert(0, str(parent))
            return
    # 如果未找到，也尽力把两级父目录加入
    fallback = current_dir.parent.parent
    if str(fallback) not in sys.path:
        sys.path.insert(0, str(fallback))


def _load_examples_module():
    """使用文件路径方式加载同目录下的 context_examples.py，避免包名包含数字导致的导入问题。"""
    current_dir = Path(__file__).resolve().parent
    examples_path = current_dir / "context_examples.py"
    if not examples_path.exists():
        print("未找到 context_examples.py：", examples_path)
        sys.exit(1)
    _ensure_project_root_on_syspath(current_dir)
    spec = importlib.util.spec_from_file_location("context_examples", str(examples_path))
    if spec is None or spec.loader is None:
        print("无法创建导入 spec：", examples_path)
        sys.exit(1)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
    except Exception as exc:
        print("加载示例模块失败：", exc)
        sys.exit(1)
    return module


_examples_module = _load_examples_module()
list_examples = getattr(_examples_module, "list_examples", None)
if list_examples is None:
    print("示例模块缺少 list_examples 函数。")
    sys.exit(1)


def run_single(name: str, func: Callable[[], None]) -> None:
    print(f"\n=== 正在运行：{name} ===")
    try:
        func()
    except KeyboardInterrupt:
        print("[中断] 用户取消运行。")
    except Exception as exc:
        print(f"[错误] 运行示例出现异常：{exc}")
    finally:
        print(f"=== 结束：{name} ===\n")


def run_all(examples: Dict[str, Callable[[], None]]) -> None:
    for name, func in examples.items():
        run_single(name, func)


def main() -> None:
    examples = list_examples()
    idx_to_name = {i + 1: name for i, name in enumerate(examples.keys())}

    while True:
        print("\n======= LangGraph 上下文示例菜单 =======")
        for idx, name in idx_to_name.items():
            print(f"{idx}. {name}")
        print("a. 运行全部示例")
        print("q. 退出")

        choice = input("请选择要运行的示例（数字/a/q）：").strip().lower()
        if choice == "q":
            print("已退出。")
            break
        if choice == "a":
            run_all(examples)
            continue
        if choice.isdigit():
            idx = int(choice)
            if idx in idx_to_name:
                name = idx_to_name[idx]
                run_single(name, examples[name])
            else:
                print("无效的编号，请重试。")
        else:
            print("无效的选项，请输入数字、a 或 q。")


if __name__ == "__main__":
    main()


