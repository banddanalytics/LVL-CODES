/*
================================================================================
SAP B1 Sales Extract - SIMPLIFIED VERSION
================================================================================
Use this if you just want basic sales data without complex mappings.
Customize the hardcoded values in the CASE statements based on your SAP B1 setup.
================================================================================
*/

-- Set date range
DECLARE @StartDate DATE = '2022-01-01'
DECLARE @EndDate DATE = '2025-12-31'

-- Simple sales extract with returns
SELECT
    -- Basic dimensions
    CAST(OINV.DocDate AS DATE) AS [date],
    INV1.ItemCode AS [sku_id],
    OITM.ItemName AS [sku_name],

    -- TODO: Map your item groups to categories
    CASE
        WHEN OITM.ItmsGrpCod BETWEEN 101 AND 103 THEN 'Dog Food'
        WHEN OITM.ItmsGrpCod BETWEEN 104 AND 106 THEN 'Cat Food'
        WHEN OITM.ItmsGrpCod BETWEEN 107 AND 108 THEN 'Treats'
        ELSE 'Other'
    END AS [category],

    -- TODO: Map territories to regions
    CASE
        WHEN OTER.descript LIKE '%NY%' OR OTER.descript LIKE '%NJ%' THEN 'Northeast'
        WHEN OTER.descript LIKE '%FL%' OR OTER.descript LIKE '%GA%' THEN 'Southeast'
        WHEN OTER.descript LIKE '%IL%' OR OTER.descript LIKE '%MI%' THEN 'Midwest'
        WHEN OTER.descript LIKE '%CA%' OR OTER.descript LIKE '%WA%' THEN 'West'
        ELSE 'Other'
    END AS [region],

    -- TODO: Map customer groups to channels
    CASE
        WHEN OCRD.GroupCode = 100 THEN 'Retail'
        WHEN OCRD.GroupCode = 101 THEN 'E-commerce'
        WHEN OCRD.GroupCode = 102 THEN 'Wholesale'
        ELSE 'Retail'
    END AS [channel],

    -- Sales figures
    INV1.LineTotal AS [sales_amount],
    INV1.Quantity AS [sales_quantity],

    -- Returns (will be 0 if no matching return)
    ISNULL(Returns.returns_amount, 0) AS [returns_amount],
    ISNULL(Returns.returns_quantity, 0) AS [returns_quantity],

    -- Net sales
    INV1.LineTotal - ISNULL(Returns.returns_amount, 0) AS [net_sales_amount],
    INV1.Quantity - ISNULL(Returns.returns_quantity, 0) AS [net_sales_quantity]

FROM OINV
INNER JOIN INV1 ON OINV.DocEntry = INV1.DocEntry
LEFT JOIN OITM ON INV1.ItemCode = OITM.ItemCode
LEFT JOIN OCRD ON OINV.CardCode = OCRD.CardCode
LEFT JOIN OTER ON OCRD.Territory = OTER.territryID

-- Get returns (credit memos) for matching transactions
LEFT JOIN (
    SELECT
        CAST(ORIN.DocDate AS DATE) AS [date],
        RIN1.ItemCode,
        SUM(RIN1.LineTotal) AS [returns_amount],
        SUM(RIN1.Quantity) AS [returns_quantity]
    FROM ORIN
    INNER JOIN RIN1 ON ORIN.DocEntry = RIN1.DocEntry
    WHERE ORIN.DocDate BETWEEN @StartDate AND @EndDate
        AND ORIN.CANCELED = 'N'
    GROUP BY CAST(ORIN.DocDate AS DATE), RIN1.ItemCode
) Returns ON
    CAST(OINV.DocDate AS DATE) = Returns.[date]
    AND INV1.ItemCode = Returns.ItemCode

WHERE
    OINV.DocDate BETWEEN @StartDate AND @EndDate
    AND OINV.CANCELED = 'N'
    AND INV1.LineTotal > 0

ORDER BY OINV.DocDate, INV1.ItemCode

/*
QUICK CUSTOMIZATION CHECKLIST:

1. Line 14-18: Update item group codes (check OITG table)
2. Line 21-26: Update territory names (check OTER table)
3. Line 29-33: Update customer group codes (check OCRG table)
4. Line 9-10: Set your desired date range

TO FIND YOUR VALUES:
- Item Groups: SELECT * FROM OITG
- Territories: SELECT * FROM OTER
- Customer Groups: SELECT * FROM OCRG

EXPORT TO CSV:
1. Run query in SQL Server Management Studio
2. Results → Save Results As → CSV
3. Save to: LVL-STMS/data/raw/sap_sales.csv
*/
