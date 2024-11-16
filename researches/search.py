import asyncio
from typing import List, Optional

from selectolax.lexbor import LexborHTMLParser

from .markdown import get_markdown
from .primp import Client, Response
from .schemas import (
    Answer,
    Aside,
    Flight,
    Lyrics,
    News,
    PartialWeatherForReport,
    Result,
    Snippet,
    Source,
    Target,
    Translation,
    Weather,
    WeatherForecast,
    Web,
)
from .utils import some, textof

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/114.0.0.0"
)


def parse(res: Response) -> Result:
    parser = LexborHTMLParser(res.text)
    return Result(
        snippet=get_snippet(parser),
        aside=get_aside_block(parser),
        weather=get_weather(parser),
        web=get_web(parser),
        flights=get_flights(parser),
        lyrics=get_lyrics(parser),
        answer=get_answer(parser),
        news=get_news(parser),
        translation=get_translation(parser),
    )


def get(q: str, hl: str, ua: Optional[str], **kwargs) -> Response:
    client = Client(impersonate="chrome_130", verify=False)
    res = client.get(
        "https://www.google.com/search",
        params={"q": q, "hl": hl, "client": "opera"},
        headers={"User-Agent": ua or USER_AGENT},
        **kwargs,
    )
    assert res.status_code == 200, res.text
    return res


def search(q: str, *, hl: str = "en", ua: Optional[str] = None, **kwargs) -> Result:
    return parse(get(q, hl, ua, **kwargs))


async def asearch(
    q: str,
    *,
    hl: str = "en",
    ua: Optional[str] = None,
    **kwargs,
) -> Result:
    res = await asyncio.to_thread(get, q, hl, ua, **kwargs)
    return await asyncio.to_thread(parse, res)


def get_snippet(parser: LexborHTMLParser) -> Optional[Snippet]:
    # Get featured snippet (aka. quick answer)
    fsnippet_ele = parser.css_first(".xpdopen .hgKElc")

    if not fsnippet_ele:
        return None

    return Snippet(
        text=get_markdown(fsnippet_ele.html or "", ".hgKElc"),
        highlighted=textof(fsnippet_ele.css_first("b"), deep=True, strip=True),
    )


def get_aside_block(parser: LexborHTMLParser) -> Optional[Aside]:
    # Usually wikipedia blocks
    aside_ele = parser.css(".xGj8Mb .wDYxhc")
    detail_ele = parser.css_first(".SW5pqf.ZZhrTe.xXEKkb.fl")

    if not aside_ele:
        return None

    return Aside(
        text="\n".join(
            textof(value).replace(textof(detail_ele), "") for value in aside_ele
        ),
    )


def get_weather(parser: LexborHTMLParser) -> Optional[WeatherForecast]:
    # Get weather. Usually present when using the query "<place> weather"
    block = parser.css_first("#wob_wc")

    if not block:
        return None

    forecast = [
        PartialWeatherForReport(
            weekday=textof(wth.css_first(".Z1VzSb")),
            high_c=textof(wth.css(".gNCp2e .wob_t")[0]),
            high_f=textof(wth.css(".gNCp2e .wob_t")[1]),
            low_c=textof(wth.css(".ZXCv8e .wob_t")[0]),
            low_f=textof(wth.css(".ZXCv8e .wob_t")[1]),
        )
        for wth in block.css(".wob_df")
    ]

    now = Weather(
        c=textof(block.css_first("#wob_tm")),
        f=textof(block.css_first("#wob_ttm")),
        precipitation=textof(block.css_first("#wob_pp")),
        humidity=textof(block.css_first("#wob_hm")),
        wind_metric=textof(block.css_first("#wob_ws")),
        wind_imperial=textof(block.css_first("#wob_tws")),
        description=textof(block.css_first("#wob_dc")),
        forecast=forecast,
    )

    return WeatherForecast(
        now=now, forecast=forecast, warning=textof(block.css_first(".vk_h")) or None
    )


def get_web(parser: LexborHTMLParser) -> List[Web]:
    # Get links
    return [
        Web(
            title=textof(item.css_first("h3"), strip=True),
            url=some(item.css_first("a")).attributes.get("href", ""),
            text=textof(item.css_first(".VwiC3b")),
        )
        for item in parser.css(".asEBEc")
    ]


def get_flights(parser: LexborHTMLParser) -> List[Flight]:
    # Get flights when using the query "<place> to <place> [flights]"
    return [
        Flight(
            title=textof(item.css_first(".ZhosBf"), strip=True),
            description=textof(item.css_first(".GfzIoc"), strip=True),
            duration=textof(item.css_first(".TM2JYd"), strip=True),
            price=textof(item.css_first(".YK0p7d"), strip=True),
        )
        for item in parser.css(".Ww4FFb.vt6azd .wyccme")
    ]


def get_lyrics(parser: LexborHTMLParser) -> Optional[Lyrics]:
    # Get lyrics
    lyrics_ele = parser.css(".ujudUb span")
    source_ele = parser.css_first(".S4TQId")

    if not lyrics_ele:
        return None

    return Lyrics(
        text="\n".join(textof(value, strip=True) for value in lyrics_ele),
        is_partial=parser.css_first(".oRJe3d") is not None,
        source=textof(source_ele),
    )


def get_answer(parser: LexborHTMLParser) -> Optional[Answer]:
    # Get Answer
    answer_ele = parser.css_first(".CfV8xf") or parser.css_first(".YwPhnf")

    if not answer_ele:
        return None

    return Answer(text=textof(answer_ele))


def get_news(parser: LexborHTMLParser) -> Optional[News]:
    # Get News
    news_ele = parser.css(".zP82e")

    if not news_ele:
        return None

    return [
        News(
            title=textof(item.css_first(".nDgy9d")),
            source=textof(item.css_first(".NUnG9d span")),
            url=item.css_first(".WlydOe").attributes.get("href", ""),
            date=textof(item.css_first(".OSrXXb span")),
        )
        for item in news_ele
    ]


def get_translation(parser: LexborHTMLParser) -> Optional[Translation]:
    # Get Translation
    translation_ele = parser.css_first(".Ww4FFb.vt6azd.obcontainer.wDYxhc")

    if not translation_ele:
        return None

    return Translation(
        Source(
            textof(translation_ele.css(".Y2IQFc")[0]),
            textof(translation_ele.css_first(".source-language")),
            textof(translation_ele.css(".Y2IQFc")[1]),
        ),
        Target(
            textof(translation_ele.css(".Y2IQFc")[2]),
            textof(translation_ele.css_first(".target-language")),
            textof(translation_ele.css(".Y2IQFc")[3]),
        ),
    )
