"""
RAG 召回效果评测脚本
测试多个文档的索引、检索和召回准确性
"""
import os
from src.rag_engine import RAGEngine

# 初始化 RAG 引擎
rag = RAGEngine()

# 第一步：批量索引文档
docs_dir = "rag_test_docs"
print("=" * 60)
print("开始索引文档...")
print("=" * 60)

total_chunks = 0
for filename in os.listdir(docs_dir):
    if filename.endswith('.txt'):
        filepath = os.path.join(docs_dir, filename)
        chunks = rag.index_document(filepath)
        total_chunks += chunks
        print(f"? {filename} → {chunks} 个文本块")

print(f"\\\\n?? 总计索引 {len(os.listdir(docs_dir))} 个文档，{total_chunks} 个文本块")

# 第二步：设计测试用例
print("\\\\n" + "=" * 60)
print("RAG 召回效果评估")
print("=" * 60)

test_cases = [
    {
        "id": 1,
        "question": "公司的主要产品是什么？",
        "expected_keywords": ["智能语音助手", "小千"],
        "expected_source": "公司介绍.txt"
    },
    {
        "id": 2,
        "question": "如何联系客服？",
        "expected_keywords": ["400", "电话", "邮箱"],
        "expected_source": "联系方式.txt"
    },
    {
        "id": 3,
        "question": "设备无法响应怎么办？",
        "expected_keywords": ["复位", "无响应", "针状物"],
        "expected_source": "产品手册.txt"
    },
    {
        "id": 4,
        "question": "保修期是多长时间？",
        "expected_keywords": ["一年", "免费保修", "延保"],
        "expected_source": "常见问题.txt"
    },
    {
        "id": 5,
        "question": "公司总部在哪里？",
        "expected_keywords": ["北京", "海淀", "中关村"],
        "expected_source": "公司介绍.txt"
    }
]

# 第三步：逐条测试并分析
results = []

for test in test_cases:
    print(f"\\\\n--- 测试 {test['id']}：{test['question']} ---")

    # 检索
    search_results = rag.search(test['question'], top_k=3)
    retrieved_docs = search_results['documents'][0]
    retrieved_sources = [m['source'] for m in search_results['metadatas'][0]]

    # 分析关键词命中情况
    hit_keywords = []
    for kw in test['expected_keywords']:
        for doc in retrieved_docs:
            if kw in doc:
                hit_keywords.append(kw)
                break

    # 分析期望来源是否被召回
    source_hit = test['expected_source'] in retrieved_sources

    # 输出结果
    print(f"  召回来源: {retrieved_sources}")
    print(f"  关键词命中: {hit_keywords}/{test['expected_keywords']}")
    print(f"  期望来源召回: {'? 成功' if source_hit else '? 失败'}")
    print(f"  Top-1 内容预览: {retrieved_docs[0][:80]}...")

    results.append({
        "id": test['id'],
        "question": test['question'],
        "source_hit": source_hit,
        "keyword_hit_rate": len(hit_keywords) / len(test['expected_keywords'])
    })

# 第四步：汇总报告
print("\\\\n" + "=" * 60)
print("?? 召回效果汇总")
print("=" * 60)

source_hit_count = sum(1 for r in results if r['source_hit'])
avg_keyword_rate = sum(r['keyword_hit_rate'] for r in results) / len(results)

print(f"期望来源召回率: {source_hit_count}/{len(results)} = {source_hit_count / len(results) * 100:.1f}%")
print(f"平均关键词命中率: {avg_keyword_rate * 100:.1f}%")

print("\\\\n" + "=" * 60)
print("?? 详细结果表格")
print("=" * 60)
print(f"{'ID':<5} {'问题':<25} {'来源召回':<10} {'关键词命中率':<12}")
print("-" * 60)
for r in results:
    status = "?" if r['source_hit'] else "?"
    print(f"{r['id']:<5} {r['question']:<25} {status:<10} {r['keyword_hit_rate'] * 100:.0f}%")

# 第五步：召回内容价值分析
print("\\\\n" + "=" * 60)
print("?? 召回内容价值分析")
print("=" * 60)

# 示例分析
analysis_question = "公司的主要产品是什么？"
print(f"\\\\n以问题「{analysis_question}」为例：")
search_results = rag.search(analysis_question, top_k=2)
retrieved_docs = search_results['documents'][0]
retrieved_sources = [m['source'] for m in search_results['metadatas'][0]]

for i, (doc, source) in enumerate(zip(retrieved_docs, retrieved_sources)):
    print(f"\\\\n  召回块 {i + 1} [来源: {source}]:")
    print(f"  内容: {doc}")
    print(f"  分析: ", end="")
    if "小千" in doc or "智能语音" in doc:
        print("? 包含核心产品信息，可直接用于回答")
    elif "未来科技" in doc:
        print("? 包含公司背景信息，作为上下文补充")
    else:
        print("?? 相关性较低，但可作为参考")

print("\\\\n" + "=" * 60)
print("?? 结论")
print("=" * 60)
print("""
RAG 系统的核心价值在于：
1. 模型训练数据中没有"未来科技"这家公司的信息，但通过 RAG 检索，
   模型能从本地文档中获取准确信息，避免了"幻觉"。
2. 召回内容被作为上下文提供给 LLM，使得答案准确、有据可查。
3. 来源标注（文件名）让用户可以追溯信息的出处，增加可信度。
4. 相比于纯生成模式，RAG 的答案在事实准确性上有质的提升。
""")