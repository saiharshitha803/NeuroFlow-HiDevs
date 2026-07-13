from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium
import pytesseract
from tabulate import tabulate

from pipelines.ingestion.models import ExtractedPage


class PDFExtractor:
    """
    Extract text and tables from PDF documents.

    Features:
    - Digital PDF text extraction
    - OCR for scanned pages
    - Table extraction as Markdown
    - Preserves page metadata
    """

    def __init__(self) -> None:

        # Update if Tesseract is installed elsewhere.
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

    def _ocr_page(
        self,
        page: pdfium.PdfPage,
    ) -> str:
        """
        Run OCR on a scanned PDF page.
        """

        bitmap = page.render(scale=2)

        image = bitmap.to_pil()

        text = pytesseract.image_to_string(
            image,
            config="--psm 6",
        )

        return text.strip()

    def _extract_tables(
        self,
        file_path: str | Path,
    ) -> list[ExtractedPage]:
        """
        Extract tables from the PDF and convert
        them into Markdown.
        """

        extracted_tables = []

        with pdfplumber.open(str(file_path)) as pdf:

            for page_number, page in enumerate(
                pdf.pages,
                start=1,
            ):

                tables = page.extract_tables()

                for table in tables:

                    if not table:
                        continue

                    markdown = tabulate(
                        table,
                        headers="firstrow",
                        tablefmt="github",
                    )

                    extracted_tables.append(

                        ExtractedPage(

                            page_number=page_number,

                            content=markdown,

                            content_type="table",

                            metadata={
                                "page": page_number,
                                "source": str(file_path),
                            },
                        )
                    )

        return extracted_tables

    def extract(
        self,
        file_path: str | Path,
    ) -> list[ExtractedPage]:
        """
        Extract text and tables from a PDF.
        """

        pdf = pdfium.PdfDocument(str(file_path))

        extracted_pages = []

        try:

            for page_index in range(len(pdf)):

                page = pdf.get_page(page_index)

                text_page = page.get_textpage()

                try:

                    digital_text = (
                        text_page
                        .get_text_range()
                        .strip()
                    )

                    text = digital_text

                    ocr_used = False

                    # Detect scanned pages
                    if len(digital_text) < 50:

                        text = self._ocr_page(
                            page
                        )

                        ocr_used = True

                    extracted_pages.append(

                        ExtractedPage(

                            page_number=page_index + 1,

                            content=text,

                            content_type="text",

                            metadata={

                                "page": page_index + 1,

                                "source": str(file_path),

                                "ocr_used": ocr_used,

                            },
                        )

                    )

                finally:

                    text_page.close()

                    page.close()

        finally:

            pdf.close()

        # Extract tables separately

        extracted_pages.extend(

            self._extract_tables(
                file_path
            )

        )

        return extracted_pages