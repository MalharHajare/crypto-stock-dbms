-- ============================================================
-- Cryptocurrency & Stock Transaction Management System
-- Full SQL + PL/SQL Reference
-- Subject: Database Management Systems
-- ============================================================


-- ============================================================
-- SECTION 1: CREATE TABLE Commands
-- ============================================================

-- Table 1: USERS
CREATE TABLE USERS (
    user_id        NUMBER(10)    PRIMARY KEY,
    username       VARCHAR2(50)  NOT NULL UNIQUE,
    email          VARCHAR2(100) NOT NULL UNIQUE,
    password_hash  VARCHAR2(256) NOT NULL,
    full_name      VARCHAR2(100),
    phone          VARCHAR2(20),
    country        VARCHAR2(60),
    kyc_verified   CHAR(1)       DEFAULT 'N' CHECK (kyc_verified IN ('Y','N')),
    account_status VARCHAR2(20)  DEFAULT 'ACTIVE'
                   CHECK (account_status IN ('ACTIVE','SUSPENDED','CLOSED')),
    created_at     TIMESTAMP     DEFAULT SYSTIMESTAMP,
    last_login     TIMESTAMP
);

-- Table 2: ASSETS
CREATE TABLE ASSETS (
    asset_id   NUMBER(10)    PRIMARY KEY,
    symbol     VARCHAR2(20)  NOT NULL UNIQUE,
    asset_name VARCHAR2(100) NOT NULL,
    asset_type VARCHAR2(20)  NOT NULL
               CHECK (asset_type IN ('CRYPTO','STOCK','ETF','COMMODITY')),
    exchange   VARCHAR2(50),
    currency   VARCHAR2(10)  DEFAULT 'USD',
    is_active  CHAR(1)       DEFAULT 'Y' CHECK (is_active IN ('Y','N')),
    listed_date DATE
);

-- Table 3: WALLETS
CREATE TABLE WALLETS (
    wallet_id    NUMBER(10)    PRIMARY KEY,
    user_id      NUMBER(10)    NOT NULL REFERENCES USERS(user_id),
    asset_id     NUMBER(10)    NOT NULL REFERENCES ASSETS(asset_id),
    balance      NUMBER(20,8)  DEFAULT 0 CHECK (balance >= 0),
    locked_amt   NUMBER(20,8)  DEFAULT 0 CHECK (locked_amt >= 0),
    last_updated TIMESTAMP     DEFAULT SYSTIMESTAMP,
    CONSTRAINT uq_wallet UNIQUE (user_id, asset_id)
);

-- Table 4: PRICE_HISTORY
CREATE TABLE PRICE_HISTORY (
    price_id      NUMBER(15)   PRIMARY KEY,
    asset_id      NUMBER(10)   NOT NULL REFERENCES ASSETS(asset_id),
    recorded_at   TIMESTAMP    NOT NULL,
    open_price    NUMBER(18,6) NOT NULL,
    high_price    NUMBER(18,6) NOT NULL,
    low_price     NUMBER(18,6) NOT NULL,
    close_price   NUMBER(18,6) NOT NULL,
    volume        NUMBER(24,8),
    interval_type VARCHAR2(10) DEFAULT '1D'
                  CHECK (interval_type IN ('1M','5M','15M','1H','4H','1D','1W')),
    CONSTRAINT uq_price UNIQUE (asset_id, recorded_at, interval_type)
);

-- Table 5: ORDERS
CREATE TABLE ORDERS (
    order_id   NUMBER(15)   PRIMARY KEY,
    user_id    NUMBER(10)   NOT NULL REFERENCES USERS(user_id),
    asset_id   NUMBER(10)   NOT NULL REFERENCES ASSETS(asset_id),
    order_type VARCHAR2(10) NOT NULL CHECK (order_type IN ('BUY','SELL')),
    order_mode VARCHAR2(10) DEFAULT 'MARKET'
               CHECK (order_mode IN ('MARKET','LIMIT','STOP','STOP_LIMIT')),
    quantity   NUMBER(20,8) NOT NULL CHECK (quantity > 0),
    limit_price  NUMBER(18,6),
    stop_price   NUMBER(18,6),
    status       VARCHAR2(15) DEFAULT 'PENDING'
                 CHECK (status IN ('PENDING','FILLED','PARTIAL','CANCELLED','REJECTED')),
    placed_at    TIMESTAMP    DEFAULT SYSTIMESTAMP,
    filled_at    TIMESTAMP,
    expires_at   TIMESTAMP
);

