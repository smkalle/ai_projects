"""
collocate_analysis.py — Extract and compare collocate sets for cognate words.

Provides utilities for computing token-window collocates from raw text corpora
and comparing collocate profiles between Avestan and Sanskrit attestations of
Proto-Indo-Iranian cognate pairs.
"""

from __future__ import annotations

import re
from collections import Counter


# ---------------------------------------------------------------------------
# Tokenisation helper
# ---------------------------------------------------------------------------

def _tokenise(text: str) -> list[str]:
    """Lower-case and split *text* into word tokens, stripping punctuation."""
    return re.findall(r"[^\W\d_]+", text.lower())


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_collocates(
    word: str,
    corpus: list[str],
    window: int = 3,
    top_n: int = 10,
) -> dict[str, int]:
    """Extract the most frequent collocates of *word* from *corpus*.

    For every passage in *corpus* that contains *word*, the function collects
    the tokens within a symmetric ±*window* token window around each
    occurrence of *word* (the node word itself is excluded).  The resulting
    frequency counts are returned, capped at *top_n* entries.

    Parameters
    ----------
    word:
        The node word to search for.  Matching is case-insensitive and is
        performed on whole tokens (not substrings).
    corpus:
        List of strings, each representing one passage / sentence / line.
    window:
        Number of tokens to include on each side of the node word.
    top_n:
        Maximum number of collocates to return (most frequent first).

    Returns
    -------
    dict[str, int]
        Mapping of collocate token → frequency, sorted descending by
        frequency and truncated to *top_n* entries.  Returns an empty dict
        when *word* is not found in any passage.

    Examples
    --------
    >>> av_corpus = ["ahura mazda asha vohu manah", "asha vahishta mazda"]
    >>> extract_collocates("asha", av_corpus, window=2, top_n=5)
    {'mazda': 2, 'ahura': 1, 'vohu': 1, 'vahishta': 1}
    """
    word_lower = word.lower()
    freq: Counter[str] = Counter()

    for passage in corpus:
        tokens = _tokenise(passage)
        for idx, token in enumerate(tokens):
            if token != word_lower:
                continue
            start = max(0, idx - window)
            end = min(len(tokens), idx + window + 1)
            for neighbour in tokens[start:end]:
                if neighbour != word_lower:
                    freq[neighbour] += 1

    return dict(freq.most_common(top_n))


def jaccard_similarity(set1: set, set2: set) -> float:
    """Compute the Jaccard similarity coefficient between two sets.

    Parameters
    ----------
    set1, set2:
        The two sets to compare.  Elements should be comparable (e.g. strings).

    Returns
    -------
    float
        |intersection| / |union| in [0.0, 1.0].  Returns 0.0 when both sets
        are empty (undefined similarity is treated as no overlap).

    Examples
    --------
    >>> jaccard_similarity({'a', 'b', 'c'}, {'b', 'c', 'd'})
    0.5
    """
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union


def collocate_divergence(
    word_av: str,
    word_sa: str,
    av_corpus: list[str],
    sa_corpus: list[str],
    window: int = 3,
    top_n: int = 10,
) -> dict:
    """Compare the collocate profiles of two cognate words across corpora.

    The function extracts the top-*top_n* collocates for each word from its
    respective corpus, then computes the Jaccard similarity and divergence
    between the two collocate *sets* (keys only, ignoring frequencies).

    Parameters
    ----------
    word_av:
        The Avestan cognate word.
    word_sa:
        The Sanskrit cognate word.
    av_corpus:
        List of Avestan passage strings.
    sa_corpus:
        List of Sanskrit passage strings.
    window:
        Token window size passed to :func:`extract_collocates`.
    top_n:
        Number of top collocates extracted per word.

    Returns
    -------
    dict
        A result dictionary with the following keys:

        ``av_collocates`` : dict[str, int]
            Frequency-ranked collocates for *word_av*.
        ``sa_collocates`` : dict[str, int]
            Frequency-ranked collocates for *word_sa*.
        ``jaccard`` : float
            Jaccard similarity between the two collocate key sets.
        ``divergence`` : float
            1 − jaccard; higher values indicate greater collocate divergence.
        ``shared_collocates`` : list[str]
            Sorted list of collocate tokens shared between both words.

    Examples
    --------
    >>> result = collocate_divergence(
    ...     "daeva", "deva",
    ...     av_corpus=["daeva druj drug", "daeva ahriman"],
    ...     sa_corpus=["deva indra agni", "deva soma"],
    ... )
    >>> result['divergence']  # expected near 1.0 — no shared collocates
    1.0
    """
    av_collocates = extract_collocates(word_av, av_corpus, window=window, top_n=top_n)
    sa_collocates = extract_collocates(word_sa, sa_corpus, window=window, top_n=top_n)

    av_keys = set(av_collocates.keys())
    sa_keys = set(sa_collocates.keys())

    jac = jaccard_similarity(av_keys, sa_keys)
    shared = sorted(av_keys & sa_keys)

    return {
        'av_collocates': av_collocates,
        'sa_collocates': sa_collocates,
        'jaccard': jac,
        'divergence': 1.0 - jac,
        'shared_collocates': shared,
    }
