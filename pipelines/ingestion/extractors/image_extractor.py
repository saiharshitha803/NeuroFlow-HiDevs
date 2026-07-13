from pathlib import Path

import pytesseract
from PIL import Image

from backend.providers.base import ChatMessage
from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria

from pipelines.ingestion.models import ExtractedPage


class ImageExtractor:
    """
    Extract information from images using
    OCR + Vision LLM.
    """

    def __init__(
        self,
        client: NeuroFlowClient,
    ):
        self.client = client

        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

    def _resize_image(
        self,
        image: Image.Image,
    ) -> Image.Image:

        image.thumbnail(
            (1024, 1024)
        )

        return image

    async def extract(
        self,
        file_path: str | Path,
    ) -> list[ExtractedPage]:

        image = Image.open(file_path)

        image = self._resize_image(image)

        ocr_text = pytesseract.image_to_string(
            image,
            config="--psm 6",
        )

        messages = [

            ChatMessage(

                role="user",

                content=[
                    {
                        "type": "text",
                        "text": (
                            "Describe this image in detail."
                        ),
                    },
                    {
                        "type": "image",
                        "image": str(file_path),
                    },
                ],
            )

        ]

        result = await self.client.chat(

            messages,

            RoutingCriteria(
                task_type="rag_generation",
                require_vision=True,
            ),

        )

        content = (
            result.content
            + "\n\nText found in image:\n"
            + ocr_text
        )

        return [

            ExtractedPage(

                page_number=1,

                content=content,

                content_type="image_description",

                metadata={

                    "source": str(file_path),

                    "ocr": True,

                    "vision": True,

                },

            )

        ]