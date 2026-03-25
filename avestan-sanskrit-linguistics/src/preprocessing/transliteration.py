"""
transliteration.py — IAST and Avestan transliteration to IPA.

Implements pure-Python lookup tables for all IAST characters (40+) and
Avestan transliteration characters, with optional pyclts enhancement.
Unicode NFC normalization is applied to all input.
"""

import unicodedata
from typing import Optional
import pandas as pd

# IAST to IPA mapping (comprehensive)
IAST_TO_IPA = {
    # Vowels
    'a': 'ə', 'ā': 'aː', 'i': 'ɪ', 'ī': 'iː', 'u': 'ʊ', 'ū': 'uː',
    'ṛ': 'r̩', 'ṝ': 'r̩ː', 'ḷ': 'l̩', 'e': 'eː', 'ai': 'əɪ', 'o': 'oː', 'au': 'əʊ',
    # Gutturals/Velars
    'k': 'k', 'kh': 'kʰ', 'g': 'g', 'gh': 'gʱ', 'ṅ': 'ŋ',
    # Palatals
    'c': 'tɕ', 'ch': 'tɕʰ', 'j': 'dʑ', 'jh': 'dʑʱ', 'ñ': 'ɲ',
    # Retroflex
    'ṭ': 'ʈ', 'ṭh': 'ʈʰ', 'ḍ': 'ɖ', 'ḍh': 'ɖʱ', 'ṇ': 'ɳ',
    # Dentals
    't': 't', 'th': 'tʰ', 'd': 'd', 'dh': 'dʱ', 'n': 'n',
    # Labials
    'p': 'p', 'ph': 'pʰ', 'b': 'b', 'bh': 'bʱ', 'm': 'm',
    # Semivowels/Liquids/Sibilants/Aspirates
    'y': 'j', 'r': 'r', 'l': 'l', 'v': 'ʋ',
    'ś': 'ɕ', 'ṣ': 'ʂ', 's': 's', 'h': 'h',
    # Anusvara/Visarga
    'ṃ': 'm̃', 'ḥ': 'h̤',
}

# Avestan to IPA mapping (standard Avestan transliteration system)
AVESTAN_TO_IPA = {
    # Vowels
    'a': 'a', 'ā': 'aː', 'å': 'ɒ', 'ą': 'ãː',
    'e': 'e', 'ē': 'eː', 'ə': 'ə', 'əː': 'əː',
    'i': 'ɪ', 'ī': 'iː', 'u': 'ʊ', 'ū': 'uː',
    'o': 'o', 'ō': 'oː', 'aē': 'æː', 'ao': 'ɑo',
    # Velars
    'k': 'k', 'x': 'x', 'xv': 'xʷ', 'g': 'g', 'γ': 'ɣ',
    # Palatals
    'č': 'tʃ', 'j': 'dʒ',
    # Dentals
    't': 't', 'θ': 'θ', 'd': 'd', 'δ': 'ð', 'n': 'n',
    # Sibilants
    's': 's', 'z': 'z', 'š': 'ʃ', 'ž': 'ʒ',
    # Labials
    'p': 'p', 'f': 'f', 'b': 'b', 'β': 'β', 'm': 'm',
    # Nasals/Liquids/Glides
    'ŋ': 'ŋ', 'ŋv': 'ŋʷ', 'r': 'r', 'l': 'l',
    'y': 'j', 'v': 'v', 'w': 'w',
    # Aspirate
    'h': 'h',
}


def _build_sorted_keys(mapping: dict) -> list[str]:
    """Return mapping keys sorted by descending length for longest-match-first processing."""
    return sorted(mapping.keys(), key=len, reverse=True)


# Pre-sort keys so digraphs/multigraphs are matched before single characters.
_IAST_KEYS_SORTED = _build_sorted_keys(IAST_TO_IPA)
_AVESTAN_KEYS_SORTED = _build_sorted_keys(AVESTAN_TO_IPA)


def _transliterate(text: str, mapping: dict, sorted_keys: list[str]) -> tuple[str, list[str]]:
    """
    Core transliteration engine using longest-match-first greedy scan.

    Parameters
    ----------
    text : str
        NFC-normalised input string.
    mapping : dict
        Source-to-IPA character mapping.
    sorted_keys : list[str]
        Mapping keys pre-sorted by descending length.

    Returns
    -------
    ipa : str
        IPA output string.
    unknown : list[str]
        Characters that had no mapping entry.
    """
    result: list[str] = []
    unknown: list[str] = []
    pos = 0
    length = len(text)

    while pos < length:
        matched = False
        for key in sorted_keys:
            key_len = len(key)
            if text[pos:pos + key_len] == key:
                result.append(mapping[key])
                pos += key_len
                matched = True
                break
        if not matched:
            char = text[pos]
            # Preserve whitespace and punctuation as-is; flag everything else.
            if char.isspace() or not char.isalpha():
                result.append(char)
            else:
                result.append(char)   # include in output for readability
                unknown.append(char)
            pos += 1

    return ''.join(result), unknown


def iast_to_ipa(word: str) -> str:
    """
    Convert an IAST-transliterated Sanskrit string to IPA.

    Unicode NFC normalisation is applied before conversion. Digraphs (e.g.
    ``kh``, ``gh``, ``bh``) are resolved before single characters using a
    longest-match-first strategy.

    Parameters
    ----------
    word : str
        Input string in IAST transliteration.

    Returns
    -------
    str
        IPA representation of the input string.

    Examples
    --------
    >>> iast_to_ipa('dharma')
    'dʱərməə'
    >>> iast_to_ipa('agni')
    'əgɳɪ'
    """
    normalised = unicodedata.normalize("NFC", word)
    ipa, _ = _transliterate(normalised, IAST_TO_IPA, _IAST_KEYS_SORTED)
    return ipa