-- Table 6: TRANSACTIONS
CREATE TABLE TRANSACTIONS (
    txn_id         NUMBER(15)   PRIMARY KEY,
    order_id       NUMBER(15)   NOT NULL REFERENCES ORDERS(order_id),
    user_id        NUMBER(10)   NOT NULL REFERENCES USERS(user_id),
    asset_id       NUMBER(10)   NOT NULL REFERENCES ASSETS(asset_id),
    txn_type       VARCHAR2(10) NOT NULL CHECK (txn_type IN ('BUY','SELL')),
    quantity       NUMBER(20,8) NOT NULL,
    price_per_unit NUMBER(18,6) NOT NULL,
    total_amount   NUMBER(24,6) NOT NULL,
    fee_amount     NUMBER(12,6) DEFAULT 0,
    net_amount     NUMBER(24,6) NOT NULL,
    txn_hash       VARCHAR2(128),
    txn_at         TIMESTAMP    DEFAULT SYSTIMESTAMP
);

-- Table 7: PORTFOLIO_SNAPSHOTS
CREATE TABLE PORTFOLIO_SNAPSHOTS (
    snap_id         NUMBER(15)   PRIMARY KEY,
    user_id         NUMBER(10)   NOT NULL REFERENCES USERS(user_id),
    snap_date       DATE         NOT NULL,
    total_value_usd NUMBER(24,6) NOT NULL,
    total_invested  NUMBER(24,6),
    pnl_usd         NUMBER(24,6),
    pnl_pct         NUMBER(10,4),
    CONSTRAINT uq_snap UNIQUE (user_id, snap_date)
);


-- ============================================================
-- SECTION 2: DML Queries
-- ============================================================

-- Query 1: Insert new user Aryan Shah
INSERT INTO USERS
    (user_id, username, email, password_hash,
     full_name, phone, country, kyc_verified, account_status)
VALUES
    (101, 'aryan_shah', 'aryan@trade.com',
     'hashed_pwd_xyz', 'Aryan Shah', '+91-9876543210',
     'India', 'Y', 'ACTIVE');

-- Query 2: Add Solana (SOL) asset
INSERT INTO ASSETS
    (asset_id, symbol, asset_name, asset_type,
     exchange, currency, is_active, listed_date)
VALUES
    (501, 'SOL', 'Solana', 'CRYPTO',
     'Binance', 'USD', 'Y', TO_DATE('2020-03-24','YYYY-MM-DD'));

-- Query 3: BUY order for 2.5 Bitcoin at limit $62,000 by user 101
INSERT INTO ORDERS
    (order_id, user_id, asset_id, order_type, order_mode,
     quantity, limit_price, status, placed_at)
VALUES
    (9001, 101, 1, 'BUY', 'LIMIT',
     2.5, 62000.000000, 'PENDING', SYSTIMESTAMP);

-- Query 4: Log completed BUY transaction for order 9001
INSERT INTO TRANSACTIONS
    (txn_id, order_id, user_id, asset_id, txn_type,
     quantity, price_per_unit, total_amount, fee_amount, net_amount, txn_at)
VALUES
    (70001, 9001, 101, 1, 'BUY',
     2.5, 62000.00, 155000.00, 232.50, 154767.50, SYSTIMESTAMP);

-- Query 5: Update wallet balance of user 101 after 2.5 BTC purchase
UPDATE WALLETS
SET    balance      = balance + 2.5,
       last_updated = SYSTIMESTAMP
WHERE  user_id  = 101
AND    asset_id = 1;  -- asset_id 1 = Bitcoin

-- Query 6: Suspend user 205 for compliance violation
UPDATE USERS
SET   account_status = 'SUSPENDED'
WHERE user_id = 205;

-- Query 7: Cancel all PENDING orders older than 30 days
UPDATE ORDERS
SET    status = 'CANCELLED'
WHERE  status    = 'PENDING'
AND    placed_at < SYSTIMESTAMP - INTERVAL '30' DAY;

-- Query 8: Top 5 most active users by transactions in last 90 days
SELECT u.user_id,
       u.username,
       COUNT(t.txn_id)       AS total_transactions,
       SUM(t.total_amount)   AS total_traded_usd
FROM   USERS U
JOIN   TRANSACTIONS T ON T.user_id = U.user_id
WHERE  T.txn_at >= SYSTIMESTAMP - INTERVAL '90' DAY
GROUP  BY u.user_id, u.username
ORDER  BY total_transactions DESC
FETCH  FIRST 5 ROWS ONLY;

-- Query 9: 7-day average closing price for each active crypto asset
SELECT a.symbol,
       a.asset_name,
       ROUND(AVG(ph.close_price), 4) AS avg_close_7d
FROM   ASSETS A
JOIN   PRICE_HISTORY PH ON PH.asset_id = A.asset_id
WHERE  A.asset_type   = 'CRYPTO'
AND    A.is_active    = 'Y'
AND    PH.recorded_at >= SYSTIMESTAMP - INTERVAL '7' DAY
AND    PH.interval_type = '1D'
GROUP  BY a.symbol, a.asset_name
ORDER  BY avg_close_7d DESC;

