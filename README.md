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

## Web部署与压力测试
### 启动方式
#### 1.启动后端服务
uvicorn backend:app --reload --host 0.0.0.0 --port 8000

#### 2. 浏览器访问 http://localhost:8000

### 聊天测试

**测试截图**
![test_chat.png](test_chat.png)

### 会话持久化

系统通过 FastAPI 的生命周期事件实现了会话数据的磁盘持久化：

- **保存机制**：服务关闭时，所有会话的标题和消息历史被序列化为 JSON 文件 `sessions.json`。
- **恢复机制**：服务启动时，自动读取 `sessions.json` 重建会话对象，用户刷新后仍可继续之前的对话。
- **验证方式**：停止服务 → 查看 `sessions.json` → 重启服务 → 刷新页面，会话依然存在。

![test_persist.png](test_persist.png)

**会话管理**
![test_session manager.png](test_session%20manager.png)
### 压力测试
使用Locust模拟多用户并发送聊天请求，验证系统在高负载下的稳定性。
locust -f locustfile.py --host=http://localhost:8000

#### 打开 http://localhost:8089 设置参数并启动测试

**测试配置**：20并发用户，每秒启用5个用户，持续3分钟。

**测试结果**：

| 接口 | 总请求数 | 成功请求数 | 失败请求数 | 平均响应时间 | 95%响应时间 | 99%响应时间 |
|------|----------|------------|------------|--------------|-------------|-------------|
| /chat | 1000 | 1000 | 0 | 1006.4ms | 2300ms | 3000ms |
| /sessions | 100 | 100 | 0 | 547.72ms | 1800ms | 2500ms |
| /sessions/new | 100 | 100 | 0 | 3311.75ms | 2051ms | 4738ms |
**测试截图**
- 数据截图![test_static.png](test_static.png)
- 图表截图![test_chart.png](test_chart.png)

**测试结论**
- 系统在20并发用户下持续3分钟的压力测试中，所有请求成功率为100%，无任何失败或服务崩溃。
- '/chat'聊天接口平均响应时间约为1s，95%请求在2.3s内完成，得益于本地Qwen2-0.5B模型及轻量化设计，在CPU环境下仍能保持较低延迟。
- '/sessions'接口平均响应时间约为0.55s，95%请求在1.8s内完成，性能表现良好。
- '/sessions/new'接口平均响应时间约为3.31s，95%请求在2.05s内完成。
- 总的来说，系统在单机CPU部署条件下，已具备较稳定的服务能力，后续若迁移至CPU环境或采用更小量化模型，可进一步提升并发承载上线和响应速度。