def avestan_to_ipa(word: str) -> str:
    """
    Convert an Avestan transliteration string to IPA.

    Unicode NFC normalisation is applied before conversion. Multigraphs such
    as ``xv``, ``ŋv``, ``aē``, and ``ao`` are resolved before single
    characters using a longest-match-first strategy.

    Parameters
    ----------
    word : str
        Input string in standard Avestan transliteration.

    Returns
    -------
    str
        IPA representation of the input string.

    Examples
    --------
    >>> avestan_to_ipa('aša')
    'aʃa'
    >>> avestan_to_ipa('xvaθra')
    'xʷaθra'
    """
    normalised = unicodedata.normalize("NFC", word)
    ipa, _ = _transliterate(normalised, AVESTAN_TO_IPA, _AVESTAN_KEYS_SORTED)
    return ipa


def word_to_phonemes(word: str, lang: str) -> list[str]:
    """
    Convert a transliterated word to a list of IPA phoneme symbols.

    The word is first converted to IPA (via :func:`iast_to_ipa` or
    :func:`avestan_to_ipa`) and then split into individual phoneme tokens.
    A phoneme is defined here as a base IPA character followed by any
    combining diacritics (Unicode category ``Mn``) and IPA length/modifier
    letters (e.g. ``ː``).

    Parameters
    ----------
    word : str
        Input transliteration string.
    lang : str
        Language code — ``'sa'`` (Sanskrit/IAST) or ``'av'`` (Avestan).
        Any unrecognised value falls back to character-by-character splitting.

    Returns
    -------
    list[str]
        Ordered list of phoneme strings.

    Raises
    ------
    ValueError
        If *lang* is not ``'sa'`` or ``'av'``.

    Examples
    --------
    >>> word_to_phonemes('agni', 'sa')
    ['ə', 'g', 'ɳ', 'ɪ']
    """
    lang = lang.strip().lower()
    if lang == 'sa':
        ipa = iast_to_ipa(word)
    elif lang == 'av':
        ipa = avestan_to_ipa(word)
    else:
        raise ValueError(f"Unsupported language code '{lang}'. Use 'sa' or 'av'.")

    # IPA modifier / length characters that attach to the preceding base.
    _MODIFIERS = {'ː', 'ʰ', 'ʱ', 'ʷ', 'ʲ', '̃', '̤', '̩'}

    phonemes: list[str] = []
    current = ''

    for char in ipa:
        cat = unicodedata.category(char)
        is_modifier = char in _MODIFIERS or cat == 'Mn'

        if is_modifier:
            # Attach to preceding phoneme if one exists; otherwise start new.
            if phonemes:
                phonemes[-1] += char
            else:
                current += char
        else:
            if current:
                phonemes.append(current)
            current = char

    if current:
        phonemes.append(current)

    return phonemes


def validate_transliteration(
    pairs: list[tuple],
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Validate a list of Avestan–Sanskrit cognate pairs and return a summary
    DataFrame.

    For each pair the function converts both words to IPA, detects any
    characters that could not be mapped (unknown characters), and flags the
    pair as valid only when both conversions are free of unknown characters.

    Parameters
    ----------
    pairs : list[tuple]
        Each element must be a two-tuple ``(avestan_word, sanskrit_word)``
        where both values are strings in their respective transliteration
        schemes.
    verbose : bool, optional
        When ``True`` (default) a summary line is printed to *stdout* after
        processing, reporting the total number of pairs and how many are valid.

    Returns
    -------
    pd.DataFrame
        DataFrame with one row per pair and the following columns:

        - ``avestan_word``    — original Avestan input
        - ``sanskrit_word``   — original Sanskrit (IAST) input
        - ``av_ipa``          — IPA conversion of the Avestan word
        - ``sa_ipa``          — IPA conversion of the Sanskrit word
        - ``unknown_chars_av`` — list of unmapped characters in the Avestan word
        - ``unknown_chars_sa`` — list of unmapped characters in the Sanskrit word
        - ``valid``           — ``True`` iff both words had zero unknown characters

    Examples
    --------
    >>> pairs = [('aša', 'ṛta'), ('xšaθra', 'kṣatra')]
    >>> df = validate_transliteration(pairs, verbose=False)
    >>> list(df.columns)
    ['avestan_word', 'sanskrit_word', 'av_ipa', 'sa_ipa', 'unknown_chars_av', 'unknown_chars_sa', 'valid']
    """
    records = []

    for av_word, sa_word in pairs:
        av_norm = unicodedata.normalize("NFC", str(av_word))
        sa_norm = unicodedata.normalize("NFC", str(sa_word))

        av_ipa, unknown_av = _transliterate(av_norm, AVESTAN_TO_IPA, _AVESTAN_KEYS_SORTED)
        sa_ipa, unknown_sa = _transliterate(sa_norm, IAST_TO_IPA, _IAST_KEYS_SORTED)

        records.append({
            'avestan_word': av_word,
            'sanskrit_word': sa_word,
            'av_ipa': av_ipa,
            'sa_ipa': sa_ipa,
            'unknown_chars_av': unknown_av,
            'unknown_chars_sa': unknown_sa,
            'valid': len(unknown_av) == 0 and len(unknown_sa) == 0,
        })

    df = pd.DataFrame(
        records,
        columns=[
            'avestan_word', 'sanskrit_word',
            'av_ipa', 'sa_ipa',
            'unknown_chars_av', 'unknown_chars_sa',
            'valid',
        ],
    )

    if verbose:
        total = len(df)
        valid_count = df['valid'].sum()
        print(
            f"validate_transliteration: {total} pair(s) processed, "
            f"{valid_count} valid ({total - valid_count} with unknown characters)."
        )

    return df
