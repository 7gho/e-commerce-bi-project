-- ============================================================
-- TMDT_BI — Views phục vụ Power BI
-- ============================================================

-- ─── VIEW 1: Doanh thu theo tháng ───────────────────────────
CREATE OR REPLACE VIEW vw_revenue_by_month AS
SELECT
    t.year,
    t.month,
    t.month_name,
    t.quarter,
    COUNT(DISTINCT f.invoice_no)    AS total_orders,
    SUM(f.quantity)                 AS total_quantity,
    ROUND(SUM(f.total_amount), 2)   AS total_revenue,
    ROUND(AVG(f.total_amount), 2)   AS avg_order_value
FROM fact_orders f
JOIN dim_time t ON f.time_key = t.time_key
WHERE f.is_return = FALSE
GROUP BY t.year, t.month, t.month_name, t.quarter
ORDER BY t.year, t.month;

-- ─── VIEW 2: Top sản phẩm bán chạy ─────────────────────────
CREATE OR REPLACE VIEW vw_top_products AS
SELECT
    p.stock_code,
    p.description,
    p.category,
    COUNT(DISTINCT f.invoice_no)    AS total_orders,
    SUM(f.quantity)                 AS total_quantity,
    ROUND(SUM(f.total_amount), 2)   AS total_revenue
FROM fact_orders f
JOIN dim_product p ON f.product_key = p.product_key
WHERE f.is_return = FALSE
GROUP BY p.stock_code, p.description, p.category
ORDER BY total_revenue DESC;

-- ─── VIEW 3: Hành vi mua hàng theo quốc gia ─────────────────
CREATE OR REPLACE VIEW vw_revenue_by_region AS
SELECT
    r.country,
    r.region,
    r.continent,
    COUNT(DISTINCT f.invoice_no)    AS total_orders,
    COUNT(DISTINCT f.customer_key)  AS unique_customers,
    ROUND(SUM(f.total_amount), 2)   AS total_revenue
FROM fact_orders f
JOIN dim_region r ON f.region_key = r.region_key
WHERE f.is_return = FALSE
GROUP BY r.country, r.region, r.continent
ORDER BY total_revenue DESC;

-- ─── VIEW 4: Hành vi theo khách hàng (RFM base) ─────────────
CREATE OR REPLACE VIEW vw_customer_behavior AS
SELECT
    c.customer_id,
    c.country,
    COUNT(DISTINCT f.invoice_no)    AS frequency,
    SUM(f.quantity)                 AS total_items,
    ROUND(SUM(f.total_amount), 2)   AS monetary,
    MAX(t.full_date)                AS last_purchase_date,
    MIN(t.full_date)                AS first_purchase_date
FROM fact_orders f
JOIN dim_customer c ON f.customer_key = c.customer_key
JOIN dim_time t     ON f.time_key = t.time_key
WHERE f.is_return = FALSE
GROUP BY c.customer_id, c.country
ORDER BY monetary DESC;

-- ─── VIEW 5: Tỷ lệ hoàn trả ─────────────────────────────────
CREATE OR REPLACE VIEW vw_return_analysis AS
SELECT
    t.year,
    t.month,
    t.month_name,
    COUNT(CASE WHEN f.is_return = FALSE THEN 1 END) AS normal_orders,
    COUNT(CASE WHEN f.is_return = TRUE  THEN 1 END) AS returned_orders,
    ROUND(
        COUNT(CASE WHEN f.is_return = TRUE THEN 1 END)::NUMERIC /
        NULLIF(COUNT(*), 0) * 100, 2
    ) AS return_rate_pct
FROM fact_orders f
JOIN dim_time t ON f.time_key = t.time_key
GROUP BY t.year, t.month, t.month_name
ORDER BY t.year, t.month;
