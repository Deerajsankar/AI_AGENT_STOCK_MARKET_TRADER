# 🤖 Agentic RAG: Stock Analyst & Autonomous Trader

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![LangChain](https://img.shields.io/badge/Framework-LangChain-green)
![FAISS](https://img.shields.io/badge/Vector%20DB-FAISS-yellow)
![Status](https://img.shields.io/badge/Status-MVP%20Complete-success)

## 📖 Executive Summary
We developed an **Autonomous AI Investment Agent** that bridges the gap between static knowledge and real-time action. While traditional RAG systems can only *answer questions* from a document, this Agent actively *applies* that knowledge to the real world.

**What we actually built:**
1.  **A "Learning" Analyst:** The system ingests custom trading strategies (PDFs), "reads" them using Vector Search, and understands specific rules (e.g., "Buy if P/E < 20").
2.  **Real-Time Execution:** It connects to the **Live Stock Market** (via Yahoo Finance) to fetch real-time prices and compares them against the user's strategy.
3.  **Automated Trading:** Instead of just giving advice, the Agent has **"Hands"**—it autonomously executes buy/sell orders and manages a persistent virtual wallet for multiple users (e.g., keeping Deeraj's money separate from Dhoni'

## 🏗️ System Architecture

The Agent operates on a cognitive **Perceive-Reason-Act** loop:

| Component | Role | Technology Stack |
| :--- | :--- | :--- |
| **🧠 Brain (Knowledge)** | Stores trading rules & strategies. | **RAG Pipeline**: PDF → FAISS Vector DB → LLM |
| **👀 Eyes (Perception)** | Fetches live market data. | **Tool**: `yfinance` API (Real-time Prices & P/E Ratios) |
| **✋ Hands (Action)** | Executes buy/sell orders. | **Tool**: `PortfolioManager` Class (Transaction Logic) |
| **💾 Memory (State)** | Persists user funds & holdings. | **Database**: JSON-based Ledger (`portfolio_{user}.json`) |

### 🔄 The Agentic Workflow
1.  **Input:** User asks to analyze a stock (e.g., "TSLA").
2.  **Perception:** Agent fetches live price ($400) and P/E ratio (50) via `yfinance`.
3.  **Retrieval:** Agent queries the Vector DB for strategy rules (e.g., "Buy if P/E < 25").
4.  **Reasoning:** Agent compares **Data (50)** vs. **Rule (25)** → Verdict: **SELL**.
5.  **Action:** If the user approves, the Agent updates the JSON ledger to deduct cash/add stock.

---

## 📂 Project Structure

The project follows a modular "Source Folder" structure to separate core logic from configuration.

```text
F:\Agentic_RAG_Module1\
├── AI_AGENT\                   # 🧠 Core Source Code
│   ├── app.py                  # Frontend Orchestrator (Streamlit)
│   ├── portfolio_manager.py    # Backend Logic (Ledger & State Management)
│   ├── portfolio_Deeraj.json   # Auto-generated User Database
│   └── portfolio_Virat.json    # Auto-generated User Database
├── requirements.txt            # Dependency Management
├── .gitignore                  # Git Configuration
└── README.md                   # Project Documentation
```

---

## 🚀 Key Features

### 1. Multi-User Authentication (NoSQL Style)
- Dynamic login system where users enter a username (e.g., "Deeraj").
- Automatically hydrates the specific user's portfolio state (`cash`, `holdings`) from the disk.
- Ensures data isolation: User A cannot see or spend User B's money.

### 2. Live "Simulation Mode" & Timezone Handling
- **The Challenge:** The US Market (NYSE) is closed during Indian daytime (IST).
- **The Solution:** The Agent defaults to **Simulation Mode**, utilizing the *last available closing price* to allow 24/7 testing.
- **Strict Mode (Optional):** Developers can enforce strict US Market Hours (9:30 AM - 4:00 PM EST) by using the following logic in `app.py`:

```python
from datetime import datetime, time
import pytz

def is_market_open():
    """Checks if US Market is open (09:30 - 16:00 EST, Mon-Fri)"""
    ny_now = datetime.now(pytz.timezone('US/Eastern'))
    if ny_now.weekday() >= 5: return False # Weekend
    return time(9, 30) <= ny_now.time() <= time(16, 0)

# Use in app.py:
# if not is_market_open(): st.error("Market Closed")
```

### 3. Integrated RAG Pipeline
- Users can upload custom Strategy PDFs (e.g., "Warren Buffet Principles").
- The system chunks, embeds, and indexes the document into a FAISS Vector Store on the fly.
- The Agent bases its "Buy/Sell" verdict on *this specific document*.

---

## 🛠️ Installation & Setup

**1. Clone the Repository**
```bash
git clone [https://github.com/YOUR_USERNAME/Agentic_RAG_Trader.git](https://github.com/YOUR_USERNAME/Agentic_RAG_Trader.git)
cd Agentic_RAG_Trader
```

**2. Install Dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the Application**
> ⚠️ **Important:** You must navigate into the `AI_AGENT` folder first!
```bash
cd AI_AGENT
streamlit run app.py
```

---

## 🔮 Future Roadmap
- [ ] **Database Migration:** Move from JSON files to **SQLite/PostgreSQL** for enterprise scaling.
- [ ] **LLM Integration:** Connect to DeepSeek-R1 or OpenAI for unstructured reasoning explanations.
- [ ] **Limit Orders:** Add functionality to "Buy at X Price" rather than Market Orders.

---

## ⚖️ Disclaimer
This project is for **educational and demonstration purposes only**. The financial analysis provided by the AI Agent is based on simulated strategies and should not be used for real-world investment decisions.
