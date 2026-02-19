"""
TimesFM Tutorial - Part 2: DataFrame-Based Forecasting
======================================================

This script shows how to use TimesFM with pandas DataFrames, which is the
standard format for real-world time series data. Covers single-series and
multi-series forecasting using forecast_on_df().

The DataFrame API expects a specific format:
  - unique_id: identifier for each time series
  - ds: datetime column
  - <value_column>: numeric values to forecast

Requirements:
    pip install timesfm[torch] numpy pandas matplotlib

Reference:
    https://github.com/google-research/timesfm
"""

import numpy as np
import pandas as pd
import torch
import timesfm
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def setup_model():
    """Load and compile TimesFM 2.5."""
    torch.set_float32_matmul_precision("high")
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        "google/timesfm-2.5-200m-pytorch"
    )
    model.compile(
        timesfm.ForecastConfig(
            max_context=1024,
            max_horizon=256,
            normalize_inputs=True,
            use_continuous_quantile_head=True,
            force_flip_invariance=True,
            infer_is_positive=False,
            fix_quantile_crossing=True,
        )
    )
    return model


def generate_retail_data():
    """Generate synthetic retail sales data for multiple stores."""
    np.random.seed(42)
    dates = pd.date_range(start="2022-01-01", end="2024-12-31", freq="D")

    records = []
    stores = {
        "store_A": {"base": 200, "trend": 0.15, "seasonal_amp": 80},
        "store_B": {"base": 500, "trend": 0.30, "seasonal_amp": 150},
        "store_C": {"base": 100, "trend": -0.05, "seasonal_amp": 40},
    }

    for store_id, params in stores.items():
        for i, date in enumerate(dates):
            # Yearly seasonality
            yearly = params["seasonal_amp"] * np.sin(2 * np.pi * i / 365.25)
            # Weekly pattern (lower on weekends)
            weekly = -20 if date.weekday() >= 5 else 10
            # Trend
            trend = params["trend"] * i
            # Noise
            noise = np.random.normal(0, 15)
            # Holiday boost
            holiday = 100 if (date.month == 12 and date.day >= 20) else 0

            value = max(0, params["base"] + yearly + weekly + trend + noise + holiday)
            records.append({
                "unique_id": store_id,
                "ds": date,
                "sales": round(value, 2),
            })

    return pd.DataFrame(records)


def example_1_single_series():
    """Forecast a single time series from a DataFrame."""
    print("=" * 60)
    print("Example 1: Single Series DataFrame Forecast")
    print("=" * 60)

    model = setup_model()

    # Generate data and pick one store
    df = generate_retail_data()
    single_store = df[df["unique_id"] == "store_A"].copy()
    print(f"Data shape: {single_store.shape}")
    print(f"Date range: {single_store['ds'].min()} to {single_store['ds'].max()}")
    print(single_store.head())

    # forecast_on_df expects: unique_id, ds, <value_col>
    # freq: pandas frequency string — "D" for daily, "M" for monthly, etc.
    forecast_df = model.forecast_on_df(
        inputs=single_store,
        freq="D",
        value_name="sales",
        num_jobs=1,
    )

    print(f"\nForecast shape: {forecast_df.shape}")
    print(forecast_df.head(10))

    # Visualize: last 90 days of history + forecast
    fig, ax = plt.subplots(figsize=(14, 5))
    recent = single_store.tail(90)
    ax.plot(recent["ds"], recent["sales"], label="Historical Sales", color="steelblue")
    ax.plot(
        forecast_df["ds"],
        forecast_df["sales"],
        label="Forecast",
        color="coral",
        linewidth=2,
    )
    ax.axvline(x=single_store["ds"].max(), color="gray", linestyle="--", alpha=0.5)
    ax.set_title("Store A — Daily Sales Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Sales ($)")
    ax.legend()
    plt.tight_layout()
    plt.savefig("02_single_series_forecast.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 02_single_series_forecast.png")


def example_2_multi_series():
    """Forecast multiple time series in a single call."""
    print("\n" + "=" * 60)
    print("Example 2: Multi-Series DataFrame Forecast")
    print("=" * 60)

    model = setup_model()
    df = generate_retail_data()

    print(f"Total records: {len(df)}")
    print(f"Unique stores: {df['unique_id'].nunique()}")
    print(f"Records per store:\n{df['unique_id'].value_counts()}")

    # Forecast all stores at once — TimesFM batches internally
    forecast_df = model.forecast_on_df(
        inputs=df,
        freq="D",
        value_name="sales",
        num_jobs=1,
    )

    print(f"\nForecast shape: {forecast_df.shape}")
    print(f"Stores in forecast: {forecast_df['unique_id'].unique()}")

    # Visualize each store
    stores = df["unique_id"].unique()
    fig, axes = plt.subplots(len(stores), 1, figsize=(14, 4 * len(stores)), sharex=False)

    for ax, store in zip(axes, stores):
        hist = df[df["unique_id"] == store].tail(120)
        fc = forecast_df[forecast_df["unique_id"] == store]

        ax.plot(hist["ds"], hist["sales"], label="Historical", color="steelblue")
        ax.plot(fc["ds"], fc["sales"], label="Forecast", color="coral", linewidth=2)
        ax.axvline(
            x=df[df["unique_id"] == store]["ds"].max(),
            color="gray",
            linestyle="--",
            alpha=0.5,
        )
        ax.set_title(f"{store} — Daily Sales Forecast")
        ax.set_ylabel("Sales ($)")
        ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig("02_multi_series_forecast.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 02_multi_series_forecast.png")


def example_3_monthly_aggregation():
    """Aggregate daily data to monthly and forecast."""
    print("\n" + "=" * 60)
    print("Example 3: Monthly Aggregation + Forecast")
    print("=" * 60)

    model = setup_model()
    df = generate_retail_data()

    # Aggregate to monthly for store_B
    store_b = df[df["unique_id"] == "store_B"].copy()
    store_b["month"] = store_b["ds"].dt.to_period("M")
    monthly = store_b.groupby("month").agg({"sales": "sum"}).reset_index()
    monthly["ds"] = monthly["month"].dt.to_timestamp()
    monthly["unique_id"] = "store_B"
    monthly = monthly[["unique_id", "ds", "sales"]]

    print(f"Monthly data shape: {monthly.shape}")
    print(monthly.tail())

    # Use "MS" (month start) or "M" for monthly frequency
    forecast_df = model.forecast_on_df(
        inputs=monthly,
        freq="MS",
        value_name="sales",
        num_jobs=1,
    )

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(monthly["ds"], monthly["sales"], marker="o", label="Historical Monthly Sales", color="steelblue")
    ax.plot(
        forecast_df["ds"],
        forecast_df["sales"],
        marker="s",
        label="Monthly Forecast",
        color="coral",
        linewidth=2,
    )
    ax.axvline(x=monthly["ds"].max(), color="gray", linestyle="--", alpha=0.5)
    ax.set_title("Store B — Monthly Aggregated Sales Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Total Monthly Sales ($)")
    ax.legend()
    plt.tight_layout()
    plt.savefig("02_monthly_forecast.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 02_monthly_forecast.png")


if __name__ == "__main__":
    example_1_single_series()
    example_2_multi_series()
    example_3_monthly_aggregation()
    print("\nAll DataFrame examples completed.")
