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

(Usage is coming soon.)

## Background
Data comes in different shapes and sizes, and Google played it extremely well. That also includes randomizing CSS class names making it almost impossible to scrape data.

Google sucks, but it's actually the knowledge base we all need. Say, there are these types of result pages:
- **Links** – What made Google, "Google." Or, `&udm=14`.
- **Rich blocks** – Rich blocks that introduce persons, places and more.
- **Weather** – Weather forecast.
- **Wikipedia (aside)** – Wikipedia text.

...and many more. (please contribute)

Scraper APIs out there are hella expensive, and there's no way I'm paying or entering their free tier. So, I made my own that's perfect for extracting data with LLMs.
