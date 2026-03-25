"""
sound_law_miner.py — Extract phonological correspondence rules from aligned cognate pairs.

Mines sound correspondence patterns (like the Sanskrit s → Avestan h shift) from
pairwise phoneme alignments, with chi-squared statistical validation.
"""

import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


class SoundLawMiner:
    """
    Mines sound correspondence rules from pairwise phoneme alignments.

    Given a list of aligned cognate pairs (each alignment is a list of
    (sa_phone, av_phone) tuples), this class builds correspondence matrices
    and extracts statistically supported sound laws.

    Parameters
    ----------
    min_support : float
        Minimum support threshold: count(sa→av) / count(sa) in any pairing.
    min_count : int
        Minimum absolute occurrence count for a rule to be reported.
    positional : bool
        Whether to track positional variants (initial / medial / final).
    """

    def __init__(self, min_support: float = 0.8, min_count: int = 3, positional: bool = True):
        self.min_support = min_support
        self.min_count = min_count
        self.positional = positional

        # (sa_phone, av_phone) -> count
        self.correspondence_matrix: Counter = Counter()
        # (sa_phone, av_phone, position) -> count  where position in {initial, medial, final}
        self.positional_matrix: Counter = Counter()
        # sa_phone -> total count across all pairings (including gap pairings)
        self._sa_totals: Counter = Counter()

        self._fitted = False

    # ------------------------------------------------------------------
    # Fitting
    # ------------------------------------------------------------------

    def fit(self, alignments: list[list[tuple]]) -> "SoundLawMiner":
        """
        Build correspondence and positional matrices from aligned cognate pairs.

        Parameters
        ----------
        alignments : list[list[tuple]]
            Each element is an alignment: a list of (sa_phone, av_phone) pairs.
            '-' is used for gaps. Example:
                [('s','h'), ('a','a'), ('p','p'), ('t','t'), ('a','a')]

        Returns
        -------
        self
        """
        self.correspondence_matrix = Counter()
        self.positional_matrix = Counter()
        self._sa_totals = Counter()

        for alignment in alignments:
            n = len(alignment)
            for idx, (sa_phone, av_phone) in enumerate(alignment):
                # Determine positional label
                if n == 1:
                    position = "initial"
                elif idx == 0:
                    position = "initial"
                elif idx == n - 1:
                    position = "final"
                else:
                    position = "medial"

                self.correspondence_matrix[(sa_phone, av_phone)] += 1
                self._sa_totals[sa_phone] += 1

                if self.positional:
                    self.positional_matrix[(sa_phone, av_phone, position)] += 1

        self._fitted = True
        return self

    # ------------------------------------------------------------------
    # Rule extraction
    # ------------------------------------------------------------------

    def extract_rules(self) -> pd.DataFrame:
        """
        Extract sound correspondence rules that pass support and count thresholds.

        Support for rule (sa → av) is defined as:
            count(sa_phone, av_phone) / count(sa_phone appears in any pairing)

        Returns
        -------
        pd.DataFrame
            Columns: sa_phoneme, av_phoneme, count, support,
                     position_breakdown (dict), rule_string
        """
        if not self._fitted:
            raise RuntimeError("Call fit() before extract_rules().")

        rows = []
        for (sa_phone, av_phone), count in self.correspondence_matrix.items():
            sa_total = self._sa_totals[sa_phone]
            if sa_total == 0:
                continue

            support = count / sa_total

            if support < self.min_support or count < self.min_count:
                continue

            # Build positional breakdown
            position_breakdown: dict[str, int] = {}
            if self.positional:
                for pos in ("initial", "medial", "final"):
                    pos_count = self.positional_matrix.get((sa_phone, av_phone, pos), 0)
                    if pos_count > 0:
                        position_breakdown[pos] = pos_count

            rule_string = f"SA *{sa_phone} → Av. {av_phone}"
            if position_breakdown:
                dominant_pos = max(position_breakdown, key=position_breakdown.get)
                rule_string += f" (dominant: {dominant_pos})"

            rows.append(
                {
                    "sa_phoneme": sa_phone,
                    "av_phoneme": av_phone,
                    "count": count,
                    "support": round(support, 4),
                    "position_breakdown": position_breakdown,
                    "rule_string": rule_string,
                }
            )

        df = pd.DataFrame(
            rows,
            columns=["sa_phoneme", "av_phoneme", "count", "support", "position_breakdown", "rule_string"],
        )
        if not df.empty:
            df = df.sort_values("support", ascending=False).reset_index(drop=True)
        return df

    # ------------------------------------------------------------------
    # Gold-standard validation
    # ------------------------------------------------------------------

    def validate_against_gold(self, gold_rules_path: str) -> dict:
        """
        Compare extracted rules against a gold-standard seed file.

        The JSON file is expected to contain a list of objects with at least
        ``sa_phoneme`` and ``av_phoneme`` keys, e.g.:
            [{"sa_phoneme": "s", "av_phoneme": "h", "description": "..."}, ...]

        Parameters
        ----------
        gold_rules_path : str
            Path to ``sound_law_seeds.json``.

        Returns
        -------
        dict
            precision, recall, f1, recovered_rules (list), missed_rules (list)
        """
        if not self._fitted:
            raise RuntimeError("Call fit() before validate_against_gold().")

        path = Path(gold_rules_path)
        if not path.exists():
            raise FileNotFoundError(f"Gold rules file not found: {gold_rules_path}")

        with path.open("r", encoding="utf-8") as fh:
            gold_data = json.load(fh)

        # Normalise gold rules to (sa, av) tuples
        gold_set: set[tuple[str, str]] = set()
        gold_meta: dict[tuple[str, str], dict] = {}
        for entry in gold_data:
            key = (entry["sa_phoneme"], entry["av_phoneme"])
            gold_set.add(key)
            gold_meta[key] = entry

        # Extracted rules (no threshold filtering here — use whatever was mined)
        extracted_rules = self.extract_rules()
        extracted_set: set[tuple[str, str]] = set(
            zip(extracted_rules["sa_phoneme"], extracted_rules["av_phoneme"])
        )

        true_positives = extracted_set & gold_set
        false_positives = extracted_set - gold_set
        false_negatives = gold_set - extracted_set

        precision = len(true_positives) / len(extracted_set) if extracted_set else 0.0
        recall = len(true_positives) / len(gold_set) if gold_set else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        recovered_rules = [gold_meta[k] for k in sorted(true_positives)]
        missed_rules = [gold_meta[k] for k in sorted(false_negatives)]

        return {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
            "recovered_rules": recovered_rules,
            "missed_rules": missed_rules,
        }

    # ------------------------------------------------------------------
    # Correspondence matrix
    # ------------------------------------------------------------------

    def get_correspondence_matrix(self) -> pd.DataFrame:
        """
        Return a pivot table of (sa_phoneme × av_phoneme) correspondence counts.

        Returns
        -------
        pd.DataFrame
            Rows = Sanskrit phonemes, columns = Avestan phonemes, values = counts.
            Missing combinations are filled with 0.
        """
        if not self._fitted:
            raise RuntimeError("Call fit() before get_correspondence_matrix().")

        if not self.correspondence_matrix:
            return pd.DataFrame()

        records = [
            {"sa_phoneme": sa, "av_phoneme": av, "count": cnt}
            for (sa, av), cnt in self.correspondence_matrix.items()
        ]
        df = pd.DataFrame(records)
        pivot = df.pivot_table(
            index="sa_phoneme",
            columns="av_phoneme",
            values="count",
            aggfunc="sum",
            fill_value=0,
        )
        pivot.columns.name = None
        pivot.index.name = "sa_phoneme"
        return pivot


