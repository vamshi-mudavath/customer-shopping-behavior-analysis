# Customer Shopping Behavior Analysis: Project Report
**Prepared by:** Vamshi Mudavath · **Tools:** Python (Pandas, Matplotlib, Seaborn), SQL (SQLite / PostgreSQL), Power BI

## 1. Business problem
A retail company wants to understand how its customers shop so it can grow sales, improve satisfaction and build loyalty. The question for this analysis: *how can the company use its customer shopping data to identify trends, improve engagement and optimise its marketing and product strategy?*

## 2. Data
- 3,900 purchases (one per customer), 18 columns: demographics, purchase details and shopping behaviour.
- Total revenue: **USD 233,081**. Average order: **USD 59.76**. Average review rating: **3.75 / 5**.

## 3. Data preparation (Python)
| Issue found | Action taken |
|---|---|
| 37 missing review ratings (about 1%) | Filled with the median rating of the same product category |
| Column names with spaces and units | Renamed to `snake_case`; `purchase_amount_(usd)` became `purchase_amount` |
| `Promo Code Used` identical to `Discount Applied` on every row | Dropped `promo_code_used` |
| Bi-Weekly = Fortnightly, Quarterly = Every 3 Months | Kept the labels; mapped each pair to the same `purchase_frequency_days` |
| Discounts and subscriptions recorded only for male customers | Kept the data, flagged it, and did not base decisions on it |

New features: `age_group` (Young Adult 18–31, Adult 32–44, Middle-aged 45–57, Senior 58–70), `purchase_frequency_days`, and `customer_segment` (New, Returning, Loyal).

## 4. Analysis (SQL)
The clean table was loaded into a SQL database and 13 business questions were answered (see `sql/business_queries.sql`). Main results:

| Area | Result |
|---|---|
| Revenue by category | Clothing USD 104,264 (44.7%), Accessories 74,200 (31.8%), Footwear 36,093 (15.5%), Outerwear 18,524 (7.9%) |
| Revenue by gender | Male 67.7%, Female 32.3%; average order almost equal (USD 59.54 vs 60.25) |
| Subscriptions | 27% subscribe; average order USD 59.49 for subscribers vs 59.87 for non-subscribers |
| Discounts | 43% of orders; average order USD 59.28 with discount vs 60.13 without |
| Most-discounted items | Hat 50.0%, Sneakers 49.7%, Coat 49.1%, Sweater 48.2%, Pants 47.4% |
| Top-rated items | Gloves 3.86, Sandals 3.84, Boots 3.82, Hat 3.80, Skirt 3.78 |
| Segments | Loyal 3,116 (80%), Returning 701 (18%), New 83 (2%) |
| Repeat buyers (>5 purchases) | 27.6% subscribe vs 22.4% of occasional buyers |
| Shipping | Average order ranges only from USD 58.46 (Standard) to 60.73 (2-Day) |
| Seasons | Fall USD 60,018 (best), Spring 58,679, Winter 58,607, Summer 55,777 (weakest) |
| Age groups | Young Adult 26.7%, Middle-aged 25.4%, Adult 24.0%, Senior 23.9% of revenue |

## 5. Power BI dashboard
`powerbi/customer_shopping_behavior_dashboard.pbix`: KPI cards for Total Revenue ($233K), Number of Customers (3.9K), Average Purchase Amount ($59.76) and Average Review Rating (3.75); slicers for subscription status, gender, category and shipping type; charts for subscription share, revenue and sales by category, and revenue and sales by age group.

## 6. Key findings
1. Two categories, Clothing and Accessories, bring in three quarters of revenue.
2. Basket size is flat across every customer group, so growth must come from more orders and more customers.
3. The subscription programme is not increasing spend per order.
4. Discounts are common and do not raise basket size.
5. The customer base is mature and loyal, with very few new customers.
6. Fall is the strongest season and Summer the weakest.

## 7. Recommendations
1. **Redesign the subscription** around perks that reward bigger baskets, and target repeat buyers who have not subscribed.
2. **Test smaller discounts** on the five most-discounted items and track sales.
3. **Grow acquisition**, starting with Young Adults, the largest revenue group.
4. **Plan stock and campaigns around Fall**; run Summer promotions to lift the weakest season.
5. **Feature top-rated products** in marketing and collect review text to explain average ratings.
6. **Fix data collection** for discounts and subscriptions across all customers.

## 8. Limitations
- One purchase per customer, with no dates, so trends over time and true repeat behaviour cannot be measured directly.
- Discounts and subscriptions appear only for male customers, which limits gender analysis.
- Purchase amounts are whole US dollars between 20 and 100, which suggests the data may be simulated; results describe this dataset rather than a specific real company.
