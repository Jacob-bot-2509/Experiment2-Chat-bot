from context_stack import ContextStack
from llm_client import chat_completion
from rag_engine import RAGEngine
rag_engine = RAGEngine()
from session_manager import SessionManager
from llm_client import chat_completion

def main():
    manager = SessionManager()
    current_session = manager.new_session()
    print("=" * 40)
    print("欢迎使用 DeepSeek Chat 系统")
    print("输入 /help 查看命令列表")
    print("=" * 40)

    while True:
        try:
            user_input = input("\\\\\\\\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\\\\\\\\n再见！")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            if user_input == "/help":
                print("""
可用命令：
/help      显示此帮助信息
/new       开始一个新的对话
/list      查看所有历史对话
/switch <id> 切换到指定ID的对话
/ctx_test  运行上下栈对比测试
/agent     进入工具调用模式，输入 /exit_agent 退出
/rag load <文件路径> 加载文档到知识库
/rag ask <问题>     基于知识库提问
/exit      退出程序
""")
            elif user_input == "/new":
                current_session = manager.new_session()
                print(f"新会话已创建 [{current_session.id}]")
            elif user_input == "/list":
                manager.list_sessions()
            elif user_input.startswith("/switch"):
                parts = user_input.split()
                if len(parts) == 2 and manager.switch_session(parts[1]):
                    current_session = manager.get_current_session()
                    print(f"已切换到会话 [{current_session.id}]: {current_session.title}")
                else:
                    print("切换失败，请检查会话ID是否正确。")
            elif user_input == "/ctx_test":
                print("加载测试历史...")
                ctx = ContextStack(max_tokens=512, recent_rounds=3)
                ctx.import_history("D:/Python/PythonProject1/test_history.json")
                test_question = "你还记得我叫什么名字吗？请用你的角色语气回答。"
                plain_messages = ctx.working_memory[-10:]
                plain_messages.append({"role": "user", "content": test_question})

                ctx.add_message("user", test_question)
                stack_messages = ctx.get_full_context()

                print("=== 普通策略（简单截断）回答 ===")
                try:
                   ans_plain = chat_completion(plain_messages, model="qwen2:0.5b")
                   print(ans_plain)
                except Exception as e:
                   print(f"错误: {e}")

                print("\\\\\\\\n=== 上下文栈策略回答 ===")
                try:
                   ans_stack = chat_completion(stack_messages, model="qwen2:0.5b")
                   print(ans_stack)
                except Exception as e:
                   print(f"错误: {e}")
            elif user_input == "/agent":
                from agent_tools import TOOLS_DESC, calculate
                print("进入工具调用模式（输入 /exit_agent 退出）")
                agent_mode = True
                agent_system = {"role": "system", "content": TOOLS_DESC}
                while agent_mode:
                    try:
                       user_input = input("\\\\\\\\n你(Agent): ").strip()
                    except:
                       break
                    if user_input == "/exit_agent":
                       agent_mode = False
                       continue
                    msgs = [agent_system, {"role": "user", "content": user_input}]
                    response = chat_completion(msgs, model="qwen2:0.5b")
                    if "<<TOOL_CALL>>" in response:
                       expr = response.split("<<TOOL_CALL>>")[1].strip()
                       print(f"[工具调用] 计算: {expr}")
                       tool_result = calculate(expr)
                       print(f"[工具结果] {tool_result}")
                       msgs.append({"role": "assistant", "content": response})
                       msgs.append({"role": "user", "content": f"工具执行结果：{tool_result}，请根据此结果回答用户。"})
                       final_response = chat_completion(msgs, model="qwen2:0.5b")
                       print(f"助手: {final_response}")
                    else:
                       print(f"助手: {response}")
            elif user_input.startswith("/rag load"):
                from rag_engine import RAGEngine
                rag = RAGEngine()
                parts = user_input.split(maxsplit=2)
                if len(parts) == 3:
                    file_path = parts[2]
                    try:
                        num = rag.index_document(file_path)
                        print(f"文档已索引，共 {num} 个文本块。")
                    except Exception as e:
                        print(f"索引失败: {e}")
                else:
                    print("用法: /rag load <文件路径>")
            elif user_input.startswith("/rag ask"):
                from rag_engine import RAGEngine
                rag = RAGEngine()
                parts = user_input.split(maxsplit=2)
                if len(parts) == 3:
                        question = parts[2]
                        results = rag.search(question)
                        context = rag.format_context(results)
                        prompt = f"基于以下参考资料回答问题，如果无法回答请说明。\\\\n\\\\n参考资料:\\\\n{context}\\\\n\\\\n问题: {question}\\\\n答案:"
                        msgs = [{"role": "user", "content": prompt}]
                        reply = chat_completion(msgs, model="qwen2:0.5b")
                        print(f"助手: {reply}")
                        print("\\\\n--- 检索到的原文块（来源） ---")
                        print(context)
                else:
                    print("用法: /rag ask <问题>")
            elif user_input == "/exit":
                print("再见！")
                break
            else:
                print("未知命令，请重试。")
            continue

        current_session.add_message("user", user_input)
        reply = chat_completion(current_session.messages)
        print(f"助手: {reply}")
        current_session.add_message("assistant", reply)

if __name__ == "__main__":
    main()