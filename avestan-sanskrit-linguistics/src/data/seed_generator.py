"""
seed_generator.py — Generate synthetic seed corpora for offline tutorial use.

Produces deterministic (seeded) synthetic mini-corpora for Avestan and Sanskrit
that demonstrate the key linguistic phenomena (especially the Asura/Daeva reversal
and the s→h phonological shift) without requiring licensed corpus data.

IMPORTANT: These corpora are for method demonstration only.
Real research requires actual Avestan and Vedic Sanskrit texts.
"""

from __future__ import annotations

import csv
import io
import random
from pathlib import Path

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Minimal fallback cognate seed data (used when CSV is absent)
# ---------------------------------------------------------------------------

_FALLBACK_COGNATE_ROWS = [
    # avestan_word, sanskrit_word, pii_root, domain, meaning_av, meaning_sa,
    # expert_cognate_label, manual_drift_score, drift_type
    ("ahura",    "asura",   "*asura-",   "religion", "lord (benevolent)",          "demon (malevolent)",         True,  0.95, "REVERSED"),
    ("daeva",    "deva",    "*daiwá-",   "religion", "demon (evil spirit)",         "god (deity)",                True,  0.95, "REVERSED"),
    ("haoma",    "soma",    "*sauma-",   "religion", "sacred ritual plant/drink",   "sacred ritual plant/drink",  True,  0.25, "SHIFTED"),
    ("ātar",     "atharva", "*āθr-",     "religion", "fire (sacred)",               "fire priest/fire",           True,  0.30, "SHIFTED"),
    ("aša",      "ṛta",     "*Hr̥tá-",   "religion", "cosmic truth/order",          "cosmic truth/order",         True,  0.10, "STABLE"),
    ("mazdā",    "medhā",   "*mazdha-",  "religion", "wisdom (divine)",             "wisdom/intelligence",        True,  0.10, "STABLE"),
    ("yazata",   "yajata",  "*yaz-",     "religion", "worthy of worship",           "worthy of worship",          True,  0.00, "STABLE"),
    ("hapta",    "sapta",   "*saptá",    "numbers",  "seven",                       "seven",                      True,  0.00, "STABLE"),
    ("nava",     "nava",    "*náwa-",    "numbers",  "nine",                        "nine",                       True,  0.00, "STABLE"),
    ("dasa",     "daśa",    "*daśa-",    "numbers",  "ten",                         "ten",                        True,  0.00, "STABLE"),
    ("pitar",    "pitṛ",    "*pitár-",   "kinship",  "father",                      "father",                     True,  0.00, "STABLE"),
    ("mātar",    "mātṛ",    "*mātár-",   "kinship",  "mother",                      "mother",                     True,  0.00, "STABLE"),
    ("brātar",   "bhrātṛ",  "*bhrātar-", "kinship",  "brother",                     "brother",                    True,  0.00, "STABLE"),
    ("puθra",    "putra",   "*putra-",   "kinship",  "son",                         "son",                        True,  0.00, "STABLE"),
    ("aspa",     "aśva",    "*aćwa-",    "warfare",  "horse",                       "horse",                      True,  0.00, "STABLE"),
    ("xšaθra",   "kṣatra",  "*xšatram",  "warfare",  "dominion/rule",               "warrior power/rule",         True,  0.10, "STABLE"),
    ("vīra",     "vīra",    "*wīra-",    "warfare",  "warrior/hero",                "warrior/hero",               True,  0.00, "STABLE"),
    ("gao",      "go",      "*gwáw-",    "animals",  "cow",                         "cow",                        True,  0.00, "STABLE"),
    ("yava",     "yava",    "*yáwa-",    "agriculture", "grain/barley",             "grain/barley",               True,  0.00, "STABLE"),
    ("vāyu",     "vāyu",    "*wāyu-",    "nature",   "wind (divine)",               "wind/god of wind",           True,  0.05, "STABLE"),
]

_FALLBACK_COLUMNS = [
    "avestan_word", "sanskrit_word", "pii_root", "domain",
    "meaning_av", "meaning_sa", "expert_cognate_label",
    "manual_drift_score", "drift_type",
]

# ---------------------------------------------------------------------------
# Avestan vocabulary pools (transliteration)
# ---------------------------------------------------------------------------

# Theologically charged terms that cluster around ahura (divine/wisdom)
_AV_AHURA_CONTEXT = ["mazdā", "xšaθra", "aša", "vohu", "manah", "yazata", "spəṇta"]
# Terms that cluster around daēva (demonic/impure)
_AV_DAEVA_CONTEXT = ["drug", "aŋra", "nasu", "dušita", "druj", "aēšma"]

