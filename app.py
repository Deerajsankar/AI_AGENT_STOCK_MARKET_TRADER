import streamlit as st
import yfinance as yf
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import tempfile
from portfolio_manager import PortfolioManager

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="Agentic RAG Trader", layout="wide")

# --- LOGIN & ONBOARDING SYSTEM ---
st.sidebar.header("🔐 User Profile")
user_id = st.sidebar.text_input("Username", value="Guest")

# Allow user to set starting money
initial_cash = st.sidebar.number_input(
    "Initial Investment ($)", 
    min_value=1000, 
    max_value=1000000, 
    value=10000, 
    step=1000
)

# Manage Session State for User Switching
if 'current_user' not in st.session_state:
    st.session_state.current_user = user_id

if st.session_state.current_user != user_id:
    st.session_state.current_user = user_id
    if 'manager' in st.session_state:
        del st.session_state.manager 
    if 'market_data' in st.session_state:
        del st.session_state.market_data

# Initialize Wallet
if 'manager' not in st.session_state:
    st.session_state.manager = PortfolioManager(user_id, initial_cash)

# ==========================================
# 2. PROFESSIONAL RAG PIPELINE
# ==========================================

@st.cache_resource
def initialize_vector_db(uploaded_file):
    if not uploaded_file: return None
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_path = tmp_file.name

    try:
        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = text_splitter.split_documents(documents)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vector_db = FAISS.from_documents(chunks, embeddings)
        return vector_db
    finally:
        if os.path.exists(tmp_path): os.remove(tmp_path)

def retrieve_strategy_rules(vector_db, query):
    if not vector_db: return "No Knowledge Base found.", 25 
    docs = vector_db.similarity_search(query, k=2)
    context_text = " ".join([d.page_content for d in docs])
    
    pe_limit = 25
    lower_context = context_text.lower()
    if "150" in lower_context or "growth" in lower_context: pe_limit = 150
    elif "conservative" in lower_context: pe_limit = 15
        
    return context_text, pe_limit

# ==========================================
# 3. MARKET DATA TOOL
# ==========================================
def tool_get_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if hist.empty: return None
        return {
            "price": hist['Close'].iloc[-1],
            "pe": stock.info.get('trailingPE', 0) or 0,
            "name": ticker.upper()
        }
    except: return None

# ==========================================
# 4. THE UI (Streamlit Frontend)
# ==========================================

st.sidebar.markdown("---")
st.sidebar.title("💼 Portfolio Dashboard")

# --- IMPROVED SIDEBAR DISPLAY ---
# 1. Cash Balance (Big Number)
current_cash = st.session_state.manager.portfolio["cash"]
st.sidebar.metric("💰 Available Cash", f"${current_cash:,.2f}")

# 2. Holdings Section (Dynamic List)
st.sidebar.subheader("🎒 My Holdings")
holdings = st.session_state.manager.portfolio["holdings"]

if holdings:
    # Loop through the dictionary and create a mini-card for each stock
    for ticker, qty in holdings.items():
        st.sidebar.info(f"**{ticker}**: {qty} Shares")
else:
    st.sidebar.warning("No stocks owned yet.")

# B. Upload Strategy
st.sidebar.markdown("---")
st.sidebar.header("📁 Knowledge Base")
uploaded_pdf = st.sidebar.file_uploader("Upload Strategy PDF", type="pdf")

vector_db = None
if uploaded_pdf:
    with st.sidebar.spinner("Ingesting Knowledge..."):
        vector_db = initialize_vector_db(uploaded_pdf)
    st.sidebar.success("✅ Brain Updated")

# --- MAIN PAGE ---
st.title("🤖 AI Agent : Stock Analyst & Trader")
st.markdown("I Analyze stocks using your PDF strategy and **Trade** them using your Virtual Wallet.")

# INPUT
col1, col2 = st.columns([2, 1])
ticker = col1.text_input("Enter Ticker (e.g., AAPL, TSLA):", "TSLA")

# --- CORE FIX: Store Data in Session State ---
if col1.button("Run Analysis"):
    with st.spinner("Analyzing Market & Strategy..."):
        data = tool_get_stock_data(ticker)
        if data:
            st.session_state.market_data = data 
            st.session_state.analysis_done = True
        else:
            st.error("Ticker not found.")

# Display Results if Analysis was run (Persists across reloads)
if 'analysis_done' in st.session_state and st.session_state.analysis_done:
    market_data = st.session_state.market_data
    
    # 1. RAG DECISION
    query = "What is the P/E limit?"
    context, limit = retrieve_strategy_rules(vector_db, query)
    
    verdict = "BUY"
    color = "green"
    if market_data['pe'] > limit:
        verdict = "SELL"
        color = "red"
    
    # 2. DISPLAY METRICS
    st.markdown("---")
    m1, m2, m3 = st.columns(3)
    m1.metric("Price", f"${market_data['price']:.2f}")
    m2.metric("P/E Ratio", f"{market_data['pe']:.1f}")
    m3.metric("Limit", f"<{limit}")
    
    st.subheader(f"Analyst Verdict: :{color}[{verdict}]")
    
    # 3. TRADING ACTION BUTTONS
    st.markdown("### ⚡ Execute Trade")
    c1, c2 = st.columns(2)
    
    # BUY BUTTON
    if c1.button(f"BUY 1 {market_data['name']}"):
        success, msg = st.session_state.manager.buy_stock(market_data['name'], market_data['price'], 1)
        if success: 
            st.balloons()
            st.success(msg)
        else:
            st.error(msg)
        st.rerun() # Refresh to update wallet sidebar
    
    # SELL BUTTON
    if c2.button(f"SELL 1 {market_data['name']}"):
        success, msg = st.session_state.manager.sell_stock(market_data['name'], market_data['price'], 1)
        if success:
            st.success(msg)
        else:
            st.error(msg)
        st.rerun() # Refresh to update wallet sidebar