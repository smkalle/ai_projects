"""
TimesFM Tutorial - Part 1: Basic Zero-Shot Forecasting
======================================================

This script demonstrates how to use TimesFM 2.5 for zero-shot time series
forecasting using raw numpy arrays. No training data, no fine-tuning — just
load and predict.

TimesFM treats time series patches (groups of contiguous time points) as tokens
in a decoder-only transformer, similar to how LLMs process text tokens. This
lets it generalize across unseen datasets with zero-shot capability.

Requirements:
    pip install timesfm[torch] numpy matplotlib

Reference:
    https://github.com/google-research/timesfm
"""

import numpy as np
import torch
import timesfm
import matplotlib.pyplot as plt


def setup_model():
    """Load TimesFM 2.5 (200M params) and compile with forecast config."""
    # Use high precision matmul for better GPU performance
    torch.set_float32_matmul_precision("high")

    # Load pretrained weights from Hugging Face Hub
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        "google/timesfm-2.5-200m-pytorch"
    )

    # Compile with forecasting configuration
    # max_context: how many historical points the model sees (multiple of 32)
    # max_horizon: how far ahead to forecast (multiple of 128)
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


def example_1_simple_forecast():
    """Forecast simple synthetic signals."""
    print("=" * 60)
    print("Example 1: Forecasting Synthetic Signals")
    print("=" * 60)

    model = setup_model()

    # Create synthetic time series of different lengths
    # TimesFM handles variable-length inputs natively
    series_1 = np.sin(np.linspace(0, 4 * np.pi, 200))  # sine wave
    series_2 = np.linspace(0, 5, 150) + np.random.normal(0, 0.3, 150)  # noisy trend
    series_3 = np.sin(np.linspace(0, 6 * np.pi, 180)) + np.linspace(0, 2, 180)  # trend + seasonal

    horizon = 48  # forecast 48 steps ahead

    # forecast() accepts a list of numpy arrays (variable lengths OK)
    point_forecast, quantile_forecast = model.forecast(
        horizon=horizon,
        inputs=[series_1, series_2, series_3],
    )

    # point_forecast shape: (3, 48) — one row per series
    # quantile_forecast shape: (3, 48, 10) — mean + 10th-90th percentile quantiles
    print(f"Point forecast shape: {point_forecast.shape}")
    print(f"Quantile forecast shape: {quantile_forecast.shape}")

    # Visualize
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    series_list = [series_1, series_2, series_3]
    titles = ["Sine Wave", "Noisy Linear Trend", "Trend + Seasonal"]

    for i, (ax, series, title) in enumerate(zip(axes, series_list, titles)):
        n = len(series)
        # Historical data
        ax.plot(range(n), series, label="Historical", color="steelblue")
        # Point forecast
        forecast_x = range(n, n + horizon)
        ax.plot(forecast_x, point_forecast[i], label="Forecast", color="coral")
        # Uncertainty band (10th to 90th percentile)
        ax.fill_between(
            forecast_x,
            quantile_forecast[i, :, 1],   # 10th percentile
            quantile_forecast[i, :, -1],   # 90th percentile
            alpha=0.2,
            color="coral",
            label="10-90th percentile",
        )
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.axvline(x=n, color="gray", linestyle="--", alpha=0.5)

    plt.suptitle("TimesFM 2.5 Zero-Shot Forecasting", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("01_basic_forecast.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 01_basic_forecast.png")


def example_2_different_horizons():
    """Demonstrate forecasting with different horizon lengths."""
    print("\n" + "=" * 60)
    print("Example 2: Varying Forecast Horizons")
    print("=" * 60)

    model = setup_model()

    # Generate a complex signal: multiple seasonalities
    t = np.linspace(0, 10, 500)
    signal = (
        2.0 * np.sin(2 * np.pi * t / 1.0)   # short cycle
        + 1.0 * np.sin(2 * np.pi * t / 3.5)  # medium cycle
        + 0.5 * t                              # linear trend
        + np.random.normal(0, 0.2, len(t))    # noise
    )

    horizons = [12, 48, 128]
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for ax, h in zip(axes, horizons):
        point_fc, quantile_fc = model.forecast(horizon=h, inputs=[signal])

        n = len(signal)
        ax.plot(range(n), signal, label="Historical", color="steelblue", linewidth=0.8)
        forecast_x = range(n, n + h)
        ax.plot(forecast_x, point_fc[0], label=f"Forecast (h={h})", color="coral")
        ax.fill_between(
            forecast_x,
            quantile_fc[0, :, 1],
            quantile_fc[0, :, -1],
            alpha=0.2,
            color="coral",
        )
        ax.set_title(f"Horizon = {h} steps")
        ax.axvline(x=n, color="gray", linestyle="--", alpha=0.5)
        ax.legend(fontsize=8)

    plt.suptitle("Effect of Forecast Horizon Length", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("01_varying_horizons.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 01_varying_horizons.png")


def example_3_context_length_impact():
    """Show how context length affects forecast quality."""
    print("\n" + "=" * 60)
    print("Example 3: Context Length Impact on Forecast Quality")
    print("=" * 60)

    model = setup_model()

    # Generate full signal
    np.random.seed(42)
    t = np.linspace(0, 20, 1000)
    full_signal = 3.0 * np.sin(2 * np.pi * t / 2.0) + 0.5 * t

    # Use different amounts of context from the same signal
    context_lengths = [64, 256, 512, 1024]
    horizon = 64

    # Ground truth: the actual future values
    ground_truth = full_signal[-horizon:]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    for ax, ctx_len in zip(axes.flat, context_lengths):
        # Take last ctx_len points before the held-out horizon as context
        context = full_signal[-(ctx_len + horizon):-horizon]
        point_fc, quantile_fc = model.forecast(horizon=horizon, inputs=[context])

        n = len(context)
        ax.plot(range(n), context, label="Context", color="steelblue", linewidth=0.8)
        forecast_x = range(n, n + horizon)
        ax.plot(forecast_x, ground_truth, label="Ground Truth", color="green", linewidth=1.5, linestyle="--")
        ax.plot(forecast_x, point_fc[0], label="Forecast", color="coral")
        ax.fill_between(
            forecast_x,
            quantile_fc[0, :, 1],
            quantile_fc[0, :, -1],
            alpha=0.2,
            color="coral",
        )
        ax.set_title(f"Context = {ctx_len} points")
        ax.axvline(x=n, color="gray", linestyle="--", alpha=0.5)
        ax.legend(fontsize=8)

    plt.suptitle(
        "Impact of Context Length on Forecast Accuracy",
        fontsize=14,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig("01_context_length_impact.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 01_context_length_impact.png")


if __name__ == "__main__":
    example_1_simple_forecast()
    example_2_different_horizons()
    example_3_context_length_impact()
    print("\nAll examples completed.")