# Supplemental vocabulary by domain
_AV_RITUAL  = ["haoma", "ātar", "yasna", "gāθā", "manthra", "nāman", "zaraθuštra"]
_AV_NATURE  = ["vāyu", "āp", "raocah", "asman", "zam", "vāta", "bāmya"]
_AV_KINSHIP = ["pitar", "mātar", "brātar", "puθra", "napāt", "xvaŋhar"]
_AV_WARFARE = ["aspa", "vīra", "xšaθra", "aēša", "dāθra", "ərəzu"]
_AV_NUMBERS = ["aēva", "dva", "θri", "caθru", "panca", "hapta", "ašta", "nava", "dasa"]
_AV_ANIMALS = ["gao", "spā", "mərəγa", "uštra", "maēša", "xara"]
_AV_GENERIC = _AV_RITUAL + _AV_NATURE + _AV_KINSHIP + _AV_WARFARE + _AV_ANIMALS

# Avestan sentence templates — slot types: {AHURA_CTX}, {DAEVA_CTX}, {GEN}, {NUM}
_AV_TEMPLATES = [
    # Templates featuring ahura in divine context
    "ahura {A} {A} {G} aša",
    "ahura mazdā {A} {G} {G}",
    "{A} ahura {A} xšaθra {G}",
    "ahura {A} vohu manah {G}",
    "zaraθuštra ahura mazdā {A} {G}",
    "yasna ahura {A} {G} aša",
    "{G} ahura mazdā {A} {A}",
    "ahura mazdā spəṇta {A} {G}",
    # Templates featuring daēva in demonic context
    "daēva {D} {D} {G} drug",
    "aŋra mainyu daēva {D} {G}",
    "{D} daēva {D} nasu {G}",
    "daēva drug {D} {G} {G}",
    "{G} daēva {D} aēšma {D}",
    "druj daēva {D} {G} nasu",
    # Neutral / nature / ritual templates
    "{G} {G} aša {G} yazata",
    "haoma {G} {G} ātar {G}",
    "{G} vāyu āp {G} asman",
    "gāθā {G} {G} manthra {G}",
    "{G} pitar mātar {G} puθra",
    "{N} aspa {G} vīra {G}",
]

# ---------------------------------------------------------------------------
# Sanskrit vocabulary pools (transliteration)
# ---------------------------------------------------------------------------

# Terms that cluster around deva (divine/ritual)
_SA_DEVA_CONTEXT  = ["brahman", "ṛta", "soma", "yajña", "ṛṣi", "mantra", "sura"]
# Terms that cluster around asura in its late (demonic) sense
_SA_ASURA_NEG_CTX = ["rakṣasa", "dānava", "māyā", "andha", "dambha", "tamas"]
# Early Rigvedic positive asura context (lord/powerful)
_SA_ASURA_POS_CTX = ["bala", "śakti", "prabhava", "mahā", "tejas"]

_SA_RITUAL  = ["soma", "yajña", "mantra", "ṛta", "brahman", "ṛṣi", "agni", "havana"]
_SA_NATURE  = ["vāyu", "āpa", "bhānu", "aśman", "kṣam", "vāta", "ākāśa"]
_SA_KINSHIP = ["pitṛ", "mātṛ", "bhrātṛ", "putra", "napāt", "svasar"]
_SA_WARFARE = ["aśva", "vīra", "kṣatra", "iṣu", "dātra", "ṛju"]
_SA_NUMBERS = ["eka", "dvi", "tri", "catur", "pañca", "sapta", "aṣṭa", "nava", "daśa"]
_SA_ANIMALS = ["go", "śvan", "mṛga", "uṣṭra", "meṣa", "khara"]
_SA_GENERIC = _SA_RITUAL + _SA_NATURE + _SA_KINSHIP + _SA_WARFARE + _SA_ANIMALS

# Sanskrit sentence templates
_SA_TEMPLATES = [
    # Templates featuring deva in divine context
    "deva {V} {V} {G} ṛta",
    "deva brahman {V} {G} {G}",
    "{V} deva {V} yajña {G}",
    "deva {V} soma mantra {G}",
    "ṛṣi deva brahman {V} {G}",
    "soma deva {V} {G} ṛta",
    "{G} deva brahman {V} {V}",
    "deva agni {V} ṛta {G}",
    # Templates featuring asura in late (demonic) context
    "asura {N} {N} {G} rakṣasa",
    "asura dānava {N} {G} {G}",
    "{N} asura {N} māyā {G}",
    "asura rakṣasa {N} tamas {G}",
    "{G} asura {N} andha {N}",
    # Templates featuring asura in early (positive) Rigvedic context
    "asura {P} {P} {G} mahā",
    "{P} asura bala śakti {G}",
    "asura {P} tejas {G} prabhava",
    # Neutral / nature / ritual templates
    "{G} {G} ṛta {G} yajña",
    "soma {G} {G} agni {G}",
    "{G} vāyu āpa {G} aśman",
    "mantra {G} {G} ṛṣi {G}",
    "{G} pitṛ mātṛ {G} putra",
    "{N2} aśva {G} vīra {G}",
]


