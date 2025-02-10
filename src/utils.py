from __future__ import annotations

import re

from src.models import PriceModel


def is_valid_regex_query(query: str) -> bool:
    if query.startswith("r/"):
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
    price_str = re.sub(r"[^\d.]", "", price_str.replace(",", "."))

    if "." not in price_str:
        amount = float(price_str or 0)
    else:
        price_split = price_str.split(".")
        amount = float(f"{''.join(price_split[0:-1])}.{price_split[-1]}")

    return PriceModel(amount=amount, currency="€")
