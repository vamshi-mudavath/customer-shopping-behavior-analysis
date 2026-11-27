-- =====================================================================
-- Customer Shopping Behavior Analysis: business questions in SQL
-- Author : Vamshi Mudavath
-- Table  : customer  (cleaned data loaded from notebooks/shopping_behavior_analysis.ipynb)
-- Engine : written to run unchanged on SQLite and PostgreSQL
-- Each query starts with a "-- Q<n>." line; the notebook runs them one by one.
-- =====================================================================

-- Q1. Revenue by gender: how much do male and female customers spend in total?
SELECT gender,
       COUNT(*)                     AS orders,
       SUM(purchase_amount)         AS revenue,
       ROUND(100.0 * SUM(purchase_amount) / (SELECT SUM(purchase_amount) FROM customer), 1) AS revenue_share_pct
FROM customer
GROUP BY gender
ORDER BY revenue DESC;

-- Q2. Discount users who still spent more than the average purchase amount
SELECT COUNT(*)                       AS customers,
       ROUND(AVG(purchase_amount), 2) AS their_avg_spend,
       (SELECT ROUND(AVG(purchase_amount), 2) FROM customer) AS overall_avg_spend
FROM customer
WHERE discount_applied = 'Yes'
  AND purchase_amount >= (SELECT AVG(purchase_amount) FROM customer);

-- Q3. Top 5 products by average review rating
SELECT item_purchased,
       COUNT(*) AS orders,
       ROUND(CAST(AVG(review_rating) AS NUMERIC), 2) AS avg_rating
FROM customer
GROUP BY item_purchased
ORDER BY AVG(review_rating) DESC
LIMIT 5;

-- Q4. Average purchase amount by shipping type (Standard vs Express and the rest)
SELECT shipping_type,
       COUNT(*)                       AS orders,
       ROUND(AVG(purchase_amount), 2) AS avg_purchase
FROM customer
GROUP BY shipping_type
ORDER BY avg_purchase DESC;

-- Q5. Do subscribers spend more? Average spend and total revenue by subscription status
SELECT subscription_status,
       COUNT(customer_id)             AS customers,
       ROUND(AVG(purchase_amount), 2) AS avg_spend,
       SUM(purchase_amount)           AS total_revenue
FROM customer
GROUP BY subscription_status
ORDER BY total_revenue DESC;

-- Q6. Top 5 products most often bought with a discount
SELECT item_purchased,
       COUNT(*) AS orders,
       ROUND(100.0 * SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS discount_rate_pct
FROM customer
GROUP BY item_purchased
ORDER BY discount_rate_pct DESC
LIMIT 5;

-- Q7. Customer segments (New = 1 previous purchase, Returning = 2-10, Loyal = more than 10)
WITH segments AS (
    SELECT customer_id,
           purchase_amount,
           CASE WHEN previous_purchases = 1 THEN 'New'
                WHEN previous_purchases BETWEEN 2 AND 10 THEN 'Returning'
                ELSE 'Loyal' END AS customer_segment
    FROM customer
)
SELECT customer_segment,
       COUNT(*)                       AS customers,
       ROUND(AVG(purchase_amount), 2) AS avg_spend
FROM segments
GROUP BY customer_segment
ORDER BY customers DESC;

-- Q8. Top 3 most purchased products in each category (window function)
WITH item_counts AS (
    SELECT category,
           item_purchased,
           COUNT(*) AS orders,
           ROW_NUMBER() OVER (PARTITION BY category ORDER BY COUNT(*) DESC, item_purchased) AS item_rank
    FROM customer
    GROUP BY category, item_purchased
)
SELECT category, item_rank, item_purchased, orders
FROM item_counts
WHERE item_rank <= 3
ORDER BY category, item_rank;

-- Q9. Are repeat buyers (more than 5 previous purchases) more likely to subscribe?
SELECT CASE WHEN previous_purchases > 5 THEN 'Repeat buyer (>5)' ELSE 'Occasional (<=5)' END AS buyer_type,
       COUNT(*) AS customers,
       ROUND(100.0 * SUM(CASE WHEN subscription_status = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS subscribed_pct
FROM customer
GROUP BY buyer_type;

-- Q10. Revenue contribution of each age group
SELECT age_group,
       MIN(age) AS min_age,
       MAX(age) AS max_age,
       SUM(purchase_amount) AS revenue,
       ROUND(100.0 * SUM(purchase_amount) / (SELECT SUM(purchase_amount) FROM customer), 1) AS revenue_share_pct
FROM customer
GROUP BY age_group
ORDER BY revenue DESC;

-- Q11. Revenue and average order value by season
SELECT season,
       COUNT(*)                       AS orders,
       SUM(purchase_amount)           AS revenue,
       ROUND(AVG(purchase_amount), 2) AS avg_purchase
FROM customer
GROUP BY season
ORDER BY revenue DESC;

-- Q12. Data check: who receives discounts and subscriptions, split by gender?
SELECT gender,
       ROUND(100.0 * SUM(CASE WHEN discount_applied = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1)    AS discount_pct,
       ROUND(100.0 * SUM(CASE WHEN subscription_status = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 1) AS subscribed_pct
FROM customer
GROUP BY gender;

-- Q13. Top 5 states by revenue
SELECT location,
       COUNT(*) AS orders,
       SUM(purchase_amount) AS revenue
FROM customer
GROUP BY location
ORDER BY revenue DESC
LIMIT 5;
