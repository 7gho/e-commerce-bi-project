-- ============================================================
-- TMDT_BI — Star Schema DDL
-- Database: PostgreSQL
-- ============================================================

-- Xóa bảng cũ nếu tồn tại (theo thứ tự phụ thuộc)
DROP TABLE IF EXISTS fact_orders CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_time CASCADE;
DROP TABLE IF EXISTS dim_region CASCADE;

-- ============================================================
-- DIMENSION TABLES
-- ============================================================

CREATE TABLE dim_region (
    region_key  SERIAL PRIMARY KEY,
    country     VARCHAR(100) NOT NULL,
    region      VARCHAR(50),   -- e.g. Western Europe, North America
    continent   VARCHAR(50)    -- e.g. Europe, Americas, Asia
);

CREATE TABLE dim_customer (
    customer_key   SERIAL PRIMARY KEY,
    customer_id    VARCHAR(20)  NOT NULL,
    country        VARCHAR(100),
    region         VARCHAR(50)
);

CREATE TABLE dim_product (
    product_key  SERIAL PRIMARY KEY,
    stock_code   VARCHAR(20)  NOT NULL,
    description  VARCHAR(255),
    category     VARCHAR(100)  -- Gán thủ công hoặc tự động nhóm
);

CREATE TABLE dim_time (
    time_key     SERIAL PRIMARY KEY,
    full_date    DATE         NOT NULL,
    day          SMALLINT     NOT NULL,
    month        SMALLINT     NOT NULL,
    month_name   VARCHAR(15)  NOT NULL,
    quarter      SMALLINT     NOT NULL,
    year         SMALLINT     NOT NULL,
    day_of_week  VARCHAR(10)  NOT NULL,
    is_weekend   BOOLEAN      NOT NULL
);

-- ============================================================
-- FACT TABLE
-- ============================================================

CREATE TABLE fact_orders (
    order_key      SERIAL PRIMARY KEY,
    invoice_no     VARCHAR(20)    NOT NULL,
    customer_key   INT            REFERENCES dim_customer(customer_key),
    product_key    INT            NOT NULL REFERENCES dim_product(product_key),
    time_key       INT            NOT NULL REFERENCES dim_time(time_key),
    region_key     INT            REFERENCES dim_region(region_key),
    quantity       INT            NOT NULL,
    unit_price     NUMERIC(10,2)  NOT NULL,
    total_amount   NUMERIC(12,2)  NOT NULL,  -- quantity * unit_price
    is_return      BOOLEAN        NOT NULL DEFAULT FALSE
);
