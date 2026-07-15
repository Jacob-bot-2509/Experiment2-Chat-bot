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
            user_input = input("\\\\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\\\\n再见！")
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