from pipelines.ingestion.extractors.url_extractor import URLExtractor


def test_url_extractor():

    extractor = URLExtractor()

    assert extractor is not None