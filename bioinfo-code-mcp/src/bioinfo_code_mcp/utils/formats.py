"""Bioinformatics file format parsers for the Code MCP sandbox.

Lightweight parsers for common formats (FASTA, GenBank, GFF, BED) that
agents can use to process data returned from API calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FastaRecord:
    """A single FASTA record."""

    header: str
    sequence: str

    @property
    def id(self) -> str:
        """Extract the ID (first word of header)."""
        return self.header.split()[0] if self.header else ""

    @property
    def description(self) -> str:
        """Everything after the ID in the header."""
        parts = self.header.split(maxsplit=1)
        return parts[1] if len(parts) > 1 else ""

    @property
    def length(self) -> int:
        return len(self.sequence)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "sequence": self.sequence,
            "length": self.length,
        }


def parse_fasta(text: str) -> list[FastaRecord]:
    """Parse FASTA-formatted text into records.

    Args:
        text: FASTA-formatted string (one or more records).

    Returns:
        List of FastaRecord objects.
    """
    records: list[FastaRecord] = []
    current_header = ""
    current_seq_parts: list[str] = []

    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_header or current_seq_parts:
                records.append(FastaRecord(
                    header=current_header,
                    sequence="".join(current_seq_parts),
                ))
            current_header = line[1:].strip()
            current_seq_parts = []
        else:
            current_seq_parts.append(line)

    if current_header or current_seq_parts:
        records.append(FastaRecord(
            header=current_header,
            sequence="".join(current_seq_parts),
        ))

    return records


def write_fasta(records: list[FastaRecord], line_width: int = 80) -> str:
    """Write FASTA records to a formatted string.

    Args:
        records: List of FastaRecord objects.
        line_width: Characters per sequence line.

    Returns:
        FASTA-formatted string.
    """
    lines: list[str] = []
    for rec in records:
        lines.append(f">{rec.header}")
        seq = rec.sequence
        for i in range(0, len(seq), line_width):
            lines.append(seq[i : i + line_width])
    return "\n".join(lines) + "\n"


@dataclass
class GFFRecord:
    """A single GFF3/GTF record."""

    seqid: str
    source: str
    feature_type: str
    start: int
    end: int
    score: str
    strand: str
    phase: str
    attributes: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "seqid": self.seqid,
            "source": self.source,
            "type": self.feature_type,
            "start": self.start,
            "end": self.end,
            "score": self.score,
            "strand": self.strand,
            "phase": self.phase,
            "attributes": self.attributes,
        }


def parse_gff(text: str) -> list[GFFRecord]:
    """Parse GFF3-formatted text.

    Args:
        text: GFF3-formatted string.

    Returns:
        List of GFFRecord objects.
    """
    records: list[GFFRecord] = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 9:
            continue

        # Parse attributes (key=value pairs separated by ;)
        attrs: dict[str, str] = {}
        for attr in parts[8].split(";"):
            attr = attr.strip()
            if "=" in attr:
                k, v = attr.split("=", 1)
                attrs[k.strip()] = v.strip()

        records.append(GFFRecord(
            seqid=parts[0],
            source=parts[1],
            feature_type=parts[2],
            start=int(parts[3]),
            end=int(parts[4]),
            score=parts[5],
            strand=parts[6],
            phase=parts[7],
            attributes=attrs,
        ))
    return records


@dataclass
class BEDRecord:
    """A single BED record."""

    chrom: str
    start: int
    end: int
    name: str = ""
    score: int = 0
    strand: str = "."

    @property
    def length(self) -> int:
        return self.end - self.start

    def to_dict(self) -> dict[str, Any]:
        return {
            "chrom": self.chrom,
            "start": self.start,
            "end": self.end,
            "name": self.name,
            "score": self.score,
            "strand": self.strand,
            "length": self.length,
        }


def parse_bed(text: str) -> list[BEDRecord]:
    """Parse BED-formatted text.

    Args:
        text: BED-formatted string (BED3 through BED6 supported).

    Returns:
        List of BEDRecord objects.
    """
    records: list[BEDRecord] = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("track") or line.startswith("browser"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        rec = BEDRecord(
            chrom=parts[0],
            start=int(parts[1]),
            end=int(parts[2]),
        )
        if len(parts) > 3:
            rec.name = parts[3]
        if len(parts) > 4:
            try:
                rec.score = int(parts[4])
            except ValueError:
                pass
        if len(parts) > 5:
            rec.strand = parts[5]
        records.append(rec)
    return records


def parse_clustal(text: str) -> dict[str, str]:
    """Parse a simple Clustal alignment into a dict of id → aligned sequence.

    Args:
        text: Clustal-formatted alignment text.

    Returns:
        Dict mapping sequence ID to its aligned sequence.
    """
    sequences: dict[str, list[str]] = {}
    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("CLUSTAL") or line.startswith(" ") or line.startswith("*"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            seq_id = parts[0]
            seq_fragment = parts[1]
            if seq_id not in sequences:
                sequences[seq_id] = []
            sequences[seq_id].append(seq_fragment)
    return {k: "".join(v) for k, v in sequences.items()}
