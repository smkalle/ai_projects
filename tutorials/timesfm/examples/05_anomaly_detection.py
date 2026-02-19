"""
TimesFM Tutorial - Part 5: Anomaly Detection Pipeline
=====================================================

TimesFM can be used for anomaly detection by comparing actual observations
against model predictions and their uncertainty intervals. Points that fall
far outside predicted confidence bands are flagged as anomalies.

This approach leverages TimesFM's zero-shot forecasting — no need to train
an anomaly detector. The model's quantile predictions provide natural
thresholds.

Detection strategy:
  1. Use a rolling window: feed historical context, forecast 1+ steps ahead
  2. Compare actual values against predicted quantile bands
  3. Flag points outside the P10-P90 (or custom) bands as anomalies
  4. Compute anomaly scores based on deviation magnitude

Requirements:
    pip install timesfm[torch] numpy pandas matplotlib seaborn

Reference:
    https://github.com/google-research/timesfm
    https://docs.cloud.google.com/bigquery/docs/timesfm-anomaly-detection-tutorial
"""

import numpy as np
import pandas as pd
import torch
import timesfm
import matplotlib.pyplot as plt


def setup_model():
    """Load TimesFM for anomaly detection."""
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
            infer_is_positive=False,
            fix_quantile_crossing=True,
        )
    )
    return model


def generate_anomalous_data():
    """Generate sensor data with injected anomalies."""
    np.random.seed(42)
    n = 1000

    # Normal pattern: daily cycle + weekly cycle + noise
    t = np.arange(n)
    daily = 10 * np.sin(2 * np.pi * t / 24)
    weekly = 5 * np.sin(2 * np.pi * t / 168)
    trend = 0.01 * t
    noise = np.random.normal(0, 1.5, n)

    signal = 50 + daily + weekly + trend + noise

    # Inject anomalies at known positions
    anomaly_indices = []

    # Point anomaly: sudden spike
    for idx in [200, 201]:
        signal[idx] += 40
        anomaly_indices.append(idx)

    # Point anomaly: sudden drop
    for idx in [450, 451]:
        signal[idx] -= 35
        anomaly_indices.append(idx)

    # Contextual anomaly: unusual pattern for 5 timesteps
    for idx in range(600, 610):
        signal[idx] = 90 + np.random.normal(0, 2)
        anomaly_indices.append(idx)

    # Gradual drift anomaly
    for idx in range(800, 820):
        signal[idx] += 3 * (idx - 800)
        anomaly_indices.append(idx)

    return signal, sorted(set(anomaly_indices))


