"""
TimesFM Tutorial - Part 4: External Covariates (XReg)
=====================================================

TimesFM 2.5 restores support for external regressors (covariates) via XReg.
Covariates are additional features beyond the target time series that can
improve forecast accuracy — things like temperature, promotions, holidays,
day-of-week, and other external factors.

Two XReg modes:
  1. "xreg + timesfm" (default): Fit a linear model on covariates first, then
     use TimesFM to forecast the residuals. Best when covariates explain most
     of the variance.
  2. "timesfm + xreg": Use TimesFM first, then fit a linear model on the
     residuals. Best when the time series pattern dominates.

Covariate types:
  - Static Numerical:     one number per series  (e.g., store area in sq ft)
  - Static Categorical:   one category per series (e.g., store type)
  - Dynamic Numerical:    one number per timestep (e.g., temperature)
  - Dynamic Categorical:  one category per timestep (e.g., is_holiday)

IMPORTANT: Dynamic covariates must include values for BOTH the context window
AND the forecast horizon.

Requirements:
    pip install timesfm[torch] timesfm[xreg] numpy pandas matplotlib
    # XReg requires JAX: pip install jax jaxlib

Reference:
    https://github.com/google-research/timesfm
"""

import numpy as np
import torch
import timesfm
import matplotlib.pyplot as plt


def setup_model():
    """Load and compile TimesFM 2.5 with XReg support."""
    torch.set_float32_matmul_precision("high")
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        "google/timesfm-2.5-200m-pytorch"
    )
    model.compile(
        timesfm.ForecastConfig(
            max_context=512,
            max_horizon=256,
            normalize_inputs=True,
            use_continuous_quantile_head=True,
            force_flip_invariance=True,
            infer_is_positive=True,
            fix_quantile_crossing=True,
        )
    )
    return model


def generate_covariate_data(n_context=365, n_horizon=30):
    """
    Generate synthetic retail data where sales are driven by:
    - Temperature (dynamic numerical)
    - Day of week (dynamic categorical)
    - Is promotion day (dynamic categorical)
    - Store size in sq ft (static numerical)
    - Store type (static categorical)
    """
    np.random.seed(42)
    n_total = n_context + n_horizon

    # --- Dynamic Covariates (need context + horizon values) ---
    # Temperature: seasonal pattern
    days = np.arange(n_total)
    temperature = 20 + 15 * np.sin(2 * np.pi * days / 365) + np.random.normal(0, 2, n_total)

    # Day of week: 0=Mon, 6=Sun
    day_of_week = days % 7

    # Promotion indicator: random promotions ~15% of days
    is_promotion = (np.random.random(n_total) < 0.15).astype(int)

    # --- Static Covariates (one value per series) ---
    store_size = 2500.0   # sq ft
    store_type = "urban"

    # --- Generate target series driven by covariates ---
    base_sales = 200
    temp_effect = 2.0 * (temperature - 20)           # higher temp → more sales
    weekday_effect = np.where(day_of_week >= 5, 50, 0)  # weekend boost
    promo_effect = 80 * is_promotion                    # promotion boost
    noise = np.random.normal(0, 15, n_total)

    sales = base_sales + temp_effect + weekday_effect + promo_effect + noise
    sales = np.maximum(sales, 0)

    return {
        "sales_context": sales[:n_context],
        "sales_full": sales,
        "temperature": temperature,
        "day_of_week": day_of_week,
        "is_promotion": is_promotion,
        "store_size": store_size,
        "store_type": store_type,
        "n_context": n_context,
        "n_horizon": n_horizon,
    }


