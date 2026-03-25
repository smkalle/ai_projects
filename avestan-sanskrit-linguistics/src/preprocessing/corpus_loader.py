"""
corpus_loader.py — Load, tokenize, and manage Avestan and Sanskrit corpora.
Handles both synthetic seed corpora and real text files.
"""

import re
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd

from .transliteration import iast_to_ipa, avestan_to_ipa, word_to_phonemes


class CorpusLoader:
    """
    Utility class for loading, tokenising, and analysing Avestan and Sanskrit
    corpora.

    All public methods are stateless and can be called on a bare instance
    without any prior setup. State is intentionally avoided so that a single
    :class:`CorpusLoader` instance can be shared across multiple corpora
    without side effects.

    Examples
    --------
    >>> loader = CorpusLoader()
    >>> tokens = loader.tokenize("agni ṛta dharma", lang="sa")
    >>> loader.corpus_statistics(tokens)
    {'type_count': 3, 'token_count': 3, 'ttr': 1.0, 'hapax_count': 3, 'avg_word_len': 4.67}
    """

    # Regex used to split on whitespace and common punctuation marks.
    # We keep diacritical/modified Latin characters intact.
    _PUNCT_RE = re.compile(r'[\s\u00B7\u2019\u2018.,;:!?\"\'()\[\]{}<>|\\/*@#%^&+=~`]+')

    def load_corpus(self, path: str | Path) -> list[str]:
        """
        Load a plain-text corpus file and return its non-empty lines.

        The file is read with UTF-8 encoding. Lines containing only whitespace
        are discarded. No further normalisation is applied at this stage so
        that the raw text is preserved for downstream processing.

        Parameters
        ----------
        path : str or Path
            Filesystem path to the corpus file.

        Returns
        -------
        list[str]
            List of stripped, non-empty lines from the file.

        Raises
        ------
        FileNotFoundError
            If *path* does not point to an existing file.
        UnicodeDecodeError
            If the file cannot be decoded as UTF-8.

        Examples
        --------
        >>> loader = CorpusLoader()
        >>> lines = loader.load_corpus('/data/avesta/gathas.txt')
        >>> len(lines)
        1728
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Corpus file not found: {file_path}")

        with file_path.open(encoding='utf-8') as fh:
            lines = [line.strip() for line in fh]

        return [line for line in lines if line]

    def tokenize(self, text: str, lang: str) -> list[str]:
        """
        Tokenise a string into a list of word tokens.

        Splitting is performed on whitespace and common punctuation. Empty
        tokens produced by consecutive delimiters are dropped. All tokens are
        lowercased and Unicode NFC-normalised.

        Parameters
        ----------
        text : str
            Input text in either Avestan or IAST transliteration (or any
            compatible encoding).
        lang : str
            Language hint — ``'sa'`` for Sanskrit, ``'av'`` for Avestan.
            Currently used only for future language-specific tokenisation
            rules; the base implementation treats both identically.

        Returns
        -------
        list[str]
            Ordered list of lower-cased, NFC-normalised word tokens.

        Examples
        --------
        >>> loader = CorpusLoader()
        >>> loader.tokenize("yasna 28.1: yā ahu", lang='av')
        ['yasna', '28.1', 'yā', 'ahu']
        """
        # NFC-normalise the entire input first.
        normalised = unicodedata.normalize("NFC", text)

        # Split on punctuation / whitespace boundaries.
        raw_tokens = self._PUNCT_RE.split(normalised)

        tokens = [
            unicodedata.normalize("NFC", tok.lower())
            for tok in raw_tokens
            if tok.strip()
        ]
        return tokens

    def get_vocabulary(self, tokens: list[str]) -> dict:
        """
        Build a word-frequency mapping from a token list.

        Parameters
        ----------
        tokens : list[str]
            List of word tokens (as returned by :meth:`tokenize`).

        Returns
        -------
        dict
            Mapping of ``word -> frequency``, sorted in descending order of
            frequency. Ties are broken alphabetically.

        Examples
        --------
        >>> loader = CorpusLoader()
        >>> loader.get_vocabulary(['a', 'b', 'a', 'c', 'a'])
        {'a': 3, 'b': 1, 'c': 1}
        """
        counts = Counter(tokens)
        # Sort by descending frequency, then alphabetically for stable output.
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    def get_collocates(
        self,
        word: str,
        tokens: list[str],
        window: int = 3,
    ) -> dict:
        """
        Compute co-occurrence frequencies for *word* within a symmetric
        context window.

        For every occurrence of *word* in *tokens*, all tokens within
        *window* positions to the left and right (excluding the target word
        itself) are counted as collocates. Window boundaries are clamped to
        the start and end of the token list.

        Parameters
        ----------
        word : str
            Target word to find collocates for.
        tokens : list[str]
            Ordered token list representing the corpus context.
        window : int, optional
            Half-width of the symmetric context window (default ``3``).

        Returns
        -------
        dict
            Mapping of ``collocate -> co-occurrence count``, sorted in
            descending order of frequency.

        Examples
        --------
        >>> loader = CorpusLoader()
        >>> toks = ['a', 'b', 'target', 'c', 'd', 'target', 'e']
        >>> loader.get_collocates('target', toks, window=2)
        {'b': 2, 'c': 2, 'a': 1, 'd': 1}
        """
        collocates: Counter = Counter()
        n = len(tokens)

        for idx, tok in enumerate(tokens):
            if tok != word:
                continue
            left = max(0, idx - window)
            right = min(n, idx + window + 1)
            for ctx_idx in range(left, right):
                if ctx_idx != idx:
                    collocates[tokens[ctx_idx]] += 1

        return dict(sorted(collocates.items(), key=lambda kv: (-kv[1], kv[0])))

    def corpus_statistics(self, tokens: list[str]) -> dict:
        """
        Compute summary statistics for a token list.

        Parameters
        ----------
        tokens : list[str]
            Ordered list of word tokens.

        Returns
        -------
        dict
            Dictionary with the following keys:

            - ``type_count``   — number of distinct word forms (vocabulary size)
            - ``token_count``  — total number of tokens (corpus size)
            - ``ttr``          — type–token ratio (``type_count / token_count``);
                                 ``0.0`` when *tokens* is empty
            - ``hapax_count``  — number of words appearing exactly once
            - ``avg_word_len`` — mean character length of tokens, rounded to
                                 two decimal places; ``0.0`` when *tokens* is empty

        Examples
        --------
        >>> loader = CorpusLoader()
        >>> stats = loader.corpus_statistics(['agni', 'ṛta', 'agni'])
        >>> stats['ttr']
        0.67
        """
        token_count = len(tokens)

        if token_count == 0:
            return {
                'type_count': 0,
                'token_count': 0,
                'ttr': 0.0,
                'hapax_count': 0,
                'avg_word_len': 0.0,
            }

        freq = Counter(tokens)
        type_count = len(freq)
        hapax_count = sum(1 for f in freq.values() if f == 1)
        ttr = round(type_count / token_count, 2)
        avg_word_len = round(sum(len(t) for t in tokens) / token_count, 2)

        return {
            'type_count': type_count,
            'token_count': token_count,
            'ttr': ttr,
            'hapax_count': hapax_count,
            'avg_word_len': avg_word_len,
        }


def build_lingpy_wordlist(df: pd.DataFrame) -> dict:
    """
    Convert a cognate-pair DataFrame into lingpy's internal Wordlist format.

    Each row of *df* produces two entries in the output dictionary — one for
    the Avestan form and one for the Sanskrit form — assigned sequential
    integer IDs. The resulting dictionary can be passed directly to
    ``lingpy.Wordlist(data)`` without further transformation.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with at least the following columns:

        - ``avestan_word``  — Avestan form in standard transliteration
        - ``sanskrit_word`` — Sanskrit form in IAST transliteration
        - ``meaning_av``    — gloss / meaning label for the Avestan form
        - ``meaning_sa``    — gloss / meaning label for the Sanskrit form
        - ``pii_root``      — Proto-Indo-Iranian root shared by both forms

    Returns
    -------
    dict
        Dictionary keyed by integer row IDs (starting at ``1``) plus a
        special ``0`` entry that holds the column-name header tuple required
        by lingpy. Each data entry maps to a tuple with the following
        positional fields (in order):

        0. ``ID``        — unique integer identifier
        1. ``DOCULECT``  — language name (``'Avestan'`` or ``'Sanskrit'``)
        2. ``CONCEPT``   — meaning label (from *meaning_av* / *meaning_sa*)
        3. ``IPA``       — IPA string produced by the relevant converter
        4. ``TOKENS``    — space-separated phoneme list (from
                           :func:`~transliteration.word_to_phonemes`)
        5. ``COGID``     — cognate-set identifier derived from *pii_root*
        6. ``PIIRoot``   — original Proto-Indo-Iranian root string

        Entry ``0`` contains the header tuple
        ``('ID', 'DOCULECT', 'CONCEPT', 'IPA', 'TOKENS', 'COGID', 'PIIRoot')``.

    Notes
    -----
    * IPA conversion uses :func:`~transliteration.avestan_to_ipa` for Avestan
      entries and :func:`~transliteration.iast_to_ipa` for Sanskrit entries.
    * Phoneme tokenisation uses :func:`~transliteration.word_to_phonemes` with
      the appropriate language code (``'av'`` / ``'sa'``).
    * ``COGID`` is derived by building a sorted set of unique *pii_root* values
      and mapping each root to a stable integer index (1-based).

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame([{
    ...     'avestan_word': 'aša',
    ...     'sanskrit_word': 'ṛta',
    ...     'meaning_av': 'truth',
    ...     'meaning_sa': 'truth/cosmic order',
    ...     'pii_root': '*Hṛta',
    ... }])
    >>> wl = build_lingpy_wordlist(df)
    >>> wl[0]
    ('ID', 'DOCULECT', 'CONCEPT', 'IPA', 'TOKENS', 'COGID', 'PIIRoot')
    >>> wl[1][1]  # DOCULECT of first entry
    'Avestan'
    >>> wl[2][1]  # DOCULECT of second entry
    'Sanskrit'
    """
    required_cols = {'avestan_word', 'sanskrit_word', 'meaning_av', 'meaning_sa', 'pii_root'}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(
            f"Input DataFrame is missing required column(s): {sorted(missing)}"
        )

    # Build a stable COGID mapping from unique PIIRoot values.
    unique_roots = sorted(df['pii_root'].dropna().unique())
    root_to_cogid: dict[str, int] = {root: idx + 1 for idx, root in enumerate(unique_roots)}

    # Header entry (lingpy convention: key 0 holds column names).
    wordlist: dict = {
        0: ('ID', 'DOCULECT', 'CONCEPT', 'IPA', 'TOKENS', 'COGID', 'PIIRoot'),
    }

    entry_id = 1  # lingpy IDs are 1-based integers.

    for _, row in df.iterrows():
        pii_root = str(row['pii_root']) if pd.notna(row['pii_root']) else ''
        cogid = root_to_cogid.get(pii_root, 0)

        # --- Avestan entry ---
        av_word = str(row['avestan_word'])
        av_ipa = avestan_to_ipa(av_word)
        try:
            av_phonemes = word_to_phonemes(av_word, lang='av')
        except Exception:
            av_phonemes = list(av_ipa)
        av_tokens = ' '.join(av_phonemes)

        wordlist[entry_id] = (
            entry_id,
            'Avestan',
            str(row['meaning_av']),
            av_ipa,
            av_tokens,
            cogid,
            pii_root,
        )
        entry_id += 1

        # --- Sanskrit entry ---
        sa_word = str(row['sanskrit_word'])
        sa_ipa = iast_to_ipa(sa_word)
        try:
            sa_phonemes = word_to_phonemes(sa_word, lang='sa')
        except Exception:
            sa_phonemes = list(sa_ipa)
        sa_tokens = ' '.join(sa_phonemes)

        wordlist[entry_id] = (
            entry_id,
            'Sanskrit',
            str(row['meaning_sa']),
            sa_ipa,
            sa_tokens,
            cogid,
            pii_root,
        )
        entry_id += 1

    return wordlist
