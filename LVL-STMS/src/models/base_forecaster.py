"""
LVL-CODES: Base Forecaster Class
================================================================================
This module provides an abstract base class for all forecasting models.
All specific models (SARIMA, Prophet, XGBoost, etc.) inherit from this class
to ensure consistent interface and functionality.

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

from src.utils.logging import get_logger, log_execution_time
from src.utils.helpers import load_config

# Initialize logger
logger = get_logger(__name__)


class BaseForecaster(ABC):
    """
    Abstract base class for all forecasting models.

    All forecasting models must implement:
        - fit(): Train the model on historical data
        - predict(): Generate forecasts
        - evaluate(): Calculate performance metrics

    Attributes:
        model_name: Name of the forecasting model
        model: Trained model instance
        is_fitted: Whether the model has been trained
        config: Model configuration dictionary

    Example:
        >>> class MyForecaster(BaseForecaster):
        >>>     def fit(self, data):
        >>>         # Training logic
        >>>         pass
        >>>
        >>>     def predict(self, horizon):
        >>>         # Prediction logic
        >>>         pass
    """

    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize base forecaster.

        Args:
            model_name: Name of the model (e.g., 'sarima', 'prophet')
            config: Optional configuration dictionary
        """
        self.model_name = model_name
        self.model = None
        self.is_fitted = False
        self.fit_date = None
        self.train_data_shape = None

        # Load configuration
        if config is None:
            all_config = load_config("models")
            self.config = all_config.get(model_name, {})
        else:
            self.config = config

        logger.info(f"Initialized {model_name} forecaster")

    @abstractmethod
    def fit(self, data: pd.DataFrame, target_col: str = "sales", **kwargs) -> 'BaseForecaster':
        """
        Train the forecasting model on historical data.

        This method must be implemented by all subclasses.

        Args:
            data: Historical data DataFrame with date index
            target_col: Name of the target column to forecast
            **kwargs: Additional model-specific parameters

        Returns:
            Self (for method chaining)

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement fit()")

    @abstractmethod
    def predict(
        self,
        horizon: int,
        frequency: str = "D",
        return_conf_int: bool = False
    ) -> Union[pd.Series, Tuple[pd.Series, pd.DataFrame]]:
        """
        Generate forecasts for future periods.

        This method must be implemented by all subclasses.

        Args:
            horizon: Number of periods to forecast
            frequency: Forecast frequency ('D', 'W', 'M', 'Q', 'Y')
            return_conf_int: Whether to return confidence intervals

        Returns:
            Series of forecasts, or tuple of (forecasts, confidence_intervals)

        Raises:
            NotImplementedError: If not implemented by subclass
            ValueError: If model is not fitted
        """
        if not self.is_fitted:
            raise ValueError(f"{self.model_name} model must be fitted before prediction")

        raise NotImplementedError("Subclasses must implement predict()")

    def evaluate(
        self,
        actual: pd.Series,
        predicted: pd.Series
    ) -> Dict[str, float]:
        """
        Evaluate model performance using multiple metrics.

        Args:
            actual: Actual values
            predicted: Predicted values

        Returns:
            Dictionary of performance metrics

        Metrics calculated:
            - RMSE: Root Mean Squared Error
            - MAE: Mean Absolute Error
            - MAPE: Mean Absolute Percentage Error
            - SMAPE: Symmetric MAPE
            - R²: R-squared
            - MSE: Mean Squared Error
        """
        # Ensure same length
        if len(actual) != len(predicted):
            min_len = min(len(actual), len(predicted))
            actual = actual[:min_len]
            predicted = predicted[:min_len]

        # Remove NaN values
        mask = ~(actual.isna() | predicted.isna())
        actual_clean = actual[mask]
        predicted_clean = predicted[mask]

        if len(actual_clean) == 0:
            logger.warning("No valid data points for evaluation")
            return {}

        # Calculate metrics
        errors = actual_clean - predicted_clean
        squared_errors = errors ** 2
        abs_errors = np.abs(errors)

        # RMSE (Root Mean Squared Error)
        rmse = np.sqrt(np.mean(squared_errors))

        # MAE (Mean Absolute Error)
        mae = np.mean(abs_errors)

        # MSE (Mean Squared Error)
        mse = np.mean(squared_errors)

        # MAPE (Mean Absolute Percentage Error)
        # Avoid division by zero
        mape_mask = actual_clean != 0
        if mape_mask.any():
            mape = np.mean(np.abs(errors[mape_mask] / actual_clean[mape_mask])) * 100
        else:
            mape = np.nan

        # SMAPE (Symmetric Mean Absolute Percentage Error)
        denominator = (np.abs(actual_clean) + np.abs(predicted_clean)) / 2
        smape_mask = denominator != 0
        if smape_mask.any():
            smape = np.mean(np.abs(errors[smape_mask] / denominator[smape_mask])) * 100
        else:
            smape = np.nan

        # R² (R-squared)
        ss_res = np.sum(squared_errors)
        ss_tot = np.sum((actual_clean - np.mean(actual_clean)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else np.nan

        metrics = {
            "rmse": rmse,
            "mae": mae,
            "mse": mse,
            "mape": mape,
            "smape": smape,
            "r2": r2,
            "n_samples": len(actual_clean)
        }

        logger.info(f"Evaluation metrics for {self.model_name}: RMSE={rmse:.2f}, MAE={mae:.2f}, R²={r2:.3f}")

        return metrics

    @log_execution_time("cross_validate")
    def cross_validate(
        self,
        data: pd.DataFrame,
        target_col: str = "sales",
        n_splits: int = 5,
        test_size: int = 30
    ) -> Dict[str, List[float]]:
        """
        Perform time series cross-validation.

        Uses expanding window strategy to respect temporal order.

        Args:
            data: Historical data
            target_col: Target column name
            n_splits: Number of CV splits
            test_size: Size of test set in each split

        Returns:
            Dictionary of metric lists for each split

        Example:
            >>> cv_results = model.cross_validate(df, n_splits=5)
            >>> print(f"Average RMSE: {np.mean(cv_results['rmse']):.2f}")
        """
        logger.info(f"Starting {n_splits}-fold time series cross-validation")

        # Initialize results storage
        cv_metrics = {
            "rmse": [],
            "mae": [],
            "mape": [],
            "r2": []
        }

        # Minimum training size
        min_train_size = len(data) - (n_splits * test_size)

        for i in range(n_splits):
            # Calculate split indices
            train_end = min_train_size + (i * test_size)
            test_start = train_end
            test_end = test_start + test_size

            # Split data
            train_data = data.iloc[:train_end]
            test_data = data.iloc[test_start:test_end]

            logger.debug(f"CV Fold {i+1}: Train size={len(train_data)}, Test size={len(test_data)}")

            try:
                # Fit model
                self.fit(train_data, target_col=target_col)

                # Predict
                forecast = self.predict(horizon=len(test_data))

                # Evaluate
                actual = test_data[target_col]
                metrics = self.evaluate(actual, forecast)

                # Store results
                for metric in cv_metrics.keys():
                    if metric in metrics:
                        cv_metrics[metric].append(metrics[metric])

            except Exception as e:
                logger.warning(f"CV Fold {i+1} failed: {str(e)}")
                continue

        # Log average metrics
        for metric, values in cv_metrics.items():
            if values:
                avg = np.mean(values)
                std = np.std(values)
                logger.info(f"CV {metric.upper()}: {avg:.2f} ± {std:.2f}")

        return cv_metrics

    def save_model(self, filepath: Union[str, Path]) -> None:
        """
        Save trained model to disk.

        Args:
            filepath: Path to save the model

        Raises:
            ValueError: If model is not fitted

        Example:
            >>> model.save_model("./models/saved_models/sarima_2026.pkl")
        """
        if not self.is_fitted:
            raise ValueError("Cannot save model that has not been fitted")

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Create model metadata
        metadata = {
            "model_name": self.model_name,
            "fit_date": self.fit_date,
            "train_data_shape": self.train_data_shape,
            "config": self.config
        }

        # Save model and metadata
        save_data = {
            "model": self.model,
            "metadata": metadata
        }

        joblib.dump(save_data, filepath)
        logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath: Union[str, Path]) -> 'BaseForecaster':
        """
        Load trained model from disk.

        Args:
            filepath: Path to the saved model

        Returns:
            Self (for method chaining)

        Raises:
            FileNotFoundError: If file doesn't exist

        Example:
            >>> model = SARIMAForecaster()
            >>> model.load_model("./models/saved_models/sarima_2026.pkl")
        """
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")

        # Load model and metadata
        save_data = joblib.load(filepath)

        self.model = save_data["model"]
        metadata = save_data["metadata"]

        self.fit_date = metadata["fit_date"]
        self.train_data_shape = metadata["train_data_shape"]
        self.is_fitted = True

        logger.info(f"Model loaded from {filepath}")
        return self

    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Get feature importance (if applicable for the model).

        Returns:
            DataFrame with feature importance, or None if not applicable

        Note:
            Only applicable for tree-based models (XGBoost, LightGBM, Random Forest)
        """
        logger.warning(f"Feature importance not available for {self.model_name}")
        return None

    def plot_forecast(
        self,
        historical: pd.Series,
        forecast: pd.Series,
        conf_int: Optional[pd.DataFrame] = None,
        title: Optional[str] = None
    ):
        """
        Plot historical data and forecast (requires matplotlib).

        Args:
            historical: Historical data
            forecast: Forecasted values
            conf_int: Optional confidence intervals
            title: Plot title

        Example:
            >>> model.plot_forecast(train_data["sales"], forecast, title="2026 Forecast")
        """
        try:
            import matplotlib.pyplot as plt

            plt.figure(figsize=(14, 6))

            # Plot historical
            plt.plot(historical.index, historical.values, label="Historical", color="black")

            # Plot forecast
            plt.plot(forecast.index, forecast.values, label="Forecast", color="blue", linestyle="--")

            # Plot confidence intervals if provided
            if conf_int is not None:
                plt.fill_between(
                    forecast.index,
                    conf_int.iloc[:, 0],
                    conf_int.iloc[:, 1],
                    alpha=0.2,
                    color="blue",
                    label="95% CI"
                )

            plt.xlabel("Date")
            plt.ylabel("Sales")
            plt.title(title or f"{self.model_name.upper()} Forecast")
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()

        except ImportError:
            logger.warning("matplotlib not installed, cannot plot")

    def __repr__(self) -> str:
        """String representation of the forecaster."""
        fitted_status = "fitted" if self.is_fitted else "not fitted"
        return f"{self.model_name.upper()}Forecaster({fitted_status})"


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["BaseForecaster"]