def example_1_dynamic_covariates():
    """Forecast with dynamic numerical and categorical covariates."""
    print("=" * 60)
    print("Example 1: Forecasting with Dynamic Covariates")
    print("=" * 60)

    model = setup_model()
    data = generate_covariate_data()

    horizon = data["n_horizon"]
    context = data["sales_context"]

    print(f"Context length: {len(context)}")
    print(f"Horizon: {horizon}")
    print(f"Temperature values (context+horizon): {len(data['temperature'])}")

    try:
        # forecast_with_covariates returns (combined_forecast, xreg_only_forecast)
        cov_forecast, xreg_forecast = model.forecast_with_covariates(
            horizon=horizon,
            inputs=[context],
            dynamic_numerical_covariates={
                "temperature": [data["temperature"].tolist()],
            },
            dynamic_categorical_covariates={
                "day_of_week": [data["day_of_week"].tolist()],
                "is_promotion": [data["is_promotion"].tolist()],
            },
        )

        # Also get baseline forecast without covariates
        baseline_fc, _ = model.forecast(horizon=horizon, inputs=[context])

        # Ground truth (held-out horizon)
        ground_truth = data["sales_full"][data["n_context"]:]

        # Compare
        mae_baseline = np.mean(np.abs(baseline_fc[0] - ground_truth))
        mae_covariates = np.mean(np.abs(cov_forecast[0] - ground_truth))

        print(f"\nBaseline MAE (no covariates):  {mae_baseline:.2f}")
        print(f"Covariate MAE:                 {mae_covariates:.2f}")
        print(f"Improvement:                   {(mae_baseline - mae_covariates) / mae_baseline * 100:.1f}%")

        # Visualize
        fig, ax = plt.subplots(figsize=(14, 6))
        n = len(context)
        ax.plot(range(n - 60, n), context[-60:], label="Historical", color="steelblue")

        forecast_x = range(n, n + horizon)
        ax.plot(forecast_x, ground_truth, label="Ground Truth", color="green", linestyle="--", linewidth=2)
        ax.plot(forecast_x, baseline_fc[0], label=f"Baseline (MAE={mae_baseline:.1f})", color="gray", alpha=0.7)
        ax.plot(forecast_x, cov_forecast[0], label=f"With Covariates (MAE={mae_covariates:.1f})", color="coral", linewidth=2)
        ax.axvline(x=n, color="gray", linestyle="--", alpha=0.5)
        ax.set_title("Forecast Improvement with External Covariates")
        ax.set_xlabel("Day")
        ax.set_ylabel("Sales ($)")
        ax.legend()
        plt.tight_layout()
        plt.savefig("04_covariate_improvement.png", dpi=150, bbox_inches="tight")
        plt.show()
        print("Plot saved: 04_covariate_improvement.png")

    except Exception as e:
        print(f"\nNote: forecast_with_covariates requires JAX/jaxlib.")
        print(f"Install with: pip install timesfm[xreg]")
        print(f"Error: {e}")
        print("\nFalling back to standard forecast demonstration...")


def example_2_all_covariate_types():
    """Use all four covariate types together."""
    print("\n" + "=" * 60)
    print("Example 2: All Covariate Types Combined")
    print("=" * 60)

    model = setup_model()
    data = generate_covariate_data()

    horizon = data["n_horizon"]
    context = data["sales_context"]

    try:
        cov_forecast, xreg_forecast = model.forecast_with_covariates(
            horizon=horizon,
            inputs=[context],
            # Dynamic: varies per timestep (must include context + horizon)
            dynamic_numerical_covariates={
                "temperature": [data["temperature"].tolist()],
            },
            dynamic_categorical_covariates={
                "day_of_week": [data["day_of_week"].tolist()],
                "is_promotion": [data["is_promotion"].tolist()],
            },
            # Static: one value per series
            static_numerical_covariates={
                "store_size": [data["store_size"]],
            },
            static_categorical_covariates={
                "store_type": [data["store_type"]],
            },
        )

        print("Combined forecast with all covariate types:")
        print(f"  Forecast shape: {cov_forecast.shape}")
        print(f"  XReg-only shape: {xreg_forecast.shape}")
        print(f"  First 5 values: {cov_forecast[0, :5]}")

    except Exception as e:
        print(f"Note: Requires JAX/jaxlib for XReg support.")
        print(f"Install with: pip install timesfm[xreg]")
        print(f"Error: {e}")


