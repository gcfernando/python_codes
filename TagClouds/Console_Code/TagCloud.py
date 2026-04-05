# Developer ::> Gehan Fernando

from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import requests
from inscriptis import get_text
from PIL import Image
from wordcloud import STOPWORDS, WordCloud

concatText = ""
font_path = r"C:\Windows\Fonts\ITCKRIST.ttf"
background = "https://cdn3.iconfinder.com/data/icons/popular-services-brands-vol-2/512/nike-512.png"

webPages = [
    "https://en.wikipedia.org/wiki/Nike,_Inc.",
    "https://www.trustpilot.com/review/www.nike.com",
    "https://www.trustpilot.com/review/www.nike.com?page=2",
    "https://www.businessinsider.com/nike-colin-kaepernick-ad-sparks-boycott-2018-9",
    "https://www.cnbc.com/2018/09/04/nike-shares-tumble-after-company-reveals-new-ad-campaign-featuring-colin-kaepernick.html",
    "https://www.ig.com/en-ch/news-and-trade-ideas/shares-news/the-battle-for-sporting-goods-supremacy--nike-vs-adidas-180329",
    "http://www.researchomatic.com/Comparing-Two-Brands-Nike-And-Adidas-79623.html",
]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

session = requests.Session()
session.headers.update(headers)

for pageUrl in reversed(webPages):
    try:
        response = session.get(pageUrl, timeout=15)
        response.raise_for_status()
        concatText += get_text(response.text) + "\n"
        print(f"Fetched: {pageUrl}")
    except requests.RequestException as ex:
        print(f"Failed to fetch {pageUrl}: {ex}")

if not concatText.strip():
    raise ValueError("No webpage text could be retrieved. All requests failed or returned empty content.")

try:
    bg_response = session.get(background, timeout=15)
    bg_response.raise_for_status()

    with Image.open(BytesIO(bg_response.content)) as img:
        mask = np.array(img)
except requests.RequestException as ex:
    raise RuntimeError(f"Failed to download background image: {ex}") from ex
except OSError as ex:
    raise RuntimeError(f"Failed to read background image: {ex}") from ex

stopwords = set(STOPWORDS)

wordcloud = WordCloud(
    background_color="black",
    stopwords=stopwords,
    width=512,
    height=512,
    font_path=font_path,
    max_words=500,
    min_font_size=4,
    max_font_size=50,
    random_state=None,
    mask=mask,
    mode="RGB",
    relative_scaling="auto",
    regexp=None,
    collocations=True,
    colormap=None,
    normalize_plurals=True,
).generate(concatText)

plt.figure(figsize=(10, 8), facecolor="black", edgecolor="blue")
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.tight_layout(pad=0)
plt.show()
