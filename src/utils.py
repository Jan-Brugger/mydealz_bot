from __future__ import annotations

import logging
import re

from price_parser import Price

from src.models import PriceModel

logger = logging.getLogger(__name__)


def is_valid_regex_query(query: str | None) -> bool:
    if query and query.startswith("r/"):
        try:
            re.compile(query.lstrip("r/"))
        except re.error:
            pass
        else:
            return True

    return False


def prettify_query(query: str) -> str:
    if is_valid_regex_query(query):
        return query

    query = " ".join(query.split()).lower()  # remove unnecessary whitespaces and lower
    query = re.sub(r"[! ]{2,}", "!", query)  # remove redundant exclamation marks
    query = re.sub(r"[, ]{2,}", ",", query)  # remove redundant commas
    queries = re.findall(r"([&,])?\s*(!?[^&,!\s]+)", query)  # find queries
    query = "".join([f"{q[0] or '&'}{q[1]}" for q in queries])  # put together

    return query.strip("&, ").replace("&", " & ").replace(",", ", ")


def parse_price(price_str: str) -> PriceModel:
    price = Price.fromstring(price_str)

    return PriceModel(amount=float(price.amount or 0), currency=price.currency or "")


def remove_html_tags(text: str) -> str:
    text = re.sub(r"<.*?>", " ", text)  # remove html tags

    return " ".join(text.split())  # remove and strip spaces
