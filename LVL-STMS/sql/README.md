# SAP Business One SQL Queries

SQL queries for extracting sales data from SAP B1 for use in the LVL-STMS forecasting system.

## Files

### `sap_b1_sales_extract.sql` (Full Version)
Comprehensive sales data extract with extensive customization options.

**Features**:
- ✅ Complete sales transactions with all dimensions
- ✅ Returns/credit memos integration
- ✅ Product hierarchy (category, subgroup, SKU)
- ✅ Geographic dimensions (region, territory)
- ✅ Channel breakdown
- ✅ Extensive documentation and customization notes
- ✅ Data validation queries included

**Use when**: You need full control and want to customize all mappings

### `sap_b1_simple_extract.sql` (Simplified Version)
Streamlined version with basic mappings.

**Features**:
- ✅ Essential fields only
- ✅ Easier to customize (fewer lines)
- ✅ Faster execution
- ✅ Good for testing

**Use when**: You want to get started quickly

---

## Quick Start

### Option 1: Manual Export (Easiest)

1. **Open SQL file** in SQL Server Management Studio or SAP B1 Query Manager
2. **Customize mappings** (see below)
3. **Run query**
4. **Export results** to CSV
5. **Save to**: `LVL-STMS/data/raw/sap_sales.csv`

### Option 2: Automated Extraction (Recommended)

```bash
# Configure database connection
nano .env

# Add these lines:
SAP_B1_SERVER=your_sap_server
SAP_B1_DATABASE=your_company_db
SAP_B1_USER=your_username
SAP_B1_PASSWORD=your_password

# Run extractor script
python scripts/extract_from_sap_b1.py
```

---

## Required Customizations

### 1. Item Group Mapping (Category)

**Find your item group codes**:
```sql
SELECT ItmsGrpCod, ItmsGrpNam
FROM OITG
ORDER BY ItmsGrpNam
```

**Update in query** (lines 50-56):
```sql
CASE
    WHEN OITM.ItmsGrpCod IN (101, 102, 103) THEN 'Dog Food'  -- Replace with your codes
    WHEN OITM.ItmsGrpCod IN (104, 105, 106) THEN 'Cat Food'
    WHEN OITM.ItmsGrpCod IN (107, 108) THEN 'Treats'
    ELSE 'Other'
END AS [category]
```

### 2. Product Type Mapping (Sub-Group)

**Option A: Use User-Defined Field**
```sql
-- Check if you have product type UDF
SELECT TOP 10 ItemCode, U_ProductType FROM OITM

-- Update query to use your UDF name
WHEN OITM.U_YourFieldName = 'DRY' THEN 'Dry Dog Food'
```

**Option B: Use Item Name Patterns**
```sql
CASE
    WHEN OITM.ItemName LIKE '%Dry%' THEN 'Dry Dog Food'
    WHEN OITM.ItemName LIKE '%Wet%' THEN 'Wet Dog Food'
    ...
END
```

**Option C: Use Price List or Vendor**
```sql
CASE
    WHEN OITM.U_Vendor = 'VendorA' THEN 'Dry Dog Food'
    ...
END
```

### 3. Territory Mapping (Region)

**Find your territories**:
```sql
SELECT territryID, descript
FROM OTER
ORDER BY descript
```

**Update in query** (lines 75-81):
```sql
CASE
    WHEN OTER.descript IN ('New York', 'New Jersey') THEN 'Northeast'  -- Replace
    WHEN OTER.descript IN ('Florida', 'Georgia') THEN 'Southeast'
    ...
END AS [region]
```

### 4. Channel Mapping

**Option A: Customer Group**
```sql
-- Find customer groups
SELECT GroupCode, GroupName
FROM OCRG

-- Update query
CASE
    WHEN OCRD.GroupCode = 100 THEN 'Retail'     -- Replace with your codes
    WHEN OCRD.GroupCode = 101 THEN 'E-commerce'
    ...
END
```

