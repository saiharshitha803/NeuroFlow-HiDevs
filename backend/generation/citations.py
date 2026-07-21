import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Citation:
    """
    Structured citation information.
    """

    reference: str
    chunk_id: str
    document_name: str
    page_number: Optional[int]
    content_preview: str



class CitationParser:
    """
    Extracts [Source N] references from generated answers
    and maps them back to retrieved chunks.
    """


    SOURCE_PATTERN = r"\[Source (\d+)\]"


    def parse(
        self,
        response: str,
        context_sources: list,
    ) -> list[Citation | dict]:

        citations = []


        matches = re.findall(
            self.SOURCE_PATTERN,
            response,
        )


        for source_number in matches:

            index = int(source_number) - 1


            # Hallucinated citation
            if index >= len(context_sources):

                citations.append(
                    {
                        "reference": f"Source {source_number}",
                        "invalid_citation": True,
                    }
                )

                continue



            source = context_sources[index]


            citations.append(
                Citation(
                    reference=f"Source {source_number}",
                    chunk_id=str(
                        source.get("chunk_id")
                    ),
                    document_name=source.get(
                        "document",
                        "unknown",
                    ),
                    page_number=source.get(
                        "page"
                    ),
                    content_preview=source.get(
                        "content",
                        "",
                    )[:100],
                )
            )


        return citations