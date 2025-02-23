from src.models import DealModel
from src.queries import Queries
from src.utils import prettify_query


def test_queries(
    deal0: DealModel,
    deal1: DealModel,
    deal2: DealModel,
    deal3: DealModel,
    deal4: DealModel,
    deal5: DealModel,
) -> None:
    assert Queries(prettify_query("Funko pop star wars, funko pop one piece")).any_match(deal0.search_title)

    assert not Queries(prettify_query("funko pop !lokal")).any_match(deal0.search_title_and_description)

    assert Queries(prettify_query(r"r/1\d{2} ?PS")).any_match(deal1.search_title)

    assert not Queries(prettify_query(r"r/1\d{2} ?ps")).any_match(deal1.search_title)

    assert Queries(prettify_query(r"r/1\d{2} ?PS/i")).any_match(deal1.search_title)

    assert Queries(prettify_query(r"r/1\d{2} ?PS\/i")).any_match(deal1.search_title)

    assert not Queries(prettify_query("Skoda+Octavia !automatik")).any_match(deal1.search_title)

    assert Queries(prettify_query("2für1, 2+für+1")).any_match(deal2.search_title)

    assert Queries(prettify_query("[Bauhaus]")).any_match(deal3.search_title)

    assert Queries(prettify_query("BIO-Dinkelbrot")).any_match(deal4.search_title)

    assert not Queries(prettify_query("Kein Match ")).any_match(deal5.search_title)

    assert Queries(prettify_query(" Pentax+ ")).any_match(deal5.search_title)

    assert not Queries(prettify_query("Neu+")).any_match(deal1.search_title)
