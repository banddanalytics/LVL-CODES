"""
LVL-CODES: Database Connector
================================================================================
This module provides database connectivity to the data warehouse, handling
connection pooling, query execution, and data retrieval.

Supports:
    - PostgreSQL
    - SQL Server
    - MySQL
    - Oracle (with appropriate drivers)

Features:
    - Connection pooling for performance
    - Automatic query logging
    - Transaction management
    - Parameterized queries for security
    - Connection health checking

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

from typing import Optional, Dict, List, Any, Union
from contextlib import contextmanager
import pandas as pd
from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
import urllib

from src.utils.logging import get_logger, log_execution_time
from src.utils.helpers import load_config
from src.utils.constants import TableNames, ColumnNames

# Initialize logger
logger = get_logger(__name__)


class DatabaseConnector:
    """
    Database connector with connection pooling and query execution capabilities.

    This class manages connections to the data warehouse and provides
    methods for executing queries, loading data, and managing transactions.

    Attributes:
        engine: SQLAlchemy engine instance
        config: Database configuration dictionary

    Example:
        >>> db = DatabaseConnector()
        >>> df = db.query_to_dataframe("SELECT * FROM fact_sales LIMIT 1000")
        >>> db.close()
    """

    def __init__(self, config_path: str = "./config/database.yaml", profile: str = "data_warehouse"):
        """
        Initialize database connector.

        Args:
            config_path: Path to database configuration file
            profile: Configuration profile to use (e.g., 'data_warehouse', 'sql_server')

        Raises:
            ValueError: If configuration is invalid
            SQLAlchemyError: If connection fails
        """
        logger.info(f"Initializing DatabaseConnector with profile '{profile}'")

        # Load configuration
        self.config = load_config("database")

        if profile not in self.config:
            raise ValueError(f"Profile '{profile}' not found in database configuration")

        self.profile_config = self.config[profile]
        self.engine: Optional[Engine] = None
        self.metadata = MetaData()

        # Create engine
        self._create_engine()

        # Test connection
        self._test_connection()

    def _create_engine(self) -> None:
        """
        Create SQLAlchemy engine with connection pooling.

        This method builds the connection string and creates an engine
        with appropriate pool settings for optimal performance.
        """
        db_type = self.profile_config.get("type", "postgresql")
        host = self.profile_config["host"]
        port = self.profile_config["port"]
        database = self.profile_config["database"]
        user = self.profile_config["user"]
        password = self.profile_config["password"]

        # Build connection string based on database type
        if db_type == "postgresql":
            connection_string = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

        elif db_type == "mssql":
            # URL encode password to handle special characters
            password_encoded = urllib.parse.quote_plus(password)
            driver = self.profile_config.get("driver", "{ODBC Driver 17 for SQL Server}")
            connection_string = (
                f"mssql+pyodbc://{user}:{password_encoded}@{host}:{port}/{database}"
                f"?driver={urllib.parse.quote_plus(driver)}"
            )

        elif db_type == "mysql":
            connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

        elif db_type == "oracle":
            connection_string = f"oracle+cx_oracle://{user}:{password}@{host}:{port}/{database}"

        else:
            raise ValueError(f"Unsupported database type: {db_type}")

        # Pool configuration
        pool_config = self.profile_config.get("pool", {})
        pool_size = pool_config.get("size", 10)
        max_overflow = pool_config.get("max_overflow", 20)
        pool_timeout = pool_config.get("timeout", 30)
        pool_recycle = pool_config.get("recycle", 3600)

        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_timeout=pool_timeout,
                pool_recycle=pool_recycle,
                echo=False,  # Set to True for SQL query logging
                future=True,  # Use SQLAlchemy 2.0 style
            )

            logger.info(f"Database engine created successfully for {db_type}")

        except Exception as e:
            logger.error(f"Failed to create database engine: {str(e)}")
            raise

    def _test_connection(self) -> None:
        """
        Test database connection.

        Raises:
            SQLAlchemyError: If connection test fails
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")

        except SQLAlchemyError as e:
            logger.error(f"Database connection test failed: {str(e)}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields a database connection that is automatically closed
        when the context exits.

        Yields:
            SQLAlchemy connection object

        Example:
            >>> with db.get_connection() as conn:
            >>>     result = conn.execute(text("SELECT * FROM table"))
        """
        connection = self.engine.connect()
        try:
            yield connection
        finally:
            connection.close()

    @log_execution_time("query_to_dataframe")
    def query_to_dataframe(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        parse_dates: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Execute a SQL query and return results as a pandas DataFrame.

        Args:
            query: SQL query string (use :param_name for parameters)
            params: Dictionary of query parameters for safe parameterization
            parse_dates: List of column names to parse as dates

        Returns:
            DataFrame containing query results

        Raises:
            SQLAlchemyError: If query execution fails

        Example:
            >>> query = "SELECT * FROM fact_sales WHERE date >= :start_date"
            >>> df = db.query_to_dataframe(
            >>>     query,
            >>>     params={"start_date": "2025-01-01"},
            >>>     parse_dates=["date"]
            >>> )
        """
        try:
            logger.debug(f"Executing query: {query[:100]}...")  # Log first 100 chars

            # Execute query with parameters for safety
            if params:
                df = pd.read_sql(
                    text(query),
                    self.engine,
                    params=params,
                    parse_dates=parse_dates
                )
            else:
                df = pd.read_sql(
                    query,
                    self.engine,
                    parse_dates=parse_dates
                )

            logger.info(f"Query returned {len(df)} rows, {len(df.columns)} columns")
            return df

        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    @log_execution_time("execute_query")
    def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        commit: bool = True
    ) -> int:
        """
        Execute a SQL query (INSERT, UPDATE, DELETE, etc.).

        Args:
            query: SQL query string
            params: Dictionary of query parameters
            commit: Whether to commit the transaction

        Returns:
            Number of rows affected

        Raises:
            SQLAlchemyError: If query execution fails

        Example:
            >>> query = "UPDATE fact_targets SET value = :new_value WHERE id = :id"
            >>> rows = db.execute_query(
            >>>     query,
            >>>     params={"new_value": 1000, "id": 123}
            >>> )
        """
        try:
            with self.engine.begin() as conn:
                result = conn.execute(text(query), params or {})

                if commit:
                    # Transaction is automatically committed when context exits
                    pass

                rows_affected = result.rowcount
                logger.info(f"Query executed successfully, {rows_affected} rows affected")
                return rows_affected

        except SQLAlchemyError as e:
            logger.error(f"Query execution failed: {str(e)}")
            raise

    def table_exists(self, table_name: str, schema: Optional[str] = None) -> bool:
        """
        Check if a table exists in the database.

        Args:
            table_name: Name of the table
            schema: Schema name (optional)

        Returns:
            True if table exists, False otherwise

        Example:
            >>> if db.table_exists("fact_sales"):
            >>>     print("Table exists")
        """
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names(schema=schema)
            return table_name in tables

        except Exception as e:
            logger.error(f"Failed to check table existence: {str(e)}")
            return False

    def get_table_columns(self, table_name: str, schema: Optional[str] = None) -> List[str]:
        """
        Get column names for a table.

        Args:
            table_name: Name of the table
            schema: Schema name (optional)

        Returns:
            List of column names

        Example:
            >>> columns = db.get_table_columns("fact_sales")
            >>> print(f"Columns: {columns}")
        """
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name, schema=schema)
            column_names = [col["name"] for col in columns]

            logger.debug(f"Table '{table_name}' has {len(column_names)} columns")
            return column_names

        except Exception as e:
            logger.error(f"Failed to get table columns: {str(e)}")
            return []

    def load_table(
        self,
        table_name: str,
        schema: Optional[str] = None,
        columns: Optional[List[str]] = None,
        where_clause: Optional[str] = None,
        limit: Optional[int] = None,
        parse_dates: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Load data from a table with optional filtering.

        Args:
            table_name: Name of the table
            schema: Schema name (optional)
            columns: List of columns to select (None = all columns)
            where_clause: WHERE clause for filtering (without the WHERE keyword)
            limit: Maximum number of rows to return
            parse_dates: List of date columns to parse

        Returns:
            DataFrame containing table data

        Example:
            >>> df = db.load_table(
            >>>     "fact_sales",
            >>>     columns=["date", "sku_id", "sales_amount"],
            >>>     where_clause="date >= '2025-01-01'",
            >>>     limit=10000,
            >>>     parse_dates=["date"]
            >>> )
        """
        # Build SELECT clause
        if columns:
            select_clause = ", ".join(columns)
        else:
            select_clause = "*"

        # Build full table name with schema
        if schema:
            full_table_name = f"{schema}.{table_name}"
        else:
            full_table_name = table_name

        # Build query
        query = f"SELECT {select_clause} FROM {full_table_name}"

        if where_clause:
            query += f" WHERE {where_clause}"

        if limit:
            query += f" LIMIT {limit}"

        return self.query_to_dataframe(query, parse_dates=parse_dates)

    def insert_dataframe(
        self,
        df: pd.DataFrame,
        table_name: str,
        schema: Optional[str] = None,
        if_exists: str = "append",
        chunksize: int = 1000
    ) -> None:
        """
        Insert a DataFrame into a database table.

        Args:
            df: DataFrame to insert
            table_name: Target table name
            schema: Schema name (optional)
            if_exists: Action if table exists ('fail', 'replace', 'append')
            chunksize: Number of rows to insert at a time

        Raises:
            ValueError: If df is empty or invalid
            SQLAlchemyError: If insertion fails

        Example:
            >>> df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
            >>> db.insert_dataframe(df, "my_table", if_exists="append")
        """
        if df.empty:
            logger.warning("DataFrame is empty, nothing to insert")
            return

        try:
            df.to_sql(
                name=table_name,
                con=self.engine,
                schema=schema,
                if_exists=if_exists,
                index=False,
                chunksize=chunksize,
                method="multi"  # Use multi-row INSERT for performance
            )

            logger.info(f"Inserted {len(df)} rows into {table_name}")

        except SQLAlchemyError as e:
            logger.error(f"Failed to insert DataFrame: {str(e)}")
            raise

    def get_table_info(self, table_name: str, schema: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive information about a table.

        Args:
            table_name: Name of the table
            schema: Schema name (optional)

        Returns:
            Dictionary containing table metadata

        Example:
            >>> info = db.get_table_info("fact_sales")
            >>> print(f"Row count: {info['row_count']}")
        """
        try:
            # Get column info
            columns = self.get_table_columns(table_name, schema)

            # Get row count
            full_table_name = f"{schema}.{table_name}" if schema else table_name
            count_query = f"SELECT COUNT(*) as count FROM {full_table_name}"
            count_df = self.query_to_dataframe(count_query)
            row_count = count_df["count"].iloc[0] if not count_df.empty else 0

            return {
                "table_name": table_name,
                "schema": schema,
                "columns": columns,
                "column_count": len(columns),
                "row_count": row_count
            }

        except Exception as e:
            logger.error(f"Failed to get table info: {str(e)}")
            return {}

    def close(self) -> None:
        """
        Close database connection and dispose of the engine.

        Call this when you're done with the connector to free up resources.

        Example:
            >>> db = DatabaseConnector()
            >>> # ... use db ...
            >>> db.close()
        """
        if self.engine:
            self.engine.dispose()
            logger.info("Database connection closed")

    def __enter__(self):
        """Enable usage as context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically close connection when exiting context."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the connector."""
        return f"DatabaseConnector(engine={self.engine.url if self.engine else 'None'})"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_default_connector() -> DatabaseConnector:
    """
    Get a database connector with default settings.

    Returns:
        DatabaseConnector instance

    Example:
        >>> db = get_default_connector()
        >>> df = db.load_table("fact_sales", limit=1000)
    """
    return DatabaseConnector()


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "DatabaseConnector",
    "get_default_connector",
]
