from __future__ import annotations

import re
from abc import abstractmethod


class Queries:
    def __init__(self, query: str):
        self._queries: set[Query] = set()

        if query.strip().startswith("r/"):
            self._queries.add(RegexQuery(query))

            return

        for query_part in query.split(","):
            self._queries.add(AndQuery(query_part))

    def any_match(self, text: str) -> bool:
        return any(query.matches(text) for query in self._queries)


class Query:
    @abstractmethod
    def matches(self, text: str) -> bool:
        """Check if the query is matching the given text.

        :param text: The text to check if the query matches
        :return: True if match false if not
        """
        raise NotImplementedError


class AndQuery(Query):
    def __init__(self, query_string: str):
        self._contains: set[str] = set()
        self._contains_not: set[str] = set()

        for query in query_string.split("&"):
            stripped_query = query.strip().replace("+", " ")

            if stripped_query.startswith("!"):
                self._contains_not.add(stripped_query.lstrip(" !"))
            else:
                self._contains.add(stripped_query)

    def matches(self, text: str) -> bool:
        text = text.lower()

        return not any(cn in text for cn in self._contains_not) and all(c in text for c in self._contains)


class RegexQuery(Query):
    def __init__(self, query: str):
        flags = 0
        query = query.strip().removeprefix("r/")

        if query.endswith(r"/i"):
            flags = re.IGNORECASE
            query = query.removesuffix(r"/i").rstrip("\\")

        self._regex_query = re.compile(query, flags=flags)

    def matches(self, text: str) -> bool:
        try:
            return bool(re.search(self._regex_query, text))
        except re.error:
            return False
