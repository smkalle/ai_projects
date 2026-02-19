"""
TimesFM Tutorial - Part 3: Quantile Forecasting & Uncertainty Estimation
=========================================================================

Quantile forecasting goes beyond point predictions by providing a distribution
of possible outcomes. TimesFM 2.5 includes a 30M-parameter continuous quantile
head that produces calibrated uncertainty intervals up to 1000-step horizons.

This is critical for:
  - Risk management (worst-case planning)
  - Inventory optimization (safety stock calculations)
  - Capacity planning (peak load estimation)
  - Financial forecasting (VaR computation)

Requirements:
    pip install timesfm[torch] numpy pandas matplotlib seaborn

Reference:
    https://github.com/google-research/timesfm
"""

import numpy as np
import torch
import timesfm
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def setup_model(use_quantile=True, positive_only=False):
    """Load TimesFM with configurable quantile head."""
    torch.set_float32_matmul_precision("high")
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        "google/timesfm-2.5-200m-pytorch"
    )
    model.compile(
        timesfm.ForecastConfig(
            max_context=1024,
            max_horizon=256,
            normalize_inputs=True,
            use_continuous_quantile_head=use_quantile,
            force_flip_invariance=True,
            infer_is_positive=positive_only,
            fix_quantile_crossing=True,
        )
    )
    return model


def example_1_understanding_quantiles():
    """Understand the quantile forecast output structure."""
    print("=" * 60)
    print("Example 1: Understanding Quantile Forecast Output")
    print("=" * 60)

    model = setup_model()

    # Simple sine wave
    signal = np.sin(np.linspace(0, 8 * np.pi, 400))
    horizon = 64

    point_fc, quantile_fc = model.forecast(horizon=horizon, inputs=[signal])

    print(f"Point forecast shape:    {point_fc.shape}")      # (1, 64)
    print(f"Quantile forecast shape: {quantile_fc.shape}")    # (1, 64, 10)
    print()
    print("Quantile channels (10 values per timestep):")
    print("  Index 0: Mean forecast")
    print("  Index 1: 10th percentile (P10)")
    print("  Index 2: 20th percentile (P20)")
    print("  Index 3: 30th percentile (P30)")
    print("  Index 4: 40th percentile (P40)")
    print("  Index 5: 50th percentile (P50 / Median)")
    print("  Index 6: 60th percentile (P60)")
    print("  Index 7: 70th percentile (P70)")
    print("  Index 8: 80th percentile (P80)")
    print("  Index 9: 90th percentile (P90)")
    print()
    print(f"Sample timestep 0 quantiles: {quantile_fc[0, 0, :]}")

    # Visualize the full quantile fan
    fig, ax = plt.subplots(figsize=(14, 6))
    n = len(signal)
    ax.plot(range(n), signal, label="Historical", color="steelblue")

    forecast_x = range(n, n + horizon)
    ax.plot(forecast_x, point_fc[0], label="Point Forecast", color="coral", linewidth=2)

    # Plot nested confidence bands
    quantile_labels = [
        ("P10-P90", 1, 9, 0.15),
        ("P20-P80", 2, 8, 0.20),
        ("P30-P70", 3, 7, 0.25),
        ("P40-P60", 4, 6, 0.30),
    ]

    colors = plt.cm.Oranges(np.linspace(0.2, 0.6, len(quantile_labels)))

    for (label, lo_idx, hi_idx, alpha), color in zip(quantile_labels, colors):
        ax.fill_between(
            forecast_x,
            quantile_fc[0, :, lo_idx],
            quantile_fc[0, :, hi_idx],
            alpha=alpha,
            color=color,
            label=label,
        )

    ax.axvline(x=n, color="gray", linestyle="--", alpha=0.5)
    ax.set_title("Quantile Fan Chart — Full Uncertainty Distribution", fontsize=13)
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Value")
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.savefig("03_quantile_fan_chart.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 03_quantile_fan_chart.png")


