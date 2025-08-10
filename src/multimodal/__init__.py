"""
多模态模型模块
包含多模态模型的加载和使用功能
"""

from .load_multimodal_model import (
    MultimodalModelLoader,
    demo_basic_chat,
    demo_image_chat
)

__all__ = [
    "MultimodalModelLoader",
    "demo_basic_chat", 
    "demo_image_chat"
]
