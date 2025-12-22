/*
================================================================================
LVL-CODES: SAP Business One Sales Data Extract Query
================================================================================
Purpose:
    Extract historical sales data from SAP B1 for use in the Sales Target
    Management System (STMS) forecasting models.

Output Structure:
    Matches the sample data format used in generate_sample_data.py
    - Daily/monthly sales transactions
    - Product hierarchy (category, subgroup, SKU)
    - Geographic dimensions (region, territory)
    - Channel breakdown
    - Returns data
    - Net sales calculations

SAP B1 Tables Used:
    - OINV: AR Invoices (Sales Orders)
    - INV1: Invoice Line Items
    - OITM: Items Master Data
    - OCRD: Business Partners (Customers)
    - OSLP: Sales Persons
    - OTER: Territories
    - ORIN: AR Credit Memos (Returns)
    - RIN1: Credit Memo Line Items

Date Range:
    Modify @StartDate and @EndDate variables as needed
    Recommended: Last 3-5 years for forecasting

Author: LVL-CODES Analytics Team
Version: 1.0.0
Last Updated: 2025-12-17
================================================================================
*/

-- ============================================================================
-- CONFIGURATION VARIABLES
-- ============================================================================

DECLARE @StartDate DATE = '2022-01-01'  -- Start of historical data
DECLARE @EndDate DATE = '2025-12-31'    -- End of historical data

-- ============================================================================
-- MAIN QUERY: SALES TRANSACTIONS WITH ALL DIMENSIONS
-- ============================================================================

WITH SalesData AS (
    -- ========================================================================
    -- EXTRACT SALES INVOICES
    -- ========================================================================
    SELECT
        -- Date Information
        CAST(OINV.DocDate AS DATE) AS [date],
        YEAR(OINV.DocDate) AS [year],
        MONTH(OINV.DocDate) AS [month],
        DATEPART(QUARTER, OINV.DocDate) AS [quarter],
        DATEPART(WEEKDAY, OINV.DocDate) AS [day_of_week],

        -- Product Information
        INV1.ItemCode AS [sku_id],
        ISNULL(OITM.ItemName, 'Unknown') AS [sku_name],

        -- Product Hierarchy (customize based on your SAP B1 setup)
        CASE
            -- Map your SAP B1 item groups to categories
            WHEN OITM.ItmsGrpCod IN (101, 102, 103) THEN 'Dog Food'
            WHEN OITM.ItmsGrpCod IN (104, 105, 106) THEN 'Cat Food'
            WHEN OITM.ItmsGrpCod IN (107, 108) THEN 'Treats'
            WHEN OITM.ItmsGrpCod IN (109, 110) THEN 'Supplements'
            ELSE 'Other'
        END AS [category],

        -- Sub-group classification (customize based on item attributes)
        CASE
            WHEN OITM.U_ProductType = 'DRY' AND OITM.ItmsGrpCod IN (101, 102) THEN 'Dry Dog Food'
            WHEN OITM.U_ProductType = 'WET' AND OITM.ItmsGrpCod IN (101, 102) THEN 'Wet Dog Food'
            WHEN OITM.U_ProductType = 'GRAINFREE' AND OITM.ItmsGrpCod IN (101, 102) THEN 'Grain-Free Dog'
            WHEN OITM.U_ProductType = 'ORGANIC' AND OITM.ItmsGrpCod IN (101, 102) THEN 'Organic Dog'
            WHEN OITM.U_ProductType = 'DRY' AND OITM.ItmsGrpCod IN (104, 105) THEN 'Dry Cat Food'
            WHEN OITM.U_ProductType = 'WET' AND OITM.ItmsGrpCod IN (104, 105) THEN 'Wet Cat Food'
            WHEN OITM.U_ProductType = 'GRAINFREE' AND OITM.ItmsGrpCod IN (104, 105) THEN 'Grain-Free Cat'
            WHEN OITM.U_ProductType = 'ORGANIC' AND OITM.ItmsGrpCod IN (104, 105) THEN 'Organic Cat'
            WHEN OITM.ItmsGrpCod = 107 THEN 'Dog Treats'
            WHEN OITM.ItmsGrpCod = 108 THEN 'Cat Treats'
            ELSE OITM.ItemName
        END AS [subgroup],

        -- Geographic Information
        CASE
            -- Map your SAP B1 territories to regions
            WHEN OTER.descript IN ('New York', 'New Jersey', 'Pennsylvania', 'Connecticut', 'Massachusetts') THEN 'Northeast'
            WHEN OTER.descript IN ('Florida', 'Georgia', 'North Carolina', 'South Carolina', 'Virginia') THEN 'Southeast'
            WHEN OTER.descript IN ('Illinois', 'Michigan', 'Ohio', 'Wisconsin', 'Indiana') THEN 'Midwest'
            WHEN OTER.descript IN ('California', 'Oregon', 'Washington', 'Nevada', 'Arizona') THEN 'West'
            ELSE 'Other'
        END AS [region],

        ISNULL(OTER.descript, 'Unknown') AS [territory],

        -- Channel Information (customize based on your business)
        CASE
            -- Map based on customer type, sales person, or custom field
            WHEN OCRD.U_Channel = 'ECOM' THEN 'E-commerce'
            WHEN OCRD.U_Channel = 'RETAIL' THEN 'Retail'
            WHEN OCRD.U_Channel = 'WHOLESALE' THEN 'Wholesale'
            WHEN OCRD.U_Channel = 'DIST' THEN 'Distribution'
            WHEN OCRD.GroupCode = 100 THEN 'Retail'  -- Example: group code mapping
            WHEN OCRD.GroupCode = 101 THEN 'E-commerce'
            WHEN OCRD.GroupCode = 102 THEN 'Wholesale'
            ELSE 'Retail'  -- Default
        END AS [channel],

        -- Sales Metrics (Gross)
        INV1.LineTotal AS [sales_amount],
        INV1.Quantity AS [sales_quantity],

        -- Transaction Identifiers
        OINV.DocNum AS [invoice_number],
        OCRD.CardCode AS [customer_id],
        OCRD.CardName AS [customer_name]

    FROM OINV

    -- Join to invoice line items
    INNER JOIN INV1 ON OINV.DocEntry = INV1.DocEntry

    -- Join to items master
    LEFT JOIN OITM ON INV1.ItemCode = OITM.ItemCode

    -- Join to business partners (customers)
    LEFT JOIN OCRD ON OINV.CardCode = OCRD.CardCode

    -- Join to territories
    LEFT JOIN OTER ON OCRD.Territory = OTER.territryID

    WHERE
        -- Date filter
        OINV.DocDate BETWEEN @StartDate AND @EndDate

        -- Only posted/closed invoices
        AND OINV.CANCELED = 'N'

        -- Exclude specific document types if needed
        -- AND OINV.DocType = 'I'  -- Only items (not services)

        -- Exclude zero-value transactions
        AND INV1.LineTotal > 0
),

