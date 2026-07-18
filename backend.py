import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.session_manager import Session, SessionManager
from src.llm_client import chat_completion
from src.rag_engine import RAGEngine
from src.context_stack import ContextStack
from src.agent_tools import TOOLS_DESC, calculate

# 持久化文件路径
SESSION_FILE = "sessions.json"

# 全局会话管理器
session_manager = SessionManager()
rag_engine = RAGEngine()


# 生命周期管理：启动时加载会话，关闭时保存会话
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时加载
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for sid, info in data.items():
                # 手动创建 Session 对象并放入字典，避免 ID 自增冲突
                session = Session(sid)
                session.title = info.get("title", "恢复的会话")
                session.messages = info.get("messages", [])
                session_manager.sessions[sid] = session
            print(f"已从 {SESSION_FILE} 恢复 {len(data)} 个会话。")
        except Exception as e:
            print(f"加载会话失败: {e}")
    else:
        print("未找到会话文件，初始化为空。")

    yield  # 应用运行期间

    # 关闭时保存
    sessions_data = {}
    for sid, s in session_manager.sessions.items():
        sessions_data[sid] = {
            "title": s.title,
            "messages": s.messages
        }
    with open(SESSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions_data, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(sessions_data)} 个会话到 {SESSION_FILE}。")


app = FastAPI(lifespan=lifespan)


# 请求/响应模型
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    title: str | None = None


class RAGLoadRequest(BaseModel):
    file_path: str


class RAGAskRequest(BaseModel):
    question: str


# ---------- 基础聊天接口 ----------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if req.session_id and req.session_id in session_manager.sessions:
        session_manager.current_session_id = req.session_id
        session = session_manager.sessions[req.session_id]
    else:
        session = session_manager.new_session()

    session.add_message("user", req.message)
    reply = chat_completion(session.messages, model="qwen2:0.5b")
    session.add_message("assistant", reply)
    return ChatResponse(session_id=session.id, reply=reply, title=session.title)


# ---------- 会话管理接口 ----------
@app.get("/sessions")
async def list_sessions():
    sessions = []
    for sid, s in session_manager.sessions.items():
        sessions.append({
            "id": s.id,
            "title": s.title,
            "message_count": len(s.messages)
        })
    return sessions


@app.post("/sessions/new")
async def new_session():
    session = session_manager.new_session()
    return {"id": session.id, "title": session.title}


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_id in session_manager.sessions:
        del session_manager.sessions[session_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Session not found")


# ---------- 进阶C：RAG 接口 ----------
@app.post("/rag/load")
async def rag_load(req: RAGLoadRequest):
    try:
        num = rag_engine.index_document(req.file_path)
        return {"status": "success", "chunks": num}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/rag/ask")
async def rag_ask(req: RAGAskRequest):
    try:
        results = rag_engine.search(req.question)
        context = rag_engine.format_context(results)
        prompt = f"基于以下参考资料回答问题，如果无法回答请说明。\\\\n\\\\n参考资料:\\\\n{context}\\\\n\\\\n问题: {req.question}\\\\n答案:"
        reply = chat_completion([{"role": "user", "content": prompt}], model="qwen2:0.5b")
        return {"reply": reply, "sources": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------- 进阶A：上下文栈测试接口 ----------
@app.post("/ctx_test")
async def ctx_test():
    ctx = ContextStack(max_tokens=512, recent_rounds=3)
    ctx.import_history("test_history.json")
    test_question = "你还记得我叫什么名字吗？请用你的角色语气回答。"

    plain_messages = ctx.working_memory[-10:]
    plain_messages.append({"role": "user", "content": test_question})
    ans_plain = chat_completion(plain_messages, model="qwen2:0.5b")

    ctx.add_message("user", test_question)
    stack_messages = ctx.get_full_context()
    ans_stack = chat_completion(stack_messages, model="qwen2:0.5b")

    return {
        "plain": ans_plain,
        "stack": ans_stack,
        "explanation": "普通策略直接截断，上下文栈策略保持了角色设定"
    }


# ---------- 进阶B：工具调用接口 ----------
@app.post("/agent")
async def agent(req: ChatRequest):
    msgs = [{"role": "system", "content": TOOLS_DESC}, {"role": "user", "content": req.message}]
    response = chat_completion(msgs, model="qwen2:0.5b")
    if "<<TOOL_CALL>>" in response:
        expr = response.split("<<TOOL_CALL>>")[1].strip()
        tool_result = calculate(expr)
        msgs.append({"role": "assistant", "content": response})
        msgs.append({"role": "user", "content": f"工具执行结果：{tool_result}，请根据此结果回答用户。"})
        final_response = chat_completion(msgs, model="qwen2:0.5b")
        return {"reply": final_response, "tool_used": expr, "tool_result": tool_result}
    return {"reply": response, "tool_used": None}


# ---------- 静态文件服务（前端） ----------
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def root():
    return FileResponse("frontend/index.html")