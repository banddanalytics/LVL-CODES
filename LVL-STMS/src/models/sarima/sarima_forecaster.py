"""
LVL-CODES: SARIMA Forecasting Model
================================================================================
This module implements Seasonal AutoRegressive Integrated Moving Average (SARIMA)
forecasting for sales prediction.

SARIMA is ideal for time series data with:
    - Trends (increasing/decreasing patterns)
    - Seasonality (recurring patterns - yearly, monthly, weekly)
    - Autocorrelation (past values influence future values)

The model automatically selects optimal parameters using Auto-ARIMA.

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

from typing import Dict, Any, Optional, Tuple, Union
import pandas as pd
import numpy as np
from datetime import datetime

# SARIMA model libraries
from statsmodels.tsa.statespace.sarimax import SARIMAX
import pmdarima as pm
from pmdarima import auto_arima

# Base class
from src.models.base_forecaster import BaseForecaster
from src.utils.logging import get_logger, log_execution_time, log_step
from src.utils.helpers import load_config

# Initialize logger
logger = get_logger(__name__)


class SARIMAForecaster(BaseForecaster):
    """
    SARIMA forecasting model with automatic parameter selection.

    This forecaster uses Auto-ARIMA to automatically determine the best
    (p,d,q)(P,D,Q,m) parameters for the SARIMA model, where:
        - p: AR (autoregressive) order
        - d: I (integrated/differencing) order
        - q: MA (moving average) order
        - P: Seasonal AR order
        - D: Seasonal differencing order
        - Q: Seasonal MA order
        - m: Seasonal period (e.g., 365 for daily data with yearly seasonality)

    Attributes:
        model: Fitted SARIMA model
        model_params: Selected SARIMA parameters
        aic: Akaike Information Criterion (model quality metric)
        bic: Bayesian Information Criterion (model quality metric)

    Example:
        >>> # Create forecaster
        >>> forecaster = SARIMAForecaster()
        >>>
        >>> # Load and prepare data
        >>> df = pd.read_csv("sales_timeseries.csv", parse_dates=["date"])
        >>> df = df.set_index("date")
        >>>
        >>> # Train model
        >>> forecaster.fit(df, target_col="sales")
        >>>
        >>> # Generate 12-month forecast
        >>> forecast = forecaster.predict(horizon=12, frequency="M")
        >>>
        >>> # Save forecast to Excel
        >>> forecast.to_csv("forecast_2026.csv")
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize SARIMA forecaster.

        Args:
            config: Optional configuration dictionary. If None, loads from
                   config/models.yaml file.
        """
        super().__init__(model_name="sarima", config=config)

        # Model-specific attributes
        self.model_params = None
        self.aic = None
        self.bic = None
        self.training_data = None

        logger.info("SARIMA Forecaster initialized")

    @log_step("Fit SARIMA Model")
    @log_execution_time("sarima_fit")
    def fit(
        self,
        data: pd.DataFrame,
        target_col: str = "sales",
        seasonal_period: Optional[int] = None,
        **kwargs
    ) -> 'SARIMAForecaster':
        """
        Train SARIMA model on historical data with automatic parameter selection.

        This method:
        1. Prepares the time series data
        2. Runs Auto-ARIMA to find optimal parameters
        3. Fits the SARIMA model
        4. Stores model for predictions

        Args:
            data: DataFrame with DatetimeIndex and target column
            target_col: Name of column containing values to forecast
            seasonal_period: Seasonal period (m parameter). If None, auto-detected:
                           - Daily data: 365 (yearly seasonality)
                           - Weekly data: 52 (yearly seasonality)
                           - Monthly data: 12 (yearly seasonality)
            **kwargs: Additional arguments passed to auto_arima

        Returns:
            Self (for method chaining)

        Raises:
            ValueError: If data is invalid or insufficient

        Example:
            >>> # Monthly data
            >>> forecaster.fit(monthly_df, target_col="net_sales_amount")
            >>>
            >>> # Daily data with custom seasonal period
            >>> forecaster.fit(daily_df, target_col="sales", seasonal_period=7)
        """
        logger.info(f"Training SARIMA model on {len(data)} observations")

        # ====================================================================
        # 1. VALIDATE AND PREPARE DATA
        # ====================================================================

        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data must have a DatetimeIndex")

        if target_col not in data.columns:
            raise ValueError(f"Target column '{target_col}' not found in data")

        # Extract target series
        y = data[target_col].copy()

        # Remove any NaN values
        if y.isna().any():
            logger.warning(f"Removing {y.isna().sum()} NaN values from data")
            y = y.dropna()

        if len(y) < 24:  # Need at least 2 years of monthly data (or equivalent)
            raise ValueError(
                f"Insufficient data: {len(y)} observations. "
                "SARIMA requires at least 24 observations."
            )

        # Store training data shape
        self.train_data_shape = y.shape
        self.training_data = y.copy()

        # ====================================================================
        # 2. DETERMINE SEASONAL PERIOD
        # ====================================================================

        if seasonal_period is None:
            # Auto-detect based on data frequency
            freq = pd.infer_freq(y.index)

            if freq is None:
                logger.warning("Could not infer frequency, assuming monthly data (m=12)")
                seasonal_period = 12
            elif 'D' in freq:  # Daily
                seasonal_period = 365
                logger.info("Detected daily data, using seasonal period m=365")
            elif 'W' in freq:  # Weekly
                seasonal_period = 52
                logger.info("Detected weekly data, using seasonal period m=52")
            elif 'M' in freq or 'MS' in freq:  # Monthly
                seasonal_period = 12
                logger.info("Detected monthly data, using seasonal period m=12")
            elif 'Q' in freq:  # Quarterly
                seasonal_period = 4
                logger.info("Detected quarterly data, using seasonal period m=4")
            else:
                seasonal_period = 12
                logger.warning(f"Unknown frequency '{freq}', assuming m=12")
        else:
            logger.info(f"Using specified seasonal period m={seasonal_period}")

        # ====================================================================
        # 3. CONFIGURE AUTO-ARIMA
        # ====================================================================

        # Get configuration from config file
        auto_arima_config = self.config.get("auto_arima", {})

        # Merge with kwargs (kwargs take precedence)
        auto_arima_params = {
            # Seasonal settings
            "seasonal": auto_arima_config.get("seasonal", True),
            "m": seasonal_period,

            # Search parameters
            "start_p": auto_arima_config.get("start_p", 0),
            "start_q": auto_arima_config.get("start_q", 0),
            "max_p": auto_arima_config.get("max_p", 5),
            "max_q": auto_arima_config.get("max_q", 5),
            "start_P": auto_arima_config.get("start_P", 0),
            "start_Q": auto_arima_config.get("start_Q", 0),
            "max_P": auto_arima_config.get("max_P", 2),
            "max_Q": auto_arima_config.get("max_Q", 2),
            "max_d": auto_arima_config.get("max_d", 2),
            "max_D": auto_arima_config.get("max_D", 1),

            # Model selection
            "information_criterion": auto_arima_config.get("information_criterion", "aic"),
            "trace": auto_arima_config.get("trace", True),
            "error_action": auto_arima_config.get("error_action", "ignore"),
            "suppress_warnings": auto_arima_config.get("suppress_warnings", True),
            "stepwise": auto_arima_config.get("stepwise", True),

            # Other settings
            "n_jobs": -1,  # Use all CPU cores
            "random_state": 42
        }

        # Override with any kwargs provided
        auto_arima_params.update(kwargs)

        logger.info("Running Auto-ARIMA to find optimal parameters...")
        logger.debug(f"Auto-ARIMA configuration: {auto_arima_params}")

        # ====================================================================
        # 4. FIT AUTO-ARIMA
        # ====================================================================

        try:
            # Run Auto-ARIMA to find best model
            self.model = auto_arima(
                y,
                **auto_arima_params
            )

            # Extract model parameters
            self.model_params = {
                "order": self.model.order,  # (p, d, q)
                "seasonal_order": self.model.seasonal_order,  # (P, D, Q, m)
            }

            # Extract model quality metrics
            self.aic = self.model.aic()
            self.bic = self.model.bic()

            logger.info(f"✓ Best SARIMA model found: "
                       f"SARIMA{self.model_params['order']}"
                       f"x{self.model_params['seasonal_order']}")
            logger.info(f"  AIC: {self.aic:.2f}, BIC: {self.bic:.2f}")

        except Exception as e:
            logger.error(f"Auto-ARIMA fitting failed: {str(e)}")
            raise

        # ====================================================================
        # 5. FINALIZE
        # ====================================================================

        self.is_fitted = True
        self.fit_date = datetime.now()

        logger.info("✓ SARIMA model training complete")

        return self

    @log_execution_time("sarima_predict")
    def predict(
        self,
        horizon: int,
        frequency: str = "D",
        return_conf_int: bool = False,
        alpha: float = 0.05
    ) -> Union[pd.Series, Tuple[pd.Series, pd.DataFrame]]:
        """
        Generate forecasts for future periods.

        Args:
            horizon: Number of periods to forecast
            frequency: Forecast frequency ('D'=daily, 'W'=weekly, 'M'=monthly, etc.)
            return_conf_int: Whether to return confidence intervals
            alpha: Significance level for confidence intervals (default: 0.05 for 95% CI)

        Returns:
            If return_conf_int=False:
                pd.Series with forecasted values
            If return_conf_int=True:
                Tuple of (forecasts, confidence_intervals_dataframe)

        Raises:
            ValueError: If model is not fitted

        Example:
            >>> # Simple forecast
            >>> forecast = forecaster.predict(horizon=12)
            >>> forecast.to_csv("forecast_2026.csv")
            >>>
            >>> # Forecast with confidence intervals
            >>> forecast, conf_int = forecaster.predict(horizon=12, return_conf_int=True)
            >>> # conf_int has columns: 'lower' and 'upper'
        """
        # Validation handled by parent class
        super().predict(horizon, frequency, return_conf_int)

        logger.info(f"Generating {horizon}-period forecast with SARIMA")

        # ====================================================================
        # 1. GENERATE FORECAST
        # ====================================================================

        # Get forecast values and confidence intervals
        forecast_values, conf_int = self.model.predict(
            n_periods=horizon,
            return_conf_int=True,
            alpha=alpha
        )

        # ====================================================================
        # 2. CREATE FUTURE DATES
        # ====================================================================

        # Get last date from training data
        last_date = self.training_data.index[-1]

        # Generate future dates
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=horizon,
            freq=frequency
        )

        # ====================================================================
        # 3. CREATE FORECAST SERIES
        # ====================================================================

        forecast_series = pd.Series(
            forecast_values,
            index=future_dates,
            name="forecast"
        )

        logger.info(f"Forecast generated for {future_dates[0].date()} to {future_dates[-1].date()}")
        logger.info(f"Forecast range: ${forecast_series.min():,.2f} to ${forecast_series.max():,.2f}")
        logger.info(f"Mean forecast: ${forecast_series.mean():,.2f}")

        # ====================================================================
        # 4. RETURN RESULTS
        # ====================================================================

        if return_conf_int:
            # Create confidence interval DataFrame
            conf_int_df = pd.DataFrame(
                conf_int,
                index=future_dates,
                columns=["lower", "upper"]
            )

            logger.debug("Returning forecast with confidence intervals")
            return forecast_series, conf_int_df
        else:
            return forecast_series

    def get_model_summary(self) -> str:
        """
        Get a text summary of the fitted model.

        Returns:
            String with model summary including parameters and diagnostics

        Example:
            >>> print(forecaster.get_model_summary())
        """
        if not self.is_fitted:
            return "Model not fitted yet"

        summary = f"""
