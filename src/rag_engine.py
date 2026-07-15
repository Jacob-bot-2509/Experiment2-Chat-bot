import os
import requests
import json
import chromadb
from chromadb.config import Settings
from PyPDF2 import PdfReader

class RAGEngine:
    def __init__(self, persist_dir="./chroma_db", ollama_base_url="http://localhost:11434"):
        self.ollama_embed_url = f"{ollama_base_url}/api/embeddings"
        self.embed_model_name = "nomic-embed-text"
        self.chroma_client = chromadb.Client(Settings(persist_directory=persist_dir, anonymized_telemetry=False))
        self.collection = self.chroma_client.get_or_create_collection(name="docs")
        self._ensure_embed_model()

    def _ensure_embed_model(self):
        """检查并自动拉取 embedding 模型"""
        try:
            resp = requests.post(self.ollama_embed_url, json={"model": self.embed_model_name, "prompt": "test"})
            if resp.status_code != 200:
                print(f"正在拉取 Embedding 模型 {self.embed_model_name}...")
                pull_resp = requests.post(f"{self.ollama_embed_url.replace('/embeddings', '/pull')}",
                                         json={"name": self.embed_model_name})
                if pull_resp.status_code != 200:
                    raise RuntimeError(f"无法拉取 Embedding 模型: {pull_resp.text}")
                print("Embedding 模型就绪。")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Ollama 服务未运行，请先启动 Ollama。")

    def _embed_texts(self, texts):
        """使用 Ollama 获取文本向量"""
        embeddings = []
        for text in texts:
            resp = requests.post(self.ollama_embed_url, json={"model": self.embed_model_name, "prompt": text})
            if resp.status_code == 200:
                embedding = resp.json()["embedding"]
                embeddings.append(embedding)
            else:
                raise RuntimeError(f"Embedding 请求失败: {resp.text}")
        return embeddings

    def load_document(self, file_path):
        """加载txt或pdf文件，返回文本内容"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        elif ext == '.pdf':
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\\\\n"
            return text
        else:
            raise ValueError("不支持的文件格式，仅支持 txt 和 pdf")

    def chunk_text(self, text, chunk_size=500, overlap=50):
        """简单按字符切块"""
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start += chunk_size - overlap
        return chunks

    def index_document(self, file_path):
        """将文档切块、向量化并存入chroma"""
        text = self.load_document(file_path)
        chunks = self.chunk_text(text)
        doc_name = os.path.basename(file_path)
        ids = [f"{doc_name}_chunk_{i}" for i in range(len(chunks))]
        embeddings = self._embed_texts(chunks)
        metadatas = [{"source": doc_name, "chunk_index": i} for i in range(len(chunks))]
        self.collection.add(embeddings=embeddings, documents=chunks, metadatas=metadatas, ids=ids)
        return len(chunks)

    def search(self, query, top_k=3):
        """检索最相关的top_k个原文块"""
        query_embedding = self._embed_texts([query])[0]
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results

    def format_context(self, results):
        """将检索结果格式化成上下文文本"""
        contexts = []
        for i, doc in enumerate(results['documents'][0]):
            source = results['metadatas'][0][i]['source']
            contexts.append(f"[来源: {source}] {doc}")
        return "\\\\n\\\\n".join(contexts)