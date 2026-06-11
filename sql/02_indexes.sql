-- ============================================================
-- TMDT_BI — Indexes tối ưu truy vấn Power BI
-- ============================================================

-- Fact table — Foreign key indexes
CREATE INDEX idx_fact_customer  ON fact_orders(customer_key);
CREATE INDEX idx_fact_product   ON fact_orders(product_key);
CREATE INDEX idx_fact_time      ON fact_orders(time_key);
CREATE INDEX idx_fact_region    ON fact_orders(region_key);
CREATE INDEX idx_fact_invoice   ON fact_orders(invoice_no);
CREATE INDEX idx_fact_return    ON fact_orders(is_return);

-- dim_time — thường filter theo year/month
CREATE INDEX idx_time_year      ON dim_time(year);
CREATE INDEX idx_time_month     ON dim_time(month);
CREATE INDEX idx_time_quarter   ON dim_time(quarter);

-- dim_customer — filter theo country
CREATE INDEX idx_cust_country   ON dim_customer(country);

-- dim_product — filter theo stock_code
CREATE INDEX idx_prod_code      ON dim_product(stock_code);
