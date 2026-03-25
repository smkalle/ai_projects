"""
aligner.py — Phoneme-level alignment using ALINE algorithm via lingpy.

Provides clean wrappers around lingpy's alignment functions with graceful
fallback to simple Levenshtein alignment when lingpy is unavailable.
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional lingpy import
# ---------------------------------------------------------------------------

try:
    from lingpy.align.pairwise import pw_align as _lingpy_pw_align  # type: ignore
    _LINGPY_AVAILABLE = True
    logger.debug("lingpy loaded successfully; using ALINE algorithm for alignment.")
except ImportError:  # pragma: no cover
    _LINGPY_AVAILABLE = False
    logger.warning(
        "lingpy is not installed. Falling back to simple Levenshtein alignment. "
        "Install lingpy for linguistically informed phoneme alignment."
    )

_GAP = "-"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _tokenise(ipa_string: str) -> list[str]:
    """
    Split an IPA string into a list of phoneme tokens.

    Handles simple IPA by treating each character as a phoneme, but keeps
    common multi-character digraphs (tʃ, dʒ, ts, dz, pf, tɕ, dʑ) intact and
    preserves length marks (ː) and diacritics attached to the preceding base.

    For production use, replace with a dedicated IPA tokeniser such as
    ``ipapy`` or ``lingpy.sequence.sound_classes.ipa2tokens``.
    """
    if not ipa_string:
        return []

    # Attempt lingpy tokenisation first — it handles IPA properly
    if _LINGPY_AVAILABLE:
        try:
            from lingpy.sequence.sound_classes import ipa2tokens  # type: ignore
            return list(ipa2tokens(ipa_string, merge_vowels=False))
        except Exception:
            pass

    # Fallback: character-by-character with diacritic merging
    tokens: list[str] = []
    diacritics = set("ʰʷʲʼːˑ̥̬̹̞̠̟̝̘̙̤̰̺̻̼̈̃͜͡")
    for char in ipa_string:
        if tokens and char in diacritics:
            tokens[-1] += char
        else:
            tokens.append(char)
    return tokens


def _levenshtein_align(seq1: list[str], seq2: list[str]) -> list[tuple[str, str]]:
    """
    Produce a pairwise alignment via simple edit-distance dynamic programming.

    Costs: match=0, substitution=1, gap=1.  When there are ties the algorithm
    prefers substitutions over gaps (standard Needleman–Wunsch behaviour).

    Parameters
    ----------
    seq1, seq2 : list[str]
        Tokenised phoneme sequences.

    Returns
    -------
    list[tuple[str, str]]
        Aligned pairs; gap positions marked with ``'-'``.
    """
    m, n = len(seq1), len(seq2)
    # DP table
    dp: list[list[int]] = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if seq1[i - 1] == seq2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j - 1] + cost,   # substitution / match
                dp[i - 1][j] + 1,           # delete from seq1
                dp[i][j - 1] + 1,           # insert into seq1
            )

    # Traceback
    alignment: list[tuple[str, str]] = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            cost = 0 if seq1[i - 1] == seq2[j - 1] else 1
            if dp[i][j] == dp[i - 1][j - 1] + cost:
                alignment.append((seq1[i - 1], seq2[j - 1]))
                i -= 1
                j -= 1
                continue
        if i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            alignment.append((seq1[i - 1], _GAP))
            i -= 1
        else:
            alignment.append((_GAP, seq2[j - 1]))
            j -= 1

    alignment.reverse()
    return alignment


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def align_word_pair(word1_ipa: str, word2_ipa: str) -> list[tuple[str, str]]:
    """
    Align two IPA transcriptions at the phoneme level.

    Attempts to use lingpy's ALINE-based pairwise aligner first.  If lingpy is
    unavailable or raises an exception, falls back to a simple Levenshtein
    (Needleman–Wunsch) alignment.

    Parameters
    ----------
    word1_ipa : str
        IPA transcription of the first word (treated as Sanskrit / source).
    word2_ipa : str
        IPA transcription of the second word (treated as Avestan / target).

    Returns
    -------
    list[tuple[str, str]]
        List of (phone1, phone2) pairs.  ``'-'`` indicates a gap.
    """
    if not word1_ipa and not word2_ipa:
        return []

    tokens1 = _tokenise(word1_ipa)
    tokens2 = _tokenise(word2_ipa)

    if _LINGPY_AVAILABLE:
        try:
            # lingpy pw_align returns two aligned sequences as lists
            aligned1, aligned2, _ = _lingpy_pw_align(
                tokens1, tokens2, distance=False
            )
            return list(zip(aligned1, aligned2))
        except Exception as exc:
            logger.debug(
                "lingpy alignment failed for (%r, %r): %s — using fallback.",
                word1_ipa, word2_ipa, exc,
            )

    return _levenshtein_align(tokens1, tokens2)


def align_all_cognates(
    df: pd.DataFrame,
    av_ipa_col: str = "av_ipa",
    sa_ipa_col: str = "sa_ipa",
) -> list[list[tuple]]:
    """
    Align every cognate pair in a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain at least the two IPA columns specified.
    av_ipa_col : str
        Column name for Avestan IPA transcriptions.
    sa_ipa_col : str
        Column name for Sanskrit IPA transcriptions.

    Returns
    -------
    list[list[tuple]]
        One alignment list per row; inner tuples are (sa_phone, av_phone).
    """
    required = {av_ipa_col, sa_ipa_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {missing}")

    alignments: list[list[tuple]] = []
    for _, row in df.iterrows():
        sa_ipa = str(row[sa_ipa_col]) if pd.notna(row[sa_ipa_col]) else ""
        av_ipa = str(row[av_ipa_col]) if pd.notna(row[av_ipa_col]) else ""
        alignment = align_word_pair(sa_ipa, av_ipa)
        alignments.append(alignment)

    return alignments


def format_alignment(
    alignment: list[tuple[str, str]],
    word1: str,
    word2: str,
) -> str:
    """
    Format an alignment as a human-readable three-line string.

    Example output::

        s  a  p  t  a
        |  |  |  |  |
        h  a  p  t  a

    Gap characters (``'-'``) are displayed literally so the column structure
    remains clear.

    Parameters
    ----------
    alignment : list[tuple[str, str]]
        Aligned pairs as returned by :func:`align_word_pair`.
    word1 : str
        Label / original form for the top row (e.g. Sanskrit word).
    word2 : str
        Label / original form for the bottom row (e.g. Avestan word).

    Returns
    -------
    str
        Multi-line formatted alignment string (no trailing newline).
    """
    if not alignment:
        return f"{word1}\n|\n{word2}"

    # Column width = max(len(phone1), len(phone2), 1) + 1 padding
    col_widths = [max(len(p1), len(p2), 1) for p1, p2 in alignment]

    top_row = "  ".join(p1.center(w) for (p1, _), w in zip(alignment, col_widths))
    mid_row = "  ".join("|".center(w) for w in col_widths)
    bot_row = "  ".join(p2.center(w) for (_, p2), w in zip(alignment, col_widths))

    header = f"[{word1}] ↔ [{word2}]"
    return f"{header}\n{top_row}\n{mid_row}\n{bot_row}"


def extract_phoneme_pairs(
    alignments: list[list[tuple]],
    exclude_gaps: bool = True,
) -> list[tuple[str, str]]:
    """
    Flatten all alignments into a single list of (sa_phone, av_phone) pairs.

    Parameters
    ----------
    alignments : list[list[tuple]]
        Output of :func:`align_all_cognates` or :func:`align_word_pair`.
    exclude_gaps : bool
        If ``True`` (default), pairs where either element is ``'-'`` are
        discarded.

    Returns
    -------
    list[tuple[str, str]]
        Flat list of phoneme correspondences.
    """
    pairs: list[tuple[str, str]] = []
    for alignment in alignments:
        for sa_phone, av_phone in alignment:
            if exclude_gaps and (_GAP in (sa_phone, av_phone)):
                continue
            pairs.append((sa_phone, av_phone))
    return pairs
