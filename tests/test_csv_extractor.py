from pipelines.ingestion.extractors.csv_extractor import CSVExtractor


def test_csv_extractor():

    extractor = CSVExtractor()

    assert extractor is not None