**Option B: Customer UDF**
```sql
-- Check for channel UDF
SELECT TOP 10 CardCode, U_Channel FROM OCRD

-- Update query
CASE
    WHEN OCRD.U_Channel = 'ECOM' THEN 'E-commerce'  -- Your values
    WHEN OCRD.U_Channel = 'RETAIL' THEN 'Retail'
    ...
END
```

**Option C: Sales Person Territory**
```sql
CASE
    WHEN OSLP.SlpName LIKE '%Online%' THEN 'E-commerce'
    WHEN OSLP.SlpName LIKE '%Store%' THEN 'Retail'
    ...
END
```

### 5. Date Range

Update at top of query:
```sql
DECLARE @StartDate DATE = '2022-01-01'  -- Change to your start date
DECLARE @EndDate DATE = '2025-12-31'    -- Change to your end date
```

---

## Testing Your Customizations

### Step 1: Test Item Groups
```sql
SELECT
    OITM.ItmsGrpCod,
    OITG.ItmsGrpNam,
    CASE
        WHEN OITM.ItmsGrpCod IN (101, 102) THEN 'Dog Food'  -- Your mapping
        ELSE 'Other'
    END AS [category],
    COUNT(*) AS item_count
FROM OITM
LEFT JOIN OITG ON OITM.ItmsGrpCod = OITG.ItmsGrpCod
GROUP BY OITM.ItmsGrpCod, OITG.ItmsGrpNam
ORDER BY item_count DESC
```

### Step 2: Test Territory Mapping
```sql
SELECT
    OTER.descript,
    CASE
        WHEN OTER.descript IN ('New York') THEN 'Northeast'  -- Your mapping
        ELSE 'Other'
    END AS [region],
    COUNT(DISTINCT OCRD.CardCode) AS customer_count
FROM OCRD
LEFT JOIN OTER ON OCRD.Territory = OTER.territryID
GROUP BY OTER.descript
ORDER BY customer_count DESC
```

### Step 3: Test Channel Mapping
```sql
SELECT
    OCRD.GroupCode,
    OCRG.GroupName,
    CASE
        WHEN OCRD.GroupCode = 100 THEN 'Retail'  -- Your mapping
        ELSE 'Other'
    END AS [channel],
    COUNT(DISTINCT OCRD.CardCode) AS customer_count
FROM OCRD
LEFT JOIN OCRG ON OCRD.GroupCode = OCRG.GroupCode
GROUP BY OCRD.GroupCode, OCRG.GroupName
ORDER BY customer_count DESC
```

---

## Common SAP B1 Tables Reference

| Table | Description | Key Fields |
|-------|-------------|------------|
| `OINV` | AR Invoices | DocDate, DocTotal, CardCode |
| `INV1` | Invoice Lines | ItemCode, LineTotal, Quantity |
| `ORIN` | AR Credit Memos | DocDate, DocTotal (returns) |
| `RIN1` | Credit Memo Lines | ItemCode, LineTotal, Quantity |
| `OITM` | Items Master | ItemCode, ItemName, ItmsGrpCod |
| `OITG` | Item Groups | ItmsGrpCod, ItmsGrpNam |
| `OCRD` | Business Partners | CardCode, CardName, GroupCode, Territory |
| `OCRG` | BP Groups | GroupCode, GroupName |
| `OTER` | Territories | territryID, descript |
| `OSLP` | Sales Persons | SlpCode, SlpName |

---

## Performance Optimization

### Add Indexes (Run Once)
```sql
-- Speed up date filtering
CREATE INDEX idx_oinv_docdate ON OINV(DocDate)
CREATE INDEX idx_orin_docdate ON ORIN(DocDate)

-- Speed up joins
CREATE INDEX idx_inv1_itemcode ON INV1(ItemCode)
CREATE INDEX idx_rin1_itemcode ON RIN1(ItemCode)
```

### Large Dataset Tips

1. **Extract in chunks**:
   ```sql
   -- Month by month
   DECLARE @StartDate DATE = '2022-01-01'
   DECLARE @EndDate DATE = '2022-01-31'  -- One month at a time
   ```

