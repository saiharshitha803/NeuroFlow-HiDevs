from pathlib import Path

import pandas as pd
from tabulate import tabulate

from pipelines.ingestion.models import ExtractedPage


class CSVExtractor:
    """
    Extract structured information from CSV files.
    """

    def extract(
        self,
        file_path: str | Path,
    ) -> list[ExtractedPage]:

        df = pd.read_csv(file_path)

        extracted_pages: list[ExtractedPage] = []

        row_count = len(df)

        numeric_columns = list(
            df.select_dtypes(include="number").columns
        )

        text_columns = list(
            df.select_dtypes(exclude="number").columns
        )

        # -------------------------
        # Small CSV
        # -------------------------

        if row_count < 1000:

            for start in range(0, row_count, 100):

                chunk = df.iloc[start:start + 100]

                markdown = tabulate(
                    chunk,
                    headers="keys",
                    tablefmt="github",
                    showindex=False,
                )

                extracted_pages.append(

                    ExtractedPage(

                        page_number=(start // 100) + 1,

                        content=markdown,

                        content_type="table",

                        metadata={
                            "rows": len(chunk),
                            "numeric_columns": numeric_columns,
                            "text_columns": text_columns,
                            "source": str(file_path),
                        },

                    )

                )

            return extracted_pages

        # -------------------------
        # Large CSV
        # -------------------------

        summary = []

        summary.append(
            f"Total Rows: {row_count}"
        )

        summary.append(
            f"Total Columns: {len(df.columns)}"
        )

        summary.append("")

        summary.append("Numeric Columns:")

        for column in numeric_columns:

            summary.append(
                f"{column}"
            )

            summary.append(
                f"  Min : {df[column].min()}"
            )

            summary.append(
                f"  Max : {df[column].max()}"
            )

            summary.append(
                f"  Mean: {df[column].mean()}"
            )

            summary.append("")

        summary.append("Categorical Columns:")

        for column in text_columns:

            summary.append(column)

            values = (
                df[column]
                .value_counts()
                .head(5)
            )

            summary.append(values.to_string())

            summary.append("")

        extracted_pages.append(

            ExtractedPage(

                page_number=1,

                content="\n".join(summary),

                content_type="text",

                metadata={
                    "summary": True,
                    "source": str(file_path),
                },

            )

        )

        for start in range(0, row_count, 100):

            chunk = df.iloc[start:start + 100]

            markdown = tabulate(
                chunk,
                headers="keys",
                tablefmt="github",
                showindex=False,
            )

            extracted_pages.append(

                ExtractedPage(

                    page_number=(start // 100) + 2,

                    content=markdown,

                    content_type="table",

                    metadata={
                        "rows": len(chunk),
                        "source": str(file_path),
                    },

                )

            )

        return extracted_pages