ReturnsData AS (
    -- ========================================================================
    -- EXTRACT RETURNS (CREDIT MEMOS)
    -- ========================================================================
    SELECT
        -- Date Information
        CAST(ORIN.DocDate AS DATE) AS [date],

        -- Product Information
        RIN1.ItemCode AS [sku_id],

        -- Geographic Information
        CASE
            WHEN OTER.descript IN ('New York', 'New Jersey', 'Pennsylvania', 'Connecticut', 'Massachusetts') THEN 'Northeast'
            WHEN OTER.descript IN ('Florida', 'Georgia', 'North Carolina', 'South Carolina', 'Virginia') THEN 'Southeast'
            WHEN OTER.descript IN ('Illinois', 'Michigan', 'Ohio', 'Wisconsin', 'Indiana') THEN 'Midwest'
            WHEN OTER.descript IN ('California', 'Oregon', 'Washington', 'Nevada', 'Arizona') THEN 'West'
            ELSE 'Other'
        END AS [region],

        -- Channel Information
        CASE
            WHEN OCRD.U_Channel = 'ECOM' THEN 'E-commerce'
            WHEN OCRD.U_Channel = 'RETAIL' THEN 'Retail'
            WHEN OCRD.U_Channel = 'WHOLESALE' THEN 'Wholesale'
            WHEN OCRD.U_Channel = 'DIST' THEN 'Distribution'
            WHEN OCRD.GroupCode = 100 THEN 'Retail'
            WHEN OCRD.GroupCode = 101 THEN 'E-commerce'
            WHEN OCRD.GroupCode = 102 THEN 'Wholesale'
            ELSE 'Retail'
        END AS [channel],

        -- Return Metrics
        RIN1.LineTotal AS [returns_amount],
        RIN1.Quantity AS [returns_quantity]

    FROM ORIN

    -- Join to credit memo line items
    INNER JOIN RIN1 ON ORIN.DocEntry = RIN1.DocEntry

    -- Join to business partners
    LEFT JOIN OCRD ON ORIN.CardCode = OCRD.CardCode

    -- Join to territories
    LEFT JOIN OTER ON OCRD.Territory = OTER.territryID

    WHERE
        -- Date filter
        ORIN.DocDate BETWEEN @StartDate AND @EndDate

        -- Only posted/closed credit memos
        AND ORIN.CANCELED = 'N'

        -- Exclude zero-value transactions
        AND RIN1.LineTotal > 0
)

-- ============================================================================
-- FINAL OUTPUT: COMBINE SALES AND RETURNS
-- ============================================================================

SELECT
    -- Date dimensions
    S.[date],
    S.[year],
    S.[month],
    S.[quarter],
    S.[day_of_week],
    CASE WHEN S.[day_of_week] IN (1, 7) THEN 1 ELSE 0 END AS [is_weekend],  -- Sunday=1, Saturday=7

    -- Product dimensions
    S.[sku_id],
    S.[sku_name],
    S.[category],
    S.[subgroup],

    -- Geographic dimensions
    S.[region],
    S.[territory],

    -- Channel
    S.[channel],

    -- Sales metrics (Gross)
    ISNULL(S.[sales_amount], 0) AS [sales_amount],
    ISNULL(S.[sales_quantity], 0) AS [sales_quantity],

    -- Returns metrics
    ISNULL(R.[returns_amount], 0) AS [returns_amount],
    ISNULL(R.[returns_quantity], 0) AS [returns_quantity],

    -- Net sales (Sales - Returns)
    ISNULL(S.[sales_amount], 0) - ISNULL(R.[returns_amount], 0) AS [net_sales_amount],
    ISNULL(S.[sales_quantity], 0) - ISNULL(R.[returns_quantity], 0) AS [net_sales_quantity],

    -- Additional fields
    S.[invoice_number],
    S.[customer_id],
    S.[customer_name]

