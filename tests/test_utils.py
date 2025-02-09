from src.models import PriceModel
from src.utils import parse_price, prettify_query


def test_prettify_query() -> None:
    assert prettify_query("THIS is a TEst QuErY") == "this & is & a & test & query"
    assert prettify_query("THIS is ,a TEst ,QuErY") == "this & is, a & test, query"
    assert prettify_query(" THIS     is   ,   a   TEst ,    QuErY  ") == "this & is, a & test, query"
    assert prettify_query("!not, !search,! ! !!for this & values") == "!not, !search, !for & this & values"
    assert (
        prettify_query("  !   !   try,&,,to make &!&,&! hgg, incompatible   &  &  & symbols,,,!&!")
        == "!try, to & make & !hgg, incompatible & symbols"
    )
    assert prettify_query("&what & happens! & !with!this ! query") == "what & happens & !with & !this & !query"


def test_parse_price() -> None:
    assert parse_price("943, 498, 238.0") == PriceModel(amount=943498238.0)
    assert parse_price("192, 5 ¢") == PriceModel(amount=192.50)
    assert parse_price("123123") == PriceModel(amount=123123)
    assert parse_price("10, 215.24 $") == PriceModel(amount=10215.24)
    assert parse_price("10215.24 €") == PriceModel(amount=10215.24)
    assert parse_price("239.329  ") == PriceModel(amount=239.329)
    assert parse_price("943, 498, 238.") == PriceModel(amount=943498238.0)
    assert parse_price("943498,238 YEN") == PriceModel(amount=943498.238)
