"""
Agentic RAG 系统（基于 LangGraph 的智能检索增强生成）

这个文件展示了如何构建一个完整的 Agentic RAG 系统，它具备以下智能能力：
1. 自主决策是否需要检索信息
2. 评估检索到的文档是否相关
3. 如果文档不相关，自动重写问题并重新检索
4. 基于相关文档生成准确的答案

工作流程：
用户提问 → 决策是否检索 → 检索文档 → 评估相关性 → 生成答案/重写问题
"""

import os
import sys
from typing import Literal

from pydantic import BaseModel, Field

# 添加父目录到路径，以便导入自定义工具
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import load_chat_model  # 使用自定义的load_chat_model（支持硅基流动）
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage

# ============ 环境配置 ============

# 设置 DeepSeek API 密钥
os.environ["SILICONFLOW_API_KEY"] = "sk-rmcrubplntqwdjumperktjbnepklekynmnmianaxtkneocem"

# 初始化 DeepSeek 聊天模型
response_model = load_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp", temperature=0)
grader_model = load_chat_model("siliconflow:deepseek-ai/DeepSeek-V3.2-Exp", temperature=0)


# ============ 第一步：预处理文档 ============
# 从网页加载文档并分割成小块

print("📚 正在加载文档...")

# 定义要加载的博客文章URL列表
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",
]

# 从每个URL加载文档
docs = [WebBaseLoader(url).load() for url in urls]

# 将嵌套列表展平为单一列表
docs_list = [item for sublist in docs for item in sublist]

# 创建文本分割器，将长文档分割成小块
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=500,      # 每个文本块的大小（token数）
    chunk_overlap=100    # 文本块之间的重叠部分（token数）
)

# 分割文档
doc_splits = text_splitter.split_documents(docs_list)
print(f"✅ 文档已分割成 {len(doc_splits)} 个小块")


# ============ 第二步：创建检索工具 ============
# 使用向量存储和嵌入模型创建检索器

print("🔧 正在创建检索工具...")

# 创建嵌入模型（用于将文本转换为向量）
embeddings = DeterministicFakeEmbedding(size=4096)

# 创建向量存储并添加文档
vectorstore = InMemoryVectorStore.from_documents(
    documents=doc_splits,
    embedding=embeddings
)

# 创建检索器
retriever = vectorstore.as_retriever(k=3)  # 每次检索返回3个最相关的文档

# 创建检索工具
@tool
def retriever_tool(query: str) -> str:
    """搜索并返回关于 Lilian Weng 博客文章的信息。当需要回答关于 AI、LLM、提示工程、代理等主题的问题时使用此工具。"""
    docs = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

print("✅ 检索工具创建完成")


# ============ 第三步：生成查询或响应节点 ============
# 决定是否需要检索信息

def generate_query_or_respond(state: MessagesState):
    """
    根据当前状态调用模型生成响应。
    
    给定问题后，模型会决定：
    1. 使用检索工具获取信息
    2. 直接回答用户（如果不需要额外信息）
    
    参数:
        state: 包含消息历史的状态对象
        
    返回:
        包含模型响应的字典
    """
    response = (
        response_model
        .bind_tools([retriever_tool])  # 绑定检索工具
        .invoke(state["messages"])
    )
    return {"messages": [response]}


# ============ 第四步：评估文档相关性 ============
# 判断检索到的文档是否与问题相关

# 定义评估提示词
GRADE_PROMPT = (
    "你是一个评估检索文档与用户问题相关性的评分员。\n"
    "这是检索到的文档：\n\n{context}\n\n"
    "这是用户的问题：{question}\n"
    "如果文档包含与用户问题相关的关键词或语义含义，则将其评为相关。\n"
    "给出二元评分 'yes' 或 'no'，表示文档是否与问题相关。"
)

# 定义评分数据模型
class GradeDocuments(BaseModel):
    """使用二元评分检查文档相关性。"""
    reasoning: str = Field(
        description="评估文档相关性的推理过程"
    )
    answer: str = Field(
        description="相关性评分：'yes' 表示相关，'no' 表示不相关"
    )

def grade_documents(
    state: MessagesState,
) -> Literal["generate_answer", "rewrite_question"]:
    """
    判断检索到的文档是否与问题相关。
    
    参数:
        state: 包含消息历史的状态对象
        
    返回:
        下一个节点的名称：
        - "generate_answer": 如果文档相关
        - "rewrite_question": 如果文档不相关
    """
    # 获取原始问题和检索到的上下文
    question = state["messages"][0].content
    context = state["messages"][-1].content
    
    # 构建评估提示
    prompt = GRADE_PROMPT.format(question=question, context=context)
    
    try:
        # 调用模型进行评分
        response = (
            grader_model
            .with_structured_output(GradeDocuments)
            .invoke([{"role": "user", "content": prompt}])
        )
        
        score = response.answer
        
    except Exception as e:
        print(f"⚠️ 结构化输出失败，尝试解析文本响应: {e}")
        # 如果结构化输出失败，尝试获取文本响应并手动解析
        text_response = grader_model.invoke([{"role": "user", "content": prompt}])
        
        # 简单的文本解析来提取 yes/no
        content = text_response.content.lower()
        if "yes" in content or "相关" in content:
            score = "yes"
        else:
            score = "no"
    
    if score == "yes":
        print("✅ 文档相关，继续生成答案")
        return "generate_answer"
    else:
        print("⚠️ 文档不相关，重写问题")
        return "rewrite_question"


