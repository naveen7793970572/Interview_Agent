import os
import glob
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from typing import TypedDict, Literal
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
    temperature=0
)
print("LLM connected.")


# -----------------------------
# LangGraph Agent with Guardrail
# -----------------------------

class AgentState(TypedDict):
    query: str
    is_relevant: bool
    response: str


# ---- Node 1: Guardrail ----

def check_relevance(state: AgentState) -> dict:
    """
    Classify whether the query is related to academic subjects,
    interview preparation, or technical/educational topics.
    """
    prompt = f"""You are a strict topic classifier for an Interview Preparation Assistant.

Your job is to decide if the user's question is related to ANY of the following allowed categories:
- Academic subjects (Mathematics, Physics, Chemistry, Biology, History, Geography, Economics, etc.)
- Computer Science & Engineering (Programming, DSA, DBMS, OS, Networking, etc.)
- Interview preparation questions for ANY subject or field
- Technical concepts, algorithms, system design, DevOps, Cloud, AI/ML
- Aptitude, reasoning, or logical questions asked in interviews
- Any subject taught in schools, colleges, or universities
- Career guidance related to studies or technical jobs

NOT ALLOWED (return IRRELEVANT):
- Current events, news, politics
- Celebrity or sports gossip
- Specific people's personal lives (politicians, actors, cricketers, etc.)
- Entertainment, movies, songs
- General chit-chat or personal questions
- Questions about specific places, colleges, people, or organizations that are NOT educational in nature

User's question:
"{state["query"]}"

Respond with ONLY one word:
- RELEVANT (if it fits any allowed category)
- IRRELEVANT (if it does not)
"""
    response = llm.invoke(prompt)
    decision = response.content.strip().upper()
    is_relevant = "RELEVANT" in decision
    return {"is_relevant": is_relevant}


# ---- Router ----

def route_query(state: AgentState) -> Literal["answer", "refuse"]:
    """Route to answer node or refuse node based on relevance check."""
    return "answer" if state["is_relevant"] else "refuse"


# ---- Node 2a: Answer ----

def generate_answer(state: AgentState) -> dict:
    """Generate a precise answer using the LLM with the full knowledge base."""
    prompt = f"""You are an expert Interview Preparation Assistant with deep knowledge across ALL academic subjects and technical domains.

A user has asked the following question:
"{state["query"]}"

Reference material from our knowledge base (use if relevant):
---
{KNOWLEDGE_BASE}
---

Instructions:
- Answer the user's question directly and precisely.
- If they ask for interview questions on ANY topic (technical or academic), provide a comprehensive, numbered list with brief answers or explanations.
- If they ask to explain a concept, explain it clearly with examples.
- If they ask about coding problems, provide solutions with explanations.
- Use the reference material above only if it is relevant; otherwise rely on your own expert knowledge.
- Format your answer using markdown (bullet points, numbered lists, code blocks, bold headers) for readability.
- Be thorough, accurate, and helpful.
"""
    response = llm.invoke(prompt)
    return {"response": response.content}


# ---- Node 2b: Refuse ----

def refuse_answer(state: AgentState) -> dict:
    """Return a polite refusal for off-topic questions."""
    return {
        "response": (
            "🚫 **I'm not authorized to answer this question.**\n\n"
            "This assistant is designed **only** for interview preparation and academic learning.\n\n"
            "I can help you with:\n"
            "- 📚 Interview questions for any subject or technical domain\n"
            "- 💡 Concepts from Computer Science, Math, Science, and more\n"
            "- 🧠 DSA, DBMS, OS, Networking, System Design\n"
            "- 🎯 Aptitude and reasoning questions\n\n"
            "Please ask a question related to studies, academics, or interview preparation!"
        )
    }


# ---- Build the Graph ----

workflow = StateGraph(AgentState)

workflow.add_node("check", check_relevance)
workflow.add_node("answer", generate_answer)
workflow.add_node("refuse", refuse_answer)

workflow.add_edge(START, "check")
workflow.add_conditional_edges("check", route_query, {"answer": "answer", "refuse": "refuse"})
workflow.add_edge("answer", END)
workflow.add_edge("refuse", END)

agent = workflow.compile()


def ask(query: str) -> str:
    """Send a query to the agent and get a response."""
    result = agent.invoke({"query": query})
    return result["response"]
