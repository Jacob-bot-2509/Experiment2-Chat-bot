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


