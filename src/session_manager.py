class Session:
    def __init__(self, session_id, title="新对话"):
        self.id = session_id
        self.title = title
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        if role == "user" and self.title == "新对话":
            self.title = content[:20] + ("..." if len(content) > 20 else "")

class SessionManager:
    def __init__(self):
        self.sessions = {}
        self.current_session_id = None

    def new_session(self):
        sid = str(len(self.sessions) + 1)
        self.sessions[sid] = Session(sid)
        self.current_session_id = sid
        return self.sessions[sid]

    def get_current_session(self):
        return self.sessions.get(self.current_session_id)

    def switch_session(self, sid):
        if sid in self.sessions:
            self.current_session_id = sid
            return True
        return False

    def list_sessions(self):
        print("\\\\n--- 历史会话 ---")
        for sid, s in self.sessions.items():
            mark = " ← 当前" if sid == self.current_session_id else ""
            print(f"[{sid}] {s.title}{mark}")
        print("----------------")