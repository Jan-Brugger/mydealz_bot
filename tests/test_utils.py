from src.utils import prettify_query


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
    assert prettify_query(" NEU+  ") == "neu+"
