"""
LVL-CODES: SAP Business One Data Extractor
================================================================================
This script connects to SAP B1 database and extracts sales data for forecasting.

Features:
    - Direct connection to SAP B1 SQL Server database
    - Executes the sales extract query
    - Saves to Excel-compatible CSV files
    - Data validation and quality checks
    - Progress tracking

Prerequisites:
    1. Install ODBC driver: pip install pyodbc
    2. Configure database connection in .env file:
       SAP_B1_SERVER=your_server
       SAP_B1_DATABASE=your_company_db
       SAP_B1_USER=your_user
       SAP_B1_PASSWORD=your_password

Usage:
    python scripts/extract_from_sap_b1.py

    # Or with custom date range
    python scripts/extract_from_sap_b1.py --start-date 2022-01-01 --end-date 2025-12-31

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

import sys
from pathlib import Path
import pandas as pd
import pyodbc
from datetime import datetime, timedelta
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logging import get_logger, ProgressLogger
from src.utils.helpers import ensure_directory, load_config
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize logger
logger = get_logger(__name__)


class SAPB1Extractor:
    """
    SAP Business One data extractor.

    Connects to SAP B1 SQL Server database and extracts sales data
    using the predefined SQL query.
    """

    def __init__(self):
        """Initialize SAP B1 connection."""
        self.connection = None
        self.server = os.getenv('SAP_B1_SERVER')
        self.database = os.getenv('SAP_B1_DATABASE')
        self.username = os.getenv('SAP_B1_USER')
        self.password = os.getenv('SAP_B1_PASSWORD')

        # Validate configuration
        if not all([self.server, self.database, self.username, self.password]):
            raise ValueError(
                "SAP B1 connection not configured. Please set in .env file:\n"
                "  SAP_B1_SERVER=your_server\n"
                "  SAP_B1_DATABASE=your_company_db\n"
                "  SAP_B1_USER=your_user\n"
                "  SAP_B1_PASSWORD=your_password"
            )

    def connect(self):
        """
        Establish connection to SAP B1 database.

        Returns:
            pyodbc connection object

        Raises:
            Exception: If connection fails
        """
        logger.info(f"Connecting to SAP B1: {self.server}/{self.database}")

        try:
            # Build connection string
            conn_str = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                f"TrustServerCertificate=yes;"
            )

            # Connect
            self.connection = pyodbc.connect(conn_str, timeout=30)
            logger.info("✓ Connected to SAP B1 successfully")

            return self.connection

        except Exception as e:
            logger.error(f"Failed to connect to SAP B1: {str(e)}")
            raise

    def load_query(self, query_file: str = None):
        """
        Load SQL query from file.

        Args:
            query_file: Path to SQL file (default: sql/sap_b1_sales_extract.sql)

        Returns:
            SQL query string
        """
        if query_file is None:
            query_file = Path(__file__).parent.parent / "sql" / "sap_b1_sales_extract.sql"
        else:
            query_file = Path(query_file)

        if not query_file.exists():
            raise FileNotFoundError(f"Query file not found: {query_file}")

        logger.info(f"Loading query from: {query_file}")

        with open(query_file, 'r') as f:
            query = f.read()

        return query

    def extract_sales_data(
        self,
        start_date: str,
        end_date: str,
        query_file: str = None
    ) -> pd.DataFrame:
        """
        Extract sales data from SAP B1.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            query_file: Optional custom SQL file

        Returns:
            DataFrame with sales data

        Example:
            >>> extractor = SAPB1Extractor()
            >>> df = extractor.extract_sales_data('2022-01-01', '2025-12-31')
        """
        logger.info(f"Extracting sales data from {start_date} to {end_date}")

        # Load query
        query = self.load_query(query_file)

        # Replace date placeholders
        query = query.replace(
            "DECLARE @StartDate DATE = '2022-01-01'",
            f"DECLARE @StartDate DATE = '{start_date}'"
        )
        query = query.replace(
            "DECLARE @EndDate DATE = '2025-12-31'",
            f"DECLARE @EndDate DATE = '{end_date}'"
        )

        # Connect to database
        if self.connection is None:
            self.connect()

        # Execute query
        logger.info("Executing SQL query...")
        logger.info("This may take several minutes for large datasets...")

        try:
            df = pd.read_sql(query, self.connection, parse_dates=['date'])

            logger.info(f"✓ Extracted {len(df):,} records")
            logger.info(f"  Date range: {df['date'].min()} to {df['date'].max()}")
            logger.info(f"  Total sales: ${df['sales_amount'].sum():,.2f}")
            logger.info(f"  Net sales: ${df['net_sales_amount'].sum():,.2f}")

            return df

        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    def save_to_csv(self, df: pd.DataFrame, output_dir: str = "./data/raw") -> dict:
        """
        Save extracted data to CSV files.

        Args:
            df: DataFrame with sales data
            output_dir: Output directory

        Returns:
            Dictionary of saved file paths
        """
        output_path = ensure_directory(output_dir)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        logger.info(f"Saving data to {output_path}")

        files = {}

        # ====================================================================
        # 1. FULL EXTRACT
        # ====================================================================
        full_file = output_path / f"sap_b1_sales_extract_{timestamp}.csv"
        df.to_csv(full_file, index=False)
        files['full'] = str(full_file)
        logger.info(f"✓ Saved full extract: {full_file}")

        # ====================================================================
        # 2. TIME SERIES (for quick forecasting)
        # ====================================================================
        ts = df.groupby('date').agg({
            'net_sales_amount': 'sum'
        }).reset_index()
        ts.columns = ['date', 'sales']

        ts_file = output_path / f"sap_b1_timeseries_{timestamp}.csv"
        ts.to_csv(ts_file, index=False)
        files['timeseries'] = str(ts_file)
        logger.info(f"✓ Saved time series: {ts_file}")

        # ====================================================================
        # 3. MONTHLY SUMMARY
        # ====================================================================
        monthly = df.groupby([
            pd.Grouper(key='date', freq='M'),
            'category', 'region', 'channel'
        ]).agg({
            'sales_amount': 'sum',
            'sales_quantity': 'sum',
            'returns_amount': 'sum',
            'returns_quantity': 'sum',
            'net_sales_amount': 'sum',
            'net_sales_quantity': 'sum',
            'sku_id': 'nunique'
        }).reset_index()

        monthly.columns = [
            'date', 'category', 'region', 'channel',
            'sales_amount', 'sales_quantity',
            'returns_amount', 'returns_quantity',
            'net_sales_amount', 'net_sales_quantity',
            'distinct_skus'
        ]

        monthly_file = output_path / f"sap_b1_monthly_{timestamp}.csv"
        monthly.to_csv(monthly_file, index=False)
        files['monthly'] = str(monthly_file)
        logger.info(f"✓ Saved monthly summary: {monthly_file}")

        return files

    def validate_data(self, df: pd.DataFrame) -> dict:
        """
        Validate extracted data quality.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary with validation results
        """
        logger.info("Validating data quality...")

        validation = {
            'total_records': len(df),
            'date_range': (df['date'].min(), df['date'].max()),
            'null_checks': {},
            'data_quality': {},
            'warnings': []
        }

        # Check for nulls
        for col in df.columns:
            null_count = df[col].isna().sum()
            null_pct = (null_count / len(df)) * 100
            validation['null_checks'][col] = {
                'count': null_count,
                'percentage': null_pct
            }

            if null_pct > 5:
                validation['warnings'].append(
                    f"Column '{col}' has {null_pct:.1f}% null values"
                )

        # Data quality checks
        validation['data_quality']['negative_sales'] = (df['net_sales_amount'] < 0).sum()
        validation['data_quality']['zero_sales'] = (df['net_sales_amount'] == 0).sum()
        validation['data_quality']['high_returns'] = (df['returns_amount'] > df['sales_amount']).sum()

        # Log warnings
        if validation['warnings']:
            logger.warning("Data quality issues found:")
            for warning in validation['warnings']:
                logger.warning(f"  - {warning}")

        logger.info("✓ Data validation complete")

        return validation

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")


def main():
    """
    Main function to run SAP B1 data extraction.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract sales data from SAP B1')
    parser.add_argument('--start-date', default='2022-01-01',
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', default='2025-12-31',
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--query-file', default=None,
                       help='Custom SQL query file')
    parser.add_argument('--output-dir', default='./data/raw',
                       help='Output directory')

    args = parser.parse_args()

    print("="*80)
    print("SAP Business One Sales Data Extractor")
    print("="*80)
    print()
    print(f"Date Range: {args.start_date} to {args.end_date}")
    print(f"Output Directory: {args.output_dir}")
    print()

    try:
        # Create extractor
        extractor = SAPB1Extractor()

        # Extract data
        df = extractor.extract_sales_data(
            start_date=args.start_date,
            end_date=args.end_date,
            query_file=args.query_file
        )

        # Validate data
        validation = extractor.validate_data(df)

        # Save to CSV
        files = extractor.save_to_csv(df, output_dir=args.output_dir)

        # Close connection
        extractor.close()

        # Print summary
        print()
        print("="*80)
        print("✓ Extraction Complete!")
        print("="*80)
        print()
        print("Files Created:")
        for name, path in files.items():
            print(f"  • {name:12s}: {path}")
        print()
        print("Data Summary:")
        print(f"  • Total Records: {validation['total_records']:,}")
        print(f"  • Date Range: {validation['date_range'][0].date()} to {validation['date_range'][1].date()}")
        print(f"  • Total Sales: ${df['sales_amount'].sum():,.2f}")
        print(f"  • Net Sales: ${df['net_sales_amount'].sum():,.2f}")
        print(f"  • Categories: {df['category'].nunique()}")
        print(f"  • SKUs: {df['sku_id'].nunique()}")
        print(f"  • Regions: {df['region'].nunique()}")
        print()
        print("Next Steps:")
        print("  1. Open CSV files in Excel to review data")
        print("  2. Use time series file for forecasting:")
        print(f"     python scripts/demo_forecast_with_excel.py --data {files['timeseries']}")
        print("  3. Check data quality warnings above (if any)")
        print()

    except Exception as e:
        print()
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
