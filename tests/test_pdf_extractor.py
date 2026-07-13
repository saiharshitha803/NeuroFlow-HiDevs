from backend.pipelines.ingestion.extractors.pdf_extractor import PDFExtractor


def test_pdf_extractor_exists():
    extractor = PDFExtractor()
    assert extractor is not None