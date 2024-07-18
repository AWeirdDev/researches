from typing import List, Optional

import httpx
from selectolax.lexbor import LexborHTMLParser

from .markdown import get_markdown
from .schemas import (
    Aside,
    Flight,
    PartialWeatherForReport,
    Result,
    RichBlock,
    Snippet,
    PartialWeather,
    Weather,
    WeatherForecast,
    Web,
)
from .utils import some, textof


user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36 OPR/111.0.0.0"
)


def search(q: str, *, hl: str = "en", ua: Optional[str] = None, **kwargs) -> Result:
    with httpx.Client() as client:
        res = client.get(
            "https://www.google.com/search",
            params={"q": q, "hl": hl, "client": "opera", "sclient": "gws-wiz-serp"},
            headers={"User-Agent": ua or user_agent},
            **kwargs,
        )
        res.raise_for_status()

    with open("index.html", "wb") as f:
        f.write(res.content)

    parser = LexborHTMLParser(res.text)
    snippet = get_snippet(parser)
    rich = get_rich_block(parser)
    aside = get_aside_block(parser)
    weather = get_weather(parser)
    web = get_web(parser)
    flights = get_flights(parser)

    return Result(
        snippet=snippet,
        rich_block=rich,
        aside=aside,
        weather=weather,
        web=web,
        flights=flights,
    )


def get_snippet(parser: LexborHTMLParser) -> Optional[Snippet]:
    fsnippet_ele = parser.css_first(".xpdopen .hgKElc")

    # 1. Get featured snippet
    featured = (
        Snippet(
            text=get_markdown(fsnippet_ele.html or "", ".hgKElc"),
            highlighted=textof(fsnippet_ele.css_first("b"), deep=True, strip=True),
        )
        if fsnippet_ele
        else None
    )

    return featured


def get_rich_block(parser: LexborHTMLParser) -> Optional[RichBlock]:
    block = parser.css_first(".e6hL7d")
    if not block:
        return None

    forecast = []

    weather = block.css_first(".ij5N5d")
    if weather:
        for wth in weather.iter():
            day = textof(wth.css_first(".eidkGd"))
            tmp = textof(wth.css_first('[jsname="wcyxJ"]'))
            forecast.append(PartialWeather(day, tmp))

    return RichBlock(
        image=some(block.css_first("ol li .PZPZlf")).attributes.get("data-lpage"),
        forecast=forecast,
    )


def get_aside_block(parser: LexborHTMLParser) -> Optional[Aside]:
    aside = parser.css_first(".xGj8Mb")
    if not aside:
        return None

    return Aside(text=aside.text(strip=True, separator=" ").replace("  ", " "))


def get_weather(parser: LexborHTMLParser) -> Optional[WeatherForecast]:
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
            )
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
    items = []

    for item in parser.css(".N54PNb"):
        anchor = some(item.css_first("a")).attributes.get("href", "")
        title = textof(item.css_first("h3"), strip=True)

        items.append(
            Web(
                title=title,
                url=anchor,  # type: ignore
                text=textof(item.css_first(".VwiC3b")),
            )
        )

    return items


def get_flights(parser: LexborHTMLParser) -> List[Flight]:
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
            )
        )

    return items
