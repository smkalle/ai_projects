# Avestan–Vedic Sanskrit Comparative Linguistics: Data Science Spec

## Overview

A data science pipeline for quantifying linguistic similarities and divergences between **Avestan** (the liturgical language of Zoroastrianism) and **Vedic Sanskrit** (the language of the Rigveda). Both languages descend from a common **Proto-Indo-Iranian** (PII) ancestor and diverged roughly 3,500–4,000 years ago. This project applies NLP, statistical modeling, and machine learning to three core analytical dimensions: lexical cognate detection, phonological sound-shift analysis, and semantic drift analysis.

---

## Background & Motivation

| Feature | Avestan | Vedic Sanskrit |
|---|---|---|
| Script | Avestan alphabet | Devanagari / IAST transliteration |
| Corpus | Gathas (~17 hymns), Younger Avesta | Rigveda (~10,600 verses), Atharvaveda |
| Religious Context | Zoroastrian | Hindu / Brahminic |
| Key Divergence | *asura* = divine lord; *daeva* = demon | *asura* = demon; *deva* = god |
| Proto-ancestor | Proto-Indo-Iranian (PII) | Proto-Indo-Iranian (PII) |

The two languages share roughly **60–70% cognate vocabulary** yet diverged in systematic, detectable ways — making them an ideal case study for computational comparative linguistics.

---

## Project Goals

1. Build an automated **cognate detection pipeline** for Avestan–Sanskrit word pairs.
2. Model **phonological correspondence rules** (sound laws) as learnable transformations.
3. Detect and visualize **semantic drift** across paired cognates using contextual embeddings.
4. Produce an interactive dashboard for exploration and a reproducible research artifact.

---

## Module 1: Lexical Comparison & Cognate Detection

### Objective
Identify cognate word pairs — words derived from a common PII root — and measure lexical similarity across semantic domains (family, nature, religion, law, warfare).

### Example Cognate Pairs

| Domain | Avestan | Sanskrit | Meaning |
|---|---|---|---|
| Warfare | *vīra* | *vīra* | warrior, hero |
| Wind | *vāyu* | *vāyu* | wind deity |
| Seven | *hapta* | *sapta* | seven |
| Fire | *ātar* | *atharva* | fire (ritual) |
| Truth | *aša* | *ṛta* | cosmic order / truth |
| Horse | *aspa* | *aśva* | horse |
| Cow | *gao* | *go* | cow |
| Name | *nāman* | *nāman* | name |

### Data Sources

