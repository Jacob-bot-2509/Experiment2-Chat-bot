import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

def chat_completion(messages, model="deepseek-chat", temperature=0.7):
    try:
        response = client.chat.completions.create(
            model="qwen2:0.5b",
            messages=messages,
            temperature=temperature,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[出错了] API调用失败: {e}"