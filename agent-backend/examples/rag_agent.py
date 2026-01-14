"""
RAG智能代理示例（检索增强生成）
这个文件展示了如何创建一个基于RAG的智能代理，它可以从网页内容中检索信息来回答用户问题
"""
import os
import sys
# 添加父目录到路径，以便导入自定义工具
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_chat_model  # 导入自定义的聊天模型初始化函数（支持硅基流动）
from langchain_core.embeddings import DeterministicFakeEmbedding  # 导入嵌入模型（用于向量化文本）
from langchain_core.vectorstores import InMemoryVectorStore  # 导入内存向量存储
import bs4  # 导入BeautifulSoup4，用于解析HTML
from langchain_community.document_loaders import WebBaseLoader  # 导入网页加载器
from langchain.tools import tool  # 导入工具装饰器
from langchain_text_splitters import RecursiveCharacterTextSplitter  # 导入文本分割器
from langchain.agents import create_agent  # 导入创建代理的函数

# 全局变量用于懒加载
_model = None
_embeddings = None
_vector_store = None
_retrieve_tool = None

def _get_model():
    """延迟初始化模型"""
    global _model
    if _model is None:
        from utils import load_chat_model
        os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"
        _model = load_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp")
    return _model

def _get_embeddings():
    """延迟初始化嵌入模型"""
    global _embeddings
    if _embeddings is None:
        _embeddings = DeterministicFakeEmbedding(size=4096)
    return _embeddings

def _get_vector_store():
    """延迟初始化向量存储和文档"""
    global _vector_store
    if _vector_store is None:
        print("📚 正在加载文档...")
        
        # 初始化嵌入模型
        embeddings = _get_embeddings()
        _vector_store = InMemoryVectorStore(embeddings)
        
        # 配置HTML解析器
        bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
        
        # 创建网页加载器
        loader = WebBaseLoader(
            web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
            bs_kwargs={"parse_only": bs4_strainer},
        )
        
        # 加载和处理文档
        docs = loader.load()
        assert len(docs) == 1, "应该只加载一个文档"
        
        # 文本分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            add_start_index=True,
        )
        
        all_splits = text_splitter.split_documents(docs)
        _vector_store.add_documents(documents=all_splits)
        print("✅ 文档加载完成")
    
    return _vector_store

def _get_retrieve_tool():
    """延迟初始化检索工具"""
    global _retrieve_tool
    if _retrieve_tool is None:
        @tool(response_format="content_and_artifact")
        def retrieve_context(query: str):
            """检索信息以帮助回答查询。
            
            这个工具会在向量存储中搜索与查询最相关的文档片段。
            
            参数:
                query: 用户的查询问题
                
            返回:
                序列化的文档内容和原始文档对象
            """
            vector_store = _get_vector_store()
            retrieved_docs = vector_store.similarity_search(query, k=2)
            
            serialized = "\n\n".join(
                (f"来源: {doc.metadata}\n内容: {doc.page_content}")
                for doc in retrieved_docs
            )
            
            return serialized, retrieved_docs
        
        _retrieve_tool = retrieve_context
    return _retrieve_tool


# ============ 创建RAG代理 ============

def get_rag_agent():
    """
    工厂函数 - 返回 RAG Agent（懒加载版本）
    
    供 LangGraph API 使用
    
    Returns:
        RAG Agent 实例
    """
    model = _get_model()
    tools = [_get_retrieve_tool()]
    
    prompt = (
        "你可以使用一个工具从博客文章中检索相关内容。"
        "使用这个工具来帮助回答用户的问题。"
        "在回答之前，先检索相关信息，然后基于检索到的内容给出准确的答案。"
    )
    
    agent = create_agent(model, tools, system_prompt=prompt)
    return agent


if __name__ == "__main__":
    query = (
        "任务分解的标准方法是什么？\n\n"
        "得到答案后，请查找该方法的常见扩展。"
    )
    
    agent = get_rag_agent()
    
    for event in agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="values",
    ):
        event["messages"][-1].pretty_print()