def example_2_high_vs_low_uncertainty():
    """Compare uncertainty for predictable vs volatile signals."""
    print("\n" + "=" * 60)
    print("Example 2: Predictable vs Volatile Signal Uncertainty")
    print("=" * 60)

    model = setup_model()
    np.random.seed(42)
    horizon = 64

    # Clean periodic signal — should have tight confidence bands
    clean_signal = 5 * np.sin(np.linspace(0, 10 * np.pi, 500))

    # Noisy volatile signal — should have wide confidence bands
    volatile_signal = (
        5 * np.sin(np.linspace(0, 10 * np.pi, 500))
        + np.random.normal(0, 3, 500)
        + np.cumsum(np.random.normal(0, 0.1, 500))  # random walk component
    )

    signals = [clean_signal, volatile_signal]
    titles = ["Clean Periodic Signal (Low Uncertainty)", "Volatile Noisy Signal (High Uncertainty)"]

    point_fc, quantile_fc = model.forecast(horizon=horizon, inputs=signals)

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))

    for i, (ax, title) in enumerate(zip(axes, titles)):
        n = len(signals[i])
        ax.plot(range(n - 100, n), signals[i][-100:], label="Historical", color="steelblue")

        forecast_x = range(n, n + horizon)
        ax.plot(forecast_x, point_fc[i], label="Forecast", color="coral", linewidth=2)
        ax.fill_between(
            forecast_x,
            quantile_fc[i, :, 1],   # P10
            quantile_fc[i, :, 9],   # P90
            alpha=0.2,
            color="coral",
            label="P10-P90",
        )
        ax.fill_between(
            forecast_x,
            quantile_fc[i, :, 3],   # P30
            quantile_fc[i, :, 7],   # P70
            alpha=0.3,
            color="coral",
            label="P30-P70",
        )

        # Measure uncertainty width
        avg_width = np.mean(quantile_fc[i, :, 9] - quantile_fc[i, :, 1])
        ax.set_title(f"{title}\nAvg P10-P90 Width: {avg_width:.2f}")
        ax.axvline(x=n, color="gray", linestyle="--", alpha=0.5)
        ax.legend(fontsize=8)

    plt.suptitle("Uncertainty Adapts to Signal Characteristics", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("03_uncertainty_comparison.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 03_uncertainty_comparison.png")


def example_3_positive_constraint():
    """Demonstrate infer_is_positive for non-negative time series."""
    print("\n" + "=" * 60)
    print("Example 3: Non-Negative Forecast Constraint")
    print("=" * 60)

    np.random.seed(42)

    # Generate sales-like data (always non-negative)
    t = np.arange(300)
    sales = 50 + 20 * np.sin(2 * np.pi * t / 30) + np.random.normal(0, 5, 300)
    sales = np.maximum(sales, 0)  # ensure non-negative

    horizon = 48

    # Without positive constraint
    model_default = setup_model(positive_only=False)
    point_fc_default, q_fc_default = model_default.forecast(horizon=horizon, inputs=[sales])

    # With positive constraint
    model_positive = setup_model(positive_only=True)
    point_fc_pos, q_fc_pos = model_positive.forecast(horizon=horizon, inputs=[sales])

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    n = len(sales)
    forecast_x = range(n, n + horizon)

    for ax, pf, qf, title in [
        (axes[0], point_fc_default, q_fc_default, "Default (may go negative)"),
        (axes[1], point_fc_pos, q_fc_pos, "infer_is_positive=True"),
    ]:
        ax.plot(range(n - 60, n), sales[-60:], label="Historical", color="steelblue")
        ax.plot(forecast_x, pf[0], label="Forecast", color="coral", linewidth=2)
        ax.fill_between(
            forecast_x, qf[0, :, 1], qf[0, :, 9],
            alpha=0.2, color="coral", label="P10-P90",
        )
        ax.axhline(y=0, color="red", linestyle=":", alpha=0.5, label="Zero line")
        ax.axvline(x=n, color="gray", linestyle="--", alpha=0.5)
        ax.set_title(title)
        ax.legend(fontsize=8)

    plt.suptitle("Non-Negative Constraint for Sales Data", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig("03_positive_constraint.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 03_positive_constraint.png")


def example_4_quantile_based_decisions():
    """Use quantiles for business decision-making (safety stock)."""
    print("\n" + "=" * 60)
    print("Example 4: Quantile-Based Decision Making (Safety Stock)")
    print("=" * 60)

    model = setup_model(positive_only=True)
    np.random.seed(42)

    # Daily demand for a warehouse item
    t = np.arange(365)
    demand = (
        100
        + 30 * np.sin(2 * np.pi * t / 7)       # weekly cycle
        + 20 * np.sin(2 * np.pi * t / 365.25)   # yearly cycle
        + np.random.normal(0, 10, 365)
    )
    demand = np.maximum(demand, 0)

    horizon = 30  # forecast next 30 days

    point_fc, quantile_fc = model.forecast(horizon=horizon, inputs=[demand])

    # Business logic: use P90 for safety stock
    p50_demand = quantile_fc[0, :, 5]   # median forecast
    p90_demand = quantile_fc[0, :, 9]   # 90th percentile (safety stock level)
    p10_demand = quantile_fc[0, :, 1]   # 10th percentile (optimistic)

    total_expected = np.sum(p50_demand)
    total_safety = np.sum(p90_demand)
    safety_buffer = total_safety - total_expected

    print(f"30-day Expected Demand (P50):  {total_expected:.0f} units")
    print(f"30-day Safety Stock (P90):     {total_safety:.0f} units")
    print(f"Safety Buffer:                 {safety_buffer:.0f} units (+{safety_buffer/total_expected*100:.1f}%)")

    fig, ax = plt.subplots(figsize=(14, 6))
    days = range(1, horizon + 1)
    ax.bar(days, p50_demand, color="steelblue", alpha=0.7, label="Expected Demand (P50)")
    ax.bar(days, p90_demand - p50_demand, bottom=p50_demand, color="coral", alpha=0.5, label="Safety Buffer (P50→P90)")
    ax.plot(days, p10_demand, "g--", label="Optimistic (P10)", linewidth=1.5)
    ax.set_xlabel("Day")
    ax.set_ylabel("Units")
    ax.set_title(f"30-Day Demand Forecast with Safety Stock\nTotal Safety Stock: {total_safety:.0f} units (Buffer: +{safety_buffer:.0f})")
    ax.legend()
    plt.tight_layout()
    plt.savefig("03_safety_stock.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 03_safety_stock.png")


if __name__ == "__main__":
    example_1_understanding_quantiles()
    example_2_high_vs_low_uncertainty()
    example_3_positive_constraint()
    example_4_quantile_based_decisions()
    print("\nAll quantile examples completed.")
