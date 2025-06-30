
# Medical Document Processing with Docling 🩺📄

Docling is IBM Research’s open‑source toolkit that converts *any* document into structured data, unlocking the 70 % of enterprise information that’s still trapped in PDFs and scans.  
This guide shows you how to integrate **Docling** into a medical‑transcription workflow—turning already‑transcribed reports, discharge summaries, or lab results into analysis‑ready tables and markdown.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Deep Dive](#deep-dive)
   * 4.1 Parsing PDFs
   * 4.2 Extracting Text & Markdown
   * 4.3 Extracting Tables as DataFrames
   * 4.4 Export Options
5. [Batch Pipeline Example](#batch-pipeline-example)
6. [Integrating with LangChain / RAG](#rag)
7. [Performance & Limits](#performance)
8. [Privacy & Compliance](#privacy)
9. [Troubleshooting](#troubleshooting)
10. [Roadmap & Contributing](#roadmap)
11. [Related Resources](#related-resources)

---

## 1  Prerequisites <a name="prerequisites"></a>

* Python ≥ 3.9
* **PyTorch** (CPU or CUDA)
* Optional: `langchain`, `llama-index`, or other RAG frameworks for downstream QA.
* A sample medical PDF (e.g. an anonymised discharge summary).

> **Tip**: Run everything locally on an air‑gapped machine to keep Protected Health Information (PHI) secure.

---

## 2  Installation <a name="installation"></a>

```bash
# 1️⃣  Install PyTorch first (see https://pytorch.org for the right wheel)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 2️⃣  Install Docling
pip install docling

# macOS (Intel) quirk
pip install "docling[mac_intel]"
```
Docling bundles Tesseract OCR and layout models (DocLayNet, TableFormer) and will download them on first run.

---

## 3  Quick Start <a name="quick-start"></a>

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()                      # default pipeline
result    = converter.convert("reports/lab_123.pdf") # local path or URL

# Text
markdown = result.document.export_to_markdown()
print(markdown[:500])

# Tables
for t in result.document.tables:
    df = t.export_to_dataframe()
    print(df.head())
```
That’s it! You now have clean markdown and Pandas DataFrames ready for EHR ingestion or NLP.

---

## 4  Deep Dive <a name="deep-dive"></a>

### 4.1 Parsing PDFs

Docling ships multiple pipelines. For scanned docs use OCR:

```python
from docling.pipelines import OCRPipeline
converter = DocumentConverter(pipeline=OCRPipeline())
```

### 4.2 Extracting Text & Markdown
* `export_to_text()` – plain text
* `export_to_markdown(heading_levels=(1,3))` – preserve headings

### 4.3 Extracting Tables

```python
from docling.enums import TableFormerMode
result = converter.convert("cbc_results.pdf",
                           tableformer_mode=TableFormerMode.ACCURATE)
df = result.document.tables[0].export_to_dataframe(index=False)
```

### 4.4 Export Options
* JSON: `export_to_json(indent=2)`
* HTML: `export_to_html(embed_images=True)`
* Images: `result.document.export_images("out/")`

---

## 5  Batch Pipeline Example <a name="batch-pipeline-example"></a>

```python
import glob, json, pathlib
from tqdm import tqdm

pdfs = glob.glob("records/**/*.pdf", recursive=True)
out  = pathlib.Path("structured")
out.mkdir(exist_ok=True)

for f in tqdm(pdfs, desc="Parsing"):
    doc = converter.convert(f).document
    (out / (pathlib.Path(f).stem + ".json")).write_text(
        doc.export_to_json())
```

---

## 6  RAG with LangChain <a name="rag"></a>

```python
from langchain.document_loaders import DoclingLoader
from langchain.indexes import VectorstoreIndexCreator

loader     = DoclingLoader("records/visit_2024_06.pdf",
                           export_type="ExportType.MARKDOWN")
documents  = loader.load()
index      = VectorstoreIndexCreator().from_documents(documents)

answer = index.query("What medications was the patient discharged with?")
print(answer)
```

---

## 7  Performance & Limits <a name="performance"></a>

* **Max file size**: 20 MB  
* **Max pages**: 100 (tune with `convert_kwargs`)  
* Use the env var `OMP_NUM_THREADS` to cap CPU usage.

See the [Technical Report](https://arxiv.org/abs/2408.09869) for full benchmarks.

---

## 8  Privacy & Compliance <a name="privacy"></a>

* Run locally to avoid PHI leaks.
* Strip or hash identifiers before vector DB ingestion.
* Validate against HIPAA or your regional healthcare privacy law.

---

## 9  Troubleshooting <a name="troubleshooting"></a>

| Issue                           | Fix |
|---------------------------------|-----|
| `ImportError: libtesseract.so`  | `apt install tesseract-ocr` or brew install tesseract |
| M1/M2 Mac crash                 | `pip install docling[mac_arm]` and ensure PyTorch metal backend |
| Blank tables                    | switch to `TableFormerMode.ACCURATE` |

---

## 10  Roadmap & Contributing <a name="roadmap"></a>

Docling lives under the **LF AI & Data Foundation**.  
Pull requests are welcome—especially new OCR back‑ends (e.g. EasyOCR) and domain‑specific pipelines for digital pathology slides.

---

### External Links
* Docling GitHub – <https://github.com/docling-project/docling>  
* LangChain integration – <https://python.langchain.com/docs/integrations/document_loaders/docling>  
* Docling Technical Report (arXiv 2408.09869)  
* Matt Dancho X‑thread on Docling launch  

**Happy parsing!**

---

## 11  Related Resources <a name="related-resources"></a>

For hands-on practice with the concepts covered in this tutorial, check out the companion Jupyter notebook:

* [Docling Medical Document Processing Demo](docling_medical_transcription_demo.ipynb) – Interactive notebook with code examples and step-by-step exercises to practice medical document processing with Docling.
