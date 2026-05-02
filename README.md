# 🪙 TradeDB — Cryptocurrency & Stock Transaction Management System

> **Subject:** Database Management Systems (DBMS)  
> **Stack:** Oracle PL/SQL · Python (Tkinter) · HTML/CSS/JS  

---

## 📁 Project Structure

```
sql/
├── crypto_stock_db.sql    # Full Oracle PL/SQL schema (tables, DML, procedures, functions, triggers)
├── trading_frontend.py    # Python Tkinter GUI (demo mode with SQLite)
├── index.html             # Web Dashboard (main entry point)
├── styles.css             # Dashboard styling (dark theme)
├── data.js                # Demo data & SQL reference content
├── app.js                 # Dashboard application logic
└── README.md              # This file
```

---

## 🚀 How to Run

### Option 1: Web Dashboard (Recommended — No Setup Required)

1. Open a terminal and navigate to this folder:
   ```bash
   cd /path/to/sql
   ```
2. Open the dashboard:
   ```bash
   open index.html        # macOS
   xdg-open index.html    # Linux
   start index.html       # Windows
   ```
3. Or simply **double-click** `index.html` in Finder / File Explorer.

> **No server, no install, no dependencies.** Just open in any modern browser (Chrome, Firefox, Safari, Edge).

---

### Option 2: Python Tkinter GUI

1. Make sure Python 3 is installed:
   ```bash
   python3 --version
   ```
2. Run the GUI:
   ```bash
   python3 trading_frontend.py
   ```
3. The app launches in **Demo Mode** using an in-memory SQLite database.

> **Optional:** To connect to a real Oracle DB, install `cx_Oracle`:
> ```bash
> pip install cx_Oracle
> ```

---

### Option 3: Run the SQL Script on Oracle DB

1. Open Oracle SQL*Plus or SQL Developer.
2. Connect to your database.
3. Execute the script:
   ```sql
   @crypto_stock_db.sql
   ```

---

## 🖥️ Web Dashboard Features

| Section | Description |
|---------|-------------|
| **📊 Dashboard** | Live price ticker, stat cards, portfolio chart, BTC trend chart, recent transactions |
| **👤 Users** | Searchable user table with KYC & account status badges |
| **💰 Assets & Prices** | Asset cards with 7-day sparkline charts and price changes |
| **📋 Orders** | Filterable order book (All / Pending / Filled / Cancelled) |
| **🔄 Transactions** | Complete transaction ledger with fee breakdowns |
| **➕ Place Order** | Interactive order form — validates account, calculates 0.15% fee, updates data live |
| **🖥 SQL Reference** | Syntax-highlighted PL/SQL code with copy-to-clipboard |

---

## 🗄️ Database Schema

| Table | Description |
|-------|-------------|
| `USERS` | User accounts with KYC verification and status management |
| `ASSETS` | Tradeable assets (crypto, stocks, ETFs, commodities) |
| `WALLETS` | Per-user, per-asset balances with locking support |
| `PRICE_HISTORY` | OHLCV candle data at multiple intervals |
| `ORDERS` | Order book (BUY/SELL, MARKET/LIMIT/STOP) |
| `TRANSACTIONS` | Executed trade records with fees |
| `PORTFOLIO_SNAPSHOTS` | Daily portfolio value & PnL snapshots |

### PL/SQL Objects

| Type | Name | Purpose |
|------|------|---------|
| Procedure | `PLACE_BUY_ORDER` | Validates account, uses cursor to update wallet atomically |
| Procedure | `GENERATE_DAILY_SNAPSHOTS` | Batch job — iterates active users, calculates PnL, MERGE upsert |
| Function | `GET_USER_PNL` | Returns realized profit/loss (SELL - BUY) |
| Function | `GET_PORTFOLIO_VALUE` | Calculates live USD portfolio value |
| Trigger | `TRG_UPDATE_ORDER_STATUS` | Auto-marks orders as FILLED after transaction insert |
| Trigger | `TRG_BLOCK_SUSPENDED_ORDERS` | Prevents suspended/closed accounts from placing orders |

---

## 👤 Authors

- **Malhar Hajare** — DBMS Project

---

## 📄 License

This project is for academic/educational purposes.