- **CLDF (Cross-Linguistic Data Formats):** Standardized cognate datasets — [cldf.clld.org](https://cldf.clld.org)
- **IELex / IELEX:** Indo-European Lexical Cognacy Database
- **ASJP (Automated Similarity Judgment Program):** ~7,000 language word lists
- **Rigveda corpus:** Digital Corpus of Sanskrit (DCS) — [sanskrit.shloka.ru](https://www.sanskrit.shloka.ru), GRETIL
- **Avestan corpus:** Avestan Digital Archive (ADA), Zoroastrian Digital Library
- **Leipzig Glossing Rules data:** Morpheme-by-morpheme aligned text

### Methods

#### 1.1 String Similarity Metrics
```
cognate_score = weighted_average(
    normalized_edit_distance(w1, w2),      # Levenshtein / Damerau
    phoneme_aware_distance(w1, w2),        # ALINE algorithm
    lcs_ratio(w1, w2)                      # Longest common subsequence
)
```

#### 1.2 LexStat Algorithm (via `lingpy`)
- Compute pairwise language-internal distance matrices
- Apply SCA (Sound Class Analysis) alignment
- Cluster cognates using UPGMA or Neighbor Joining

#### 1.3 Embedding-Based Semantic Similarity
- Use multilingual sentence embeddings (LaBSE, multilingual-E5) on translations
- Cosine similarity to cluster semantically related cognates
- Cross-reference with known etymology databases

#### 1.4 Semantic Domain Classification
Tag each cognate pair by domain using a classifier:
- Domains: `kinship | nature | religion | warfare | numbers | body | animals | agriculture`
- Model: fine-tuned BERT or zero-shot classification via `transformers`

### Output
- `cognates.csv`: word pair, PII root, domain, similarity score, confidence
- Heatmap: cognate density by semantic domain
- Network graph: shared PII root → Avestan/Sanskrit branches

---

## Module 2: Phonological Analysis — Sound Shift Modeling

### Objective
Identify, validate, and model systematic phonological correspondences between Avestan and Sanskrit — particularly the **s → h** shift and related consonant mutations.

### Known Sound Laws

| Sanskrit | Avestan | Examples |
|---|---|---|
| s → h | initial/intervocalic | *sapta* → *hapta* (seven); *soma* → *haoma* (ritual drink) |
| dv → b | word-initial | *dvi* → *bi* (two) |
| śv → sp | — | *aśva* → *aspa* (horse) |
| r → r / l | — | largely preserved |
| Retroflex loss | — | Sanskrit retroflexes absent in Avestan |
| t → θ | — | dental → fricative in some positions |
| v-initial | w → v | maintained differently |

### Data Sources
- Aligned cognate pairs from Module 1
- ALINE phonetic alignment tool
- PHOIBLE database (phoneme inventories)
- IPA transcription of IAST and Avestan transliterations

### Methods

#### 2.1 Phoneme Alignment
- Convert IAST/Avestan transliterations → IPA
- Apply **pairwise phoneme alignment** (ALINE algorithm via `lingpy`)
- Build aligned phoneme pair corpus

#### 2.2 Correspondence Rule Mining
```python
# Example pipeline
alignments = aline_align(avestan_words, sanskrit_words)
correspondence_matrix = count_phoneme_pairs(alignments)
sound_laws = extract_rules(
    correspondence_matrix,
    min_support=0.8,     # rule fires >= 80% of the time
    positional=True      # track word-initial vs. medial vs. final
)
```

#### 2.3 Statistical Validation
- Chi-squared test: is the s→h shift non-random?
- Mutual information: measure phoneme co-occurrence strength
- Bootstrapped confidence intervals on correspondence frequencies

#### 2.4 Neural Phoneme Transduction (Stretch Goal)
- Train a character-level seq2seq model (transformer) to learn Sanskrit → Avestan phonological mapping
- Evaluate on held-out cognate pairs
- Attention weights reveal learned sound correspondences

### Output
- `sound_laws.json`: rule, frequency, positional context, p-value
- Correspondence matrix (heatmap): Avestan phoneme × Sanskrit phoneme
- Alignment visualization: color-coded cognate pair alignments

---

## Module 3: Semantic Drift Analysis

### Objective
Quantify how cognate word meanings have shifted — including the famous **Asura/Daeva reversal** — using diachronic embeddings and semantic field mapping.

### The Asura–Daeva Reversal

This is one of the most striking semantic inversions in language history:

| Term | Sanskrit meaning | Avestan meaning | Shift direction |
|---|---|---|---|
| *asura / ahura* | demon (later texts) | divine lord (*Ahura Mazdā*) | positive → negative (Skt) |
| *deva / daeva* | god | demon / lie-demon | positive → negative (Av) |
| *vīra* | warrior/hero | warrior/hero | stable |
| *vāyu* | wind deity | wind deity | stable |

### Data Sources
- Bilingual glosses: Avestan–Sanskrit translation pairs
- Rigveda verse corpus + Avestan Gatha corpus
- Princeton WordNet + Sanskrit WordNet (for semantic field mapping)
- Historical dictionaries: Mayrhofer's KEWA, Bartholomae's Altiranisches Wörterbuch

### Methods

#### 3.1 Contextual Embedding Comparison
```python
# Use multilingual model to embed cognates in context
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('intfloat/multilingual-e5-base')

# Get embeddings for word in context
sanskrit_context_embs = embed_in_context(word, rigveda_passages)
avestan_context_embs = embed_in_context(cognate, avestan_passages)

# Semantic shift = cosine distance between centroid embeddings
drift_score = 1 - cosine_similarity(
    np.mean(sanskrit_context_embs, axis=0),
    np.mean(avestan_context_embs, axis=0)
)
```

#### 3.2 Semantic Field Classification
- Map each word to a semantic field (divine, demonic, natural, social, military)
- Build word → field classification using Sanskrit/Avestan glossaries
- Compute semantic field overlap between cognate pairs
- Flag reversals (positive field in L1, negative field in L2)

#### 3.3 Collocate Analysis
- Extract top-10 collocates for each cognate in its language corpus
- Compute semantic similarity of collocate sets
- High collocate divergence → semantic drift

#### 3.4 Drift Typology
Classify each cognate pair's semantic relationship:
```
STABLE    → same core meaning in both languages
NARROWED  → broader PII meaning → specific meaning in one
BROADENED → specific PII meaning → broader in one
REVERSED  → opposite valence (good/bad swap)  ← Asura/Daeva
SHIFTED   → different domain (e.g., ritual → everyday)
```

### Output
- `semantic_drift.csv`: cognate pair, drift_type, drift_score, examples
- Scatter plot: drift score vs. phonological distance
- Case study narrative: Asura/Daeva reversal with corpus evidence

---

## Module 4: Integrated Dashboard

### Technology
- **Frontend:** Streamlit
- **Visualization:** Plotly (interactive), NetworkX (cognate trees), Altair
- **Backend:** FastAPI (optional for serving)

### Dashboard Panels

1. **Lexical Explorer**: Search cognates, filter by domain, view similarity scores
2. **Sound Law Map**: Interactive correspondence matrix, click phoneme pair → example words
3. **Semantic Drift Timeline**: Plot cognate pairs by drift score and type
4. **Phylogenetic View**: NetworkX tree showing PII → Avestan/Sanskrit branching
5. **Case Studies**: Deep-dives on Asura/Daeva, Sapta/Hapta, Soma/Haoma

---

## Technical Architecture

```
avestan-sanskrit-linguistics/
├── SPEC.md                        # This document
├── README.md
├── requirements.txt
├── data/
│   ├── raw/
│   │   ├── avestan_corpus.txt     # Avestan texts (transliterated)
│   │   ├── rigveda_corpus.txt     # Vedic Sanskrit texts (IAST)
│   │   ├── cognate_seeds.csv      # Hand-curated seed cognate pairs
│   │   └── sound_law_seeds.json   # Known correspondence rules
│   └── processed/
│       ├── cognates.csv
│       ├── alignments.json
│       └── semantic_drift.csv
├── src/
│   ├── preprocessing/
│   │   ├── transliteration.py    # IAST ↔ IPA, Avestan ↔ IPA converters
│   │   ├── corpus_loader.py      # Load and tokenize corpora
│   │   └── phoneme_mapper.py     # Phoneme inventory mapping
│   ├── lexical/
│   │   ├── cognate_detector.py   # LexStat + embedding-based detection
│   │   ├── similarity_metrics.py # Edit distance, ALINE, LCS
│   │   └── domain_classifier.py  # Semantic domain tagging
│   ├── phonology/
│   │   ├── aligner.py            # ALINE phoneme alignment
│   │   ├── sound_law_miner.py    # Correspondence rule extraction
│   │   └── transducer.py        # (Stretch) seq2seq phoneme model
│   ├── semantics/
│   │   ├── embedding_drift.py    # Contextual embedding comparison
│   │   ├── collocate_analysis.py # Collocate extraction and comparison
│   │   └── drift_classifier.py   # STABLE/REVERSED/SHIFTED labeling
│   └── visualization/
│       ├── network_graph.py      # PII root trees
│       ├── correspondence_heatmap.py
│       └── drift_scatter.py
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_cognate_detection.ipynb
│   ├── 03_sound_laws.ipynb
│   └── 04_semantic_drift.ipynb
├── app/
│   └── dashboard.py              # Streamlit dashboard
└── tests/
    ├── test_cognate_detector.py
    ├── test_sound_law_miner.py
    └── test_semantic_drift.py
```

---

## Key Dependencies

```txt
# Core NLP & Linguistics
lingpy>=2.6.9              # LexStat cognate detection, ALINE alignment
clldutils>=3.12            # CLDF format parsing
pyclts>=3.0                # Cross-Linguistic Transcription Systems

# ML & Embeddings
sentence-transformers>=2.6 # Multilingual embeddings (LaBSE, mE5)
transformers>=4.38         # BERT/GPT for domain classification
torch>=2.2                 # PyTorch backend

# Data Science
pandas>=2.0
numpy>=1.26
scipy>=1.12                # Statistical tests
scikit-learn>=1.4          # Clustering, classification

# Visualization
plotly>=5.19
networkx>=3.2              # Phylogenetic trees
streamlit>=1.32            # Dashboard

# Utilities
pydantic>=2.6              # Data validation
python-Levenshtein>=0.25   # Fast edit distance
```

---

## Data Pipeline

```
Raw Corpora (Avestan, Sanskrit texts)
    ↓
Preprocessing (transliteration → IPA, tokenization)
    ↓ ─────────────────────────────────────────┐
    │                                           │
Cognate Detection                     Corpus Embedding
(LexStat + string metrics)            (multilingual-E5)
    ↓                                           │
Phoneme Alignment (ALINE)         Semantic Field Mapping
    ↓                                           │
Sound Law Mining                   Collocate Extraction
    ↓                                           │
    └─────────────────────────────────────────┘
                         ↓
              Integrated Dataset
              (cognates + phonology + semantics)
                         ↓
                  Dashboard & Reports
```

---

## Evaluation Metrics

| Module | Metric | Target |
|---|---|---|
| Cognate Detection | F1 vs. expert-labeled gold set | ≥ 0.80 |
| Sound Law Mining | Precision on known rules | ≥ 0.90 |
| Semantic Drift | Spearman correlation with expert ratings | ≥ 0.70 |
| Dashboard | Latency per query | < 2s |

### Gold Standard
- Use the **IELEX cognacy database** judgments as ground truth for cognate detection
- Use **Mayrhofer's Etymological Dictionary** for phonological rule validation
- Expert-rated semantic drift scores from published comparative grammar studies

---

## Milestones

| Phase | Deliverable | Key Output |
|---|---|---|
| **Phase 1** (Weeks 1–2) | Data collection & preprocessing | Cleaned corpora, IPA-aligned word lists |
| **Phase 2** (Weeks 3–4) | Lexical Module | `cognates.csv`, domain heatmap |
| **Phase 3** (Weeks 5–6) | Phonological Module | `sound_laws.json`, correspondence matrix |
| **Phase 4** (Weeks 7–8) | Semantic Module | `semantic_drift.csv`, Asura/Daeva case study |
| **Phase 5** (Week 9) | Dashboard integration | Deployed Streamlit app |
| **Phase 6** (Week 10) | Evaluation & report | Metrics report, research write-up |

---

## Key Research Questions

1. What fraction of core vocabulary (Swadesh 200-list items) are cognates between Avestan and Sanskrit?
2. How many distinct phonological correspondence rules can be automatically recovered from cognate data alone?
3. Can the s→h shift be statistically confirmed as a systematic rule vs. random variation?
4. How many cognate pairs show significant semantic drift (drift_score > 0.3)?
5. Is there a correlation between phonological distance and semantic drift — do words that changed sound more also change meaning more?
6. Can we predict the Proto-Indo-Iranian root meaning from the centroid of Avestan and Sanskrit contextual embeddings?

---

## References & Resources

- **Mayrhofer, M.** (1992–2001). *Etymologisches Wörterbuch des Altindoarischen*
- **Bartholomae, C.** (1904). *Altiranisches Wörterbuch*
- **Fortson, B.W.** (2010). *Indo-European Language and Culture: An Introduction*
- **List, J.-M. et al.** (2017). LingPy — A Python library for quantitative tasks in historical linguistics. [lingpy.org](https://lingpy.org)
- **Jäger, G.** (2019). Computational Historical Linguistics. *Theoretical Linguistics*, 45(3-4), 151–182.
- **Cathcart et al.** (2018). Areal pressure in grammatical evolution. *Language Dynamics and Change*
- **CLDF:** Forkel, R. et al. (2018). Cross-Linguistic Data Formats. *Scientific Data*, 5, 180205
- **ASJP:** Wichmann, S. et al. (2020). The ASJP Database (v19)
- **Digital Corpus of Sanskrit (DCS):** [sanskrit.shloka.ru](https://sanskrit.shloka.ru)
- **Avestan Digital Archive (ADA):** University of Salamanca
