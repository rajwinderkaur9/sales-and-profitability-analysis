import pandas as pd
import sqlite3

print("Loading Superstore CSV into SQLite...")

# Load raw CSV data and clean column names
df = pd.read_csv("../data/raw/superstore.csv", encoding="latin1")
# Strip extra spaces and replace spaces, hyphens, and slashes with underscores
df.columns = (
    df.columns.str.strip()
    .str.replace(" ", "_")
    .str.replace("-", "_")
    .str.replace("/", "_")
)

# DATA HYGIENE: Remove duplicate rows if any exist
initial_rows = len(df)
df = df.drop_duplicates()
print(f"Removed {initial_rows - len(df)} duplicate rows.")

# DATA HYGIENE: Strip whitespace from text columns (prevents grouping bugs)
text_columns = df.select_dtypes(include=["object"]).columns
for col in text_columns:
    df[col] = df[col].str.strip()

# Add a row-level profit margin column for Power BI
df["Profit_Margin"] = df["Profit"] / df["Sales"]

# EXPORT CLEANED MASTER DATASET
df.to_csv("../data/cleaned/superstore_cleaned.csv", index=False)
print("Cleaned master dataset saved to data/cleaned/!\n")

# Create local SQLite database connection
conn = sqlite3.connect("superstore.db")
df.to_sql("superstore", conn, if_exists="replace", index=False)
print("Database table 'superstore' created successfully!\n")

# Dictionary of all 5 core analytical queries
queries = {
    "1. Category Profitability Disconnect": """
        SELECT 
            Category, 
            ROUND(SUM(Sales), 2) AS Total_Sales, 
            ROUND(SUM(Profit), 2) AS Total_Profit,
            ROUND(SUM(Profit) / SUM(Sales) * 100, 2) AS Profit_Margin_Pct
        FROM superstore
        GROUP BY Category
        ORDER BY Total_Profit DESC;
    """,
    "2. Top Loss-Making Products (Bottom 10)": """
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
    """,
    "3. Discount Impact Analysis": """
        SELECT 
            ROUND(Discount * 100, 0) AS Discount_Percentage,
            COUNT(Order_ID) AS Total_Transactions,
            ROUND(SUM(Sales), 2) AS Total_Sales,
            ROUND(SUM(Profit), 2) AS Total_Profit,
            ROUND(AVG(Profit), 2) AS Avg_Profit_Per_Order
        FROM superstore
        GROUP BY Discount
        ORDER BY Discount;
    """,
    "4. Regional Efficiency Ranking": """
        SELECT 
            Region, 
            ROUND(SUM(Sales), 2) AS Total_Sales, 
            ROUND(SUM(Profit), 2) AS Total_Profit,
            ROUND(SUM(Profit) / SUM(Sales) * 100, 2) AS Profit_Margin_Pct
        FROM superstore
        GROUP BY Region
        ORDER BY Total_Profit DESC;
    """,
    "5. Product Profit Ranking within Category (Window Function)": """
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
    """,
}

# Execute and print each query
for title, query_sql in queries.items.items() if hasattr(queries.items(), 'items') else queries.items():
    print(f"--- {title} ---")
    result_df = pd.read_sql(query_sql, conn)
    print(result_df.head(10).to_string(index=False))
    print("\n" + "=" * 60 + "\n")

# Exporting cleaned master dataset from Python:
#df.to_csv("../data/cleaned/superstore_cleaned.csv", index=False)

conn.close()
print("All queries executed successfully!")
