import re

def calculate(expression: str) -> str:
    """安全的计算器工具，仅支持数字、运算符和括号。返回计算结果字符串。"""
    # 安全检查：只允许数字、空格、+-*/().
    if not re.match(r'^[\\\\d\\\\s\\\\+\\\\-\\\\*\\\\/\\\\(\\\\)\\\\.]+$', expression):
        return "[错误] 表达式包含非法字符，仅支持基础数学运算。"
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"[计算出错] {e}"

# 工具描述，供大模型判断
TOOLS_DESC = """
你是一个智能助手，可以调用一个计算器工具。当用户的问题涉及数学计算时，请输出特殊格式：
<<TOOL_CALL>>表达式
例如：用户问“123*456等于多少”，你应该回复：
<<TOOL_CALL>>123*456
然后系统会执行计算并返回结果给你，你再根据结果回答用户。如果不需要工具，直接正常回答即可。
"""
