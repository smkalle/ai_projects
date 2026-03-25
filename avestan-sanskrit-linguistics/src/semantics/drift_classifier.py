"""
drift_classifier.py — Classify semantic drift type for cognate pairs.

Categorizes semantic change into: STABLE, NARROWED, BROADENED, REVERSED, SHIFTED
based on drift scores, semantic field assignments, and collocate analysis.
"""

from __future__ import annotations

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DRIFT_THRESHOLDS: dict[str, float] = {
    'STABLE':    0.15,
    'SHIFTED':   0.30,
    'BROADENED': 0.45,
    'NARROWED':  0.60,
    'REVERSED':  1.01,
}

# English gloss keywords that identify each semantic field.
# Words in Avestan / Sanskrit meanings are matched against these keyword lists.
SEMANTIC_FIELDS: dict[str, list[str]] = {
    'divine': [
        'god', 'divine', 'deity', 'sacred', 'holy', 'worship', 'hymn',
        'prayer', 'ritual', 'heavenly', 'celestial', 'ahura', 'deva',
        'radiant', 'immortal', 'blessed', 'righteous', 'truth', 'asha',
        'rta', 'cosmic order', 'light', 'glory', 'spirit', 'lord',
    ],
    'demonic': [
        'demon', 'evil', 'daeva', 'asura', 'devil', 'wicked', 'malevolent',
        'dark', 'darkness', 'chaos', 'destructive', 'lie', 'druj', 'drug',
        'corrupt', 'impure', 'hostile', 'adversary', 'fiend', 'monster',
        'malign', 'sinful', 'deceitful', 'treacherous',
    ],
    'natural': [
        'fire', 'water', 'earth', 'sky', 'sun', 'moon', 'star', 'wind',
        'rain', 'river', 'mountain', 'tree', 'forest', 'animal', 'horse',
        'cow', 'plant', 'stone', 'sea', 'storm', 'lightning', 'cloud',
        'night', 'day', 'season', 'spring', 'winter', 'summer', 'autumn',
    ],
    'military': [
        'war', 'battle', 'warrior', 'weapon', 'sword', 'spear', 'arrow',
        'shield', 'army', 'victory', 'conquest', 'enemy', 'hero', 'fight',
        'combat', 'strength', 'power', 'force', 'attack', 'defend',
        'guard', 'protect', 'soldier', 'chariot', 'bow',
    ],
    'kinship': [
        'father', 'mother', 'son', 'daughter', 'brother', 'sister',
        'husband', 'wife', 'family', 'clan', 'tribe', 'ancestor', 'child',
        'parent', 'offspring', 'lineage', 'descendant', 'kinsman', 'kin',
        'household', 'birth', 'born', 'uncle', 'aunt', 'cousin',
    ],
    'agricultural': [
        'grain', 'field', 'harvest', 'sow', 'crop', 'plow', 'cattle',
        'herd', 'pasture', 'farm', 'seed', 'barley', 'wheat', 'rice',
        'cultivate', 'soil', 'irrigation', 'flock', 'shepherd',
        'fertile', 'abundance', 'food', 'bread', 'grow', 'yield',
    ],
}