def example_1_sliding_window_detection():
    """Detect anomalies using a sliding window approach."""
    print("=" * 60)
    print("Example 1: Sliding Window Anomaly Detection")
    print("=" * 60)

    model = setup_model()
    signal, true_anomalies = generate_anomalous_data()

    context_size = 256  # how much history to feed the model
    forecast_step = 1   # detect 1-step-ahead anomalies
    p_low_idx = 1       # P10 quantile index
    p_high_idx = 9      # P90 quantile index

    anomaly_scores = np.zeros(len(signal))
    predicted_low = np.full(len(signal), np.nan)
    predicted_high = np.full(len(signal), np.nan)
    predicted_mean = np.full(len(signal), np.nan)

    # Batch the windows for efficiency
    batch_size = 32
    start_indices = list(range(context_size, len(signal) - forecast_step + 1))
    n_windows = len(start_indices)

    print(f"Total data points: {len(signal)}")
    print(f"Windows to evaluate: {n_windows}")
    print(f"Processing in batches of {batch_size}...")

    for batch_start in range(0, n_windows, batch_size):
        batch_end = min(batch_start + batch_size, n_windows)
        batch_indices = start_indices[batch_start:batch_end]

        # Prepare batch of context windows
        contexts = [signal[idx - context_size:idx] for idx in batch_indices]

        # Forecast one step ahead for all windows in batch
        point_fc, quantile_fc = model.forecast(
            horizon=forecast_step,
            inputs=contexts,
        )

        # Score each point
        for j, idx in enumerate(batch_indices):
            actual = signal[idx]
            pred = point_fc[j, 0]
            low = quantile_fc[j, 0, p_low_idx]
            high = quantile_fc[j, 0, p_high_idx]

            predicted_mean[idx] = pred
            predicted_low[idx] = low
            predicted_high[idx] = high

            # Anomaly score: how far outside the band
            if actual > high:
                anomaly_scores[idx] = (actual - high) / (high - low + 1e-8)
            elif actual < low:
                anomaly_scores[idx] = (low - actual) / (high - low + 1e-8)

        if (batch_start // batch_size) % 5 == 0:
            print(f"  Processed {batch_end}/{n_windows} windows")

    # Flag anomalies: score > threshold
    threshold = 1.0  # points more than 1x band-width outside
    detected = np.where(anomaly_scores > threshold)[0]

    # Evaluate detection
    true_set = set(true_anomalies)
    detected_set = set(detected)
    true_positives = true_set & detected_set
    precision = len(true_positives) / max(len(detected_set), 1)
    recall = len(true_positives) / max(len(true_set), 1)

    print(f"\nResults:")
    print(f"  True anomalies:     {len(true_set)}")
    print(f"  Detected anomalies: {len(detected_set)}")
    print(f"  True positives:     {len(true_positives)}")
    print(f"  Precision:          {precision:.2f}")
    print(f"  Recall:             {recall:.2f}")

    # Visualize
    fig, axes = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={"height_ratios": [3, 1]})

    # Top plot: signal with bands
    ax = axes[0]
    ax.plot(signal, label="Actual", color="steelblue", linewidth=0.8)
    valid = ~np.isnan(predicted_mean)
    ax.plot(np.where(valid)[0], predicted_mean[valid], label="Predicted", color="gray", alpha=0.5, linewidth=0.5)
    ax.fill_between(
        range(len(signal)), predicted_low, predicted_high,
        alpha=0.15, color="gray", label="P10-P90 Band",
    )
    # Mark true anomalies
    ax.scatter(true_anomalies, signal[true_anomalies], color="red", s=40, zorder=5, label="True Anomalies", marker="x")
    # Mark detected anomalies
    ax.scatter(detected, signal[detected], facecolors="none", edgecolors="orange", s=80, zorder=4, label="Detected", linewidth=1.5)
    ax.set_title("TimesFM Anomaly Detection — Sliding Window")
    ax.set_ylabel("Sensor Value")
    ax.legend(loc="upper left", fontsize=9)

    # Bottom plot: anomaly scores
    ax2 = axes[1]
    ax2.bar(range(len(anomaly_scores)), anomaly_scores, color="coral", alpha=0.7, width=1.0)
    ax2.axhline(y=threshold, color="red", linestyle="--", label=f"Threshold={threshold}")
    ax2.set_xlabel("Time Step")
    ax2.set_ylabel("Anomaly Score")
    ax2.legend()

    plt.tight_layout()
    plt.savefig("05_anomaly_detection.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 05_anomaly_detection.png")


def example_2_iqr_based_detection():
    """
    IQR-based anomaly detection using TimesFM quantiles.
    This mirrors the Google Dataflow pipeline approach.
    """
    print("\n" + "=" * 60)
    print("Example 2: IQR-Based Anomaly Detection")
    print("=" * 60)

    model = setup_model()
    signal, true_anomalies = generate_anomalous_data()

    # Split: use first 800 as context, detect anomalies in last 200
    context = signal[:800]
    eval_window = signal[800:]
    horizon = len(eval_window)

    point_fc, quantile_fc = model.forecast(horizon=horizon, inputs=[context])

    # IQR method: use P25 and P75 to compute IQR, then flag outliers
    # Since we have P10-P90 in steps of 10, approximate:
    # P25 ≈ average of P20 (idx 2) and P30 (idx 3)
    # P75 ≈ average of P70 (idx 7) and P80 (idx 8)
    q25 = (quantile_fc[0, :, 2] + quantile_fc[0, :, 3]) / 2
    q75 = (quantile_fc[0, :, 7] + quantile_fc[0, :, 8]) / 2
    iqr = q75 - q25

    # Classic IQR rule: anomaly if value < Q1 - 1.5*IQR or > Q3 + 1.5*IQR
    multiplier = 1.5
    lower_bound = q25 - multiplier * iqr
    upper_bound = q75 + multiplier * iqr

    # Score anomalies
    is_anomaly = (eval_window < lower_bound) | (eval_window > upper_bound)
    anomaly_indices = np.where(is_anomaly)[0] + 800  # offset back to full signal

    print(f"Evaluation window: indices 800-{len(signal)}")
    print(f"Anomalies detected: {np.sum(is_anomaly)}")
    print(f"Anomaly indices (original): {anomaly_indices.tolist()}")

    # Visualize
    fig, ax = plt.subplots(figsize=(14, 6))
    eval_x = range(800, 800 + horizon)

    ax.plot(range(700, 800), signal[700:800], label="Context (last 100)", color="steelblue")
    ax.plot(eval_x, eval_window, label="Actual", color="steelblue", linewidth=1.5)
    ax.plot(eval_x, point_fc[0], label="Forecast", color="coral", linewidth=1.5)
    ax.fill_between(eval_x, lower_bound, upper_bound, alpha=0.2, color="green", label=f"IQR Bounds (×{multiplier})")
    ax.scatter(
        anomaly_indices, signal[anomaly_indices],
        color="red", s=60, zorder=5, marker="x", linewidth=2,
        label=f"Anomalies ({np.sum(is_anomaly)})",
    )
    ax.axvline(x=800, color="gray", linestyle="--", alpha=0.5)
    ax.set_title("IQR-Based Anomaly Detection with TimesFM Quantiles")
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Value")
    ax.legend()
    plt.tight_layout()
    plt.savefig("05_iqr_anomaly_detection.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 05_iqr_anomaly_detection.png")


