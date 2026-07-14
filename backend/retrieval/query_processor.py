import re


class QueryProcessor:
    """
    Handles query preprocessing before retrieval.
    """


    async def process(
        self,
        query: str
    ):

        return {
            "original_query": query,

            "expanded_queries": [
                query,
                f"Explain {query}",
                f"Detailed information about {query}"
            ],

            "filters": self.extract_filters(query),

            "query_type": self.classify_query(query)
        }



    def extract_filters(
        self,
        query: str
    ):

        filters = {}

        year = re.search(
            r"\b(20\d{2})\b",
            query
        )

        if year:
            filters["year"] = int(year.group())


        if "climate" in query.lower():
            filters["topic"] = "climate"


        return filters



    def classify_query(
        self,
        query: str
    ):

        query = query.lower()


        if "compare" in query:
            return "comparative"


        if "how" in query:
            return "procedural"


        if "why" in query:
            return "analytical"


        return "factual"