-- Query 10: Delete price history older than 5 years
DELETE FROM PRICE_HISTORY
WHERE recorded_at < ADD_MONTHS(SYSDATE, -60);  -- -60 months = 5 years


-- ============================================================
-- SECTION 3: PL/SQL Procedures
-- ============================================================

-- Procedure 1: PLACE_BUY_ORDER
-- Validates account, fetches price, updates wallet atomically.
CREATE OR REPLACE PROCEDURE PLACE_BUY_ORDER (
    p_user_id  IN  NUMBER,
    p_asset_id IN  NUMBER,
    p_qty      IN  NUMBER,
    p_msg      OUT VARCHAR2
) AS
    v_status VARCHAR2(20);
    v_price  NUMBER;
    v_total  NUMBER;
    v_fee    NUMBER;
    CURSOR c_wallet IS
        SELECT wallet_id, balance
        FROM   WALLETS
        WHERE  user_id  = p_user_id
        AND    asset_id = p_asset_id
        FOR UPDATE;
    r_wallet c_wallet%ROWTYPE;
BEGIN
    SELECT account_status INTO v_status
    FROM   USERS
    WHERE  user_id = p_user_id;

    IF v_status != 'ACTIVE' THEN
        p_msg := 'User not active';
        RETURN;
    END IF;

    SELECT close_price INTO v_price
    FROM   PRICE_HISTORY
    WHERE  asset_id = p_asset_id
    AND    ROWNUM = 1;

    v_total := p_qty * v_price;
    v_fee   := v_total * 0.0015;

    OPEN c_wallet;
    FETCH c_wallet INTO r_wallet;

    IF c_wallet%FOUND THEN
        UPDATE WALLETS
        SET    balance = balance + p_qty
        WHERE  CURRENT OF c_wallet;
    ELSE
        INSERT INTO WALLETS (wallet_id, user_id, asset_id, balance)
        VALUES (wallet_seq.NEXTVAL, p_user_id, p_asset_id, p_qty);
    END IF;

    CLOSE c_wallet;

    INSERT INTO ORDERS (order_id, user_id, asset_id, order_type, quantity, status)
    VALUES (order_seq.NEXTVAL, p_user_id, p_asset_id, 'BUY', p_qty, 'FILLED');

    COMMIT;
    p_msg := 'Order placed. Total = ' || v_total || ', Fee = ' || v_fee;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_msg := 'Error: ' || SQLERRM;
END;
/

-- Run Procedure 1:
DECLARE
    v_msg VARCHAR2(300);
BEGIN
    PLACE_BUY_ORDER(101, 1, 0.5, v_msg);
    DBMS_OUTPUT.PUT_LINE(v_msg);
END;
/


-- Procedure 2: GENERATE_DAILY_SNAPSHOTS
-- Nightly batch: snapshots every active user's portfolio value.
CREATE OR REPLACE PROCEDURE GENERATE_DAILY_SNAPSHOTS AS
    v_total_val NUMBER(24,6);
    v_invested  NUMBER(24,6);
    v_pnl       NUMBER(24,6);
    v_pnl_pct   NUMBER(10,4);
    v_today     DATE := TRUNC(SYSDATE);

    CURSOR c_users IS
        SELECT user_id FROM USERS
        WHERE  account_status = 'ACTIVE';
BEGIN
    FOR r IN c_users LOOP
        v_total_val := GET_PORTFOLIO_VALUE(r.user_id);

        SELECT NVL(SUM(net_amount), 0) INTO v_invested
        FROM   TRANSACTIONS
        WHERE  user_id  = r.user_id
        AND    txn_type = 'BUY';

        v_pnl := v_total_val - v_invested;

        IF v_invested > 0 THEN
            v_pnl_pct := ROUND((v_pnl / v_invested) * 100, 4);
        ELSE
            v_pnl_pct := 0;
        END IF;

        MERGE INTO PORTFOLIO_SNAPSHOTS ps
        USING (SELECT r.user_id AS uid FROM DUAL) src
        ON    (ps.user_id = src.uid AND ps.snap_date = v_today)
        WHEN MATCHED THEN
            UPDATE SET total_value_usd = v_total_val,
                       total_invested  = v_invested,
                       pnl_usd         = v_pnl,
                       pnl_pct         = v_pnl_pct
        WHEN NOT MATCHED THEN
            INSERT (snap_id, user_id, snap_date,
                    total_value_usd, total_invested, pnl_usd, pnl_pct)
            VALUES (NVL((SELECT MAX(snap_id) FROM PORTFOLIO_SNAPSHOTS),0)+1,
                    r.user_id, v_today,
                    v_total_val, v_invested, v_pnl, v_pnl_pct);
    END LOOP;

    COMMIT;
    DBMS_OUTPUT.PUT_LINE('Daily snapshots generated for ' || v_today);

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        DBMS_OUTPUT.PUT_LINE('Snapshot error: ' || SQLERRM);
END GENERATE_DAILY_SNAPSHOTS;
/

