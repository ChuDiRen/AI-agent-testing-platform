"""
RAG智能代理示例（检索增强生成）
这个文件展示了如何创建一个基于RAG的智能代理，它可以从网页内容中检索信息来回答用户问题
"""
import os
import sys
# 添加父目录到路径，以便导入自定义工具
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import init_chat_model  # 导入自定义的聊天模型初始化函数（支持硅基流动）
from langchain_core.embeddings import DeterministicFakeEmbedding  # 导入嵌入模型（用于向量化文本）
from langchain_core.vectorstores import InMemoryVectorStore  # 导入内存向量存储
import bs4  # 导入BeautifulSoup4，用于解析HTML
from langchain_community.document_loaders import WebBaseLoader  # 导入网页加载器
from langchain.tools import tool  # 导入工具装饰器
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 导入文本分割器
from langchain.agents import create_agent  # 导入创建代理的函数

# 设置 DeepSeek API 密钥（这是一个大语言模型服务）
os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
# 初始化 DeepSeek 聊天模型，这个模型将被所有代理使用
model = init_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")


# ============ 向量存储初始化 ============
# 用于将文本转换为向量，以便进行相似度搜索

# 创建嵌入模型（这里使用确定性假嵌入用于演示，实际应用中应使用真实的嵌入模型）
embeddings = DeterministicFakeEmbedding(size=4096)

# 创建内存向量存储，用于存储和检索文档向量
vector_store = InMemoryVectorStore(embeddings)


# ============ 加载和处理网页内容 ============

# 配置HTML解析器，只保留文章标题、标题和内容部分
bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))

# 创建网页加载器，从指定URL加载内容
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),  # 要加载的网页URL
    bs_kwargs={"parse_only": bs4_strainer},  # 只解析指定的HTML元素
)

# 加载网页文档
docs = loader.load()

# 确保只加载了一个文档
assert len(docs) == 1, "应该只加载一个文档"


# ============ 文本分割 ============
# 将长文档分割成小块，便于检索和处理

# 创建递归字符文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # 每个文本块的大小（字符数）
    chunk_overlap=200,      # 文本块之间的重叠部分（字符数），确保上下文连贯性
    add_start_index=True,   # 记录每个块在原文档中的起始位置
)

# 将文档分割成多个小块
all_splits = text_splitter.split_documents(docs)

# 将分割后的文档添加到向量存储中
document_ids = vector_store.add_documents(documents=all_splits)


# ============ 检索工具 ============
# 创建一个工具，用于从向量存储中检索相关内容

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """检索信息以帮助回答查询。
    
    这个工具会在向量存储中搜索与查询最相关的文档片段。
    
    参数:
        query: 用户的查询问题
        
    返回:
        序列化的文档内容和原始文档对象
    """
    # 使用相似度搜索找到最相关的2个文档片段
    retrieved_docs = vector_store.similarity_search(query, k=2)
    
    # 将检索到的文档序列化为字符串格式
    serialized = "\n\n".join(
        (f"来源: {doc.metadata}\n内容: {doc.page_content}")
        for doc in retrieved_docs
    )
    
    # 返回序列化的内容和原始文档
    return serialized, retrieved_docs


# ============ 创建RAG代理 ============

# 定义代理可以使用的工具列表
tools = [retrieve_context]

# 定义代理的系统提示词
prompt = (
    "你可以使用一个工具从博客文章中检索相关内容。"
    "使用这个工具来帮助回答用户的问题。"
    "在回答之前，先检索相关信息，然后基于检索到的内容给出准确的答案。"
)

# 创建RAG代理
agent = create_agent(
    model,              # 使用的语言模型
    tools,              # 代理可以使用的工具
    system_prompt=prompt  # 代理的系统提示词
)


# ============ 主程序 ============
# 演示如何使用RAG代理回答问题

if __name__ == "__main__":
    # 定义用户查询（中文示例）
    query = (
        "任务分解的标准方法是什么？\n\n"
        "得到答案后，请查找该方法的常见扩展。"
    )
    
    # 使用流式处理执行代理
    for event in agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values",  # 流式返回值
    ):
        # 打印最后一条消息（代理的回复）
        event["messages"][-1].pretty_print()