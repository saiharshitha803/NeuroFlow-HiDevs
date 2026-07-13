from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
import trafilatura

from pipelines.ingestion.models import ExtractedPage


class URLExtractor:
    """
    Extract readable content from web pages while
    respecting robots.txt.
    """

    async def _allowed(
        self,
        url: str,
    ) -> bool:

        parsed = urlparse(url)

        robots_url = urljoin(
            f"{parsed.scheme}://{parsed.netloc}",
            "/robots.txt",
        )

        parser = RobotFileParser()

        parser.set_url(robots_url)

        try:
            parser.read()
        except Exception:
            return False

        return parser.can_fetch("*", url)

    async def extract(
        self,
        url: str,
    ) -> list[ExtractedPage]:

        if not await self._allowed(url):
            raise PermissionError(
                "robots.txt blocks crawling."
            )

        async with httpx.AsyncClient(
            timeout=30
        ) as client:

            response = await client.get(url)

            response.raise_for_status()

            html = response.text

        content = trafilatura.extract(
            html,
            include_tables=True,
            with_metadata=True,
        )

        metadata = trafilatura.extract_metadata(
            html
        )

        return [

            ExtractedPage(

                page_number=1,

                content=content or "",

                content_type="text",

                metadata={
                    "title": getattr(
                        metadata,
                        "title",
                        None,
                    ),
                    "author": getattr(
                        metadata,
                        "author",
                        None,
                    ),
                    "url": url,
                    "canonical_url": getattr(
                        metadata,
                        "url",
                        None,
                    ),
                    "publish_date": getattr(
                        metadata,
                        "date",
                        None,
                    ),
                },

            )

        ]