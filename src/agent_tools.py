import re
from datetime import datetime
import json

def calculate(expression: str) -> str:
    """安全计算器"""
    if not re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expression):
        return "[错误] 表达式包含非法字符"
    try:
        return str(eval(expression))
    except Exception as e:
        return f"[计算出错] {e}"

def get_current_time() -> str:
    """获取当前真实时间"""
    now = datetime.now()
    weekdays = ['一', '二', '三', '四', '五', '六', '日']
    return f"现在是{now.year}年{now.month}月{now.day}日，{now.hour}时{now.minute}分{now.second}秒，星期{weekdays[now.weekday()]}。"

def get_date() -> str:
    """获取当前日期"""
    now = datetime.now()
    return f"今天是{now.year}年{now.month}月{now.day}日。"

def get_weather(city: str = "北京") -> str:
    """模拟天气查询（实际可对接和风天气等API）"""
    # 模拟数据，真实场景可替换为API调用
    mock_weather = {
        "北京": "晴天，25°C，微风，湿度40%",
        "上海": "多云，28°C，东南风3级，湿度60%",
        "广州": "雷阵雨，32°C，南风2级，湿度85%，出门请带伞",
        "深圳": "多云转晴，30°C，西南风3级，湿度70%",
        "杭州": "小雨，24°C，北风1级，湿度80%",
        "成都": "阴天，22°C，无持续风向，湿度75%",
        "武汉": "晴转多云，27°C，东风2级，湿度55%",
    }
    return mock_weather.get(city, f"暂不支持查询{city}的天气，目前支持：北京、上海、广州、深圳、杭州、成都、武汉")

# 工具描述（升级版，包含多个工具）
TOOLS_DESC = """
你是一个智能助手，可以调用以下工具获取真实信息。

当用户的问题涉及以下情况时，请严格按格式输出工具调用指令，不要编造答案：

1. 数学计算 → 输出：<<CALCULATE>>表达式
   示例：<<CALCULATE>>123*456

2. 查询当前时间 → 输出：<<GET_TIME>>

3. 查询当前日期 → 输出：<<GET_DATE>>

4. 查询城市天气 → 输出：<<GET_WEATHER>>城市名
   示例：<<GET_WEATHER>>北京

如果不需要工具，直接正常回答即可。
"""