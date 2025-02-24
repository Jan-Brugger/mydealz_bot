from __future__ import annotations

import re

from src.models import PriceModel


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
    price_str = re.sub(re.compile(r"[^\d.,]"), "", price_str).strip(".,")

    if not price_str:
        amount = 0.0
    elif "." not in price_str and "," not in price_str:
        amount = float(price_str)
    elif "." in price_str and "," in price_str:
        price_split = price_str.replace(",", ".").split(".")
        amount = float(f"{''.join(price_split[0:-1])}.{price_split[-1]}")
    elif price_str.replace(",", ".").count(".") == 1:
        amount = float(price_str.replace(",", "."))
    else:
        amount = float("".join(c for c in price_str if c.isdigit()))

    return PriceModel(amount=amount, currency="€")


def remove_html_tags(text: str) -> str:
    text = re.sub(r"<.*?>", " ", text)  # remove html tags

    return " ".join(text.split())  # remove and strip spaces