2. **Filter by item group**:
   ```sql
   AND OITM.ItmsGrpCod IN (101, 102, 103)  -- Only specific groups
   ```

3. **Limit to specific customers**:
   ```sql
   AND OCRD.CardCode IN (SELECT CardCode FROM OCRD WHERE GroupCode = 100)
   ```

---

## Validation Queries

### Check Data Volume
```sql
-- Count invoices by year
SELECT YEAR(DocDate) AS Year, COUNT(*) AS Invoice_Count
FROM OINV
WHERE CANCELED = 'N'
GROUP BY YEAR(DocDate)
ORDER BY Year
```

### Check Date Coverage
```sql
SELECT
    MIN(DocDate) AS Earliest_Invoice,
    MAX(DocDate) AS Latest_Invoice,
    DATEDIFF(DAY, MIN(DocDate), MAX(DocDate)) AS Days_Coverage
FROM OINV
WHERE CANCELED = 'N'
```

### Check Returns Rate
```sql
SELECT
    YEAR(OINV.DocDate) AS Year,
    SUM(INV1.LineTotal) AS Total_Sales,
    ISNULL(SUM(Returns.returns_amount), 0) AS Total_Returns,
    ISNULL(SUM(Returns.returns_amount), 0) / SUM(INV1.LineTotal) * 100 AS Return_Rate_Pct
FROM OINV
INNER JOIN INV1 ON OINV.DocEntry = INV1.DocEntry
LEFT JOIN (
    SELECT YEAR(DocDate) AS Year, SUM(LineTotal) AS returns_amount
    FROM ORIN
    INNER JOIN RIN1 ON ORIN.DocEntry = RIN1.DocEntry
    WHERE CANCELED = 'N'
    GROUP BY YEAR(DocDate)
) Returns ON YEAR(OINV.DocDate) = Returns.Year
WHERE OINV.CANCELED = 'N'
GROUP BY YEAR(OINV.DocDate)
ORDER BY Year
```

---

## Troubleshooting

### Query Returns No Results
- Check date range is valid
- Verify table names (they're case-sensitive)
- Ensure you have read access to tables
- Check if data exists: `SELECT COUNT(*) FROM OINV`

### Mapping Returns "Other" for Everything
- Run test queries above to verify your mappings
- Check actual values in your database
- Verify CASE statement logic

### Query is Slow
- Add indexes (see Performance section)
- Reduce date range
- Filter by item group or customer
- Check execution plan in SSMS

### Permission Errors
- Contact SAP B1 administrator
- Request read access to tables:
  - OINV, INV1, ORIN, RIN1
  - OITM, OITG
  - OCRD, OCRG, OTER

---

## Using Extracted Data

### With Python/Forecasting Models
```python
import pandas as pd
from src.models.sarima import SARIMAForecaster

# Load extracted data
df = pd.read_csv('data/raw/sap_sales.csv', parse_dates=['date'])

# Aggregate to monthly
monthly = df.groupby(pd.Grouper(key='date', freq='M')).agg({
    'net_sales_amount': 'sum'
}).reset_index()

# Train model
forecaster = SARIMAForecaster()
forecaster.fit(monthly, target_col='net_sales_amount')

# Forecast 2026
forecast = forecaster.predict(horizon=12)
forecast.to_csv('forecast_2026.csv')
```

### With Excel
1. Open `sap_sales.csv` in Excel
2. Create PivotTable
3. Rows: Date (group by months)
4. Values: net_sales_amount (Sum)
5. Insert → Chart → Line Chart

---

## Getting Help

**SAP B1 Table Structure**:
```sql
-- List all columns in a table
SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'OINV'
ORDER BY ORDINAL_POSITION
```

**Find User-Defined Fields**:
```sql
-- List UDFs for Items
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'OITM' AND COLUMN_NAME LIKE 'U_%'
```

**Contact**: LVL-CODES Analytics Team

---

**Last Updated**: 2025-12-17
