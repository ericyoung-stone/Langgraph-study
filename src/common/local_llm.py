from langchain_openai import ChatOpenAI
from pydantic import SecretStr


def get_lm_studio_llm(base_url: str="http://192.168.1.22:1234/v1", model_name: str= "qwen3-4b") -> ChatOpenAI:
    return ChatOpenAI(
        timeout=60,
        base_url=base_url,
        model=model_name,
        api_key=SecretStr("lm_studio"),
        max_retries=3,
        max_tokens=8064,
        temperature=0.7,
    )