def example_3_multi_series_monitoring():
    """Monitor multiple sensors for anomalies simultaneously."""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Series Anomaly Monitoring Dashboard")
    print("=" * 60)

    model = setup_model()
    np.random.seed(42)

    n = 500
    context_len = 400
    horizon = 100

    # Generate 4 sensor series
    t = np.arange(n)
    sensors = {
        "CPU_Temp": 60 + 10 * np.sin(2 * np.pi * t / 24) + np.random.normal(0, 2, n),
        "Memory_MB": 4000 + 500 * np.sin(2 * np.pi * t / 168) + np.random.normal(0, 50, n),
        "Disk_IO": 100 + 30 * np.sin(2 * np.pi * t / 12) + np.random.normal(0, 5, n),
        "Network_Mbps": 50 + 20 * np.sin(2 * np.pi * t / 48) + np.random.normal(0, 3, n),
    }

    # Inject anomalies in specific sensors
    sensors["CPU_Temp"][420:430] += 30      # CPU overheating
    sensors["Memory_MB"][450:460] += 2000   # memory leak
    sensors["Disk_IO"][470:475] *= 5        # disk IO spike

    contexts = [s[:context_len] for s in sensors.values()]
    eval_data = [s[context_len:] for s in sensors.values()]

    # Forecast all sensors in one batch
    point_fc, quantile_fc = model.forecast(horizon=horizon, inputs=contexts)

    # Detect anomalies per sensor
    fig, axes = plt.subplots(4, 1, figsize=(16, 14))
    sensor_names = list(sensors.keys())

    for i, (ax, name) in enumerate(zip(axes, sensor_names)):
        actual = eval_data[i]
        p10 = quantile_fc[i, :, 1]
        p90 = quantile_fc[i, :, 9]

        # Flag anomalies
        is_anomaly = (actual < p10) | (actual > p90)
        anomaly_idx = np.where(is_anomaly)[0]

        eval_x = range(context_len, context_len + horizon)
        ax.plot(range(context_len - 50, context_len), sensors[name][context_len - 50:context_len],
                color="steelblue", linewidth=0.8)
        ax.plot(eval_x, actual, color="steelblue", linewidth=1, label="Actual")
        ax.plot(eval_x, point_fc[i], color="coral", linewidth=1, alpha=0.7, label="Forecast")
        ax.fill_between(eval_x, p10, p90, alpha=0.15, color="coral")
        if len(anomaly_idx) > 0:
            ax.scatter(
                anomaly_idx + context_len, actual[anomaly_idx],
                color="red", s=30, zorder=5, marker="x",
                label=f"Anomalies ({len(anomaly_idx)})",
            )
        ax.axvline(x=context_len, color="gray", linestyle="--", alpha=0.5)
        ax.set_ylabel(name)
        ax.legend(loc="upper right", fontsize=8)

    axes[0].set_title("Multi-Sensor Anomaly Monitoring Dashboard", fontsize=13, fontweight="bold")
    axes[-1].set_xlabel("Time Step")
    plt.tight_layout()
    plt.savefig("05_multi_sensor_monitoring.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 05_multi_sensor_monitoring.png")


if __name__ == "__main__":
    example_1_sliding_window_detection()
    example_2_iqr_based_detection()
    example_3_multi_series_monitoring()
    print("\nAll anomaly detection examples completed.")
