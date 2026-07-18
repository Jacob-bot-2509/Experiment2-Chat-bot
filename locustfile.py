from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        res = self.client.post("/sessions/new")
        if res.status_code == 200:
            self.session_id = res.json()["id"]
        else:
            self.session_id = None

    @task
    def chat(self):
        if not self.session_id:
            return
        self.client.post("/chat", json={
            "session_id": self.session_id,
            "message": "你好，请简单介绍一下你自己。"
        })

    @task(3)
    def list_sessions(self):
        self.client.get("/sessions")