class SeedGenerator:
    """Generate deterministic synthetic mini-corpora for Avestan and Sanskrit."""

    def __init__(self, random_seed: int = 42) -> None:
        self.random_seed = random_seed
        random.seed(random_seed)
        np.random.seed(random_seed)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fill_av_template(self, template: str, rng: random.Random) -> str:
        """Replace slot markers in an Avestan template with random vocabulary."""
        result = template
        while "{A}" in result:
            result = result.replace("{A}", rng.choice(_AV_AHURA_CONTEXT), 1)
        while "{D}" in result:
            result = result.replace("{D}", rng.choice(_AV_DAEVA_CONTEXT), 1)
        while "{G}" in result:
            result = result.replace("{G}", rng.choice(_AV_GENERIC), 1)
        while "{N}" in result:
            result = result.replace("{N}", rng.choice(_AV_NUMBERS), 1)
        return result

    def _fill_sa_template(
        self, template: str, rng: random.Random, asura_positive: bool = False
    ) -> str:
        """Replace slot markers in a Sanskrit template with random vocabulary."""
        result = template
        while "{V}" in result:
            result = result.replace("{V}", rng.choice(_SA_DEVA_CONTEXT), 1)
        if asura_positive:
            while "{N}" in result:
                result = result.replace("{N}", rng.choice(_SA_ASURA_POS_CTX), 1)
        else:
            while "{N}" in result:
                result = result.replace("{N}", rng.choice(_SA_ASURA_NEG_CTX), 1)
        while "{P}" in result:
            result = result.replace("{P}", rng.choice(_SA_ASURA_POS_CTX), 1)
        while "{G}" in result:
            result = result.replace("{G}", rng.choice(_SA_GENERIC), 1)
        while "{N2}" in result:
            result = result.replace("{N2}", rng.choice(_SA_NUMBERS), 1)
        return result

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_cognate_seeds(
        self, output_path: str | Path | None = None
    ) -> pd.DataFrame:
        """Load cognate seeds from CSV if available, otherwise build in-memory.

        Parameters
        ----------
        output_path:
            If provided, the DataFrame is saved to this path as CSV.

        Returns
        -------
        pd.DataFrame
            Cognate seed table with columns matching cognate_seeds.csv schema.
        """
        default_csv = Path("data/raw/cognate_seeds.csv")
        if default_csv.exists():
            df = pd.read_csv(default_csv)
        else:
            df = pd.DataFrame(_FALLBACK_COGNATE_ROWS, columns=_FALLBACK_COLUMNS)

        if output_path is not None:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(out, index=False)

        return df

    def generate_avestan_corpus(
        self,
        n_sentences: int = 50,
        output_path: str | Path | None = None,
    ) -> list[str]:
        """Generate synthetic Avestan sentences with deliberate collocate patterns.

        Collocate guarantees
        --------------------
        - ``ahura`` always appears with at least one of:
          mazdā, xšaθra, aša, vohu, manah, yazata, spəṇta.
        - ``daēva`` always appears with at least one of:
          drug, aŋra, nasu, dušita, druj, aēšma.

        Sentences are 5–12 tokens long, template-based, and use the
        transliterated vocabulary from cognate_seeds.csv.

        Parameters
        ----------
        n_sentences:
            Number of synthetic sentences to generate.
        output_path:
            If provided, sentences are written one-per-line to this path.

        Returns
        -------
        list[str]
            Synthetic Avestan sentences.
        """
        rng = random.Random(self.random_seed)

        # Separate templates by type for controlled sampling
        ahura_templates = [t for t in _AV_TEMPLATES if "ahura" in t]
        daeva_templates = [t for t in _AV_TEMPLATES if "daēva" in t or "daeva" in t.lower()]
        neutral_templates = [
            t for t in _AV_TEMPLATES
            if "ahura" not in t and "daēva" not in t and "daeva" not in t.lower()
        ]

        # Ensure at least 30% ahura sentences, 30% daēva sentences
        n_ahura  = max(1, int(n_sentences * 0.30))
        n_daeva  = max(1, int(n_sentences * 0.30))
        n_neutral = n_sentences - n_ahura - n_daeva

        sentences: list[str] = []

        for _ in range(n_ahura):
            tmpl = rng.choice(ahura_templates)
            sentences.append(self._fill_av_template(tmpl, rng))

        for _ in range(n_daeva):
            tmpl = rng.choice(daeva_templates)
            sentences.append(self._fill_av_template(tmpl, rng))

        for _ in range(n_neutral):
            tmpl = rng.choice(neutral_templates)
            sentences.append(self._fill_av_template(tmpl, rng))

        rng.shuffle(sentences)

        if output_path is not None:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text("\n".join(sentences) + "\n", encoding="utf-8")

        return sentences

    def generate_sanskrit_corpus(
        self,
        n_sentences: int = 50,
        output_path: str | Path | None = None,
    ) -> list[str]:
        """Generate synthetic Sanskrit sentences with deliberate collocate patterns.

        Collocate guarantees
        --------------------
        - ``deva`` always appears with at least one of:
          brahman, ṛta, soma, yajña, ṛṣi, mantra, sura.
        - ``asura`` (late, demonic sense): appears with at least one of:
          rakṣasa, dānava, māyā, andha.
        - ``asura`` (early Rigvedic, positive sense, ~30% of asura sentences):
          appears with at least one of: bala, śakti, prabhava, mahā, tejas.

        Parameters
        ----------
        n_sentences:
            Number of synthetic sentences to generate.
        output_path:
            If provided, sentences are written one-per-line to this path.

        Returns
        -------
        list[str]
            Synthetic Sanskrit sentences.
        """
        rng = random.Random(self.random_seed + 1)  # distinct stream from Avestan

        deva_templates  = [t for t in _SA_TEMPLATES if "deva" in t and "asura" not in t]
        asura_neg_templates = [
            t for t in _SA_TEMPLATES
            if "asura" in t and "{N}" in t and "{P}" not in t
        ]
        asura_pos_templates = [
            t for t in _SA_TEMPLATES
            if "asura" in t and "{P}" in t
        ]
        neutral_templates = [
            t for t in _SA_TEMPLATES
            if "deva" not in t and "asura" not in t
        ]

        n_deva = max(1, int(n_sentences * 0.30))
        # 30% of asura sentences use the early positive sense, 70% late demonic
        n_asura_total = max(2, int(n_sentences * 0.30))
        n_asura_pos = max(1, int(n_asura_total * 0.30))
        n_asura_neg = n_asura_total - n_asura_pos
        n_neutral = n_sentences - n_deva - n_asura_total

        sentences: list[str] = []

        for _ in range(n_deva):
            tmpl = rng.choice(deva_templates)
            sentences.append(self._fill_sa_template(tmpl, rng))

        for _ in range(n_asura_neg):
            tmpl = rng.choice(asura_neg_templates)
            sentences.append(self._fill_sa_template(tmpl, rng, asura_positive=False))

        for _ in range(n_asura_pos):
            tmpl = rng.choice(asura_pos_templates)
            sentences.append(self._fill_sa_template(tmpl, rng, asura_positive=True))

        for _ in range(n_neutral):
            tmpl = rng.choice(neutral_templates)
            sentences.append(self._fill_sa_template(tmpl, rng))

        rng.shuffle(sentences)

        if output_path is not None:
            out = Path(output_path)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text("\n".join(sentences) + "\n", encoding="utf-8")

        return sentences

    def save_all(self, output_dir: str | Path) -> None:
        """Save both synthetic corpora and cognate seeds to *output_dir*.

        Files written
        -------------
        - ``<output_dir>/cognate_seeds.csv``
        - ``<output_dir>/avestan_corpus.txt``
        - ``<output_dir>/sanskrit_corpus.txt``

        Parameters
        ----------
        output_dir:
            Target directory (created if necessary).
        """
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        self.generate_cognate_seeds(output_path=out / "cognate_seeds.csv")
        self.generate_avestan_corpus(output_path=out / "avestan_corpus.txt")
        self.generate_sanskrit_corpus(output_path=out / "sanskrit_corpus.txt")

        print(f"Seed data written to: {out.resolve()}")
        print(f"  cognate_seeds.csv   — {len(self.generate_cognate_seeds())} pairs")
        print(f"  avestan_corpus.txt  — 50 synthetic sentences")
        print(f"  sanskrit_corpus.txt — 50 synthetic sentences")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    generator = SeedGenerator(random_seed=42)
    generator.save_all("data/raw")
