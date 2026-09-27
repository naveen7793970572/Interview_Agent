import os
import glob
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# -----------------------------
# Load API Key
# Streamlit Cloud: reads from st.secrets
# Local: reads from .env file
# -----------------------------

load_dotenv()

try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    groq_api_key = os.getenv("GROQ_API_KEY")

os.environ["GROQ_API_KEY"] = groq_api_key or ""


# -----------------------------
# Load All Data Files Directly
# (Total size is tiny ~4KB — no vector DB needed)
# -----------------------------

def load_knowledge_base(data_dir: str = "data") -> str:
    """Read all .txt files from the data folder into one string."""
    knowledge = []
    for filepath in glob.glob(os.path.join(data_dir, "*.txt")):
        topic = os.path.splitext(os.path.basename(filepath))[0].upper()
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        knowledge.append(f"=== {topic} ===\n{content}")
    return "\n\n".join(knowledge)


KNOWLEDGE_BASE = load_knowledge_base()
print("Knowledge base loaded.")


# -----------------------------
# LLM (Groq)
# -----------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3
)
print("LLM connected.")


# -----------------------------
# LangGraph Agent
# -----------------------------

class AgentState(TypedDict):
    query: str
    response: str


def generate_answer(state: AgentState) -> dict:
    """Generate a precise answer using the LLM with the full knowledge base."""
    prompt = f"""You are an expert technical interview assistant with deep knowledge across ALL areas of computer science, software engineering, and technology.

A user has asked the following question:
"{state["query"]}"

Reference material from our knowledge base (use if relevant):
---
{KNOWLEDGE_BASE}
---

Instructions:
- Answer the user's question directly and precisely — no topic is off-limits.
- If they ask for interview questions on ANY topic, provide a comprehensive, well-structured numbered list with brief answers or explanations.
- If they ask to explain a concept, explain it clearly with examples.
- If they ask about coding problems, provide solutions with explanations.
- If they ask about system design, architecture, DevOps, cloud, ML, or anything else — answer fully.
- Use the reference material above only if it is relevant; otherwise rely on your own expert knowledge.
- Format your answer using markdown (bullet points, numbered lists, code blocks, bold headers) for readability.
- Be thorough, accurate, and helpful.
"""
    response = llm.invoke(prompt)
    return {"response": response.content}


# Build the graph (single-node: just generate the answer)
workflow = StateGraph(AgentState)
workflow.add_node("answer", generate_answer)
workflow.add_edge(START, "answer")
workflow.add_edge("answer", END)

agent = workflow.compile()


def ask(query: str) -> str:
    """Send a query to the agent and get a response."""
    result = agent.invoke({"query": query})
    return result["response"]
