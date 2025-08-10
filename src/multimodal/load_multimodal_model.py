"""
多模态模型加载器
支持根据curl命令封装请求方法，并处理图片路径转base64编码
"""

import base64
import json
import os
from typing import Dict, List

import requests

from src.get_start import get_start_dir


class MultimodalModelLoader:
    """多模态模型加载器类"""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        """
        初始化多模态模型加载器
        
        Args:
            base_url (str): API基础URL，默认为本地LM Studio服务
        """
        self.base_url = base_url.rstrip('/')
        self.chat_endpoint = f"{self.base_url}/chat/completions"
    
    def image_to_base64(self, image_path: str) -> str:
        """
        将图片文件转换为base64编码
        
        Args:
            image_path (str): 图片文件路径
            
        Returns:
            str: base64编码的图片数据
            
        Raises:
            FileNotFoundError: 当图片文件不存在时
            Exception: 其他读取错误
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"图片文件不存在: {image_path}")
            
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                return base64_data
                
        except Exception as e:
            raise Exception(f"转换图片为base64时出错: {e}")
    
    def create_image_message(self, image_path: str, text: str = "") -> Dict:
        """
        创建包含图片的消息格式
        
        Args:
            image_path (str): 图片文件路径
            text (str): 可选的文本内容
            
        Returns:
            Dict: 包含图片的消息字典
        """
        base64_image = self.image_to_base64(image_path)
        
        message = {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
        
        return message
    
    def chat_completion(
        self,
        messages: List[Dict],
        model: str = "google/gemma-3n-e4b",
        temperature: float = 0.7,
        max_tokens: int = -1,
        stream: bool = False
    ) -> Dict:
        """
        发送聊天完成请求
        
        Args:
            messages (List[Dict]): 消息列表
            model (str): 模型名称
            temperature (float): 温度参数
            max_tokens (int): 最大token数，-1表示无限制
            stream (bool): 是否流式响应
            
        Returns:
            Dict: API响应结果
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                self.chat_endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {e}")
    
    def chat_with_image(
        self,
        image_path: str,
        text: str = "",
        system_prompt: str = "You are a helpful assistant.",
        model: str = "google/gemma-3n-e4b",
        temperature: float = 0.7,
        max_tokens: int = -1,
        stream: bool = False
    ) -> Dict:
        """
        发送包含图片的聊天请求
        
        Args:
            image_path (str): 图片文件路径
            text (str): 用户文本消息
            system_prompt (str): 系统提示
            model (str): 模型名称
            temperature (float): 温度参数
            max_tokens (int): 最大token数
            stream (bool): 是否流式响应
            
        Returns:
            Dict: API响应结果
        """
        # 创建消息列表
        messages = []
        
        # 添加系统消息
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # 添加包含图片的用户消息
        image_message = self.create_image_message(image_path, text)
        messages.append(image_message)
        
        # 发送请求
        return self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
    
    def simple_chat(
        self,
        user_message: str,
        system_prompt: str = "You are a helpful assistant.",
        model: str = "google/gemma-3n-e4b",
        temperature: float = 0.7,
        max_tokens: int = -1,
        stream: bool = False
    ) -> Dict:
        """
        简单的文本聊天请求
        
        Args:
            user_message (str): 用户消息
            system_prompt (str): 系统提示
            model (str): 模型名称
            temperature (float): 温度参数
            max_tokens (int): 最大token数
            stream (bool): 是否流式响应
            
        Returns:
            Dict: API响应结果
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )


def demo_basic_chat():
    """演示基础聊天功能"""
    print("🚀 演示基础聊天功能")
    print("=" * 50)
    
    loader = MultimodalModelLoader()
    
    try:
        # 使用原始curl命令的参数
        result = loader.simple_chat(
            user_message="What day is it today?",
            system_prompt="Always answer in rhymes. Today is Thursday",
            model="google/gemma-3n-e4b",
            temperature=0.7,
            max_tokens=-1,
            stream=False
        )
        
        print("📊 API响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 提取回复内容
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print(f"\n💬 模型回复: {content}")
        
        return result
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


def demo_image_chat(image_path: str):
    """演示图片聊天功能"""
    print(f"\n🚀 演示图片聊天功能")
    print("=" * 50)
    print(f"📷 图片路径: {image_path}")
    
    loader = MultimodalModelLoader()
    
    try:
        result = loader.chat_with_image(
            image_path=image_path,
            text="请描述这张图片的内容",
            system_prompt="You are a helpful assistant that can analyze images.",
            model="google/gemma-3n-e4b",
            temperature=0.7,
            max_tokens=-1,
            stream=False
        )
        
        print("📊 API响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("="* 50)
        # 提取回复内容
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print(f"\n💬 模型回复: {content}")
        
        return result
        
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None


if __name__ == "__main__":
    # 演示基础聊天功能
    # demo_basic_chat()
    
    # 演示图片聊天功能（需要提供图片路径）
    demo_image_chat(get_start_dir + "/graph_img/human_graph.png")
