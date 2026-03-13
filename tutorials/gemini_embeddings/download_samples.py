#!/usr/bin/env python3
"""
Download open-source medical research samples for MedSearch.

Sources:
  Images   — Open-i / MedPix (NIH/NLM), public domain
  Abstracts — PubMed E-utilities (NCBI), free
  Papers   — PMC Open Access subset (CC BY / CC BY-NC), free

Usage:
    python download_samples.py
"""

import io
import json
import os
import tarfile
import time
from pathlib import Path

import requests

MEDIA = Path("./media")
BASE_OPENI = "https://openi.nlm.nih.gov"
NCBI_DELAY = 0.4   # stay under NCBI's 3 req/s limit
HEADERS = {"User-Agent": "MedSearch-tutorial/1.0 (education; open-source)"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def get(url, params=None, timeout=20, stream=False):
    r = requests.get(url, params=params, headers=HEADERS, timeout=timeout, stream=stream)
    r.raise_for_status()
    return r


def save(path: Path, data: bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(f"    saved  {path.name}  ({len(data)//1024} KB)")


# ── 1. Medical images from Open-i / MedPix (NIH NLM) ────────────────────────
# Open-i is a free image retrieval service from the National Library of Medicine.
# Images are sourced from MedPix, Indiana University, and other open repositories.

IMAGE_QUERIES = [
    ("chest xray pneumonia",   "pneumonia",    3),
    ("chest xray effusion",    "effusion",     2),
    ("chest xray normal",      "normal",       2),
    ("CT brain stroke",        "brain_ct",     2),
    ("pathology tumor histology", "pathology", 2),
    ("MRI spine",              "mri_spine",    1),
]

def download_images():
    out_dir = MEDIA / "imaging"
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0

    for query, tag, n in IMAGE_QUERIES:
        print(f"  [{tag}]  searching Open-i: '{query}'")
        try:
            r = get(BASE_OPENI + "/api/search", params={"q": query, "m": 1, "n": n, "it": "x"})
            items = r.json().get("list", [])
            time.sleep(NCBI_DELAY)
        except Exception as e:
            print(f"    search failed: {e}")
            continue

        for item in items:
            img_path = item.get("imgLarge") or item.get("imgThumbLarge") or item.get("imgThumb")
            if not img_path:
                continue
            uid = item.get("image", {}).get("id", item.get("uid", "unknown"))
            caption = item.get("image", {}).get("caption", "")[:80]
            ext = img_path.split(".")[-1].lower()
            fname = f"{tag}_{uid}.{ext}"
            out_path = out_dir / fname

            if out_path.exists():
                print(f"    skip   {fname}")
                total += 1
                continue
            try:
                img = get(BASE_OPENI + img_path, timeout=30)
                save(out_path, img.content)
                if caption:
                    (out_dir / f"{fname}.caption.txt").write_text(caption, encoding="utf-8")
                total += 1
            except Exception as e:
                print(f"    failed {fname}: {e}")
            time.sleep(0.4)

    print(f"  Images: {total} downloaded\n")


# ── 2. PubMed abstracts (E-utilities) ────────────────────────────────────────
# Free, no API key required for ≤3 req/s. Results are plain text.

ABSTRACT_TOPICS = [
    ("pneumonia CT imaging radiological findings diagnosis",     "pneumonia_ct"),
    ("ARDS acute respiratory distress syndrome ventilation management", "ards_ventilation"),
    ("lung cancer screening low dose CT nodule",                 "lung_cancer_ct"),
    ("COVID-19 chest X-ray deep learning classification",        "covid_xray_ai"),
    ("digital pathology whole slide imaging deep learning",      "pathology_ai"),
    ("myocardial infarction cardiac MRI diagnosis treatment",    "cardiac_mri"),
    ("breast cancer mammography screening detection",            "breast_mammography"),
]

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def download_abstracts():
    out_dir = MEDIA / "abstracts"
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0

    for query, fname in ABSTRACT_TOPICS:
        out_path = out_dir / f"{fname}.txt"
        if out_path.exists():
            print(f"  skip   {fname}.txt")
            total += 1
            continue

        print(f"  [{fname}]  fetching from PubMed...")
        try:
            search = get(ESEARCH, params={
                "db": "pubmed", "term": query, "retmax": 3,
                "retmode": "json", "sort": "relevance",
            })
            pmids = search.json().get("esearchresult", {}).get("idlist", [])
            time.sleep(NCBI_DELAY)

            if not pmids:
                print(f"    no results")
                continue

            fetch = get(EFETCH, params={
                "db": "pubmed", "id": ",".join(pmids[:3]),
                "rettype": "abstract", "retmode": "text",
            })
            time.sleep(NCBI_DELAY)

            out_path.write_text(fetch.text, encoding="utf-8")
            print(f"    saved  {fname}.txt  ({len(fetch.text)} chars,  {len(pmids)} abstracts)")
            total += 1

        except Exception as e:
            print(f"    failed: {e}")

    print(f"  Abstracts: {total} downloaded\n")


# ── 3. PMC open-access PDFs ───────────────────────────────────────────────────
# Uses the official PMC OA Web Service API (no scraping).
# Only fetches CC BY / CC BY-NC licensed articles.

PDF_TOPICS = [
    ("pneumonia chest imaging diagnosis radiological",  "pneumonia_imaging"),
    ("COVID-19 CT scan findings lung",                  "covid_ct"),
    ("lung cancer CT screening detection nodule",       "lung_cancer"),
    ("ARDS management treatment outcomes",              "ards"),
    ("digital pathology AI deep learning cancer",       "pathology_ai"),
]

PMC_SEARCH = ESEARCH
PMC_OA     = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
PMC_FTP    = "https://ftp.ncbi.nlm.nih.gov/pub/pmc/"

def get_tgz_url(pmcid: str) -> str | None:
    """Return the HTTPS URL for a PMC article's tar.gz package, or None."""
    import xml.etree.ElementTree as ET
    try:
        r = get(PMC_OA, params={"id": pmcid}, timeout=10)
        root = ET.fromstring(r.text)
        for link in root.iter("link"):
            href = link.get("href", "")
            if href.endswith(".tar.gz"):
                # Convert ftp:// to https://
                return href.replace(
                    "ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/",
                    PMC_FTP,
                )
    except Exception:
        pass
    return None


def extract_pdf_from_tgz(data: bytes) -> tuple[bytes, str] | tuple[None, None]:
    """Extract the first PDF from a tar.gz byte blob. Returns (pdf_bytes, filename)."""
    try:
        with tarfile.open(fileobj=io.BytesIO(data)) as tar:
            for member in tar.getmembers():
                if member.name.lower().endswith(".pdf"):
                    f = tar.extractfile(member)
                    if f:
                        return f.read(), Path(member.name).name
    except Exception:
        pass
    return None, None


def download_pdfs():
    out_dir = MEDIA / "papers"
    out_dir.mkdir(parents=True, exist_ok=True)
    total = 0

    for query, tag in PDF_TOPICS:
        print(f"  [{tag}]  searching PMC: '{query[:45]}...'")

        # Check if already downloaded
        existing = list(out_dir.glob(f"{tag}_*.pdf"))
        if existing:
            print(f"    skip   {existing[0].name}")
            total += 1
            continue

        try:
            search = get(PMC_SEARCH, params={
                "db": "pmc",
                "term": f"{query}[Title/Abstract] AND open access[filter]",
                "retmax": 8, "retmode": "json", "sort": "relevance",
            })
            ids = search.json().get("esearchresult", {}).get("idlist", [])
            time.sleep(NCBI_DELAY)
        except Exception as e:
            print(f"    search failed: {e}")
            continue

        downloaded = False
        for pmc_num in ids:
            if downloaded:
                break
            pmcid = f"PMC{pmc_num}"
            tgz_url = get_tgz_url(pmcid)
            time.sleep(NCBI_DELAY)

            if not tgz_url:
                continue

            try:
                print(f"    downloading {pmcid} package...")
                r = get(tgz_url, timeout=60)
                pdf_bytes, pdf_name = extract_pdf_from_tgz(r.content)
                if pdf_bytes:
                    out_path = out_dir / f"{tag}_{pmcid}.pdf"
                    save(out_path, pdf_bytes)
                    total += 1
                    downloaded = True
                else:
                    print(f"    no PDF inside {pmcid} package")
            except Exception as e:
                print(f"    failed {pmcid}: {e}")
            time.sleep(0.5)

        if not downloaded:
            print(f"    no downloadable PDF found for: {tag}")

    print(f"  PDFs: {total} downloaded\n")


# ── Summary ───────────────────────────────────────────────────────────────────

def print_summary():
    print("─" * 50)
    print("Downloaded samples:\n")
    total_files = 0
    for subdir in ["imaging", "abstracts", "papers"]:
        d = MEDIA / subdir
        if d.exists():
            files = [f for f in d.iterdir() if not f.name.endswith(".caption.txt")]
            print(f"  media/{subdir}/  →  {len(files)} file(s)")
            for f in sorted(files):
                print(f"      {f.name}")
            total_files += len(files)
    print(f"\nTotal: {total_files} files")
    print("\nNext step:")
    print("  ./run.sh ingest   — embed and index everything")
    print("  ./run.sh          — search")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("MedSearch — Downloading open-source medical samples\n")
    print("Sources: Open-i/MedPix (NIH), PubMed (NCBI), PMC Open Access\n")

    print("[1/3] Medical images (Open-i / MedPix / NIH)")
    download_images()

    print("[2/3] PubMed abstracts")
    download_abstracts()

    print("[3/3] PMC open-access research papers (PDF)")
    download_pdfs()

    print_summary()
