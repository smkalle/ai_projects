
# PyMC Marketing: A Hands‑On Tutorial for AI Engineers 🚀  
*Author: Google SDE3 AI Engineer (generated)*  

---

## 0 ️⃣ Overview  
PyMC Marketing is an open‑source library that marries Bayesian inference with real‑world marketing analytics.  
This guide walks you through **Marketing Mix Modeling (MMM)** from scratch, shows you how to fit a model, evaluate it, and
make budget decisions—entirely in Python.

| What you’ll learn | Why it matters |
|-------------------|----------------|
| Set up a reproducible environment | Share notebooks across teams & CI |
| Generate or load data | Works even if you can’t publish real spend |
| Specify priors & select adstock/saturation | Encodes marketing domain knowledge |
| Fit with NUTS (NumPyro backend) | Fast, scalable, GPU‑friendly sampling |
| Diagnose, interpret, & forecast | Turn posterior draws into **ROAS** & **budget curves** |
| Advanced: GP baselines, lift tests, optimisation | Production‑grade MMM in < 300 LOC |

---

## 1 ️⃣ Prerequisites  
* Python ≥ 3.9  
* Familiarity with NumPy/Pandas  
* Basic understanding of Bayesian statistics (helpful but not required)

---

## 2 ️⃣ Installation  

```bash
# ⭐ Option A: Conda (recommended for local)
conda create -n marketing_env -c conda-forge pymc-marketing python=3.11
conda activate marketing_env

# ⭐ Option B: Google Colab
pip install pymc-marketing[extra] --quiet
```

> **Tip**: The `[extra]` tag installs ArviZ, NumPyro, and JAX for GPU acceleration.

---

## 3 ️⃣ Quick Start  

```python
import pymc_marketing as pmm
print("PyMC Marketing version:", pmm.__version__)
```

---

## 4 ️⃣ Step‑by‑Step Walk‑Through  

### 4.1 Create or Ingest Data  

```python
from pathlib import Path
import numpy as np, pandas as pd

rng = np.random.default_rng(42)
dates = pd.date_range("2018-04-01", "2021-09-01", freq="W-MON")
df = pd.DataFrame({"date_week": dates})
df["x1"] = rng.uniform(0, 1, len(df))
df["x2"] = rng.uniform(0, 1, len(df))
df["event_1"] = (df["date_week"] == "2019-05-13").astype(int)
df["event_2"] = (df["date_week"] == "2020-09-14").astype(int)
# trending target
df["t"] = np.arange(len(df))
```

### 4.2 Feature Engineering  

```python
from pymc_marketing.mmm.utils import add_fourier_terms
df = add_fourier_terms(df, date_col="date_week", period=52, order=2)
```

### 4.3 Specify the MMM  

```python
from pymc_marketing.mmm import MMM, GeometricAdstock, LogisticSaturation
from pymc_marketing.prior import Prior

model_cfg = {
    "intercept":         Prior("Normal", mu=0.5, sigma=0.2),
    "saturation_beta":   Prior("HalfNormal", sigma=[1.0, 1.0]),
    "gamma_control":     Prior("Normal", mu=0, sigma=0.05),
    "gamma_fourier":     Prior("Laplace", mu=0, b=0.2),
    "likelihood":        Prior("Normal", sigma=Prior("HalfNormal", sigma=6)),
}

mmm = MMM(
    model_config=model_cfg,
    date_column="date_week",
    adstock=GeometricAdstock(l_max=8),
    saturation=LogisticSaturation(),
    channel_columns=["x1", "x2"],
    control_columns=["event_1", "event_2", "t"],
    yearly_seasonality=2,
)
```

### 4.4 Fit the Model  

```python
X = df[["x1", "x2", "event_1", "event_2", "t"]]
y = rng.normal(loc=10 + 3*df["x1"] + 2*df["x2"], scale=1.0)  # synthetic target
mmm.fit(X, y,
        chains=4,
        target_accept=0.9,
        nuts_sampler="numpyro",
        random_seed=rng)
```

### 4.5 Diagnostics & Visuals  

```python
mmm.plot_posterior_predictive(original_scale=True)
mmm.plot_components_contributions(original_scale=True)
```

### 4.6 Forecast & Budget Optimisation  

```python
# Create future spend scenarios and get predictions
future = df.tail(8).copy()
future["x1"] *= 1.2  # 20% boost in channel 1
future["x2"] *= 0.8  # 20% cut in channel 2

forecast = mmm.predict(future, include_last_observations=True)
```

---

## 5 ️⃣ Advanced Modules  

| Notebook | Topic |
|----------|-------|
| `mmm_time_varying_media_example.ipynb` | Gaussian‑Process baseline |
| `mmm_budget_allocation_example.ipynb` | Optimiser for ROAS & diminishing returns |
| `mmm_lift_test.ipynb` | Combining lift/geo tests with MMM |
| `customer_choice/mv_its_saturated.ipynb` | Choice models |

---

## 6 ️⃣ Running This on Google Colab  

1. Click the badge below or upload the provided notebook.  
2. _Runtime → Change runtime type_ → select **GPU** (optional).  
3. Run _all_ cells in order.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/your‑repo/PyMC_Marketing_Tutorial/blob/main/PyMC_Marketing_Tutorial.ipynb)

---

## 7 ️⃣ Resources & References  

* [PyMC Marketing Docs](https://www.pymc-marketing.io)
* Jin et al. (2017) “Bayesian Methods for Media Mix Modeling…”
* PyMC Labs Blog & YouTube

---

## 8 ️⃣ License  
This tutorial is released under the **MIT License**.  
