# researches
Researches is a Google scraper. Minimal requirements.

Key designs:
- **No beautifulsoup.** We want to make sure everything is running smoothly and not slowly.
- **Simple API.** Great developer experience, that's all that matters.
- **Typed.** We support typing for everything you see.

Note thet `researches` **does not clean up data for you**, meaning it's better for LLM-based content consumption.

```python
search("Who invented papers?")
# Result(snippet=Snippet(…), aside=None, weather=None, web=[Web(…), …], …)
```

## Requirements
- A decent computer with an Internet connection
- Python ≥ 3.9 (`dataclasses` support)
- `primp` – 🪞 HTTP connections & fingerprint impersonation.
- `selectolax` – 🌯 The HTML parser.

## Usage
Just start searching right away. Don't worry, Gemini won't hurt you (also [gemini](https://preview.redd.it/l-gemini-lmao-v0-6a6q0pl4ac2d1.png?auto=webp&s=31cd6b33329d895501d727e6346153bc2a3ea1d6)).

```python
# Sync code
search(
    "US to Japan",  # query
    hl="en",        # language
    ua=None,        # custom user agent or ours
    **kwargs        # kwargs to pass to primp (optional)
) -> Result
```

For people who love async, we've also got you covered:
```python
# Async code
await asearch(
    "US to Japan"   # query
    hl="en",        # language
    ua=None,        # custom user agent or ours
    **kwargs        # kwargs to pass to primp (optional)
) -> Result
```

So, what does the `Result` class has to offer? At a glance:
```haskell
result.snippet?
      ⤷  .text: str
      ⤷  .name: str?

result.aside?
      ⤷ .text: str

result.weather?
      ⤷ .c: str
      ⤷ .f: str
      ⤷ .precipitation: str
      ⤷ .humidty: str
      ⤷ .wind_metric: str
      ⤷ .wind_imperial: str
      ⤷ .description: str
      ⤷ .forecast: PartialWeatherForReport[]
                   ⤷ .weekday: str
                   ⤷ .high_c: str
                   ⤷ .low_c: str
                   ⤷ .high_f: str
                   ⤷ .low_f: str

result.web: Web[]
            ⤷ .title: str
            ⤷ .url: str
            ⤷ .text: str

result.flights: Flight[]
                ⤷ .title: str
                ⤷ .description: str
                ⤷ .duration: str
                ⤷ .price: str

result.lyrics?
      ⤷ .text: str
      ⤷ .is_partial: bool
```

## Background
Data comes in different shapes and sizes, and Google played it extremely well. That also includes randomizing CSS class names making it almost impossible to scrape data.

Google sucks, but it's actually the knowledge base we all need. Say, there are these types of result pages:
- **Links** – What made Google, "Google." Or, `&udm=14`.
- **Weather** – Weather forecast.
- **Wikipedia (aside)** – Wikipedia text.
- **Flights** – Flights.
- **Lyrics** – Both full and partial lyrics. <kbd>unstable</kbd>

...and many more. (Contribute!)

Scraper APIs out there are hella expensive, and ain't no way I'm paying or entering their free tier. So, I made my own that's perfect for extracting data with LLMs.

## Other projects
If you're looking for something other than Google or something more general-purposed, check these out:

- [`air_web`](https://github.com/AWeirdDev/air-web) – A lightweight package for crawling with the minimalist of code.
- [`ddginternal`](https://github.com/AWeirdDev/ddginternal) – Simple Duckduckgo scraper.

***

(c) 2024 AWeirdDev, [sus2790](https://github.com/sus2790), and other silly people
