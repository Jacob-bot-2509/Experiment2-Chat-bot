# 本地大模型聊天系统（Chat with Local LLM）

## 项目简介
基于Python和Ollama实现的命令行聊天系统，支持多轮对话和会话管理，无需联网，完全在本地运行，保护隐私。

## 功能特点
- 基础聊天：调用本地大模型进行多轮对话
- 会话管理：支持新建、切换、查看历史会话
- 本地运行：基于Ollama+Qwen2-o.5B，零成本，低延迟

## 技术栈
- Python 3.x
- Ollama
- OpenAI兼容接口

## 环境配置
1. 安装Ollama(https://ollama.com/download/windows)
2. 拉取模型：
   ‘’‘bash
   ollama pull qwen2:0.5b

## 安装Python依赖
pip install -r requirements.txt

## 运行方法
确保Ollama正在后台运行，然后在项目根目录执行python src/chat.py

## 使用说明
- 直接输入文本与AI对话
- 输入/help查看所有命令
- 输入/new新建会话
- 输入/list查看所有会话
- 输入/switch <id>切换到指定会话
- 输入/exit退出程序

## 项目结构
├── src/
│   ├── chat.py             # 主程序入口
│   ├── session_manager.py  # 会话管理逻辑
│   └── llm_client.py       # LLM API 封装
├── .env                    # 环境变量（已忽略）
├── requirements.txt
└── README.md

## 运行结果

![daily chat.png](daily%20chat.png)

## 进阶功能展示
### 进阶A：上下文栈
在场对话中保持角色设定和规则，对比普通截断策略效果更好。
输入 '/ctx_test'查看对比演示。

![ctx_demo.png](ctx_demo.png)

### 进阶B：工具调用
Agent模式支持计算机工具，模型会自动判断是否需要调用工具并返回精确结果。
输入'/agent'进入，输入数学题（如'123*456'）体验。

![agent_demo.png](agent_demo.png)

### 进阶C:RAG知识库问答
支持上传本地文档（txt/pdf），系统自动切分、向量化，基于原文回答。

![rag_demo.png](rag_demo.png)


**加载文档**
'/rag load D:\\Python\\PythonProject1\test.txt'

**提问**
' /rag ask 公司的主要产品是什么？'

**回答示例**
'[来源: test.txt] 我们公司叫“未来科技”，主要产品是智能语音助手“小千”。这款产品可以帮助用户订机票、查天气、控制家电。
公司位于北京市海淀区，成立于2020年。'