FROM SalesData S

-- Left join to returns (aggregated by date, SKU, region, channel)
LEFT JOIN (
    SELECT
        [date],
        [sku_id],
        [region],
        [channel],
        SUM([returns_amount]) AS [returns_amount],
        SUM([returns_quantity]) AS [returns_quantity]
    FROM ReturnsData
    GROUP BY [date], [sku_id], [region], [channel]
) R ON
    S.[date] = R.[date]
    AND S.[sku_id] = R.[sku_id]
    AND S.[region] = R.[region]
    AND S.[channel] = R.[channel]

-- Order by date and SKU
ORDER BY S.[date], S.[sku_id], S.[region], S.[channel]

-- ============================================================================
-- QUERY NOTES & CUSTOMIZATION INSTRUCTIONS
-- ============================================================================

/*
IMPORTANT CUSTOMIZATION AREAS:

1. ITEM GROUP MAPPING (Lines 50-56):
   - Replace example item group codes (101-110) with your actual SAP B1 item group codes
   - Check in SAP B1: Administration → Setup → Inventory → Item Groups
   - Get codes from OITG table: SELECT * FROM OITG

2. PRODUCT TYPE CLASSIFICATION (Lines 59-72):
   - Replace U_ProductType with your actual user-defined field
   - Or use other OITM fields like U_Category, U_SubCategory, etc.
   - Check your item master UDFs in SAP B1

3. TERRITORY MAPPING (Lines 75-81):
   - Update territory names to match your SAP B1 setup
   - Get from OTER table: SELECT * FROM OTER
   - Map to your business regions

4. CHANNEL MAPPING (Lines 86-95):
   - Update based on how you track sales channels
   - Options:
     a) Customer UDF (U_Channel)
     b) Customer Group (GroupCode)
     c) Sales Person (SlpCode)
     d) Price List
   - Check OCRD table for available fields

5. DATE RANGE (Lines 27-28):
   - Adjust @StartDate and @EndDate as needed
   - Recommended: 3-5 years for forecasting

6. FILTERS (Lines 124-132):
   - Add additional filters as needed:
     - Specific warehouses: AND OINV.Filler = 'XX'
     - Specific customers: AND OCRD.CardCode IN (...)
     - Specific item groups: AND OITM.ItmsGrpCod IN (...)

PERFORMANCE TIPS:

1. Create indexes on frequently joined columns:
   - CREATE INDEX idx_oinv_docdate ON OINV(DocDate)
   - CREATE INDEX idx_inv1_itemcode ON INV1(ItemCode)

2. For large datasets, consider:
   - Running for smaller date ranges
   - Aggregating to monthly instead of daily
   - Exporting in batches

3. Test query performance:
   - Check execution plan
   - Ensure indexes exist
   - Consider adding WHERE clauses for specific item groups

VALIDATION QUERIES:

-- Check date range coverage
SELECT MIN(DocDate), MAX(DocDate) FROM OINV

-- Check item group distribution
SELECT OITG.ItmsGrpNam, COUNT(*)
FROM OITM
INNER JOIN OITG ON OITM.ItmsGrpCod = OITG.ItmsGrpCod
GROUP BY OITG.ItmsGrpNam

-- Check territory distribution
SELECT descript, COUNT(*)
FROM OCRD
INNER JOIN OTER ON OCRD.Territory = OTER.territryID
GROUP BY descript

-- Check customer group distribution
SELECT GroupCode, GroupName, COUNT(*)
FROM OCRD
INNER JOIN OCRG ON OCRD.GroupCode = OCRG.GroupCode
GROUP BY GroupCode, GroupName

EXPORT INSTRUCTIONS:

1. Run query in SAP B1 Query Manager or SQL Server Management Studio
2. Export results to CSV
3. Save as: LVL-STMS/data/raw/sap_b1_sales_export.csv
4. Use in Python:

   import pandas as pd
   df = pd.read_csv('data/raw/sap_b1_sales_export.csv', parse_dates=['date'])

   # Now use with forecasting models
   from src.models.sarima import SARIMAForecaster
   forecaster = SARIMAForecaster()
   forecaster.fit(df, target_col='net_sales_amount')

TROUBLESHOOTING:

- Query too slow? Add date range filter: DocDate >= '2024-01-01'
- Missing categories? Check OITM.ItmsGrpCod values
- No returns? Verify ORIN table has data
- Wrong regions? Update OTER territory mapping

For questions or issues, contact LVL-CODES Analytics Team.
*/

-- ============================================================================
-- END OF QUERY
-- ============================================================================
