from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Snippet:
    text: str
    highlighted: Optional[str] = None


@dataclass
class Aside:
    text: str


@dataclass
class PartialWeatherForReport:
    weekday: str
    high_c: str
    high_f: str
    low_c: str
    low_f: str


@dataclass
class Weather:
    c: str
    f: str
    precipitation: str
    humidity: str
    wind_metric: str
    wind_imperial: str
    description: str
    forecast: List["PartialWeatherForReport"]


@dataclass
class WeatherForecast:
    now: Weather
    warning: Optional[str] = None


@dataclass
class Web:
    title: str
    url: str
    text: str


@dataclass
class Flight:
    title: str
    description: str
    duration: str
    price: str


@dataclass
class Lyrics:
    text: str
    is_partial: bool


@dataclass
class Result:
    snippet: Optional[Snippet]
    aside: Optional[Aside]
    weather: Optional[WeatherForecast]
    web: List[Web]
    flights: List[Flight]
    lyrics: Optional[Lyrics]
