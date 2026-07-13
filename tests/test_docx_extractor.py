from pipelines.ingestion.extractors.docx_extractor import DOCXExtractor


def test_docx_extractor():

    extractor = DOCXExtractor()

    assert extractor is not None
