-- WealthAI データベーススキーマ作成スクリプト
-- 作成日: 2025-07-31

-- 1. 営業担当者テーブル
CREATE TABLE sales_representatives (
    rep_id SERIAL PRIMARY KEY,
    rep_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    branch VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 顧客マスターテーブル
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    name_kana VARCHAR(100),
    birth_date DATE,
    gender VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    occupation VARCHAR(50),
    annual_income BIGINT,
    net_worth BIGINT,
    risk_tolerance VARCHAR(20), -- conservative, moderate, aggressive
    investment_experience VARCHAR(20), -- beginner, intermediate, expert
    sales_rep_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. 商品マスターテーブル
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_code VARCHAR(50) UNIQUE NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    product_type VARCHAR(50) NOT NULL, -- bond, stock, fund, structured_product, insurance
    currency VARCHAR(10) DEFAULT 'JPY',
    issuer VARCHAR(100),
    maturity_date DATE,
    interest_rate DECIMAL(5,4),
    risk_level INTEGER, -- 1-5
    minimum_investment BIGINT,
    commission_rate DECIMAL(5,4),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. 保有商品テーブル
CREATE TABLE holdings (
    holding_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity DECIMAL(15,2) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    purchase_date DATE NOT NULL,
    current_price DECIMAL(15,2),
    current_value DECIMAL(15,2),
    unrealized_gain_loss DECIMAL(15,2),
    maturity_date DATE,
    status VARCHAR(20) DEFAULT 'active', -- active, sold, matured
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. 取引履歴テーブル
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_id INTEGER REFERENCES products(product_id),
    transaction_type VARCHAR(20) NOT NULL, -- buy, sell, dividend, interest, maturity
    quantity DECIMAL(15,2) NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    total_amount DECIMAL(15,2) NOT NULL,
    commission DECIMAL(15,2) DEFAULT 0,
    transaction_date DATE NOT NULL,
    settlement_date DATE,
    sales_rep_id INTEGER REFERENCES sales_representatives(rep_id),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. 営業メモテーブル
CREATE TABLE sales_notes (
    note_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    sales_rep_id INTEGER REFERENCES sales_representatives(rep_id),
    note_type VARCHAR(30), -- meeting, phone_call, email, cash_inflow_prediction, other
    subject VARCHAR(200),
    content TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal', -- high, normal, low
    follow_up_date DATE,
    is_cash_related BOOLEAN DEFAULT FALSE,
    predicted_amount BIGINT,
    predicted_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. 入金予測テーブル
CREATE TABLE cash_inflows (
    inflow_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    source_type VARCHAR(50), -- salary, bonus, retirement, inheritance, business_sale, dividend, maturity, other
    predicted_amount BIGINT NOT NULL,
    predicted_date DATE NOT NULL,
    confidence_level VARCHAR(20), -- high, medium, low
    source_note TEXT,
    actual_amount BIGINT,
    actual_date DATE,
    status VARCHAR(20) DEFAULT 'predicted', -- predicted, confirmed, received, cancelled
    sales_rep_id INTEGER REFERENCES sales_representatives(rep_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. 市場データテーブル
CREATE TABLE market_data (
    data_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    data_type VARCHAR(30), -- stock_price, bond_yield, fx_rate, index_value
    value DECIMAL(15,6) NOT NULL,
    date DATE NOT NULL,
    time TIME,
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, data_type, date, time)
);

-- 9. 政治・経済イベントテーブル
CREATE TABLE economic_events (
    event_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50), -- election, policy_change, economic_indicator, political_event
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    impact_level VARCHAR(20), -- high, medium, low
    affected_sectors TEXT[], -- 影響を受けるセクター
    affected_currencies VARCHAR(50)[], -- 影響を受ける通貨
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. 商品推奨履歴テーブル
CREATE TABLE recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    product_id INTEGER REFERENCES products(product_id),
    sales_rep_id INTEGER REFERENCES sales_representatives(rep_id),
    recommendation_reason TEXT,
    scenario_type VARCHAR(50), -- maturity_bond, political_event, cash_inflow
    recommended_amount BIGINT,
    priority_score INTEGER, -- 1-100
    status VARCHAR(20) DEFAULT 'pending', -- pending, presented, accepted, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 外部キー制約の追加
ALTER TABLE customers ADD CONSTRAINT fk_customers_sales_rep 
    FOREIGN KEY (sales_rep_id) REFERENCES sales_representatives(rep_id);

-- インデックスの作成
CREATE INDEX idx_customers_sales_rep ON customers(sales_rep_id);
CREATE INDEX idx_holdings_customer ON holdings(customer_id);
CREATE INDEX idx_holdings_product ON holdings(product_id);
CREATE INDEX idx_holdings_maturity ON holdings(maturity_date) WHERE status = 'active';
CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_sales_notes_customer ON sales_notes(customer_id);
CREATE INDEX idx_sales_notes_cash ON sales_notes(is_cash_related) WHERE is_cash_related = TRUE;
CREATE INDEX idx_cash_inflows_customer ON cash_inflows(customer_id);
CREATE INDEX idx_cash_inflows_date ON cash_inflows(predicted_date);
CREATE INDEX idx_market_data_symbol_date ON market_data(symbol, date);
CREATE INDEX idx_recommendations_customer ON recommendations(customer_id);
