"""
PDF Processing Module for Energy Document AI
Uses pypdfium2 for high-resolution rendering and GPT-4o for OCR extraction
"""

import pypdfium2 as pdfium
from PIL import Image
from io import BytesIO
import base64
from openai import OpenAI
import os
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class EnergyPDFProcessor:
    """PDF processor optimized for energy sector documents with figures and tables"""

    def __init__(self, openai_api_key: str, dpi: int = 300):
        self.client = OpenAI(api_key=openai_api_key)
        self.dpi = dpi

    def render_page_to_image(self, pdf_path: str, page_num: int) -> Image.Image:
        """Render PDF page to high-resolution image"""
        try:
            pdf = pdfium.PdfDocument(pdf_path)
            page = pdf.get_page(page_num)
            # Render at high DPI for better OCR quality
            pil_image = page.render(scale=self.dpi / 72).to_pil()
            page.close()
            pdf.close()
            return pil_image
        except Exception as e:
            logger.error(f"Error rendering page {page_num}: {e}")
            raise

    def image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL image to base64 string"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def ocr_page_with_gpt4o(self, base64_image: str, page_context: str = "energy") -> str:
        """Extract text from image using GPT-4o with energy sector context"""
        energy_prompt = f"""
        Extract all text from this {page_context} document page, paying special attention to:

        1. Technical specifications and measurements
        2. Regulatory references and compliance requirements
        3. Tables with numerical data (energy consumption, efficiency ratings, etc.)
        4. Figure captions and diagrams descriptions
        5. Safety protocols and environmental impact data
        6. Equipment specifications and performance metrics

        Format the output in markdown with:
        - Proper headings and structure
        - Tables formatted as markdown tables
        - Figure descriptions clearly marked
        - Technical terms preserved exactly

        If you encounter tables, preserve all numerical values and units.
        If you see diagrams or charts, provide detailed descriptions of what they show.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": energy_prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}},
                        ],
                    }
                ],
                max_tokens=2000,
                temperature=0.1,  # Low temperature for accuracy
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in OCR processing: {e}")
            return f"Error processing page: {e}"

    def extract_text_from_pdf(self, pdf_path: str, document_type: str = "energy") -> Dict[int, str]:
        """Extract text from all pages of PDF with energy sector optimization"""
        try:
            pdf = pdfium.PdfDocument(pdf_path)
            num_pages = len(pdf)
            extracted_pages = {}

            logger.info(f"Processing {num_pages} pages from {pdf_path}")

            for page_num in range(num_pages):
                logger.info(f"Processing page {page_num + 1}/{num_pages}")

                # Render page to image
                image = self.render_page_to_image(pdf_path, page_num)

                # Convert to base64
                base64_image = self.image_to_base64(image)

                # Extract text with GPT-4o
                page_text = self.ocr_page_with_gpt4o(base64_image, document_type)

                extracted_pages[page_num] = {
                    'text': page_text,
                    'page_number': page_num + 1,
                    'document_type': document_type
                }

            pdf.close()
            return extracted_pages

        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            raise

    def extract_and_combine_text(self, pdf_path: str, document_type: str = "energy") -> str:
        """Extract and combine all text from PDF"""
        extracted_pages = self.extract_text_from_pdf(pdf_path, document_type)

        combined_text = f"# Document: {os.path.basename(pdf_path)}\n\n"

        for page_num, page_data in extracted_pages.items():
            combined_text += f"## Page {page_data['page_number']}\n\n"
            combined_text += page_data['text']
            combined_text += "\n\n---\n\n"

        return combined_text
