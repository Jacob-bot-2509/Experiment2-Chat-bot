import json
from src.llm_client import chat_completion

def count_tokens(text):
    """简单用字符长度除以4估算token数"""
    return len(text) // 4

class ContextStack:
    def __init__(self, max_tokens=2048, recent_rounds=5):
        self.max_tokens = max_tokens
        self.recent_rounds = recent_rounds
        self.system_prompt = ""      # 角色设定和规则
        self.long_term_memory = ""   # 压缩后的早期对话摘要
        self.working_memory = []     # 最近的消息列表（[{role, content}]）

    def import_history(self, json_path):
        """导入JSON历史消息记录"""
        with open(json_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
        # 假设JSON格式为 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, ...]
        for msg in history:
            if msg['role'] == 'system':
                self.system_prompt = msg['content']
            else:
                self.working_memory.append(msg)
        # 初始压缩
        self._compress_if_needed()

    def add_message(self, role, content):
        self.working_memory.append({"role": role, "content": content})
        self._compress_if_needed()

    def _compress_if_needed(self):
        """如果工作记忆token数超过阈值，将旧消息压缩到长时记忆"""
        tokens = sum(count_tokens(m['content']) for m in self.working_memory)
        if tokens > self.max_tokens:
            keep_n = self.recent_rounds * 2  # 每轮user+assistant共2条
            to_compress = self.working_memory[:-keep_n]
            self.working_memory = self.working_memory[-keep_n:]
            if to_compress:
                conversation_text = "\\\\\\\\n".join([f"{m['role']}: {m['content']}" for m in to_compress])
                summary_prompt = f"请用一段简短的中文总结以下对话的核心内容，保留关键事件和决定：\\\\\\\\n{conversation_text}"
                try:
                    summary = chat_completion([{"role": "user", "content": summary_prompt}], model="qwen2:1.5b")
                except:
                    summary = "（早期对话摘要生成失败）"
                self.long_term_memory = summary

    def get_full_context(self):
        """构建最终发送给模型的消息列表"""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if self.long_term_memory:
            messages.append({"role": "system", "content": f"[早期对话摘要] {self.long_term_memory}"})
        messages.extend(self.working_memory)
        return messages