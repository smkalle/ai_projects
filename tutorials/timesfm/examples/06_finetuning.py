"""
TimesFM Tutorial - Part 6: Fine-Tuning on Custom Data
=====================================================

TimesFM supports fine-tuning to adapt the pretrained model to your specific
domain. This is useful when:
  - Your domain has unique patterns (e.g., financial markets, medical signals)
  - Zero-shot performance needs improvement on your specific data
  - You have sufficient labeled data for your use case

Fine-tuning approaches:
  1. Full model fine-tuning: update all weights (needs GPU + more data)
  2. The official repo provides examples in notebooks/finetuning.ipynb
     and notebooks/finetuning_torch.ipynb
  3. Multi-GPU DDP fine-tuning is supported for larger datasets

This script demonstrates the fine-tuning pattern using PyTorch.

Requirements:
    pip install timesfm[torch] numpy pandas matplotlib torch

Reference:
    https://github.com/google-research/timesfm
    https://github.com/google-research/timesfm/pull/223
"""

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import timesfm
import matplotlib.pyplot as plt


# ==============================================================================
# Step 1: Custom Dataset for Time Series Fine-Tuning
# ==============================================================================

class TimeSeriesSlidingWindowDataset(Dataset):
    """
    Creates sliding window samples from time series data for fine-tuning.

    Each sample consists of:
      - context: historical values the model sees (input)
      - target: future values the model should predict (label)

    The sliding window moves across the series to generate multiple
    training samples from a single time series.
    """

    def __init__(self, series_list, context_length=256, horizon=64, stride=1):
        """
        Args:
            series_list: list of 1D numpy arrays (multiple time series)
            context_length: number of historical points per sample
            horizon: number of future points to predict
            stride: step size for the sliding window
        """
        self.context_length = context_length
        self.horizon = horizon
        self.samples = []

        window = context_length + horizon
        for series in series_list:
            if len(series) < window:
                continue
            for start in range(0, len(series) - window + 1, stride):
                context = series[start:start + context_length]
                target = series[start + context_length:start + window]
                self.samples.append((
                    torch.tensor(context, dtype=torch.float32),
                    torch.tensor(target, dtype=torch.float32),
                ))

        print(f"Created {len(self.samples)} training samples "
              f"(context={context_length}, horizon={horizon}, stride={stride})")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]


# ==============================================================================
# Step 2: Generate Synthetic Domain-Specific Data
# ==============================================================================

def generate_domain_data(n_series=50, length=1000):
    """
    Generate synthetic "domain-specific" data that differs from TimesFM's
    pretraining distribution. This simulates a scenario where fine-tuning
    would help.

    Example: medical heart rate data with specific patterns.
    """
    np.random.seed(42)
    series_list = []

    for i in range(n_series):
        t = np.arange(length)
        # Base heart rate with circadian rhythm
        base = 70 + 10 * np.sin(2 * np.pi * t / 1440)  # 24h cycle in minutes
        # Exercise spikes (random)
        for _ in range(np.random.randint(2, 6)):
            spike_start = np.random.randint(0, length - 60)
            spike_duration = np.random.randint(20, 60)
            spike_height = np.random.uniform(20, 50)
            base[spike_start:spike_start + spike_duration] += spike_height
        # Individual variation
        base += np.random.normal(0, 3, length)
        base = np.clip(base, 40, 180)
        series_list.append(base)

    return series_list


# ==============================================================================
# Step 3: Fine-Tuning Loop
# ==============================================================================

