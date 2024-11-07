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
    PartialWeatherForReport,
    Result,
    Snippet,
    Weather,
    WeatherForecast,
    Web,
)
from .utils import some, textof

user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/130.0.0.0 Safari/537.36 OPR/114.0.0.0"
)


def parse(res: Response) -> Result:
    parser = LexborHTMLParser(res.text)
    snippet = get_snippet(parser)
    aside = get_aside_block(parser)
    weather = get_weather(parser)
    web = get_web(parser)
    flights = get_flights(parser)
    lyrics = get_lyrics(parser)
    answer = get_answer(parser)

    return Result(
        snippet=snippet,
        aside=aside,
        weather=weather,
        web=web,
        flights=flights,
        lyrics=lyrics,
        answer=answer,
    )


def get(q: str, hl: str, ua: Optional[str], **kwargs) -> Response:
    client = Client(impersonate="chrome_130", timeout=5, verify=False)
    res = client.get(
        "https://www.google.com/search",
        params={"q": q, "hl": hl, "client": "opera"},
        headers={"User-Agent": ua or user_agent},
        **kwargs,
    )
    assert res.status_code == 200, res.text
    return res


def search(q: str, *, hl: str = "en", ua: Optional[str] = None, **kwargs) -> Result:
    return parse(get(q, hl, ua, **kwargs))


async def asearch(
    q: str, *, hl: str = "en", ua: Optional[str] = None, **kwargs,
) -> Result:
    res = await asyncio.to_thread(get, q, hl, ua, **kwargs)
    return await asyncio.to_thread(parse, res)


def get_snippet(parser: LexborHTMLParser) -> Optional[Snippet]:
    # Get featured snippet (aka. quick answer)
    fsnippet_ele = parser.css_first(".xpdopen .hgKElc")

    return (
        Snippet(
            text=get_markdown(fsnippet_ele.html or "", ".hgKElc"),
            highlighted=textof(fsnippet_ele.css_first("b"), deep=True, strip=True),
        )
        if fsnippet_ele
        else None
    )



def get_aside_block(parser: LexborHTMLParser) -> Optional[Aside]:
    # Usually wikipedia blocks
    aside_ele = parser.css(".Z1hOCe")
    detail = (
        parser.css_first(".SW5pqf.ZZhrTe.xXEKkb.fl").text(strip=True)
        if parser.css_first(".SW5pqf.ZZhrTe.xXEKkb.fl")
        else ""
    )

    if not aside_ele:
        return None

    aside_text = ""
    for item in aside_ele:
        aside_text += item.text(strip=True) + "\n"

    return Aside(text=aside_text.replace(detail, ""))


def get_weather(parser: LexborHTMLParser) -> Optional[WeatherForecast]:
    # Get weather. Usually present when using the query "<place> weather"
    block = parser.css_first("#wob_wc")
    if not block:
        return None

    temp_c = textof(block.css_first("#wob_tm"))
    temp_f = textof(block.css_first("#wob_ttm"))

    precipitation = textof(block.css_first("#wob_pp"))
    humidity = textof(block.css_first("#wob_hm"))

    wind_metric = textof(block.css_first("#wob_ws"))
    wind_imperial = textof(block.css_first("#wob_tws"))

    description = textof(block.css_first("#wob_dc"))

    forecast = []
    for wth in block.css(".wob_df"):
        day = textof(wth.css_first(".Z1VzSb"))
        items = wth.css(".gNCp2e .wob_t")
        high_c = textof(items[0])
        high_f = textof(items[1])

        items1 = wth.css(".ZXCv8e .wob_t")
        low_c = textof(items1[0])
        low_f = textof(items1[1])

        forecast.append(
            PartialWeatherForReport(
                weekday=day,
                high_c=high_c,
                high_f=high_f,
                low_c=low_c,
                low_f=low_f,
            ),
        )

    return WeatherForecast(
        now=Weather(
            c=temp_c,
            f=temp_f,
            precipitation=precipitation,
            humidity=humidity,
            wind_metric=wind_metric,
            wind_imperial=wind_imperial,
            description=description,
            forecast=forecast,
        ),
        warning=textof(block.css_first(".vk_h")) or None,
    )


def get_web(parser: LexborHTMLParser) -> List[Web]:
    # Get links
    items = []

    for item in parser.css(".N54PNb"):
        anchor = some(item.css_first("a")).attributes.get("href", "")
        title = textof(item.css_first("h3"), strip=True)

        items.append(
            Web(
                title=title,
                url=anchor,  # type: ignore
                text=textof(item.css_first(".VwiC3b")),
            ),
        )

    return items


def get_flights(parser: LexborHTMLParser) -> List[Flight]:
    # Get flights when using the query "<place> to <place> [flights]"
    items = []

    for item in parser.css(".Ww4FFb.vt6azd .wyccme"):
        title = textof(item.css_first(".ZhosBf"), strip=True)
        description = textof(item.css_first(".GfzIoc"), strip=True)
        duration = textof(item.css_first(".TM2JYd"), strip=True)
        price = textof(item.css_first(".YK0p7d"), strip=True)

        items.append(
            Flight(
                title=title,
                description=description,
                duration=duration,
                price=price,
            ),
        )

    return items


def get_lyrics(parser: LexborHTMLParser) -> Optional[Lyrics]:
    # Get lyrics
    lyrics_ele = parser.css(".xaAUmb .ujudUb span")

    if not lyrics_ele:
        return None

    lyrics = []
    for ele in lyrics_ele:
        lyrics.append(textof(ele, strip=True))

    return Lyrics(
        text="\n".join(lyrics),
        is_partial=bool(parser.css_first(".xaAUmb .ujudUb a")),
        source=textof(".S4TQId"),
    )


def get_answer(parser: LexborHTMLParser) -> Optional[Answer]:
    # Get Answer
    answer_ele = parser.css_first(".Z0LcW.t2b5Cf") or parser.css_first(".QpPSMb")

    if not answer_ele:
        return None

    return Answer(text=answer_ele.text(strip=True))
