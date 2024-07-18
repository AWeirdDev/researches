# researches
Researches is a vanilla<sup>1</sup> Google scraper. Minimal requirements.

```python
search("Who invented papers?")
```

<sub><sup>1</sup> In context, this refers to raw/unformatted data and contents. `researches` does not clean them up for you, and it's not guranteed to be 100% human-readable. However, feeding to LLMs may help as most of them use word-level tokenizers.</sub>

## Requirements
- A decent computer
- Python ≥ 3.9
- `httpx` – HTTP connections.
- `selectolax` – The HTML parser.

## Usage
Just start searching right away. Don't worry, Gemini won't hurt you (also [gemini](https://preview.redd.it/l-gemini-lmao-v0-6a6q0pl4ac2d1.png?auto=webp&s=31cd6b33329d895501d727e6346153bc2a3ea1d6)).

```python
search(
    "US to Japan",  # query
    hl="en",        # language
    ua=None,        # custom user agent or ours
    **kwargs        # kwargs to pass to httpx (optional)
) -> Result
```

For people who love async, we've also got you covered:
```python
await asearch(
    "US to Japan"   # query
    hl="en",        # language
    ua=None,        # custom user agent or ours
    **kwargs        # kwargs to pass to httpx (optional)
)
```

So, what does the `Result` class has to offer? At a glance:
```haskell
result.snippet?
      ⤷  .text: str
      ⤷  .name: str?

result.rich_block?
      ⤷  .image: str?
      ⤷  .forecast: PartialWeather[]
                    ⤷ .weekday: str
                    ⤷ .temp: str

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
```

## Background
Data comes in different shapes and sizes, and Google played it extremely well. That also includes randomizing CSS class names making it almost impossible to scrape data.

Google sucks, but it's actually the knowledge base we all need. Say, there are these types of result pages:
- **Links** – What made Google, "Google." Or, `&udm=14`.
- **Rich blocks** – Rich blocks that introduce persons, places and more.
- **Weather** – Weather forecast.
- **Wikipedia (aside)** – Wikipedia text.
- **Flights** – Flights.

...and many more. (Contribute!)

Scraper APIs out there are hella expensive, and ain't no way I'm paying or entering their free tier. So, I made my own that's perfect for extracting data with LLMs.
