"""
MediPulse: Agentic Workflow for Medical Document Extraction

A prototype designed for medical workflows, inspired by Pulse AI's document extraction platform.
"""

from .medipulse import (
    MediPulse,
    MediPulseConfig,
    DocumentType,
    ExtractedData,
    ValidationResult,
    MediState
)

__version__ = "0.1.0"
__author__ = "MediPulse Contributors"
__email__ = "contributors@medipulse.dev"

__all__ = [
    "MediPulse",
    "MediPulseConfig", 
    "DocumentType",
    "ExtractedData",
    "ValidationResult",
    "MediState"
]