def example_3_xreg_modes_comparison():
    """Compare the two XReg combination modes."""
    print("\n" + "=" * 60)
    print('Example 3: "xreg+timesfm" vs "timesfm+xreg" Modes')
    print("=" * 60)

    print("""
    Mode 1: "xreg + timesfm" (default)
    ───────────────────────────────────
    Step 1: Fit linear model on covariates → xreg predictions
    Step 2: Compute residuals: observed - xreg[in-sample]
    Step 3: TimesFM forecasts the residuals
    Step 4: Final = xreg[out-of-sample] + timesfm[residual forecast]

    Best when: Covariates explain most of the variance, TimesFM
    handles the remaining complex patterns.

    Mode 2: "timesfm + xreg"
    ─────────────────────────
    Step 1: TimesFM generates in-sample + out-of-sample predictions
    Step 2: Compute residuals: timesfm[in-sample] - observed
    Step 3: Fit linear model on residuals using covariates
    Step 4: Final = timesfm[out-of-sample] + xreg[residual corrections]

    Best when: Time series patterns dominate, covariates provide
    small corrections to the TimesFM baseline.
    """)

    model = setup_model()
    data = generate_covariate_data()
    horizon = data["n_horizon"]
    context = data["sales_context"]
    ground_truth = data["sales_full"][data["n_context"]:]

    try:
        # Mode 1: xreg + timesfm (default)
        fc_mode1, _ = model.forecast_with_covariates(
            horizon=horizon,
            inputs=[context],
            dynamic_numerical_covariates={
                "temperature": [data["temperature"].tolist()],
            },
            dynamic_categorical_covariates={
                "is_promotion": [data["is_promotion"].tolist()],
            },
            xreg_mode="xreg + timesfm",
        )

        # Mode 2: timesfm + xreg
        fc_mode2, _ = model.forecast_with_covariates(
            horizon=horizon,
            inputs=[context],
            dynamic_numerical_covariates={
                "temperature": [data["temperature"].tolist()],
            },
            dynamic_categorical_covariates={
                "is_promotion": [data["is_promotion"].tolist()],
            },
            xreg_mode="timesfm + xreg",
        )

        mae1 = np.mean(np.abs(fc_mode1[0] - ground_truth))
        mae2 = np.mean(np.abs(fc_mode2[0] - ground_truth))

        print(f'MAE "xreg + timesfm":   {mae1:.2f}')
        print(f'MAE "timesfm + xreg":   {mae2:.2f}')
        print(f'Better mode: {"xreg + timesfm" if mae1 < mae2 else "timesfm + xreg"}')

        fig, ax = plt.subplots(figsize=(14, 6))
        n = len(context)
        forecast_x = range(n, n + horizon)
        ax.plot(forecast_x, ground_truth, label="Ground Truth", color="green", linestyle="--", linewidth=2)
        ax.plot(forecast_x, fc_mode1[0], label=f'"xreg+timesfm" (MAE={mae1:.1f})', color="coral", linewidth=1.5)
        ax.plot(forecast_x, fc_mode2[0], label=f'"timesfm+xreg" (MAE={mae2:.1f})', color="purple", linewidth=1.5)
        ax.set_title('Comparing XReg Modes')
        ax.set_xlabel("Day")
        ax.set_ylabel("Sales ($)")
        ax.legend()
        plt.tight_layout()
        plt.savefig("04_xreg_modes_comparison.png", dpi=150, bbox_inches="tight")
        plt.show()
        print("Plot saved: 04_xreg_modes_comparison.png")

    except Exception as e:
        print(f"Note: Requires JAX/jaxlib. Install with: pip install timesfm[xreg]")
        print(f"Error: {e}")


if __name__ == "__main__":
    example_1_dynamic_covariates()
    example_2_all_covariate_types()
    example_3_xreg_modes_comparison()
    print("\nAll covariate examples completed.")
