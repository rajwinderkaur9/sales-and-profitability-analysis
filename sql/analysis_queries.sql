--==========================================================
--SUPERSTORE SALES & PROFITABILITY ANALYTICAL QUERIES
--==========================================================

-- 1. Category Profitability Disconnect
SELECT 
    Category, 
    ROUND(SUM(Sales), 2) AS Total_Sales, 
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2) AS Profit_Margin_Pct
FROM superstore
GROUP BY Category
ORDER BY Total_Profit DESC;

-- 2. Top Loss-Making Products (Bottom 10)
SELECT 
    Product_Name, 
    Category, 
    Sub_Category, 
    ROUND(SUM(Sales), 2) AS Total_Sales, 
    ROUND(SUM(Profit), 2) AS Total_Profit
FROM superstore
GROUP BY Product_Name, Category, Sub_Category
HAVING SUM(Profit) < 0
ORDER BY Total_Profit ASC
LIMIT 10;

-- 3. Discount Impact Analysis
SELECT 
    ROUND(Discount * 100, 0) AS Discount_Percentage,
    COUNT(Order_ID) AS Total_Transactions,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(AVG(Profit), 2) AS Avg_Profit_Per_Order
FROM superstore
GROUP BY Discount
ORDER BY Discount;

-- 4. Regional Efficiency Ranking
SELECT 
    Region, 
    ROUND(SUM(Sales), 2) AS Total_Sales, 
    ROUND(SUM(Profit), 2) AS Total_Profit,
    ROUND(SUM(Profit) / SUM(Sales) * 100, 2) AS Profit_Margin_Pct
FROM superstore
GROUP BY Region
ORDER BY Total_Profit DESC;

-- 5. Product Profit Ranking within Category (Window Function)
WITH product_performance AS (
    SELECT 
        Category, 
        Product_Name, 
        SUM(Sales) AS Total_Sales, 
        SUM(Profit) AS Total_Profit
    FROM superstore
    GROUP BY Category, Product_Name
)
SELECT 
    Category, 
    Product_Name, 
    ROUND(Total_Sales, 2) AS Total_Sales, 
    ROUND(Total_Profit, 2) AS Total_Profit,
    DENSE_RANK() OVER (PARTITION BY Category ORDER BY Total_Profit DESC) AS Profit_Rank
FROM product_performance;
