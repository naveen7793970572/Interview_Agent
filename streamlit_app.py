import streamlit as st
from app import ask

# -----------------------------
# Page Config
# -----------------------------

st.set_page_config(
    page_title="Interview Q&A Assistant",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# Custom CSS
# -----------------------------

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
    }

    .main-header h1 {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
    }

    .main-header p {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 0;
    }

    .topic-pill {
        display: inline-block;
        background: rgba(167, 139, 250, 0.15);
        border: 1px solid rgba(167, 139, 250, 0.4);
        color: #c4b5fd;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 0.2rem;
    }

    .chat-user {
        background: rgba(96, 165, 250, 0.12);
        border: 1px solid rgba(96, 165, 250, 0.25);
        border-radius: 16px 16px 4px 16px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
    }

    .chat-assistant {
        background: rgba(52, 211, 153, 0.08);
        border: 1px solid rgba(52, 211, 153, 0.2);
        border-radius: 16px 16px 16px 4px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
    }

    .chat-label-user {
        font-size: 0.75rem;
        color: #60a5fa;
        font-weight: 600;
        margin-bottom: 0.3rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .chat-label-bot {
        font-size: 0.75rem;
        color: #34d399;
        font-weight: 600;
        margin-bottom: 0.3rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .suggestion-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 0.9rem 1rem;
        color: #cbd5e1;
        font-size: 0.88rem;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 0.5rem;
    }

    .suggestion-card:hover {
        background: rgba(167, 139, 250, 0.1);
        border-color: rgba(167, 139, 250, 0.4);
        color: #e2e8f0;
    }

    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stButton"]) button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: #cbd5e1 !important;
        border-radius: 12px !important;
        text-align: left !important;
        width: 100% !important;
        padding: 0.8rem 1rem !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stButton"]) button:hover {
        background: rgba(167, 139, 250, 0.15) !important;
        border-color: rgba(167, 139, 250, 0.5) !important;
        color: #e2e8f0 !important;
    }

    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: #f1f5f9 !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(167, 139, 250, 0.6) !important;
        box-shadow: 0 0 0 2px rgba(167, 139, 250, 0.15) !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #64748b !important;
    }

    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
        border: none !important;
        border-radius: 12px !important;
        color: white !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 0.6rem 1.8rem !important;
        transition: all 0.2s ease !important;
    }

    div[data-testid="stButton"] > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
    }

    .divider {
        border: none;
        border-top: 1px solid rgba(255,255,255,0.07);
        margin: 1.5rem 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.8) !important;
        border-right: 1px solid rgba(255,255,255,0.07) !important;
    }

    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li {
        color: #94a3b8 !important;
        font-size: 0.88rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #c4b5fd !important;
    }

    .clear-btn button {
        background: rgba(239, 68, 68, 0.1) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: #f87171 !important;
        border-radius: 10px !important;
        font-size: 0.85rem !important;
    }

    .clear-btn button:hover {
        background: rgba(239, 68, 68, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Header
# -----------------------------

st.markdown("""
<div class="main-header">
    <h1>🤖 Interview Q&amp;A Assistant</h1>
    <p>Ask <strong>any</strong> technical or interview question</p>
    <div style="margin-top: 0.8rem;">
        <span class="topic-pill">☕ Java</span>
        <span class="topic-pill">🌳 DSA</span>
        <span class="topic-pill">🗄️ DBMS</span>
        <span class="topic-pill">💻 OS</span>
        <span class="topic-pill">☁️ System Design</span>
        <span class="topic-pill">🐳 DevOps</span>
        <span class="topic-pill">🤖 ML/AI</span>
        <span class="topic-pill">🐍 Python</span>
    </div>
</div>
""", unsafe_allow_html=True)


# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:
    st.markdown("## 📚 About")
    st.markdown("""
Ask **any** interview-related question

**Areas covered (and more):**
- **Java / Python / C++** – OOP, collections, frameworks
- **DSA** – Arrays, Trees, Graphs, DP, Sorting
- **DBMS / SQL** – Normalization, Transactions, Indexing
- **OS** – Processes, Memory, Scheduling, Deadlocks
- **System Design** – Scalability, Microservices, APIs
- **DevOps / Cloud** – Docker, Kubernetes, AWS
- **ML / AI** – Concepts, algorithms, interview prep
- **And literally anything else!**

**How to use:**
1. Type your question in the chat box
2. Press **Ask** or hit Enter
3. Get precise, structured answers!
    """)

    st.markdown("<hr style='border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

    st.markdown("### 🔧 Session")
    with st.container():
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if "chat_history" in st.session_state:
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")


# -----------------------------
# Session State
# -----------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""


# -----------------------------
# Suggested Questions
# -----------------------------

if not st.session_state.chat_history:
    st.markdown("### 💡 Try asking...")
    cols = st.columns(2)
    suggestions = [
        "🔥 Give me 10 Java interview questions",
        "🌳 Explain Binary Search Tree with example",
        "☁️ Top System Design interview questions",
        "🐍 Python vs Java — key differences",
        "🤖 Common Machine Learning interview questions",
        "🐳 What is Docker and how does it work?",
        "🗄️ What is normalization in DBMS?",
        "💻 Explain deadlock and how to prevent it",
    ]
    for i, suggestion in enumerate(suggestions):
        with cols[i % 2]:
            if st.button(suggestion, key=f"sug_{i}"):
                st.session_state.pending_query = suggestion
                st.rerun()

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# -----------------------------
# Display Chat History
# -----------------------------

for entry in st.session_state.chat_history:
    st.markdown(f"""
    <div class="chat-user">
        <div class="chat-label-user">👤 You</div>
        {entry["query"]}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="chat-assistant">
        <div class="chat-label-bot">🤖 Assistant</div>
    </div>
    """, unsafe_allow_html=True)

    # Use st.markdown for the response to render markdown properly
    st.markdown(entry["response"])
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)


# -----------------------------
# Input Area
# -----------------------------

col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Ask your question",
        value=st.session_state.pending_query,
        placeholder="e.g. Give me interview questions on Java multithreading...",
        label_visibility="collapsed",
        key="user_input_box"
    )

with col2:
    ask_btn = st.button("Ask ✨", type="primary", use_container_width=True)


# -----------------------------
# Handle Query
# -----------------------------

query_to_process = ""

if ask_btn and user_input.strip():
    query_to_process = user_input.strip()
elif st.session_state.pending_query:
    query_to_process = st.session_state.pending_query
    st.session_state.pending_query = ""

if query_to_process:
    with st.spinner("🔍 Thinking..."):
        response = ask(query_to_process)

    st.session_state.chat_history.append({
        "query": query_to_process,
        "response": response
    })

    st.rerun()