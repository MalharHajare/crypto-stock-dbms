"""
Cryptocurrency & Stock Transaction Management System
Python Frontend — runs against Oracle DB (cx_Oracle) or SQLite (demo mode)
Usage:
    pip install cx_Oracle         # for real Oracle DB
    python trading_frontend.py    # launches the GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sqlite3
import datetime
import random

# ─────────────────────────────────────────────
# COLOURS & FONTS
# ─────────────────────────────────────────────
BG        = "#0D1117"
PANEL     = "#161B22"
CARD      = "#1C2128"
ACCENT    = "#58A6FF"
GREEN     = "#3FB950"
RED       = "#F85149"
AMBER     = "#D29922"
TEXT      = "#E6EDF3"
MUTED     = "#8B949E"
BORDER    = "#30363D"

FONT_HEAD = ("Segoe UI", 13, "bold")
FONT_BODY = ("Segoe UI", 10)
FONT_MONO = ("Consolas", 10)
FONT_BIG  = ("Segoe UI", 22, "bold")

# ─────────────────────────────────────────────
# DEMO DATABASE (SQLite)
# ─────────────────────────────────────────────
def init_demo_db():
    conn = sqlite3.connect(":memory:")
    cur  = conn.cursor()

    cur.executescript("""
        CREATE TABLE USERS (
            user_id        INTEGER PRIMARY KEY,
            username       TEXT NOT NULL UNIQUE,
            email          TEXT NOT NULL UNIQUE,
            full_name      TEXT,
            country        TEXT,
            kyc_verified   TEXT DEFAULT 'N',
            account_status TEXT DEFAULT 'ACTIVE',
            created_at     TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE ASSETS (
            asset_id   INTEGER PRIMARY KEY,
            symbol     TEXT NOT NULL UNIQUE,
            asset_name TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            exchange   TEXT,
            currency   TEXT DEFAULT 'USD',
            is_active  TEXT DEFAULT 'Y'
        );

        CREATE TABLE WALLETS (
            wallet_id    INTEGER PRIMARY KEY,
            user_id      INTEGER REFERENCES USERS(user_id),
            asset_id     INTEGER REFERENCES ASSETS(asset_id),
            balance      REAL DEFAULT 0,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, asset_id)
        );

        CREATE TABLE ORDERS (
            order_id   INTEGER PRIMARY KEY,
            user_id    INTEGER REFERENCES USERS(user_id),
            asset_id   INTEGER REFERENCES ASSETS(asset_id),
            order_type TEXT,
            order_mode TEXT DEFAULT 'MARKET',
            quantity   REAL,
            limit_price REAL,
            status     TEXT DEFAULT 'PENDING',
            placed_at  TEXT DEFAULT CURRENT_TIMESTAMP,
            filled_at  TEXT
        );

        CREATE TABLE TRANSACTIONS (
            txn_id         INTEGER PRIMARY KEY,
            order_id       INTEGER,
            user_id        INTEGER REFERENCES USERS(user_id),
            asset_id       INTEGER REFERENCES ASSETS(asset_id),
            txn_type       TEXT,
            quantity       REAL,
            price_per_unit REAL,
            total_amount   REAL,
            fee_amount     REAL DEFAULT 0,
            net_amount     REAL,
            txn_at         TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE PRICE_HISTORY (
            price_id    INTEGER PRIMARY KEY,
            asset_id    INTEGER REFERENCES ASSETS(asset_id),
            recorded_at TEXT,
            close_price REAL,
            volume      REAL,
            interval_type TEXT DEFAULT '1D'
        );
    """)

    # Seed users
    users = [
        (101,"aryan_shah","aryan@trade.com","Aryan Shah","India","Y","ACTIVE"),
        (102,"priya_k","priya@trade.com","Priya Kumar","India","Y","ACTIVE"),
        (103,"ravi_m","ravi@trade.com","Ravi Menon","USA","N","ACTIVE"),
        (104,"test_sus","sus@trade.com","Suspended User","UK","Y","SUSPENDED"),
    ]
    cur.executemany(
        "INSERT INTO USERS VALUES(?,?,?,?,?,?,?,CURRENT_TIMESTAMP)", users)

    # Seed assets
    assets = [
        (1,"BTC","Bitcoin","CRYPTO","Binance","USD","Y"),
        (2,"ETH","Ethereum","CRYPTO","Binance","USD","Y"),
        (3,"SOL","Solana","CRYPTO","Binance","USD","Y"),
        (4,"AAPL","Apple Inc","STOCK","NASDAQ","USD","Y"),
        (5,"TSLA","Tesla Inc","STOCK","NASDAQ","USD","Y"),
    ]
    cur.executemany(
        "INSERT INTO ASSETS VALUES(?,?,?,?,?,?,?)", assets)

    # Seed price history
    prices = {1:62000, 2:3200, 3:145, 4:189, 5:254}
    pid = 1
    for aid, base in prices.items():
        for i in range(7):
            close = round(base * (1 + random.uniform(-0.05, 0.05)), 2)
            dt = (datetime.datetime.now() - datetime.timedelta(days=i)).isoformat()
            cur.execute(
                "INSERT INTO PRICE_HISTORY VALUES(?,?,?,?,?,?)",
                (pid, aid, dt, close, random.randint(1000,9999), "1D"))
            pid += 1

    # Seed wallets
    wallets = [
        (1, 101, 1, 1.5), (2, 101, 2, 10.0),
        (3, 102, 1, 0.5), (4, 102, 3, 200.0),
        (5, 103, 4, 50.0),
    ]
    cur.executemany(
        "INSERT INTO WALLETS VALUES(?,?,?,?,CURRENT_TIMESTAMP)", wallets)

    # Seed transactions
    txns = [
        (1,1,101,1,"BUY",1.5,60000,90000,135,89865),
        (2,2,101,2,"BUY",10,3000,30000,45,29955),
        (3,3,102,1,"BUY",0.5,58000,29000,43.5,28956.5),
        (4,4,102,3,"BUY",200,120,24000,36,23964),
        (5,5,103,4,"BUY",50,180,9000,13.5,8986.5),
    ]
    cur.executemany(
        "INSERT INTO TRANSACTIONS VALUES(?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)",txns)

    conn.commit()
    return conn


# ─────────────────────────────────────────────
# HELPER: styled label
# ─────────────────────────────────────────────
def lbl(parent, text, fg=TEXT, font=FONT_BODY, bg=None, **kw):
    return tk.Label(parent, text=text, fg=fg, font=font,
                    bg=bg or parent["bg"], **kw)


# ─────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────
class TradingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Crypto & Stock Trading Platform — DBMS Demo")
        self.geometry("1200x750")
        self.configure(bg=BG)
        self.resizable(True, True)

        self.conn = init_demo_db()

        self._build_sidebar()
        self._build_main()
        self._show_dashboard()

    # ── SIDEBAR ──────────────────────────────
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=PANEL, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        lbl(self.sidebar, "  TradeDB", fg=ACCENT, font=("Segoe UI",15,"bold"),
            bg=PANEL).pack(anchor="w", pady=(20,4), padx=10)
        lbl(self.sidebar, "  DBMS Project", fg=MUTED, bg=PANEL,
            font=("Segoe UI",9)).pack(anchor="w", padx=10)

        sep = tk.Frame(self.sidebar, bg=BORDER, height=1)
        sep.pack(fill="x", padx=10, pady=16)

        self.nav_btns = {}
        nav = [
            ("Dashboard",    "📊", self._show_dashboard),
            ("Users",        "👤", self._show_users),
            ("Assets",       "💰", self._show_assets),
            ("Orders",       "📋", self._show_orders),
            ("Transactions", "🔄", self._show_transactions),
            ("Place Order",  "➕", self._show_place_order),
            ("SQL Query",    "🖥", self._show_sql),
        ]
        for name, icon, cmd in nav:
            btn = tk.Button(self.sidebar,
                text=f"  {icon}  {name}", anchor="w",
                bg=PANEL, fg=TEXT, font=FONT_BODY,
                bd=0, activebackground=CARD, activeforeground=ACCENT,
                cursor="hand2", pady=8, padx=12,
                command=lambda c=cmd, n=name: self._nav(c, n))
            btn.pack(fill="x", padx=4)
            self.nav_btns[name] = btn

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=10, pady=16)
        lbl(self.sidebar, "  Demo Mode (SQLite)", fg=AMBER, bg=PANEL,
            font=("Segoe UI",8)).pack(anchor="w", padx=10)
        lbl(self.sidebar, "  Connect Oracle DB\n  via cx_Oracle", fg=MUTED, bg=PANEL,
            font=("Segoe UI",8)).pack(anchor="w", padx=10, pady=2)

    def _nav(self, cmd, name):
        for n, b in self.nav_btns.items():
            b.config(bg=PANEL if n != name else CARD, fg=TEXT if n != name else ACCENT)
        cmd()

    # ── MAIN AREA ─────────────────────────────
    def _build_main(self):
        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

    def _clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    # ── DASHBOARD ────────────────────────────
    def _show_dashboard(self):
        self._clear_main()
        f = self.main

        # Title bar
        tb = tk.Frame(f, bg=PANEL, pady=12)
        tb.pack(fill="x")
        lbl(tb, "  Dashboard", fg=TEXT, font=FONT_HEAD, bg=PANEL).pack(side="left")
        lbl(tb, datetime.datetime.now().strftime("  %d %b %Y, %H:%M"),
            fg=MUTED, bg=PANEL).pack(side="right", padx=16)

        # Stat cards
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM USERS WHERE account_status='ACTIVE'")
        active_users = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM ORDERS WHERE status='PENDING'")
        pending_orders = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM TRANSACTIONS")
        total_txns = cur.fetchone()[0]
        cur.execute("SELECT ROUND(SUM(total_amount),2) FROM TRANSACTIONS")
        vol = cur.fetchone()[0] or 0

        cards_frame = tk.Frame(f, bg=BG)
        cards_frame.pack(fill="x", padx=20, pady=20)

        stats = [
            ("Active Users",     str(active_users),   GREEN),
            ("Pending Orders",   str(pending_orders), AMBER),
            ("Total Transactions",str(total_txns),    ACCENT),
            ("Volume (USD)",     f"${vol:,.2f}",      "#DA8FFF"),
        ]
        for title, val, color in stats:
            card = tk.Frame(cards_frame, bg=CARD, bd=0, padx=20, pady=18)
            card.pack(side="left", expand=True, fill="x", padx=8)
            lbl(card, title, fg=MUTED, bg=CARD, font=("Segoe UI",9)).pack(anchor="w")
            lbl(card, val, fg=color, bg=CARD, font=("Segoe UI",20,"bold")).pack(anchor="w")

        # Recent transactions
        lbl(f, "  Recent Transactions", fg=TEXT, font=FONT_HEAD,
            bg=BG).pack(anchor="w", padx=20, pady=(10,6))

        cols = ("TXN ID","User","Asset","Type","Qty","Price","Amount","Date")
        tv   = self._make_table(f, cols)

        cur.execute("""
            SELECT t.txn_id, u.username, a.symbol, t.txn_type,
                   t.quantity, t.price_per_unit, t.total_amount, t.txn_at
            FROM TRANSACTIONS t
            JOIN USERS u  ON u.user_id  = t.user_id
            JOIN ASSETS a ON a.asset_id = t.asset_id
            ORDER BY t.txn_id DESC LIMIT 20
        """)
        for row in cur.fetchall():
            tag = "buy" if row[3]=="BUY" else "sell"
            tv.insert("", "end", values=row, tags=(tag,))
        tv.tag_configure("buy",  foreground=GREEN)
        tv.tag_configure("sell", foreground=RED)

    # ── USERS ────────────────────────────────
    def _show_users(self):
        self._clear_main()
        self._table_page("Users", """
            SELECT user_id, username, email, full_name, country,
                   kyc_verified, account_status, created_at
            FROM USERS ORDER BY user_id
        """, ("ID","Username","Email","Full Name","Country","KYC","Status","Created"))

    # ── ASSETS ───────────────────────────────
    def _show_assets(self):
        self._clear_main()

        lbl(self.main, "  Assets & Live Prices", fg=TEXT, font=FONT_HEAD,
            bg=BG).pack(anchor="w", padx=20, pady=16)

        cols = ("ID","Symbol","Name","Type","Exchange","Currency","Active","Latest Price")
        tv   = self._make_table(self.main, cols)

        cur = self.conn.cursor()
        cur.execute("""
            SELECT a.asset_id, a.symbol, a.asset_name, a.asset_type,
                   a.exchange, a.currency, a.is_active,
                   (SELECT ROUND(ph.close_price,2)
                    FROM PRICE_HISTORY ph
                    WHERE ph.asset_id=a.asset_id
                    ORDER BY ph.recorded_at DESC LIMIT 1) AS latest_price
            FROM ASSETS a ORDER BY a.asset_id
        """)
        for row in cur.fetchall():
            tv.insert("", "end", values=row)

    # ── ORDERS ───────────────────────────────
    def _show_orders(self):
        self._clear_main()
        self._table_page("Orders", """
            SELECT o.order_id, u.username, a.symbol, o.order_type,
                   o.order_mode, o.quantity, o.limit_price, o.status, o.placed_at
            FROM ORDERS o
            JOIN USERS  u ON u.user_id  = o.user_id
            JOIN ASSETS a ON a.asset_id = o.asset_id
            ORDER BY o.order_id DESC
        """, ("ID","User","Symbol","Type","Mode","Qty","Limit $","Status","Placed"))

    # ── TRANSACTIONS ─────────────────────────
    def _show_transactions(self):
        self._clear_main()
        self._table_page("Transactions", """
            SELECT t.txn_id, u.username, a.symbol, t.txn_type,
                   t.quantity, t.price_per_unit, t.total_amount, t.fee_amount, t.net_amount
            FROM TRANSACTIONS t
            JOIN USERS  u ON u.user_id  = t.user_id
            JOIN ASSETS a ON a.asset_id = t.asset_id
            ORDER BY t.txn_id DESC
        """, ("TXN","User","Symbol","Type","Qty","Price/Unit","Total","Fee","Net"))

    # ── PLACE ORDER ──────────────────────────
    def _show_place_order(self):
        self._clear_main()
        f = self.main

        lbl(f, "  Place New Order", fg=TEXT, font=FONT_HEAD, bg=BG).pack(
            anchor="w", padx=20, pady=16)

        form = tk.Frame(f, bg=CARD, padx=30, pady=24)
        form.pack(padx=20, pady=4, fill="x")

        cur = self.conn.cursor()
        cur.execute("SELECT user_id, username FROM USERS WHERE account_status='ACTIVE'")
        users = cur.fetchall()
        cur.execute("SELECT asset_id, symbol FROM ASSETS WHERE is_active='Y'")
        assets = cur.fetchall()

        fields = {}

        def row(label, widget_fn):
            r = tk.Frame(form, bg=CARD)
            r.pack(fill="x", pady=6)
            lbl(r, label, fg=MUTED, bg=CARD, width=14, anchor="w").pack(side="left")
            w = widget_fn(r)
            w.pack(side="left", fill="x", expand=True)
            return w

        user_var  = tk.StringVar()
        asset_var = tk.StringVar()
        type_var  = tk.StringVar(value="BUY")
        mode_var  = tk.StringVar(value="MARKET")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Dark.TCombobox",
            fieldbackground=PANEL, background=PANEL,
            foreground=TEXT, selectbackground=ACCENT)

        fields["user"]  = row("User",       lambda p: ttk.Combobox(p,
            textvariable=user_var,
            values=[f"{u[0]} — {u[1]}" for u in users], state="readonly",
            style="Dark.TCombobox"))
        fields["asset"] = row("Asset",      lambda p: ttk.Combobox(p,
            textvariable=asset_var,
            values=[f"{a[0]} — {a[1]}" for a in assets], state="readonly",
            style="Dark.TCombobox"))
        fields["type"]  = row("Order Type", lambda p: ttk.Combobox(p,
            textvariable=type_var, values=["BUY","SELL"], state="readonly",
            style="Dark.TCombobox"))
        fields["mode"]  = row("Order Mode", lambda p: ttk.Combobox(p,
            textvariable=mode_var, values=["MARKET","LIMIT","STOP","STOP_LIMIT"],
            state="readonly", style="Dark.TCombobox"))

        qty_var   = tk.StringVar()
        price_var = tk.StringVar()
        fields["qty"]   = row("Quantity", lambda p: tk.Entry(p,
            textvariable=qty_var, bg=PANEL, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=FONT_BODY))
        fields["price"] = row("Limit Price", lambda p: tk.Entry(p,
            textvariable=price_var, bg=PANEL, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=FONT_BODY))

        result_lbl = lbl(form, "", fg=GREEN, bg=CARD, font=FONT_BODY)
        result_lbl.pack(anchor="w", pady=6)

        def submit():
            try:
                uid   = int(user_var.get().split("—")[0].strip())
                aid   = int(asset_var.get().split("—")[0].strip())
                otype = type_var.get()
                omode = mode_var.get()
                qty   = float(qty_var.get())

                # Check account status
                c2 = self.conn.cursor()
                c2.execute("SELECT account_status FROM USERS WHERE user_id=?", (uid,))
                status = c2.fetchone()[0]
                if status != "ACTIVE":
                    result_lbl.config(
                        text=f"  ✗ Order rejected: account is {status}.", fg=RED)
                    return

                # Get latest price
                c2.execute("""SELECT close_price FROM PRICE_HISTORY
                              WHERE asset_id=? ORDER BY recorded_at DESC LIMIT 1""", (aid,))
                row = c2.fetchone()
                price = float(price_var.get()) if price_var.get() else (row[0] if row else 0)

                total   = round(qty * price, 6)
                fee     = round(total * 0.0015, 6)
                net_amt = round(total - fee, 6)

                c2.execute("SELECT MAX(order_id) FROM ORDERS")
                new_oid = (c2.fetchone()[0] or 0) + 1
                c2.execute("""INSERT INTO ORDERS
                    (order_id,user_id,asset_id,order_type,order_mode,
                     quantity,limit_price,status,placed_at)
                    VALUES(?,?,?,?,?,?,?,?,?)""",
                    (new_oid, uid, aid, otype, omode, qty, price, "FILLED",
                     datetime.datetime.now().isoformat()))

                c2.execute("SELECT MAX(txn_id) FROM TRANSACTIONS")
                new_tid = (c2.fetchone()[0] or 0) + 1
                c2.execute("""INSERT INTO TRANSACTIONS
                    (txn_id,order_id,user_id,asset_id,txn_type,
                     quantity,price_per_unit,total_amount,fee_amount,net_amount,txn_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                    (new_tid, new_oid, uid, aid, otype,
                     qty, price, total, fee, net_amt,
                     datetime.datetime.now().isoformat()))

                # Update wallet
                c2.execute("SELECT wallet_id FROM WALLETS WHERE user_id=? AND asset_id=?",
                            (uid, aid))
                w = c2.fetchone()
                delta = qty if otype == "BUY" else -qty
                if w:
                    c2.execute("UPDATE WALLETS SET balance=balance+? WHERE wallet_id=?",
                                (delta, w[0]))
                else:
                    c2.execute("INSERT INTO WALLETS VALUES(?,?,?,?,?)",
                                ((c2.execute("SELECT MAX(wallet_id) FROM WALLETS").fetchone()[0] or 0)+1,
                                 uid, aid, max(0, delta),
                                 datetime.datetime.now().isoformat()))

                self.conn.commit()
                result_lbl.config(
                    text=f"  ✓ Order #{new_oid} placed! Total=${total:,.2f}  Fee=${fee:,.2f}",
                    fg=GREEN)
            except Exception as e:
                result_lbl.config(text=f"  ✗ Error: {e}", fg=RED)

        tk.Button(form, text="  Submit Order  ", bg=ACCENT, fg="white",
                  font=FONT_HEAD, relief="flat", cursor="hand2",
                  activebackground="#1F6FEB", command=submit,
                  pady=8, padx=16).pack(anchor="w", pady=12)

    # ── SQL QUERY RUNNER ─────────────────────
    def _show_sql(self):
        self._clear_main()
        f = self.main

        lbl(f, "  SQL Query Runner", fg=TEXT, font=FONT_HEAD, bg=BG).pack(
            anchor="w", padx=20, pady=16)

        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", padx=20)

        lbl(top, "Enter SQL (SELECT only for demo):", fg=MUTED, bg=BG).pack(anchor="w")

        editor = scrolledtext.ScrolledText(top, bg=PANEL, fg=TEXT,
            font=FONT_MONO, height=7, insertbackground=TEXT,
            relief="flat", padx=10, pady=10)
        editor.pack(fill="x", pady=6)
        editor.insert("end",
            "SELECT u.username, GET_USER_PNL AS pnl\n"
            "FROM USERS u\n"
            "-- (In demo, use standard SQLite syntax)\n\n"
            "SELECT u.user_id, u.username, COUNT(t.txn_id) AS txns,\n"
            "       SUM(t.total_amount) AS volume\n"
            "FROM USERS u\n"
            "JOIN TRANSACTIONS t ON t.user_id = u.user_id\n"
            "GROUP BY u.user_id, u.username\n"
            "ORDER BY txns DESC LIMIT 5;")

        out_frame = tk.Frame(f, bg=BG)
        out_frame.pack(fill="both", expand=True, padx=20, pady=6)

        status_lbl = lbl(out_frame, "", fg=GREEN, bg=BG)
        status_lbl.pack(anchor="w")

        def run_query():
            sql = editor.get("1.0", "end").strip()
            for widget in out_frame.winfo_children():
                if widget != status_lbl:
                    widget.destroy()
            try:
                cur = self.conn.cursor()
                cur.execute(sql)
                rows = cur.fetchall()
                if not rows:
                    status_lbl.config(text="Query OK — no rows returned.", fg=AMBER)
                    return
                cols  = [d[0] for d in cur.description]
                tv    = self._make_table(out_frame, cols)
                for row in rows:
                    tv.insert("", "end", values=row)
                status_lbl.config(text=f"  ✓ {len(rows)} row(s) returned.", fg=GREEN)
            except Exception as e:
                status_lbl.config(text=f"  ✗ {e}", fg=RED)

        tk.Button(top, text="  Run Query ▶  ", bg=GREEN, fg="white",
                  font=FONT_BODY, relief="flat", cursor="hand2",
                  command=run_query, pady=6, padx=14).pack(anchor="w", pady=4)

        run_query()

    # ── SHARED HELPERS ───────────────────────
    def _make_table(self, parent, cols):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True, padx=20, pady=6)

        style = ttk.Style()
        style.configure("Dark.Treeview",
            background=CARD, foreground=TEXT,
            fieldbackground=CARD, rowheight=26,
            font=("Segoe UI", 9))
        style.configure("Dark.Treeview.Heading",
            background=PANEL, foreground=MUTED,
            font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Dark.Treeview",
            background=[("selected", ACCENT)],
            foreground=[("selected", "white")])

        tv = ttk.Treeview(frame, columns=cols, show="headings",
                          style="Dark.Treeview")
        for col in cols:
            tv.heading(col, text=col)
            tv.column(col, width=110, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical", command=tv.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tv.xview)
        tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tv.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        return tv

    def _table_page(self, title, query, cols):
        lbl(self.main, f"  {title}", fg=TEXT, font=FONT_HEAD,
            bg=BG).pack(anchor="w", padx=20, pady=16)
        tv  = self._make_table(self.main, cols)
        cur = self.conn.cursor()
        cur.execute(query)
        for row in cur.fetchall():
            tv.insert("", "end", values=row)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = TradingApp()
    app.mainloop()
