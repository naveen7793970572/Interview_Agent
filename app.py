import os
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# Load environment variables
# Streamlit Cloud: reads from st.secrets
# Local: reads from .env file
load_dotenv()

try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    groq_api_key = os.getenv("GROQ_API_KEY")

os.environ["GROQ_API_KEY"] = groq_api_key or ""



# -----------------------------
# 1. Load Documents
# -----------------------------

loader = DirectoryLoader(
    "data",
    glob="*.txt",
    loader_cls=TextLoader
)
documents = loader.load()
print(f"Loaded {len(documents)} documents.")


# -----------------------------
# 2. Split Documents
# -----------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = text_splitter.split_documents(documents)
print(f"Split into {len(chunks)} chunks.")


# -----------------------------
# 3. Embeddings + Vector Store
# -----------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
print("Vector store ready.")


# -----------------------------
# 4. LLM
# -----------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3
)
print("LLM connected.")


# -----------------------------
# 5. LangGraph Agent
# -----------------------------

class AgentState(TypedDict):
    query: str
    context: str
    response: str


def retrieve_context(state: AgentState):
    """Retrieve relevant context from the vector store."""
    results = retriever.invoke(state["query"])
    context = "\n\n".join(doc.page_content for doc in results)
    return {"context": context}


def generate_answer(state: AgentState):
    """Generate a precise answer using the LLM with retrieved context."""
    prompt = f"""You are an expert technical interview assistant with deep knowledge across ALL areas of computer science, software engineering, and technology.

A user has asked the following question:
"{state["query"]}"

Additional reference material (if relevant):
---
{state["context"]}
---

Instructions:
- Answer the user's question directly and precisely — no topic is off-limits.
- If they ask for interview questions on ANY topic, provide a comprehensive, well-structured list with brief answers or explanations.
- If they ask to explain a concept, explain it clearly with examples.
- If they ask about coding problems, provide solutions with explanations.
- If they ask about system design, architecture, DevOps, cloud, ML, or anything else — answer fully.
- Use the reference material above only if it is relevant; otherwise rely on your own knowledge.
- Format your answer using markdown (bullet points, numbered lists, code blocks, bold headers) for readability.
- Be thorough, accurate, and helpful.
"""
    response = llm.invoke(prompt)
    return {"response": response.content}


# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve_context)
workflow.add_node("answer", generate_answer)

workflow.add_edge(START, "retrieve")
workflow.add_edge("retrieve", "answer")
workflow.add_edge("answer", END)

agent = workflow.compile()


def ask(query: str) -> str:
    """Send a query to the agent and get a response."""
    result = agent.invoke({"query": query})
    return result["response"]
