"""API registry and discovery system for the Code MCP server.

This is the equivalent of Cloudflare's `search()` tool — it lets agents
dynamically discover available bioinformatics operations, databases, and
helper functions without requiring massive tool definitions in the context.

The registry is a structured catalog of everything available in the sandbox.
Agents query it with keywords, tags, or database names to find the right
API methods and helpers before generating execution code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class OperationParam:
    """Parameter descriptor for an operation."""

    name: str
    type: str
    description: str
    required: bool = True
    default: str | None = None


@dataclass
class Operation:
    """A single discoverable operation in the registry."""

    name: str
    module: str
    method: str
    description: str
    tags: list[str] = field(default_factory=list)
    params: list[OperationParam] = field(default_factory=list)
    returns: str = ""
    example: str = ""

    def matches(self, query: str) -> bool:
        """Check if this operation matches a search query."""
        query_lower = query.lower()
        terms = re.split(r"\s+", query_lower)
        searchable = (
            f"{self.name} {self.module} {self.description} "
            f"{' '.join(self.tags)} {self.returns}"
        ).lower()
        return all(term in searchable for term in terms)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "module": self.module,
            "method": self.method,
            "description": self.description,
            "tags": self.tags,
            "params": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                }
                for p in self.params
            ],
            "returns": self.returns,
            "example": self.example,
        }


class Registry:
    """Searchable catalog of all bioinformatics operations available in the sandbox."""

    def __init__(self) -> None:
        self._operations: list[Operation] = []
        self._build_registry()

    def search(
        self,
        query: str = "",
        tags: list[str] | None = None,
        module: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Search for operations matching a query.

        Args:
            query: Free-text search query (matches name, description, tags).
            tags: Filter by tags (e.g. ["sequence", "ncbi"]).
            module: Filter by module name (e.g. "ncbi", "uniprot").
            limit: Maximum number of results.

        Returns:
            List of operation dicts.
        """
        results = self._operations

        if module:
            results = [op for op in results if op.module.lower() == module.lower()]

        if tags:
            tag_set = {t.lower() for t in tags}
            results = [
                op for op in results if tag_set.intersection(t.lower() for t in op.tags)
            ]

        if query:
            results = [op for op in results if op.matches(query)]

        return [op.to_dict() for op in results[:limit]]

    def list_modules(self) -> list[dict[str, Any]]:
        """List all available modules with their operation counts."""
        modules: dict[str, int] = {}
        for op in self._operations:
            modules[op.module] = modules.get(op.module, 0) + 1
        return [{"module": m, "operation_count": c} for m, c in sorted(modules.items())]

    def list_tags(self) -> list[str]:
        """List all unique tags."""
        tags: set[str] = set()
        for op in self._operations:
            tags.update(op.tags)
        return sorted(tags)

    def get_operation(self, name: str) -> dict[str, Any] | None:
        """Get details for a specific operation by name."""
        for op in self._operations:
            if op.name == name:
                return op.to_dict()
        return None

    def _build_registry(self) -> None:
        """Populate the registry with all available operations."""
        self._register_ncbi_operations()
        self._register_uniprot_operations()
        self._register_pdb_operations()
        self._register_ensembl_operations()
        self._register_blast_operations()
        self._register_sequence_utilities()
        self._register_format_utilities()

    # ------------------------------------------------------------------
    # NCBI operations
    # ------------------------------------------------------------------

    def _register_ncbi_operations(self) -> None:
        ops = [
            Operation(
                name="ncbi.esearch",
                module="ncbi",
                method="ncbi.esearch(db, term, retmax=20, sort='relevance')",
                description="Search any NCBI database (PubMed, Gene, Nucleotide, Protein, etc.) and return matching IDs",
                tags=["ncbi", "search", "pubmed", "gene", "nucleotide", "protein"],
                params=[
                    OperationParam("db", "str", "Database name: pubmed, gene, nucleotide, protein, etc."),
                    OperationParam("term", "str", "Entrez query string"),
                    OperationParam("retmax", "int", "Max results", required=False, default="20"),
                ],
                returns="dict with idlist, count, querytranslation",
                example='result = await ncbi.esearch("pubmed", "CRISPR Cas9 2024")',
            ),
            Operation(
                name="ncbi.efetch",
                module="ncbi",
                method="ncbi.efetch(db, ids, rettype='abstract', retmode='xml')",
                description="Fetch full records (sequences, abstracts, annotations) from NCBI databases",
                tags=["ncbi", "fetch", "sequence", "record"],
                params=[
                    OperationParam("db", "str", "Database name"),
                    OperationParam("ids", "list[str]", "List of database IDs"),
                    OperationParam("rettype", "str", "Return type: abstract, fasta, gb, gp", required=False, default="abstract"),
                    OperationParam("retmode", "str", "Return format: xml, text, json", required=False, default="xml"),
                ],
                returns="Raw response text (XML, FASTA, GenBank, etc.)",
                example='fasta = await ncbi.efetch("nucleotide", ["NM_007294"], rettype="fasta", retmode="text")',
            ),
            Operation(
                name="ncbi.esummary",
                module="ncbi",
                method="ncbi.esummary(db, ids)",
                description="Get document summaries (title, authors, etc.) for a list of NCBI IDs",
                tags=["ncbi", "summary", "metadata"],
                params=[
                    OperationParam("db", "str", "Database name"),
                    OperationParam("ids", "list[str]", "List of database IDs"),
                ],
                returns="List of summary dicts",
                example='summaries = await ncbi.esummary("pubmed", ["12345678"])',
            ),
            Operation(
                name="ncbi.einfo",
                module="ncbi",
                method="ncbi.einfo(db=None)",
                description="Get information about NCBI databases — list all databases or get field details for a specific one",
                tags=["ncbi", "discovery", "database", "metadata"],
                params=[
                    OperationParam("db", "str", "Database name (omit to list all)", required=False),
                ],
                returns="Dict with database info",
                example="all_dbs = await ncbi.einfo()",
            ),
            Operation(
                name="ncbi.elink",
                module="ncbi",
                method="ncbi.elink(dbfrom, db, ids, linkname=None)",
                description="Find related records across NCBI databases (e.g., gene→protein, pubmed→gene)",
                tags=["ncbi", "link", "cross-reference"],
                params=[
                    OperationParam("dbfrom", "str", "Source database"),
                    OperationParam("db", "str", "Target database"),
                    OperationParam("ids", "list[str]", "Source IDs"),
                ],
                returns="Dict with linked ID sets",
                example='links = await ncbi.elink("gene", "protein", ["7157"])',
            ),
            Operation(
                name="ncbi.search_pubmed",
                module="ncbi",
                method="ncbi.search_pubmed(query, max_results=10)",
                description="Search PubMed and return article summaries (title, authors, journal, date)",
                tags=["ncbi", "pubmed", "literature", "search"],
                params=[
                    OperationParam("query", "str", "PubMed search query"),
                    OperationParam("max_results", "int", "Max articles", required=False, default="10"),
                ],
                returns="List of article summary dicts",
                example='articles = await ncbi.search_pubmed("BRCA1 breast cancer therapy", max_results=5)',
            ),
            Operation(
                name="ncbi.fetch_gene_info",
                module="ncbi",
                method="ncbi.fetch_gene_info(gene_symbol, organism='human')",
                description="Look up a gene by symbol (e.g., TP53, BRCA1) and return summary data",
                tags=["ncbi", "gene", "lookup"],
                params=[
                    OperationParam("gene_symbol", "str", "Gene symbol (e.g., TP53)"),
                    OperationParam("organism", "str", "Organism name", required=False, default="human"),
                ],
                returns="List of gene summary dicts",
                example='genes = await ncbi.fetch_gene_info("TP53")',
            ),
            Operation(
                name="ncbi.fetch_sequence",
                module="ncbi",
                method="ncbi.fetch_sequence(db, seq_id, rettype='fasta')",
                description="Fetch a nucleotide or protein sequence in FASTA or GenBank format",
                tags=["ncbi", "sequence", "fasta", "genbank", "fetch"],
                params=[
                    OperationParam("db", "str", "Database: nucleotide or protein"),
                    OperationParam("seq_id", "str", "Accession or GI number"),
                    OperationParam("rettype", "str", "fasta, gb, or gp", required=False, default="fasta"),
                ],
                returns="Sequence data as text",
                example='fasta = await ncbi.fetch_sequence("nucleotide", "NM_007294")',
            ),
        ]
        self._operations.extend(ops)

    # ------------------------------------------------------------------
    # UniProt operations
    # ------------------------------------------------------------------

    def _register_uniprot_operations(self) -> None:
        ops = [
            Operation(
                name="uniprot.search",
                module="uniprot",
                method="uniprot.search(query, dataset='uniprotkb', fields=None, size=25)",
                description="Search UniProt databases (UniProtKB, UniRef, UniParc, Proteomes) with structured queries",
                tags=["uniprot", "protein", "search"],
                params=[
                    OperationParam("query", "str", "UniProt query (e.g., 'gene:TP53 AND organism_id:9606')"),
                    OperationParam("dataset", "str", "Dataset: uniprotkb, uniref, uniparc, proteomes", required=False, default="uniprotkb"),
                    OperationParam("size", "int", "Max results", required=False, default="25"),
                ],
                returns="Dict with 'results' list",
                example='data = await uniprot.search("gene:TP53 AND organism_id:9606")',
            ),
            Operation(
                name="uniprot.fetch_entry",
                module="uniprot",
                method="uniprot.fetch_entry(accession, dataset='uniprotkb')",
                description="Fetch a complete UniProt entry by accession (sequence, function, structure, etc.)",
                tags=["uniprot", "protein", "entry", "fetch"],
                params=[
                    OperationParam("accession", "str", "UniProt accession (e.g., P04637)"),
                ],
                returns="Full entry dict",
                example='entry = await uniprot.fetch_entry("P04637")',
            ),
            Operation(
                name="uniprot.fetch_fasta",
                module="uniprot",
                method="uniprot.fetch_fasta(accession)",
                description="Fetch protein sequence in FASTA format from UniProt",
                tags=["uniprot", "protein", "sequence", "fasta"],
                params=[
                    OperationParam("accession", "str", "UniProt accession"),
                ],
                returns="FASTA string",
                example='fasta = await uniprot.fetch_fasta("P04637")',
            ),
            Operation(
                name="uniprot.search_protein",
                module="uniprot",
                method="uniprot.search_protein(gene, organism='Homo sapiens', reviewed=True)",
                description="Search for a protein by gene name and organism in Swiss-Prot",
                tags=["uniprot", "protein", "gene", "search"],
                params=[
                    OperationParam("gene", "str", "Gene symbol"),
                    OperationParam("organism", "str", "Scientific name", required=False, default="Homo sapiens"),
                    OperationParam("reviewed", "bool", "Swiss-Prot only", required=False, default="True"),
                ],
                returns="List of protein result entries",
                example='proteins = await uniprot.search_protein("BRCA1")',
            ),
            Operation(
                name="uniprot.get_protein_features",
                module="uniprot",
                method="uniprot.get_protein_features(accession)",
                description="Get annotated features (domains, variants, PTMs, binding sites) for a protein",
                tags=["uniprot", "protein", "features", "domains", "variants"],
                params=[
                    OperationParam("accession", "str", "UniProt accession"),
                ],
                returns="List of feature dicts",
                example='features = await uniprot.get_protein_features("P04637")',
            ),
            Operation(
                name="uniprot.get_go_terms",
                module="uniprot",
                method="uniprot.get_go_terms(accession)",
                description="Get Gene Ontology annotations (molecular function, biological process, cellular component)",
                tags=["uniprot", "protein", "go", "ontology", "annotation"],
                params=[
                    OperationParam("accession", "str", "UniProt accession"),
                ],
                returns="List of GO annotation dicts",
                example='go_terms = await uniprot.get_go_terms("P04637")',
            ),
        ]
        self._operations.extend(ops)

    # ------------------------------------------------------------------
    # PDB operations
    # ------------------------------------------------------------------

    def _register_pdb_operations(self) -> None:
        ops = [
            Operation(
                name="pdb.get_entry",
                module="pdb",
                method="pdb.get_entry(pdb_id)",
                description="Get complete entry metadata for a PDB structure",
                tags=["pdb", "structure", "entry", "metadata"],
                params=[
                    OperationParam("pdb_id", "str", "4-character PDB ID (e.g., 1TUP)"),
                ],
                returns="Dict with full entry data",
                example='entry = await pdb.get_entry("1TUP")',
            ),
            Operation(
                name="pdb.get_entity",
                module="pdb",
                method="pdb.get_entity(pdb_id, entity_id=1)",
                description="Get polymer entity info (sequence, source organism, classification)",
                tags=["pdb", "structure", "entity", "polymer"],
                params=[
                    OperationParam("pdb_id", "str", "PDB ID"),
                    OperationParam("entity_id", "int", "Entity number", required=False, default="1"),
                ],
                returns="Dict with entity data",
                example='entity = await pdb.get_entity("1TUP")',
            ),
            Operation(
                name="pdb.text_search",
                module="pdb",
                method="pdb.text_search(text, max_results=10)",
                description="Full-text search for PDB structures by keyword",
                tags=["pdb", "structure", "search"],
                params=[
                    OperationParam("text", "str", "Search text (e.g., 'CRISPR', 'hemoglobin')"),
                    OperationParam("max_results", "int", "Max results", required=False, default="10"),
                ],
                returns="List of result dicts with identifier and score",
                example='results = await pdb.text_search("CRISPR-Cas9")',
            ),
            Operation(
                name="pdb.search_by_uniprot",
                module="pdb",
                method="pdb.search_by_uniprot(uniprot_id)",
                description="Find PDB structures associated with a UniProt accession",
                tags=["pdb", "structure", "uniprot", "cross-reference"],
                params=[
                    OperationParam("uniprot_id", "str", "UniProt accession (e.g., P04637)"),
                ],
                returns="List of matching PDB entries",
                example='structures = await pdb.search_by_uniprot("P04637")',
            ),
            Operation(
                name="pdb.get_structure_summary",
                module="pdb",
                method="pdb.get_structure_summary(pdb_id)",
                description="Get a concise summary (title, resolution, method, dates) for a PDB structure",
                tags=["pdb", "structure", "summary"],
                params=[
                    OperationParam("pdb_id", "str", "PDB ID"),
                ],
                returns="Dict with title, resolution, method, dates",
                example='summary = await pdb.get_structure_summary("6LU7")',
            ),
        ]
        self._operations.extend(ops)

    # ------------------------------------------------------------------
    # Ensembl operations
    # ------------------------------------------------------------------

    def _register_ensembl_operations(self) -> None:
        ops = [
            Operation(
                name="ensembl.lookup_id",
                module="ensembl",
                method="ensembl.lookup_id(ensembl_id, expand=True)",
                description="Look up an Ensembl stable ID and return gene/transcript/protein details",
                tags=["ensembl", "gene", "lookup", "genomic"],
                params=[
                    OperationParam("ensembl_id", "str", "Ensembl ID (e.g., ENSG00000141510)"),
                    OperationParam("expand", "bool", "Include child objects", required=False, default="True"),
                ],
                returns="Dict with gene/transcript details",
                example='gene = await ensembl.lookup_id("ENSG00000141510")',
            ),
            Operation(
                name="ensembl.lookup_symbol",
                module="ensembl",
                method="ensembl.lookup_symbol(species, symbol, expand=True)",
                description="Look up a gene by symbol and species in Ensembl",
                tags=["ensembl", "gene", "symbol", "lookup"],
                params=[
                    OperationParam("species", "str", "Species: homo_sapiens, mus_musculus, etc."),
                    OperationParam("symbol", "str", "Gene symbol (e.g., BRCA2)"),
                ],
                returns="Dict with gene details and transcripts",
                example='gene = await ensembl.lookup_symbol("homo_sapiens", "BRCA2")',
            ),
            Operation(
                name="ensembl.get_sequence",
                module="ensembl",
                method="ensembl.get_sequence(ensembl_id, seq_type='genomic', format_='json')",
                description="Get nucleotide or protein sequence for an Ensembl ID",
                tags=["ensembl", "sequence", "genomic", "cdna", "protein"],
                params=[
                    OperationParam("ensembl_id", "str", "Ensembl ID"),
                    OperationParam("seq_type", "str", "genomic, cdna, cds, or protein", required=False, default="genomic"),
                ],
                returns="Sequence data dict or FASTA string",
                example='seq = await ensembl.get_sequence("ENST00000269305", seq_type="cds")',
            ),
            Operation(
                name="ensembl.get_variant",
                module="ensembl",
                method="ensembl.get_variant(variant_id, species='human')",
                description="Get details for a known variant (rsID) including alleles and MAF",
                tags=["ensembl", "variant", "snp", "variation"],
                params=[
                    OperationParam("variant_id", "str", "Variant ID (e.g., rs699)"),
                    OperationParam("species", "str", "Species name", required=False, default="human"),
                ],
                returns="Dict with variant alleles, MAF, consequences",
                example='variant = await ensembl.get_variant("rs699")',
            ),
            Operation(
                name="ensembl.get_vep",
                module="ensembl",
                method="ensembl.get_vep(species, hgvs_notation)",
                description="Run Variant Effect Predictor (VEP) for an HGVS notation to get consequence predictions",
                tags=["ensembl", "vep", "variant", "consequence", "prediction"],
                params=[
                    OperationParam("species", "str", "Species name"),
                    OperationParam("hgvs_notation", "str", "HGVS notation"),
                ],
                returns="List of predicted variant consequences",
                example='effects = await ensembl.get_vep("human", "ENST00000269305.9:c.817C>T")',
            ),
            Operation(
                name="ensembl.get_xrefs",
                module="ensembl",
                method="ensembl.get_xrefs(ensembl_id)",
                description="Get cross-references for an Ensembl ID (UniProt, HGNC, RefSeq, etc.)",
                tags=["ensembl", "cross-reference", "xref"],
                params=[
                    OperationParam("ensembl_id", "str", "Ensembl ID"),
                ],
                returns="List of cross-reference dicts",
                example='xrefs = await ensembl.get_xrefs("ENSG00000141510")',
            ),
            Operation(
                name="ensembl.get_gene_summary",
                module="ensembl",
                method="ensembl.get_gene_summary(symbol, species='homo_sapiens')",
                description="Get a compact gene summary by symbol from Ensembl",
                tags=["ensembl", "gene", "summary"],
                params=[
                    OperationParam("symbol", "str", "Gene symbol"),
                    OperationParam("species", "str", "Species name", required=False, default="homo_sapiens"),
                ],
                returns="Dict with id, biotype, location, description",
                example='summary = await ensembl.get_gene_summary("TP53")',
            ),
        ]
        self._operations.extend(ops)

    # ------------------------------------------------------------------
    # BLAST operations
    # ------------------------------------------------------------------

    def _register_blast_operations(self) -> None:
        ops = [
            Operation(
                name="blast.submit",
                module="blast",
                method="blast.submit(program, database, sequence, megablast=False, expect=10.0, hitlist_size=50)",
                description="Submit a BLAST search job and get a Request ID (RID) for polling",
                tags=["blast", "sequence", "alignment", "similarity", "search"],
                params=[
                    OperationParam("program", "str", "blastn, blastp, blastx, tblastn, tblastx"),
                    OperationParam("database", "str", "Target DB: nt, nr, swissprot, pdb, refseq_rna"),
                    OperationParam("sequence", "str", "Query sequence (FASTA or raw)"),
                ],
                returns="Request ID (RID) string",
                example='rid = await blast.submit("blastp", "swissprot", protein_seq)',
            ),
            Operation(
                name="blast.wait_for_results",
                module="blast",
                method="blast.wait_for_results(rid, format_type='JSON2')",
                description="Poll a BLAST job until complete and return results",
                tags=["blast", "results", "poll"],
                params=[
                    OperationParam("rid", "str", "Request ID from submit()"),
                ],
                returns="BLAST results dict or text",
                example='results = await blast.wait_for_results(rid)',
            ),
            Operation(
                name="blast.blastn",
                module="blast",
                method="blast.blastn(sequence, database='nt', max_hits=10, wait=True)",
                description="Run nucleotide BLAST — submit, wait, and return results in one call",
                tags=["blast", "nucleotide", "sequence", "search", "alignment"],
                params=[
                    OperationParam("sequence", "str", "Nucleotide sequence"),
                    OperationParam("database", "str", "Target DB", required=False, default="nt"),
                    OperationParam("max_hits", "int", "Max hits", required=False, default="10"),
                ],
                returns="BLAST results",
                example='results = await blast.blastn("ATGCGATCGATCG...")',
            ),
            Operation(
                name="blast.blastp",
                module="blast",
                method="blast.blastp(sequence, database='nr', max_hits=10, wait=True)",
                description="Run protein BLAST — submit, wait, and return results in one call",
                tags=["blast", "protein", "sequence", "search", "alignment"],
                params=[
                    OperationParam("sequence", "str", "Protein sequence"),
                    OperationParam("database", "str", "Target DB: nr, swissprot, pdb", required=False, default="nr"),
                    OperationParam("max_hits", "int", "Max hits", required=False, default="10"),
                ],
                returns="BLAST results",
                example='results = await blast.blastp("MEEPQSDP...")',
            ),
        ]
        self._operations.extend(ops)

    # ------------------------------------------------------------------
    # Sequence utility operations
    # ------------------------------------------------------------------

    def _register_sequence_utilities(self) -> None:
        ops = [
            Operation(
                name="seq.reverse_complement",
                module="sequence_utils",
                method="seq_utils.reverse_complement(sequence)",
                description="Get the reverse complement of a DNA sequence",
                tags=["sequence", "dna", "complement", "utility"],
                params=[OperationParam("sequence", "str", "DNA sequence")],
                returns="Reverse complement string",
                example='rc = seq_utils.reverse_complement("ATGCGATCG")',
            ),
            Operation(
                name="seq.translate",
                module="sequence_utils",
                method="seq_utils.translate(dna, reading_frame=0)",
                description="Translate DNA to protein sequence using standard genetic code",
                tags=["sequence", "translation", "protein", "utility"],
                params=[
                    OperationParam("dna", "str", "DNA sequence"),
                    OperationParam("reading_frame", "int", "0, 1, or 2", required=False, default="0"),
                ],
                returns="Protein sequence (single-letter codes)",
                example='protein = seq_utils.translate("ATGGCCATTGTAATGGGCCGC")',
            ),
            Operation(
                name="seq.gc_content",
                module="sequence_utils",
                method="seq_utils.gc_content(sequence)",
                description="Calculate GC content of a nucleotide sequence",
                tags=["sequence", "gc", "composition", "utility"],
                params=[OperationParam("sequence", "str", "DNA/RNA sequence")],
                returns="GC fraction (0.0 to 1.0)",
                example='gc = seq_utils.gc_content("ATGCGATCGATCG")',
            ),
            Operation(
                name="seq.find_orfs",
                module="sequence_utils",
                method="seq_utils.find_orfs(dna, min_length=100)",
                description="Find all open reading frames (ORFs) in a DNA sequence",
                tags=["sequence", "orf", "gene", "prediction", "utility"],
                params=[
                    OperationParam("dna", "str", "DNA sequence"),
                    OperationParam("min_length", "int", "Min ORF length in nt", required=False, default="100"),
                ],
                returns="List of ORF dicts (start, end, length, frame, protein)",
                example='orfs = seq_utils.find_orfs(dna_sequence, min_length=300)',
            ),
            Operation(
                name="seq.restriction_sites",
                module="sequence_utils",
                method="seq_utils.restriction_sites(sequence, enzyme_patterns=None)",
                description="Find restriction enzyme cut sites in a DNA sequence",
                tags=["sequence", "restriction", "enzyme", "cloning", "utility"],
                params=[
                    OperationParam("sequence", "str", "DNA sequence"),
                    OperationParam("enzyme_patterns", "dict", "Custom enzyme→pattern dict", required=False),
                ],
                returns="Dict of enzyme_name → list of positions",
                example='sites = seq_utils.restriction_sites(dna_sequence)',
            ),
            Operation(
                name="seq.molecular_weight",
                module="sequence_utils",
                method="seq_utils.molecular_weight(sequence, seq_type='protein')",
                description="Estimate molecular weight of a protein or DNA sequence",
                tags=["sequence", "molecular_weight", "protein", "utility"],
                params=[
                    OperationParam("sequence", "str", "Sequence string"),
                    OperationParam("seq_type", "str", "protein or dna", required=False, default="protein"),
                ],
                returns="Molecular weight in Daltons",
                example='mw = seq_utils.molecular_weight("MEEPQSDP", seq_type="protein")',
            ),
            Operation(
                name="seq.transcribe",
                module="sequence_utils",
                method="seq_utils.transcribe(dna)",
                description="Transcribe DNA to mRNA (T → U)",
                tags=["sequence", "transcription", "rna", "utility"],
                params=[OperationParam("dna", "str", "DNA sequence")],
                returns="mRNA sequence",
                example='mrna = seq_utils.transcribe("ATGCGATCG")',
            ),
            Operation(
                name="seq.nucleotide_composition",
                module="sequence_utils",
                method="seq_utils.nucleotide_composition(sequence)",
                description="Count nucleotide frequencies in a sequence",
                tags=["sequence", "composition", "utility"],
                params=[OperationParam("sequence", "str", "Nucleotide sequence")],
                returns="Dict of base → count",
                example='comp = seq_utils.nucleotide_composition("ATGCGATCG")',
            ),
            Operation(
                name="seq.amino_acid_composition",
                module="sequence_utils",
                method="seq_utils.amino_acid_composition(sequence)",
                description="Count amino acid frequencies in a protein sequence",
                tags=["sequence", "protein", "composition", "utility"],
                params=[OperationParam("sequence", "str", "Protein sequence")],
                returns="Dict of amino acid → count",
                example='comp = seq_utils.amino_acid_composition("MEEPQSDPSVEP")',
            ),
        ]
        self._operations.extend(ops)

    # ------------------------------------------------------------------
    # Format utility operations
    # ------------------------------------------------------------------

    def _register_format_utilities(self) -> None:
        ops = [
            Operation(
                name="fmt.parse_fasta",
                module="format_utils",
                method="fmt.parse_fasta(text)",
                description="Parse FASTA-formatted text into structured records",
                tags=["format", "fasta", "parser", "utility"],
                params=[OperationParam("text", "str", "FASTA-formatted string")],
                returns="List of FastaRecord objects (id, description, sequence, length)",
                example='records = fmt.parse_fasta(fasta_text)',
            ),
            Operation(
                name="fmt.write_fasta",
                module="format_utils",
                method="fmt.write_fasta(records, line_width=80)",
                description="Write FastaRecord objects to FASTA format",
                tags=["format", "fasta", "writer", "utility"],
                params=[OperationParam("records", "list", "List of FastaRecord objects")],
                returns="FASTA-formatted string",
                example='text = fmt.write_fasta(records)',
            ),
            Operation(
                name="fmt.parse_gff",
                module="format_utils",
                method="fmt.parse_gff(text)",
                description="Parse GFF3-formatted text into structured records",
                tags=["format", "gff", "annotation", "parser", "utility"],
                params=[OperationParam("text", "str", "GFF3 text")],
                returns="List of GFFRecord objects",
                example='features = fmt.parse_gff(gff_text)',
            ),
            Operation(
                name="fmt.parse_bed",
                module="format_utils",
                method="fmt.parse_bed(text)",
                description="Parse BED-formatted text into structured records",
                tags=["format", "bed", "genomic", "parser", "utility"],
                params=[OperationParam("text", "str", "BED text")],
                returns="List of BEDRecord objects",
                example='regions = fmt.parse_bed(bed_text)',
            ),
            Operation(
                name="fmt.parse_clustal",
                module="format_utils",
                method="fmt.parse_clustal(text)",
                description="Parse Clustal alignment format into id→sequence dict",
                tags=["format", "clustal", "alignment", "parser", "utility"],
                params=[OperationParam("text", "str", "Clustal alignment text")],
                returns="Dict of sequence_id → aligned sequence",
                example='alignment = fmt.parse_clustal(clustal_text)',
            ),
        ]
        self._operations.extend(ops)