# ---------------------------------------------------------------------------
# Module-level utilities
# ---------------------------------------------------------------------------


def statistical_validation(correspondence_matrix: pd.DataFrame) -> dict:
    """
    Run chi-squared test and compute Cramér's V on a correspondence matrix.

    Also computes mutual information for the top-5 individual (sa→av) pairs.

    Parameters
    ----------
    correspondence_matrix : pd.DataFrame
        Pivot table as returned by ``SoundLawMiner.get_correspondence_matrix()``.
        Rows = SA phonemes, columns = Avestan phonemes, values = counts.

    Returns
    -------
    dict
        chi2, p_value, cramers_v, specific_pairs (dict mapping pair label → MI).
    """
    if correspondence_matrix.empty:
        return {
            "chi2": float("nan"),
            "p_value": float("nan"),
            "cramers_v": float("nan"),
            "specific_pairs": {},
        }

    matrix_values = correspondence_matrix.values.astype(float)

    # Chi-squared contingency test
    chi2, p_value, dof, expected = stats.chi2_contingency(matrix_values)

    # Cramér's V
    n = matrix_values.sum()
    min_dim = min(matrix_values.shape) - 1
    cramers_v = math.sqrt(chi2 / (n * min_dim)) if (n > 0 and min_dim > 0) else 0.0

    # Mutual information for individual pairs
    # MI(x,y) = p(x,y) * log2( p(x,y) / (p(x)*p(y)) )
    row_totals = matrix_values.sum(axis=1, keepdims=True)
    col_totals = matrix_values.sum(axis=0, keepdims=True)
    total = matrix_values.sum()

    mi_scores: dict[str, float] = {}
    sa_phonemes = list(correspondence_matrix.index)
    av_phonemes = list(correspondence_matrix.columns)

    for i, sa in enumerate(sa_phonemes):
        for j, av in enumerate(av_phonemes):
            count = matrix_values[i, j]
            if count == 0:
                continue
            p_xy = count / total
            p_x = row_totals[i, 0] / total
            p_y = col_totals[0, j] / total
            if p_x > 0 and p_y > 0:
                mi = p_xy * math.log2(p_xy / (p_x * p_y))
                mi_scores[f"{sa}→{av}"] = round(mi, 6)

    # Top-5 by MI
    top5 = dict(
        sorted(mi_scores.items(), key=lambda kv: kv[1], reverse=True)[:5]
    )

    return {
        "chi2": round(float(chi2), 4),
        "p_value": float(p_value),
        "cramers_v": round(cramers_v, 4),
        "specific_pairs": top5,
    }


