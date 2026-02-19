# TimesFM: A Hands-On Tutorial for AI Engineers

**Google's Time Series Foundation Model — From Zero-Shot Forecasting to Production**

> TimesFM is a decoder-only foundation model pretrained on 100B+ real-world time points.
> With only 200M parameters, it achieves near-SOTA zero-shot forecasting across domains
> without any task-specific training.

| | |
|---|---|
| **Paper** | [A decoder-only foundation model for time-series forecasting](https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/) (ICML 2024) |
| **Repository** | [github.com/google-research/timesfm](https://github.com/google-research/timesfm) |
| **Latest Version** | TimesFM 2.5 (200M params, 16K context, continuous quantile head) |
| **License** | Apache 2.0 |
| **Hugging Face** | [google/timesfm-2.5-200m-pytorch](https://huggingface.co/google/timesfm-2.5-200m-pytorch) |

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Installation & Setup](#2-installation--setup)
3. [Tutorial 1: Zero-Shot Forecasting](#3-tutorial-1-zero-shot-forecasting)
4. [Tutorial 2: DataFrame-Based Forecasting](#4-tutorial-2-dataframe-based-forecasting)
5. [Tutorial 3: Quantile Forecasting & Uncertainty](#5-tutorial-3-quantile-forecasting--uncertainty)
6. [Tutorial 4: External Covariates (XReg)](#6-tutorial-4-external-covariates-xreg)
7. [Tutorial 5: Anomaly Detection](#7-tutorial-5-anomaly-detection)
8. [Tutorial 6: Fine-Tuning](#8-tutorial-6-fine-tuning)
9. [ForecastConfig Reference](#9-forecastconfig-reference)
10. [Version Comparison](#10-version-comparison)
11. [Troubleshooting](#11-troubleshooting)
12. [Resources](#12-resources)

---

## 1. Architecture Overview

TimesFM uses a **decoder-only transformer** (similar to GPT-style LLMs) adapted for time series:

```
Raw Time Series → [Patch Tokenization] → [Stacked Transformer Decoder] → [Output Head] → Forecast
                   (32 time points      (self-attention +              (point + quantile
                    per patch/token)      feed-forward layers)          predictions)
```

### Key Design Decisions

| Concept | Detail |
|---|---|
| **Patching** | Groups of 32 contiguous time points become a single token. This reduces sequence length and captures local patterns, similar to how Vision Transformers patch images. |
| **Decoder-Only** | Uses causal (left-to-right) attention. Each patch can only attend to previous patches. This naturally models the temporal causality of time series. |
| **Output Patches** | The model outputs patches of 128 time points, which are then trimmed to the requested horizon length. |
| **Pretraining Data** | Trained on 100B+ real-world time points from Google Trends, Wiki Pageviews, synthetic data, and large public time series corpora. |
| **Zero-Shot Transfer** | The model generalizes across domains (retail, energy, finance, weather, healthcare) without task-specific training — similar to how LLMs generalize across text tasks. |

### What's New in v2.5

- **200M parameters** (down from 500M in v2.0, more efficient)
- **16K context length** (up from 2048 in v2.0)
- **Continuous quantile head**: separate 30M-parameter module for calibrated uncertainty
- **Removed frequency indicator**: the model now auto-detects data frequency
- **Restored covariate support**: XReg for external regressors
- **Ranked #1** among open-source models on the GIFT-Eval benchmark

---

## 2. Installation & Setup

### System Requirements

- **Python**: 3.11+
- **RAM**: 32GB+ recommended
- **GPU**: Optional but recommended (CUDA-compatible)

### Install from PyPI

```bash
# Create virtual environment
python -m venv timesfm-env
source timesfm-env/bin/activate

# Install with PyTorch backend
pip install timesfm[torch]

# Or install with Flax/JAX backend
pip install timesfm[flax]

# For covariate support (requires JAX)
pip install timesfm[xreg]
```

### Install from Source

```bash
git clone https://github.com/google-research/timesfm.git
cd timesfm

# Using uv (recommended)
uv venv
source .venv/bin/activate
uv pip install -e .[torch]

# Or using pip
pip install -e .[torch]
```

### Install Tutorial Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

```python
import timesfm
import torch
import numpy as np

torch.set_float32_matmul_precision("high")

model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch"
)
model.compile(timesfm.ForecastConfig(
    max_context=256,
    max_horizon=128,
))

# Quick test
point_fc, quantile_fc = model.forecast(
    horizon=10,
    inputs=[np.sin(np.linspace(0, 10, 100))],
)
print(f"Forecast shape: {point_fc.shape}")  # (1, 10)
print("TimesFM is working.")
```

---

## 3. Tutorial 1: Zero-Shot Forecasting

> **Script**: [`examples/01_basic_zero_shot_forecasting.py`](examples/01_basic_zero_shot_forecasting.py)

The core value proposition of TimesFM: load a pretrained model and forecast any time series immediately, with no training.

### Model Loading and Compilation

```python
import torch
import numpy as np
import timesfm

# Optimize GPU matmul precision
torch.set_float32_matmul_precision("high")

# Load pretrained weights from Hugging Face
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "google/timesfm-2.5-200m-pytorch"
)

# Compile with forecast configuration
model.compile(
    timesfm.ForecastConfig(
        max_context=1024,       # max historical points (multiple of 32)
        max_horizon=256,        # max forecast steps (multiple of 128)
        normalize_inputs=True,  # handle extreme magnitudes
        use_continuous_quantile_head=True,
        force_flip_invariance=True,
        infer_is_positive=False,
        fix_quantile_crossing=True,
    )
)
```

### Basic Forecast

```python
# Input: list of numpy arrays (variable lengths OK)
series_1 = np.sin(np.linspace(0, 4 * np.pi, 200))
series_2 = np.linspace(0, 5, 150) + np.random.normal(0, 0.3, 150)

# Forecast 48 steps ahead
point_forecast, quantile_forecast = model.forecast(
    horizon=48,
    inputs=[series_1, series_2],
)

# point_forecast:    shape (2, 48)     — point predictions
# quantile_forecast: shape (2, 48, 10) — mean + P10 through P90
```

### Key Concepts

**Variable-length inputs**: Each series in the input list can have a different length. TimesFM handles padding/truncation internally.

**Context vs horizon**: The model uses `max_context` historical points to predict `horizon` future points. More context generally improves accuracy, especially for series with long-range patterns.

**Automatic patching**: Input series are divided into patches of 32 time points. The model processes these as tokens. `max_context` is automatically rounded up to a multiple of 32.

---

## 4. Tutorial 2: DataFrame-Based Forecasting

> **Script**: [`examples/02_dataframe_forecasting.py`](examples/02_dataframe_forecasting.py)

Real-world data lives in DataFrames. TimesFM's `forecast_on_df()` method handles the standard time series DataFrame format used by tools like Nixtla, statsforecast, and others.

### Expected DataFrame Format

| Column | Type | Description |
|---|---|---|
| `unique_id` | str | Identifier for each time series |
| `ds` | datetime | Timestamp column |
| `<value_name>` | float | The numeric values to forecast |

### Single Series Forecast

```python
import pandas as pd

# Prepare DataFrame
df = pd.DataFrame({
    "unique_id": "store_A",
    "ds": pd.date_range("2022-01-01", periods=365, freq="D"),
    "sales": your_sales_data,
})

# Forecast
forecast_df = model.forecast_on_df(
    inputs=df,
    freq="D",             # "D"=daily, "W"=weekly, "MS"=monthly, "H"=hourly
    value_name="sales",
    num_jobs=1,           # parallel jobs (-1 = all cores)
)
```

### Multi-Series Forecast

```python
# DataFrame with multiple series (different unique_id values)
# TimesFM batches and forecasts all series efficiently
forecast_df = model.forecast_on_df(
    inputs=multi_store_df,   # contains store_A, store_B, store_C
    freq="D",
    value_name="sales",
    num_jobs=1,
)
# Returns forecasts for ALL series in one call
```

### Frequency Mapping

The `freq` parameter maps to internal frequency categories:

| Freq String | Category | Use For |
|---|---|---|
| `"T"`, `"MIN"`, `"H"`, `"D"`, `"B"`, `"S"` | 0 (High) | Sub-daily to daily data |
| `"W"`, `"M"`, `"MS"` | 1 (Medium) | Weekly and monthly data |
| `"Q"`, `"Y"`, `"A"` | 2 (Low) | Quarterly and yearly data |

---

## 5. Tutorial 3: Quantile Forecasting & Uncertainty

> **Script**: [`examples/03_quantile_forecasting.py`](examples/03_quantile_forecasting.py)

TimesFM 2.5 includes a 30M-parameter **continuous quantile head** that produces calibrated probability distributions over future values.

### Quantile Output Structure

```python
point_fc, quantile_fc = model.forecast(horizon=48, inputs=[data])

# quantile_fc shape: (batch, horizon, 10)
# Channel mapping:
#   [0] = Mean
#   [1] = P10 (10th percentile)
#   [2] = P20
#   [3] = P30
#   [4] = P40
#   [5] = P50 (median)
#   [6] = P60
#   [7] = P70
#   [8] = P80
#   [9] = P90
```

### Confidence Bands

```python
# 80% confidence interval: P10 to P90
lower_80 = quantile_fc[0, :, 1]  # P10
upper_80 = quantile_fc[0, :, 9]  # P90

# 40% confidence interval: P30 to P70
lower_40 = quantile_fc[0, :, 3]  # P30
upper_40 = quantile_fc[0, :, 7]  # P70
```

### Non-Negative Forecasting

For data that cannot be negative (sales, counts, prices):

```python
model.compile(timesfm.ForecastConfig(
    max_context=1024,
    max_horizon=256,
    infer_is_positive=True,  # clamp forecasts ≥ 0
))
```

### Practical Application: Safety Stock Calculation

```python
# Use P90 for safety stock levels
p50_demand = quantile_fc[0, :, 5]  # expected demand
p90_demand = quantile_fc[0, :, 9]  # worst-case demand (90th percentile)

safety_buffer = np.sum(p90_demand) - np.sum(p50_demand)
print(f"Order {np.sum(p90_demand):.0f} units (buffer: +{safety_buffer:.0f})")
```

---

## 6. Tutorial 4: External Covariates (XReg)

> **Script**: [`examples/04_covariates_xreg.py`](examples/04_covariates_xreg.py)

TimesFM 2.5 supports external regressors (covariates) — additional features that influence the forecast like temperature, promotions, holidays, and day-of-week.

### Covariate Types

| Type | Scope | Example |
|---|---|---|
| **Static Numerical** | One value per series | Store area (sq ft), base price |
| **Static Categorical** | One category per series | Store type, region |
| **Dynamic Numerical** | One value per timestep | Temperature, price |
| **Dynamic Categorical** | One category per timestep | Day of week, is_holiday |

**Important**: Dynamic covariates must include values for both the context window AND the forecast horizon.

### Forecast with Covariates

```python
# Requires: pip install timesfm[xreg]
# (installs JAX/jaxlib dependencies)

cov_forecast, xreg_forecast = model.forecast_with_covariates(
    horizon=30,
    inputs=[sales_history],
    dynamic_numerical_covariates={
        "temperature": [temp_context_and_horizon],
    },
    dynamic_categorical_covariates={
        "day_of_week": [dow_context_and_horizon],
        "is_promotion": [promo_context_and_horizon],
    },
    static_numerical_covariates={
        "store_size": [2500.0],
    },
    static_categorical_covariates={
        "store_type": ["urban"],
    },
    xreg_mode="xreg + timesfm",  # or "timesfm + xreg"
)
```

### XReg Modes

**Mode 1: `"xreg + timesfm"` (default)**
1. Fit a linear model on covariates
2. Compute residuals: `observed - xreg_predictions`
3. Use TimesFM to forecast the residuals
4. Final = `xreg_out_of_sample + timesfm_residual_forecast`

Best when covariates explain most of the variance.

**Mode 2: `"timesfm + xreg"`**
1. TimesFM generates forecasts
2. Compute residuals: `timesfm_in_sample - observed`
3. Fit a linear model on residuals using covariates
4. Final = `timesfm_out_of_sample + xreg_residual_correction`

Best when time series patterns dominate and covariates provide corrections.

---

## 7. Tutorial 5: Anomaly Detection

> **Script**: [`examples/05_anomaly_detection.py`](examples/05_anomaly_detection.py)

TimesFM's quantile predictions provide natural anomaly detection thresholds — no separate anomaly detector needed.

### Strategy: Forecast-Based Anomaly Detection

```
For each time point t:
  1. Use history [t-context, t) as context
  2. Forecast the next step
  3. Compare actual value at t against predicted quantile bands
  4. If actual falls outside bands → anomaly
```

### Sliding Window Detection

```python
context_size = 256
for t in range(context_size, len(signal)):
    context = signal[t - context_size:t]
    actual = signal[t]

    _, quantile_fc = model.forecast(horizon=1, inputs=[context])
    p10 = quantile_fc[0, 0, 1]
    p90 = quantile_fc[0, 0, 9]

    if actual > p90:
        anomaly_score = (actual - p90) / (p90 - p10)
    elif actual < p10:
        anomaly_score = (p10 - actual) / (p90 - p10)
    else:
        anomaly_score = 0.0
```

### IQR-Based Detection

Following the approach used in Google Cloud Dataflow pipelines:

```python
# Approximate Q1 and Q3 from available quantiles
q25 = (quantile_fc[0, :, 2] + quantile_fc[0, :, 3]) / 2  # avg P20+P30
q75 = (quantile_fc[0, :, 7] + quantile_fc[0, :, 8]) / 2  # avg P70+P80
iqr = q75 - q25

# Classic IQR rule
lower_bound = q25 - 1.5 * iqr
upper_bound = q75 + 1.5 * iqr

is_anomaly = (actual_values < lower_bound) | (actual_values > upper_bound)
```

### Multi-Series Monitoring

Batch multiple sensor/metric series into a single `model.forecast()` call for efficient monitoring:

```python
# Forecast all sensors at once
contexts = [sensor_1[-256:], sensor_2[-256:], sensor_3[-256:]]
point_fc, quantile_fc = model.forecast(horizon=100, inputs=contexts)

# Check each sensor against its own predicted bands
for i, sensor_name in enumerate(sensor_names):
    p10, p90 = quantile_fc[i, :, 1], quantile_fc[i, :, 9]
    anomalies = (actual[i] < p10) | (actual[i] > p90)
```

---

## 8. Tutorial 6: Fine-Tuning

> **Script**: [`examples/06_finetuning.py`](examples/06_finetuning.py)

When zero-shot performance is insufficient for your domain, fine-tune TimesFM on your own data.

### When to Fine-Tune

| Scenario | Recommendation |
|---|---|
| Limited domain data (< 100 series) | Use zero-shot |
| Rapidly changing distribution | Use zero-shot |
| Unique domain patterns (medical, financial) | Fine-tune |
| Sufficient labeled data (100+ series) | Fine-tune |
| Zero-shot accuracy not meeting requirements | Fine-tune |

### Custom Dataset with Sliding Windows

```python
from torch.utils.data import Dataset, DataLoader

class TimeSeriesSlidingWindowDataset(Dataset):
    def __init__(self, series_list, context_length=256, horizon=64, stride=1):
        self.samples = []
        window = context_length + horizon
        for series in series_list:
            for start in range(0, len(series) - window + 1, stride):
                context = series[start:start + context_length]
                target = series[start + context_length:start + window]
                self.samples.append((
                    torch.tensor(context, dtype=torch.float32),
                    torch.tensor(target, dtype=torch.float32),
                ))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        return self.samples[idx]
```

### Fine-Tuning Loop

```python
optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
loss_fn = nn.MSELoss()

for epoch in range(num_epochs):
    model.train()
    for contexts, targets in train_loader:
        input_list = [contexts[i].numpy() for i in range(len(contexts))]
        point_fc, _ = model.forecast(horizon=horizon, inputs=input_list)

        pred = torch.tensor(point_fc, dtype=torch.float32)
        loss = loss_fn(pred, targets)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

### Save & Load Fine-Tuned Model

```python
# Save
model.save_pretrained("./my_finetuned_timesfm")

# Load
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained(
    "./my_finetuned_timesfm"
)
model.compile(timesfm.ForecastConfig(...))
```

### Multi-GPU Fine-Tuning

TimesFM supports DDP (Distributed Data Parallel) training:

```bash
torchrun --nproc_per_node=4 finetune_script.py
```

See the official `notebooks/finetuning_torch.ipynb` for the complete multi-GPU setup.

---

## 9. ForecastConfig Reference

| Parameter | Type | Default | Description |
|---|---|---|---|
| `max_context` | int | 0 | Maximum input context length. Auto-rounded to multiple of 32 (patch size). |
| `max_horizon` | int | 0 | Maximum forecast horizon. Auto-rounded to multiple of 128 (output patch size). |
| `normalize_inputs` | bool | False | Normalize extreme magnitude inputs before forecasting. |
| `per_core_batch_size` | int | 1 | Batch size per device for inference. |
| `use_continuous_quantile_head` | bool | False | Enable 30M-param continuous quantile head for uncertainty estimation. Max horizon 1024 when enabled. |
| `force_flip_invariance` | bool | True | Enforce time-reversal invariance. Extends scale-invariance to negative values. |
| `infer_is_positive` | bool | True | Auto-detect and enforce non-negative outputs for non-negative inputs. |
| `fix_quantile_crossing` | bool | False | Ensure quantile monotonicity (P10 < P20 < ... < P90). |
| `return_backcast` | bool | False | Include model predictions over the context window in output. |
| `window_size` | int | 0 | Window size for decomposed forecasting (0 = disabled). |

---

## 10. Version Comparison

| Feature | v1.0 | v2.0 | v2.5 |
|---|---|---|---|
| Parameters | 200M | 500M | 200M |
| Max Context | 512 | 2,048 | 16,384 |
| Quantile Head | No | 10 experimental | 30M continuous |
| Frequency Indicator | Required (0/1/2) | Required (0/1/2) | Removed (auto-detect) |
| Covariate Support | No | No | Yes (XReg) |
| Fine-Tuning | JAX only | JAX only | JAX + PyTorch + Multi-GPU |
| GIFT-Eval Rank | — | #1 open-source | #1 open-source |
| Install (PyTorch) | `pip install timesfm[torch]` | `pip install timesfm[torch]` | `pip install timesfm[torch]` |
| Install (legacy v1.0) | `pip install timesfm==1.3.0` | — | — |

### API Differences

**v1.0 / v2.0 (legacy)**:
```python
tfm = timesfm.TimesFm(
    hparams=timesfm.TimesFmHparams(backend="gpu", horizon_len=128, ...),
    checkpoint=timesfm.TimesFmCheckpoint(huggingface_repo_id="google/timesfm-2.0-500m-pytorch"),
)
point_fc, quantile_fc = tfm.forecast(inputs, freq=[0, 0])
```

**v2.5 (current)**:
```python
model = timesfm.TimesFM_2p5_200M_torch.from_pretrained("google/timesfm-2.5-200m-pytorch")
model.compile(timesfm.ForecastConfig(max_context=1024, max_horizon=256))
point_fc, quantile_fc = model.forecast(horizon=48, inputs=data)
```

---

## 11. Troubleshooting

### Common Issues

**`CUDA out of memory`**
- Reduce `per_core_batch_size` in ForecastConfig
- Reduce `max_context` (e.g., 512 instead of 1024)
- Use `torch.set_float32_matmul_precision("high")` for memory efficiency

**`forecast_with_covariates` throws ImportError**
- XReg requires JAX: `pip install timesfm[xreg]`
- Or manually: `pip install jax jaxlib`

**`max_context` not matching expected value**
- `max_context` is auto-rounded up to the nearest multiple of 32 (patch size)
- `max_horizon` is auto-rounded up to the nearest multiple of 128 (output patch size)
- Combined context + horizon cannot exceed the model's 16K limit

**`use_continuous_quantile_head` fails**
- The quantile head only supports horizons up to 1024 steps
- Disable it for longer horizons: `use_continuous_quantile_head=False`

**Slow inference on CPU**
- TimesFM is designed for GPU. CPU inference works but is significantly slower
- For CPU, reduce context length and batch size
- Use `torch.set_num_threads(N)` to control CPU parallelism

**DataFrame `forecast_on_df` errors**
- The `ds` column must be datetime type, not strings or integers
- Use `pd.to_datetime(df["ds"])` to convert
- The DataFrame must have `unique_id`, `ds`, and your value column

### Performance Tips

1. **Batch multiple series** in a single `model.forecast()` call instead of looping
2. **Use `torch.set_float32_matmul_precision("high")`** for faster GPU compute
3. **Pre-allocate context arrays** to avoid repeated numpy operations
4. **For production**: consider Google BigQuery's built-in TimesFM via `AI.FORECAST`

---

## 12. Resources

### Official

- [GitHub Repository](https://github.com/google-research/timesfm)
- [ICML 2024 Paper: A decoder-only foundation model for time-series forecasting](https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/)
- [Few-Shot Learning Extension (ICML 2025)](https://research.google/blog/time-series-foundation-models-can-be-few-shot-learners/)
- [Hugging Face Model Collection](https://huggingface.co/google/timesfm-2.5-200m-pytorch)
- [PyPI Package](https://pypi.org/project/timesfm/)
- [Google BigQuery TimesFM Docs](https://docs.cloud.google.com/bigquery/docs/timesfm-model)

### Community

- [TimesFM Anomaly Detection (Google Dataflow)](https://docs.cloud.google.com/dataflow/docs/notebooks/anomaly_detection_timesfm)
- [TimesFM Anomaly Detection (BigQuery)](https://docs.cloud.google.com/bigquery/docs/timesfm-anomaly-detection-tutorial)
- [TimesFM on Databricks](https://community.databricks.com/t5/technical-blog/genai-for-time-series-analysis-with-timesfm/ba-p/95507)
- [FlaMinGo: TimesFM for Classification](https://huggingface.co/PartAI/FlaMinGo-timesfm)
- [TimesFM for Financial Data](https://github.com/pfnet-research/timesfm_fin)

---

## Tutorial Files

```
tutorials/timesfm/
├── README.md                                    # This guide
├── requirements.txt                             # Dependencies
└── examples/
    ├── 01_basic_zero_shot_forecasting.py        # Zero-shot with numpy arrays
    ├── 02_dataframe_forecasting.py              # Pandas DataFrame API
    ├── 03_quantile_forecasting.py               # Uncertainty estimation
    ├── 04_covariates_xreg.py                    # External regressors
    ├── 05_anomaly_detection.py                  # Anomaly detection pipeline
    └── 06_finetuning.py                         # Fine-tuning on custom data
```

Run any example:
```bash
cd tutorials/timesfm
pip install -r requirements.txt
python examples/01_basic_zero_shot_forecasting.py
```
