import json
import os
from datetime import datetime

class PortfolioManager:
    def __init__(self, user_id="default_user", initial_capital=10000.0):
        # 1. Capture the User ID (Name Tag)
        self.user_id = user_id
        
        # 2. Create/Find the UNIQUE file (The Box Number)
        self.filename = f"portfolio_{self.user_id}.json"
        
        # 3. Load or Create the Wallet
        self.portfolio = self.load_portfolio(initial_capital)

    def load_portfolio(self, initial_capital):
        """
        Logic:
        1. If user file EXISTS -> Load it (Ignore initial_capital input).
        2. If user file MISSING -> Create new wallet with initial_capital.
        """
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    return json.load(f)
            except:
                print(f"⚠️ Error reading {self.filename}. Resetting.")
        
        # CREATE NEW USER with THEIR custom amount
        return {
            "cash": float(initial_capital),
            "holdings": {},
            "history": []
        }

    def save_portfolio(self):
        """Saves to the USER'S specific file"""
        with open(self.filename, "w") as f:
            json.dump(self.portfolio, f, indent=4)

    def buy_stock(self, ticker, price, quantity):
        ticker = ticker.upper()
        total_cost = price * quantity
        
        if self.portfolio["cash"] >= total_cost:
            self.portfolio["cash"] -= total_cost
            current_qty = self.portfolio["holdings"].get(ticker, 0)
            self.portfolio["holdings"][ticker] = current_qty + quantity
            self.log_transaction("BUY", ticker, price, quantity)
            self.save_portfolio()
            return True, f"✅ BOUGHT {quantity} {ticker} @ ${price:.2f}"
        else:
            return False, f"❌ INSUFFICIENT FUNDS. Need ${total_cost:.2f}"

    def sell_stock(self, ticker, price, quantity):
        ticker = ticker.upper()
        current_qty = self.portfolio["holdings"].get(ticker, 0)
        
        if current_qty >= quantity:
            total_revenue = price * quantity
            self.portfolio["cash"] += total_revenue
            self.portfolio["holdings"][ticker] = current_qty - quantity
            if self.portfolio["holdings"][ticker] == 0:
                del self.portfolio["holdings"][ticker]
            self.log_transaction("SELL", ticker, price, quantity)
            self.save_portfolio()
            return True, f"✅ SOLD {quantity} {ticker} @ ${price:.2f}"
        else:
            return False, f"❌ NOT ENOUGH SHARES. Own {current_qty}"

    def log_transaction(self, action, ticker, price, qty):
        record = {
            "date": str(datetime.now()),
            "action": action,
            "ticker": ticker,
            "price": price,
            "qty": qty,
            "balance_after": self.portfolio["cash"]
        }
        self.portfolio["history"].append(record)

    def get_status(self):
        return f"👤 {self.user_id} | 💰 ${self.portfolio['cash']:.2f} | 🎒 {self.portfolio['holdings']}"