def bootstrap_rule_support(
    alignments: list[list[tuple]],
    rule_sa: str,
    rule_av: str,
    n_bootstrap: int = 1000,
    random_seed: int = 42,
) -> dict:
    """
    Bootstrap the alignment corpus to estimate support distribution for a rule.

    Resamples ``alignments`` with replacement ``n_bootstrap`` times, refits a
    temporary ``SoundLawMiner`` on each sample, and records the support value
    for the (rule_sa → rule_av) correspondence.

    Parameters
    ----------
    alignments : list[list[tuple]]
        Full alignment corpus.
    rule_sa : str
        Sanskrit phoneme of the rule under test (e.g. ``'s'``).
    rule_av : str
        Avestan phoneme of the rule under test (e.g. ``'h'``).
    n_bootstrap : int
        Number of bootstrap iterations (default 1000).
    random_seed : int
        NumPy random seed for reproducibility.

    Returns
    -------
    dict
        mean, std, ci_lower (2.5th percentile), ci_upper (97.5th percentile).
    """
    rng = np.random.default_rng(random_seed)
    n = len(alignments)
    supports: list[float] = []

    for _ in range(n_bootstrap):
        indices = rng.integers(0, n, size=n)
        sample = [alignments[i] for i in indices]

        miner = SoundLawMiner(min_support=0.0, min_count=0, positional=False)
        miner.fit(sample)

        sa_total = miner._sa_totals[rule_sa]
        if sa_total == 0:
            supports.append(0.0)
        else:
            count = miner.correspondence_matrix.get((rule_sa, rule_av), 0)
            supports.append(count / sa_total)

    arr = np.array(supports)
    return {
        "mean": round(float(arr.mean()), 6),
        "std": round(float(arr.std()), 6),
        "ci_lower": round(float(np.percentile(arr, 2.5)), 6),
        "ci_upper": round(float(np.percentile(arr, 97.5)), 6),
    }