-- Run Procedure 2:
BEGIN
    GENERATE_DAILY_SNAPSHOTS;
END;
/


-- ============================================================
-- SECTION 4: PL/SQL Functions
-- ============================================================

-- Function 1: GET_USER_PNL
-- Returns realized profit or loss for a user (SELL proceeds - BUY spend).
CREATE OR REPLACE FUNCTION GET_USER_PNL (
    p_user_id IN NUMBER
) RETURN NUMBER AS
    v_bought NUMBER(24,6) := 0;
    v_sold   NUMBER(24,6) := 0;
BEGIN
    SELECT NVL(SUM(net_amount), 0) INTO v_bought
    FROM   TRANSACTIONS
    WHERE  user_id  = p_user_id
    AND    txn_type = 'BUY';

    SELECT NVL(SUM(net_amount), 0) INTO v_sold
    FROM   TRANSACTIONS
    WHERE  user_id  = p_user_id
    AND    txn_type = 'SELL';

    RETURN ROUND(v_sold - v_bought, 2);  -- Positive = profit, Negative = loss

EXCEPTION
    WHEN OTHERS THEN RETURN NULL;
END GET_USER_PNL;
/

-- Sample usage:
SELECT username, GET_USER_PNL(user_id) AS pnl_usd
FROM   USERS
WHERE  account_status = 'ACTIVE';


-- Function 2: GET_PORTFOLIO_VALUE
-- Returns total live USD value of a user's holdings.
CREATE OR REPLACE FUNCTION GET_PORTFOLIO_VALUE (
    p_user_id IN NUMBER
) RETURN NUMBER AS
    v_total NUMBER(24,6) := 0;
    v_price NUMBER(18,6);
BEGIN
    FOR r IN (
        SELECT w.asset_id, w.balance
        FROM   WALLETS w
        WHERE  w.user_id = p_user_id
        AND    w.balance > 0
    ) LOOP
        BEGIN
            SELECT close_price INTO v_price FROM (
                SELECT close_price FROM PRICE_HISTORY
                WHERE  asset_id = r.asset_id
                ORDER  BY recorded_at DESC
            ) WHERE ROWNUM = 1;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN v_price := 0;
        END;
        v_total := v_total + (r.balance * v_price);
    END LOOP;

    RETURN ROUND(v_total, 2);

EXCEPTION
    WHEN OTHERS THEN RETURN 0;
END GET_PORTFOLIO_VALUE;
/

-- Sample usage:
SELECT user_id, username,
       GET_PORTFOLIO_VALUE(user_id) AS portfolio_usd
FROM   USERS
WHERE  account_status = 'ACTIVE';


-- ============================================================
-- SECTION 5: PL/SQL Triggers
-- ============================================================

-- Trigger 1: TRG_UPDATE_ORDER_STATUS
-- After a transaction insert, auto-stamps the parent order as FILLED.
CREATE OR REPLACE TRIGGER TRG_UPDATE_ORDER_STATUS
AFTER INSERT ON TRANSACTIONS
FOR EACH ROW
BEGIN
    UPDATE ORDERS
    SET    status    = 'FILLED',
           filled_at = :NEW.txn_at
    WHERE  order_id  = :NEW.order_id
    AND    status   != 'FILLED';
END TRG_UPDATE_ORDER_STATUS;
/


-- Trigger 2: TRG_BLOCK_SUSPENDED_ORDERS
-- Prevents SUSPENDED or CLOSED accounts from placing new orders.
CREATE OR REPLACE TRIGGER TRG_BLOCK_SUSPENDED_ORDERS
BEFORE INSERT ON ORDERS
FOR EACH ROW
DECLARE
    v_status VARCHAR2(20);
BEGIN
    SELECT account_status INTO v_status
    FROM   USERS
    WHERE  user_id = :NEW.user_id;

    IF v_status IN ('SUSPENDED', 'CLOSED') THEN
        RAISE_APPLICATION_ERROR(-20002,
            'Order rejected: account is ' || v_status || '.');
    END IF;
END TRG_BLOCK_SUSPENDED_ORDERS;
/

-- Test Trigger 2:
-- UPDATE USERS SET account_status='SUSPENDED' WHERE user_id=205;
-- INSERT INTO ORDERS ... user_id=205 ...;  --> raises ORA-20002

-- ============================================================
-- End of Script
-- ============================================================
