import io
import os
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


def set_env_if_undefined(env_key: str, env_val=None):
    if not os.environ.get(env_key):
        print(f"{env_key} is not defined, use provide {env_val}")
        os.environ[env_key] = env_val

def print_agent_invoke_result(result):
    print("📊 代理响应:")
    try:
        messages = result["messages"]
        if len(messages) > 0:
            for message in messages:
                print(message)
    except Exception as e:
        print(f"<UNK>: {e}")
        print(result)


def display_graph_nodes(graph, img_path: str | Path | None = None) -> None:
    try:
        # 1. 获取graph png data
        png_data = graph.get_graph().draw_mermaid_png()

        # 2. 调用保存方法
        display_and_save_mermaid_png(
            png_data=png_data,
            save_path=img_path,
            fig_size=(8, 6),
            transparent=True,  # 透明背景
            dpi=600,
            show=True,
        )
    except Exception as e:
        # This requires some extra dependencies and is optional
        print(f"graph not display, err: {e}")


def display_and_save_mermaid_png(
        png_data: bytes,
        fig_size: tuple = (10, 8),  # 默认尺寸(宽,高)英寸
        save_path: str = None,  # 保存路径（含扩展名）
        dpi: int = 600,  # 分辨率
        show: bool = True,  # 是否显示图像
        **save_kwargs  # 其他保存参数
) -> None:
    """
    显示并保存Mermaid生成的PNG图像

    :param png_data: Mermaid生成的PNG二进制数据
    :param fig_size: 显示尺寸元组(宽度,高度)英寸，默认(10,8)
    :param save_path: 保存路径（如'/data/output.png'），不传则不保存
    :param dpi: 保存分辨率（默认600）
    :param show: 是否显示图像（默认True）
    :param save_kwargs: 其他plt.savefig参数（如bbox_inches='tight'）
    """
    # 1. 转换二进制数据为图像数组
    img = mpimg.imread(io.BytesIO(png_data))
    height, width = img.shape[0], img.shape[1]

    # 2. 动态计算显示尺寸（若未指定）
    if fig_size is None:
        fig_size = (width / 100, height / 100)  # 按像素比例计算[4](@ref)

    # 3. 创建图像窗口
    plt.figure(figsize=fig_size)
    plt.imshow(img)
    plt.axis('off')  # 隐藏坐标轴

    # 4. 保存图像（如果指定路径）
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # 创建目录[8](@ref)
        plt.savefig(
            save_path,
            dpi=dpi,
            bbox_inches='tight',  # 自动裁剪白边
            pad_inches=0.1,  # 保留0.1英寸内边距
            **save_kwargs
        )
        print(f"✅ 图像已保存至: {os.path.abspath(save_path)}")

    # 5. 显示图像
    if show:
        plt.show()

    # 6. 关闭图像释放内存
    plt.close()