def finetune_timesfm(
    model,
    train_loader,
    val_data,
    num_epochs=10,
    learning_rate=1e-5,
    horizon=64,
    device="cuda" if torch.cuda.is_available() else "cpu",
):
    """
    Fine-tune TimesFM on domain-specific data.

    This demonstrates the core fine-tuning pattern. The official TimesFM repo
    provides a more complete FinetuningConfig + TimesFMFinetuner abstraction.

    Args:
        model: compiled TimesFM model
        train_loader: DataLoader with (context, target) pairs
        val_data: list of numpy arrays for validation
        num_epochs: training epochs
        learning_rate: optimizer learning rate
        horizon: forecast horizon
        device: cuda or cpu
    """
    # Move model to device
    model = model.to(device)
    model.train()

    # Set up optimizer — only update model parameters
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = nn.MSELoss()

    train_losses = []
    val_maes = []

    print(f"\nFine-tuning on {device} for {num_epochs} epochs...")
    print(f"Learning rate: {learning_rate}")
    print(f"Train batches per epoch: {len(train_loader)}")

    for epoch in range(num_epochs):
        # --- Training ---
        model.train()
        epoch_loss = 0.0
        n_batches = 0

        for contexts, targets in train_loader:
            contexts = contexts.numpy()  # TimesFM expects numpy
            targets_tensor = targets.to(device)

            # Generate forecasts
            # Convert batch of tensors to list of numpy arrays
            input_list = [contexts[i] for i in range(contexts.shape[0])]

            try:
                point_fc, _ = model.forecast(
                    horizon=horizon,
                    inputs=input_list,
                )

                # Compute loss
                pred_tensor = torch.tensor(point_fc, dtype=torch.float32, device=device)
                loss = loss_fn(pred_tensor, targets_tensor)

                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                epoch_loss += loss.item()
                n_batches += 1

            except RuntimeError as e:
                print(f"  Skipping batch due to: {e}")
                continue

        avg_loss = epoch_loss / max(n_batches, 1)
        train_losses.append(avg_loss)

        # --- Validation ---
        model.eval()
        with torch.no_grad():
            val_mae = evaluate_model(model, val_data, horizon)
            val_maes.append(val_mae)

        print(f"  Epoch {epoch + 1}/{num_epochs} — Loss: {avg_loss:.4f}, Val MAE: {val_mae:.4f}")

    return train_losses, val_maes


def evaluate_model(model, test_series, horizon):
    """Evaluate model on held-out test data."""
    maes = []
    for series in test_series:
        if len(series) <= horizon:
            continue
        context = series[:-horizon]
        ground_truth = series[-horizon:]

        point_fc, _ = model.forecast(horizon=horizon, inputs=[context])
        mae = np.mean(np.abs(point_fc[0] - ground_truth))
        maes.append(mae)

    return np.mean(maes) if maes else float("inf")


# ==============================================================================
# Step 4: Full Fine-Tuning Pipeline
# ==============================================================================