# ============ 第五步：重写问题节点 ============
# 如果检索到的文档不相关，重写问题以改进检索效果

# 定义重写提示词
REWRITE_PROMPT = (
    "查看输入并尝试推理其潜在的语义意图/含义。\n"
    "这是初始问题：\n"
    "------- \n"
    "{question}\n"
    "------- \n"
    "制定一个改进的问题："
)

def rewrite_question(state: MessagesState):
    """
    重写原始用户问题以改进检索效果。
    
    参数:
        state: 包含消息历史的状态对象
        
    返回:
        包含重写后问题的字典
    """
    messages = state["messages"]
    question = messages[0].content
    
    # 构建重写提示
    prompt = REWRITE_PROMPT.format(question=question)
    
    # 调用模型重写问题
    response = response_model.invoke([{"role": "user", "content": prompt}])
    
    print(f"🔄 问题已重写: {response.content}")
    
    return {"messages": [HumanMessage(content=response.content)]}


# ============ 第六步：生成答案节点 ============
# 基于检索到的相关文档生成最终答案

# 定义生成答案的提示词
GENERATE_PROMPT = (
    "你是一个问答任务的助手。"
    "使用以下检索到的上下文来回答问题。"
    "如果你不知道答案，就说你不知道。"
    "最多使用三句话，保持答案简洁。\n"
    "问题：{question}\n"
    "上下文：{context}"
)

def generate_answer(state: MessagesState):
    """
    生成答案。
    
    参数:
        state: 包含消息历史的状态对象
        
    返回:
        包含生成答案的字典
    """
    # 获取原始问题和检索到的上下文
    question = state["messages"][0].content
    context = state["messages"][-1].content
    
    # 构建生成提示
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    
    # 调用模型生成答案
    response = response_model.invoke([{"role": "user", "content": prompt}])
    
    return {"messages": [response]}


# ============ 第七步：组装图 ============
# 将所有节点和边连接起来形成完整的工作流

print("🔨 正在构建 Agentic RAG 图...")

# 创建状态图
workflow = StateGraph(MessagesState)

# 添加所有节点
workflow.add_node("generate_query_or_respond", generate_query_or_respond)  # 决策节点
workflow.add_node("retrieve", ToolNode([retriever_tool]))  # 检索节点
workflow.add_node("rewrite_question", rewrite_question)  # 重写问题节点
workflow.add_node("generate_answer", generate_answer)  # 生成答案节点

# 设置起始边
workflow.add_edge(START, "generate_query_or_respond")

# 添加条件边：决定是否需要检索
workflow.add_conditional_edges(
    "generate_query_or_respond",
    tools_condition,  # 评估 LLM 决策（调用检索工具或直接响应用户）
    {
        "tools": "retrieve",  # 如果需要检索，跳转到检索节点
        END: END,  # 如果不需要检索，直接结束
    },
)

# 添加条件边：评估检索到的文档
workflow.add_conditional_edges(
    "retrieve",
    grade_documents,  # 评估文档相关性
    # 根据评分结果跳转到不同节点
)

# 添加固定边
workflow.add_edge("generate_answer", END)  # 生成答案后结束
workflow.add_edge("rewrite_question", "generate_query_or_respond")  # 重写问题后重新开始

# 编译图
graph = workflow.compile()

print("✅ Agentic RAG 图构建完成！")


# ============ LangGraph API 工厂函数 ============

def get_graph():
    """
    工厂函数 - 返回 Agentic RAG Agent Graph

    供 LangGraph API 使用

    Returns:
        编译好的 Agentic RAG Agent Graph
    """
    return graph


# ============ 第八步：运行 Agentic RAG ============
# 测试系统

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 开始测试 Agentic RAG 系统")
    print("=" * 60 + "\n")
    
    # 测试问题 1：需要检索的问题
    query1 = "什么是 LLM Agent？它有哪些关键组件？"
    
    print(f"📝 问题 1: {query1}\n")
    
    # 运行图
    for event in graph.stream(
        {"messages": [{"role": "user", "content": query1}]},
        stream_mode="values",
    ):
        # 打印最后一条消息
        event["messages"][-1].pretty_print()
        print("-" * 60)
    
    print("\n" + "=" * 60)
    
    # 测试问题 2：不需要检索的简单问题
    query2 = "你好！"
    
    print(f"📝 问题 2: {query2}\n")
    
    # 运行图
    for event in graph.stream(
        {"messages": [{"role": "user", "content": query2}]},
        stream_mode="values",
    ):
        # 打印最后一条消息
        event["messages"][-1].pretty_print()
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("✨ 测试完成！")
    print("=" * 60)