# Pairs of semantic fields considered to be of opposite polarity.
_OPPOSITE_POLARITY: set[frozenset[str]] = {
    frozenset({'divine', 'demonic'}),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _assign_semantic_field(meaning: str) -> str | None:
    """Return the best-matching semantic field for *meaning*, or None."""
    if not meaning:
        return None
    meaning_lower = meaning.lower()
    best_field: str | None = None
    best_count: int = 0
    for field, keywords in SEMANTIC_FIELDS.items():
        count = sum(1 for kw in keywords if kw in meaning_lower)
        if count > best_count:
            best_count = count
            best_field = field
    return best_field if best_count > 0 else None


def _fields_are_opposite_polarity(field_av: str | None, field_sa: str | None) -> bool:
    """Return True when the two fields form an explicitly opposite-polarity pair."""
    if field_av is None or field_sa is None:
        return False
    return frozenset({field_av, field_sa}) in _OPPOSITE_POLARITY


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def classify_drift(
    drift_score: float,
    meaning_av: str,
    meaning_sa: str,
) -> str:
    """Classify the semantic drift type for a cognate pair.

    Parameters
    ----------
    drift_score:
        Numeric drift score, typically in [0.0, 1.0].
    meaning_av:
        English gloss / meaning of the Avestan word.
    meaning_sa:
        English gloss / meaning of the Sanskrit word.

    Returns
    -------
    str
        One of: ``'STABLE'``, ``'SHIFTED'``, ``'BROADENED'``, ``'NARROWED'``,
        ``'REVERSED'``.

    Notes
    -----
    If the Avestan and Sanskrit meanings map to opposite-polarity semantic
    fields (e.g. *divine* vs *demonic*), the function returns ``'REVERSED'``
    regardless of the numeric drift score, reflecting the well-known
    Avestan *daeva* / Vedic *deva* inversion.
    """
    field_av = _assign_semantic_field(meaning_av)
    field_sa = _assign_semantic_field(meaning_sa)

    if _fields_are_opposite_polarity(field_av, field_sa):
        return 'REVERSED'

    # Fall back to threshold-based classification (ordered from lowest to highest).
    if drift_score <= DRIFT_THRESHOLDS['STABLE']:
        return 'STABLE'
    if drift_score <= DRIFT_THRESHOLDS['SHIFTED']:
        return 'SHIFTED'
    if drift_score <= DRIFT_THRESHOLDS['BROADENED']:
        return 'BROADENED'
    if drift_score <= DRIFT_THRESHOLDS['NARROWED']:
        return 'NARROWED'
    return 'REVERSED'


# ---------------------------------------------------------------------------
# DriftClassifier
# ---------------------------------------------------------------------------

class DriftClassifier:
    """Classify semantic drift for a DataFrame of cognate pairs.

    The classifier operates on a DataFrame that must contain at least the
    columns ``drift_score``, ``meaning_av``, and ``meaning_sa``.  It adds
    four new columns and, optionally, evaluates against gold-standard labels.

    Examples
    --------
    >>> clf = DriftClassifier()
    >>> enriched = clf.fit_transform(cognates_df)
    >>> metrics = clf.evaluate(enriched)
    """

    # Required input columns.
    _REQUIRED_COLS = {'drift_score', 'meaning_av', 'meaning_sa'}

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add drift-classification columns to *df* and return a copy.

        Added columns
        -------------
        drift_type : str
            One of STABLE / SHIFTED / BROADENED / NARROWED / REVERSED.
        semantic_field_av : str or None
            Best-matching semantic field for the Avestan meaning.
        semantic_field_sa : str or None
            Best-matching semantic field for the Sanskrit meaning.
        is_reversal : bool
            True when the two fields are of opposite polarity.

        Parameters
        ----------
        df:
            Input DataFrame.  Must contain ``drift_score``, ``meaning_av``,
            and ``meaning_sa`` columns.

        Returns
        -------
        pd.DataFrame
            A copy of *df* with the four new columns appended.

        Raises
        ------
        ValueError
            If any required columns are missing.
        """
        missing = self._REQUIRED_COLS - set(df.columns)
        if missing:
            raise ValueError(
                f"Input DataFrame is missing required columns: {sorted(missing)}"
            )

        out = df.copy()

        out['semantic_field_av'] = out['meaning_av'].apply(_assign_semantic_field)
        out['semantic_field_sa'] = out['meaning_sa'].apply(_assign_semantic_field)

        out['is_reversal'] = out.apply(
            lambda row: _fields_are_opposite_polarity(
                row['semantic_field_av'], row['semantic_field_sa']
            ),
            axis=1,
        )

        out['drift_type'] = out.apply(
            lambda row: classify_drift(
                row['drift_score'],
                row['meaning_av'],
                row['meaning_sa'],
            ),
            axis=1,
        )

        return out

    def evaluate(
        self,
        df: pd.DataFrame,
        gold_col: str = 'drift_type',
    ) -> dict:
        """Evaluate predictions against gold-standard labels.

        Parameters
        ----------
        df:
            DataFrame that *already contains* both a ``drift_type`` column
            (predicted, produced by :meth:`fit_transform`) and a gold-standard
            column (default ``'drift_type'``).  When the gold column name
            equals the predicted column name the method cannot operate — pass
            a DataFrame that retains the original gold labels in a separate
            column, e.g. ``'drift_type_gold'``.

        gold_col:
            Name of the column containing gold-standard drift labels.  When
            loading from ``cognate_seeds.csv`` this is typically ``'drift_type'``
            on the raw file; after :meth:`fit_transform` the predicted labels
            overwrite that column, so callers should rename before calling
            this method if they wish to compare.

        Returns
        -------
        dict
            ``{'accuracy': float, 'confusion_matrix': np.ndarray,
               'labels': list[str], 'n_samples': int}``
            Returns an empty dict with a ``'warning'`` key when gold labels
            are not available.
        """
        pred_col = 'drift_type'

        # Determine whether usable gold labels exist.
        if gold_col not in df.columns:
            return {'warning': f"Gold column '{gold_col}' not found in DataFrame."}

        if gold_col == pred_col:
            return {
                'warning': (
                    "Gold column and predicted column share the same name "
                    f"('{gold_col}'). Rename one before calling evaluate()."
                )
            }

        if pred_col not in df.columns:
            return {'warning': f"Predicted column '{pred_col}' not found. Run fit_transform() first."}

        valid = df[[gold_col, pred_col]].dropna()
        if valid.empty:
            return {'warning': 'No non-null rows available for evaluation.'}

        y_true = valid[gold_col].tolist()
        y_pred = valid[pred_col].tolist()

        labels = sorted(set(y_true) | set(y_pred))
        cm = confusion_matrix(y_true, y_pred, labels=labels)
        acc = accuracy_score(y_true, y_pred)

        return {
            'accuracy': acc,
            'confusion_matrix': cm,
            'labels': labels,
            'n_samples': len(valid),
        }