def example_1_finetune_pipeline():
    """Complete fine-tuning pipeline from data to evaluation."""
    print("=" * 60)
    print("Example 1: Full Fine-Tuning Pipeline")
    print("=" * 60)

    # --- Data Preparation ---
    print("\nStep 1: Generating domain-specific data...")
    all_series = generate_domain_data(n_series=50, length=800)

    # Train/val/test split
    train_series = all_series[:35]
    val_series = all_series[35:42]
    test_series = all_series[42:]

    print(f"  Train: {len(train_series)} series")
    print(f"  Val:   {len(val_series)} series")
    print(f"  Test:  {len(test_series)} series")

    # Create dataset and dataloader
    context_length = 256
    horizon = 64

    train_dataset = TimeSeriesSlidingWindowDataset(
        train_series,
        context_length=context_length,
        horizon=horizon,
        stride=32,  # slide by 32 steps for more samples
    )
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

    # --- Model Setup ---
    print("\nStep 2: Loading pretrained TimesFM...")
    torch.set_float32_matmul_precision("high")
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        "google/timesfm-2.5-200m-pytorch"
    )
    model.compile(
        timesfm.ForecastConfig(
            max_context=512,
            max_horizon=256,
            normalize_inputs=True,
            use_continuous_quantile_head=False,  # disable for faster training
            force_flip_invariance=True,
            infer_is_positive=True,
            fix_quantile_crossing=False,
        )
    )

    # --- Baseline Evaluation ---
    print("\nStep 3: Baseline evaluation (zero-shot)...")
    baseline_mae = evaluate_model(model, test_series, horizon)
    print(f"  Zero-shot Test MAE: {baseline_mae:.4f}")

    # --- Fine-Tuning ---
    print("\nStep 4: Fine-tuning...")
    train_losses, val_maes = finetune_timesfm(
        model=model,
        train_loader=train_loader,
        val_data=val_series,
        num_epochs=5,
        learning_rate=1e-5,
        horizon=horizon,
    )

    # --- Final Evaluation ---
    print("\nStep 5: Final evaluation...")
    finetuned_mae = evaluate_model(model, test_series, horizon)
    print(f"  Zero-shot Test MAE:  {baseline_mae:.4f}")
    print(f"  Fine-tuned Test MAE: {finetuned_mae:.4f}")
    if finetuned_mae < baseline_mae:
        improvement = (baseline_mae - finetuned_mae) / baseline_mae * 100
        print(f"  Improvement:         {improvement:.1f}%")
    else:
        print("  Note: Fine-tuning did not improve on this data.")
        print("  This can happen with synthetic data or insufficient epochs.")

    # --- Visualization ---
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Training loss
    axes[0].plot(train_losses, marker="o", color="coral")
    axes[0].set_title("Training Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("MSE Loss")
    axes[0].grid(True, alpha=0.3)

    # Validation MAE
    axes[1].plot(val_maes, marker="s", color="steelblue")
    axes[1].set_title("Validation MAE")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("MAE")
    axes[1].grid(True, alpha=0.3)

    # Example forecast comparison
    test_example = test_series[0]
    context = test_example[:-horizon]
    ground_truth = test_example[-horizon:]
    point_fc, _ = model.forecast(horizon=horizon, inputs=[context])

    n = len(context)
    axes[2].plot(range(n - 100, n), context[-100:], label="Context", color="steelblue")
    forecast_x = range(n, n + horizon)
    axes[2].plot(forecast_x, ground_truth, label="Ground Truth", color="green", linestyle="--")
    axes[2].plot(forecast_x, point_fc[0], label="Fine-tuned Forecast", color="coral", linewidth=2)
    axes[2].axvline(x=n, color="gray", linestyle="--", alpha=0.5)
    axes[2].set_title("Example Forecast (Fine-tuned)")
    axes[2].legend(fontsize=8)

    plt.suptitle("TimesFM Fine-Tuning Results", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("06_finetuning_results.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Plot saved: 06_finetuning_results.png")


def example_2_save_and_load():
    """Save and reload a fine-tuned model."""
    print("\n" + "=" * 60)
    print("Example 2: Save & Load Fine-Tuned Model")
    print("=" * 60)

    print("""
    After fine-tuning, save the model for later use:

    # Save fine-tuned weights
    model.save_pretrained("./my_finetuned_timesfm")

    # Later, load the fine-tuned model
    model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
        "./my_finetuned_timesfm"
    )
    model.compile(timesfm.ForecastConfig(
        max_context=512,
        max_horizon=256,
        normalize_inputs=True,
        use_continuous_quantile_head=True,
    ))

    # Use as normal
    point_fc, quantile_fc = model.forecast(
        horizon=64,
        inputs=[your_data],
    )
    """)

    print("Note: The official repo also provides:")
    print("  - notebooks/finetuning.ipynb (JAX-based)")
    print("  - notebooks/finetuning_torch.ipynb (PyTorch)")
    print("  - Multi-GPU DDP fine-tuning support")


def example_3_finetuning_tips():
    """Best practices for fine-tuning TimesFM."""
    print("\n" + "=" * 60)
    print("Example 3: Fine-Tuning Best Practices")
    print("=" * 60)

    print("""
    ┌─────────────────────────────────────────────────────────────┐
    │                 FINE-TUNING BEST PRACTICES                  │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  1. DATA REQUIREMENTS                                      │
    │     - Minimum: 100+ time series or 10K+ data points        │
    │     - More diverse data → better generalization             │
    │     - Ensure data is representative of deployment scenario  │
    │                                                             │
    │  2. HYPERPARAMETERS                                         │
    │     - Learning rate: 1e-5 to 1e-4 (start low)              │
    │     - Batch size: 16-64 (GPU memory dependent)              │
    │     - Epochs: 5-50 (monitor val loss for early stopping)    │
    │     - Context length: match your inference use case         │
    │                                                             │
    │  3. AVOIDING CATASTROPHIC FORGETTING                        │
    │     - Use a low learning rate (1e-5)                        │
    │     - Fine-tune for fewer epochs                            │
    │     - Consider freezing early transformer layers            │
    │     - Monitor zero-shot performance on holdout data         │
    │                                                             │
    │  4. WHEN TO FINE-TUNE vs ZERO-SHOT                          │
    │     Fine-tune when:                                         │
    │     ✓ Domain has unique patterns (medical, financial)       │
    │     ✓ You have sufficient labeled data (100+ series)        │
    │     ✓ Zero-shot accuracy is insufficient                    │
    │                                                             │
    │     Use zero-shot when:                                     │
    │     ✓ Limited domain data                                   │
    │     ✓ Data distribution changes frequently                  │
    │     ✓ Zero-shot accuracy is acceptable                      │
    │                                                             │
    │  5. MULTI-GPU TRAINING                                      │
    │     - TimesFM supports DDP multi-GPU fine-tuning            │
    │     - Use torchrun for distributed training                 │
    │     - Scale batch size linearly with GPU count              │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    example_1_finetune_pipeline()
    example_2_save_and_load()
    example_3_finetuning_tips()
    print("\nAll fine-tuning examples completed.")
