"""
交互式运行 HITL 示例脚本

功能：
- 展示菜单，允许选择运行特定示例或全部示例
- 每个示例独立运行并打印结果/错误
- 中文提示与基础错误处理
"""

from __future__ import annotations

import sys
from typing import Callable, List, Tuple

try:
    from .human_in_the_loop_examples import HumanInTheLoopExamples
except Exception:  # 兼容直接以 python 运行此脚本
    from human_in_the_loop_examples import HumanInTheLoopExamples  # type: ignore


def get_menu() -> List[Tuple[str, Callable[[], None]]]:
    demos = HumanInTheLoopExamples()

    items: List[Tuple[str, Callable[[], None]]] = [
        ("最小 interrupt 示例", lambda: demos.demo_interrupt_minimal()),
        ("扩展 interrupt 示例", lambda: demos.demo_interrupt_extended()),
        ("并行多中断一次恢复", lambda: demos.demo_resume_multiple_interrupts()),
        ("审批路由（最小示例）", lambda: demos.demo_approve_or_reject_minimal()),
        ("审批路由（扩展示例）", lambda: demos.demo_approve_or_reject_extended()),
        ("编辑状态（最小示例）", lambda: demos.demo_edit_state_minimal()),
        ("编辑状态（扩展示例）", lambda: demos.demo_edit_state_extended()),
        ("工具审阅：工具内 interrupt", lambda: demos.demo_tool_call_review_direct_interrupt()),
        ("工具審閱：封装器外挂 HITL", lambda: demos.demo_tool_call_review_wrapper()),
        ("校验输入（最小示例）", lambda: demos.demo_validate_input_minimal()),
        ("校验输入（扩展示例）", lambda: demos.demo_validate_input_extended()),
        ("静态中断（编译期）", lambda: demos.demo_static_interrupt_compile_time()),
        ("静态中断（运行期）", lambda: demos.demo_static_interrupt_runtime()),
        ("副作用放置：interrupt 之后", lambda: demos.demo_side_effects_after_interrupt()),
        ("副作用放置：拆分到独立节点", lambda: demos.demo_side_effects_separate_node()),
        ("子图与父图：子图中断恢复", lambda: demos.demo_parent_subgraph_interrupt()),
        ("同节点多中断的注意事项", lambda: demos.demo_multiple_interrupts_in_one_node_caution()),
    ]
    return items


def run_one(index: int) -> None:
    items = get_menu()
    if index < 1 or index > len(items):
        print("[错误] 无效的编号。")
        return
    title, fn = items[index - 1]
    print(f"\n=== 运行：{index}. {title} ===")
    try:
        fn()
    except KeyboardInterrupt:
        print("\n[中止] 用户取消运行。")
    except Exception as exc:
        print(f"[错误] 运行示例失败：{exc}")


def run_all() -> None:
    items = get_menu()
    for idx, (title, fn) in enumerate(items, start=1):
        print(f"\n=== 运行：{idx}. {title} ===")
        try:
            fn()
        except KeyboardInterrupt:
            print("\n[中止] 用户取消运行。")
            break
        except Exception as exc:
            print(f"[错误] 示例 {idx} 运行失败：{exc}")


def main() -> None:
    items = get_menu()
    while True:
        print("\n====== 人在回路（HITL）示例菜单 ======")
        for i, (title, _) in enumerate(items, start=1):
            print(f"{i}. {title}")
        print("A. 运行全部示例")
        print("Q. 退出")

        choice = input("\n请输入选项（数字/A/Q）：").strip().lower()
        if choice == "q":
            print("再见！")
            return
        if choice == "a":
            run_all()
            continue
        if choice.isdigit():
            run_one(int(choice))
            continue
        print("[提示] 无效的输入，请重试。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已退出。")
        sys.exit(0)