SARIMA Model Summary
{'='*60}

Model: SARIMA{self.model_params['order']}x{self.model_params['seasonal_order']}

Parameters:
  Non-seasonal: (p={self.model_params['order'][0]},
                 d={self.model_params['order'][1]},
                 q={self.model_params['order'][2]})
  Seasonal:     (P={self.model_params['seasonal_order'][0]},
                 D={self.model_params['seasonal_order'][1]},
                 Q={self.model_params['seasonal_order'][2]},
                 m={self.model_params['seasonal_order'][3]})

Model Quality:
  AIC: {self.aic:.2f}
  BIC: {self.bic:.2f}

Training Data:
  Observations: {self.train_data_shape[0]}
  Date Range: {self.training_data.index[0].date()} to {self.training_data.index[-1].date()}
  Mean: ${self.training_data.mean():,.2f}
  Std Dev: ${self.training_data.std():,.2f}

Fit Date: {self.fit_date.strftime('%Y-%m-%d %H:%M:%S') if self.fit_date else 'N/A'}
{'='*60}
        """
        return summary

    def __repr__(self) -> str:
        """String representation."""
        if self.is_fitted:
            return (f"SARIMAForecaster("
                   f"order={self.model_params['order']}, "
                   f"seasonal_order={self.model_params['seasonal_order']}, "
                   f"fitted=True)")
        else:
            return "SARIMAForecaster(fitted=False)"


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_forecast(
    data: pd.DataFrame,
    target_col: str = "sales",
    horizon: int = 12,
    **kwargs
) -> pd.Series:
    """
    Quick SARIMA forecast with sensible defaults.

    Args:
        data: DataFrame with DatetimeIndex
        target_col: Column to forecast
        horizon: Forecast horizon
        **kwargs: Additional arguments for fit()

    Returns:
        Forecast series

    Example:
        >>> df = pd.read_csv("sales.csv", parse_dates=["date"], index_col="date")
        >>> forecast = quick_forecast(df, target_col="net_sales_amount", horizon=12)
    """
    forecaster = SARIMAForecaster()
    forecaster.fit(data, target_col=target_col, **kwargs)
    return forecaster.predict(horizon=horizon)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "SARIMAForecaster",
    "quick_forecast",
]
