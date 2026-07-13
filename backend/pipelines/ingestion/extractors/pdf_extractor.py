from pathlib import Path

import pdfplumber
import pypdfium2 as pdfium

from .base import ExtractedPage


class PDFExtractor:
    """
    Extract text and tables from PDF documents.
    """

    def extract(
        self,
        file_path: str,
    ) -> list[ExtractedPage]:

        pages: list[ExtractedPage] = []

        pdf = pdfium.PdfDocument(file_path)

        with pdfplumber.open(file_path) as plumber_pdf:

            for index in range(len(pdf)):

                page = pdf[index]

                text_page = page.get_textpage()
                text = text_page.get_text_range().strip()

                # Detect scanned pages
                scanned = len(text) < 50

                pages.append(
                    ExtractedPage(
                        page_number=index + 1,
                        content=text,
                        content_type="text",
                        metadata={
                            "page": index + 1,
                            "scanned": scanned,
                        },
                    )
                )

                # Extract tables
                plumber_page = plumber_pdf.pages[index]

                tables = plumber_page.extract_tables()

                for table in tables:

                    markdown = ""

                    for row in table:
                        markdown += (
                            "| "
                            + " | ".join(
                                str(cell) if cell else ""
                                for cell in row
                            )
                            + " |\n"
                        )

                    pages.append(
                        ExtractedPage(
                            page_number=index + 1,
                            content=markdown,
                            content_type="table",
                            metadata={
                                "page": index + 1,
                            },
                        )
                    )

        return pages