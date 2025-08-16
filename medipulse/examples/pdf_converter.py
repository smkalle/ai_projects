#!/usr/bin/env python3
"""
PDF to Image Converter for MediPulse

This utility converts PDF medical documents to images for processing with MediPulse.

Usage:
    python examples/pdf_converter.py input.pdf
    python examples/pdf_converter.py input.pdf --output-dir ./images/
"""

import argparse
import sys
from pathlib import Path

try:
    from pdf2image import convert_from_path
    from PIL import Image
except ImportError:
    print("Error: Required packages not found.")
    print("Install with: pip install pdf2image pillow")
    sys.exit(1)

def convert_pdf_to_images(pdf_path, output_dir=None, dpi=200):
    """
    Convert PDF to images

    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory (default: same as PDF)
        dpi: Resolution for conversion (default: 200)
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if output_dir is None:
        output_dir = pdf_path.parent / f"{pdf_path.stem}_images"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(exist_ok=True)

    print(f"Converting {pdf_path} to images...")
    print(f"Output directory: {output_dir}")

    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)

        image_paths = []
        for i, image in enumerate(images):
            output_path = output_dir / f"page_{i+1:03d}.jpg"
            image.save(output_path, "JPEG", quality=95)
            image_paths.append(output_path)
            print(f"  Saved: {output_path}")

        print(f"\nConversion complete! Created {len(image_paths)} images.")
        return image_paths

    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Convert PDF medical documents to images for MediPulse")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", "-o", help="Output directory for images")
    parser.add_argument("--dpi", type=int, default=200, help="DPI for image conversion (default: 200)")

    args = parser.parse_args()

    try:
        image_paths = convert_pdf_to_images(args.pdf_path, args.output_dir, args.dpi)

        print("\nNext steps:")
        print("1. Use these images with MediPulse:")
        for path in image_paths:
            print(f"   medipulse.process_document_from_file('{path}')")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
