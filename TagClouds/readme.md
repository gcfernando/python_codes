# Generate a Word Cloud from Web Pages in Python — wordcloud with an Image Mask

A Python script that **creates a word cloud from text scraped from several web pages**, shaped by a mask image, using `requests`, `inscriptis`, `wordcloud`, and `matplotlib`.

## Overview

This script fetches content from a list of web pages about Nike, extracts the plain text from the HTML using `inscriptis`, concatenates all the text, and generates a word cloud masked to the shape of a downloaded Nike logo image. The result is displayed using `matplotlib`.

## Features

- Scrapes multiple web pages using `requests` with a browser-like User-Agent header
- Extracts clean text from HTML using `inscriptis`
- Downloads a PNG image from the web and uses it as a mask for the word cloud shape
- Generates a word cloud with up to 500 words, excluding common stopwords
- Uses a custom font (`ITCKRIST.ttf` from the Windows Fonts directory)
- Displays the word cloud with a black background using `matplotlib`

## Requirements

```
requests
inscriptis
Pillow
wordcloud
numpy
matplotlib
```

Install dependencies:

```bash
pip install requests inscriptis Pillow wordcloud numpy matplotlib
```

## Configuration

The following variables at the top of `TagCloud.py` can be modified:

| Variable | Description |
|---|---|
| `font_path` | Path to the font file used in the word cloud |
| `background` | URL of the PNG image used as the word cloud mask |
| `webPages` | List of URLs to scrape for text content |

## Usage

From the `Console_Code` folder:

```bash
python TagCloud.py
```

The script will:
1. Fetch text from all configured web pages (skipping any that fail)
2. Download the mask image
3. Generate and display the word cloud

## File Structure

```
TagClouds/
└── Console_Code/
    └── TagCloud.py    # Main script
```

## Notes

- An internet connection is required to fetch web pages and the mask image.
- Pages that return HTTP errors or connection failures are silently skipped.
- If all pages fail, the script raises a `ValueError` rather than generating an empty cloud.
- The font path is hardcoded to `C:\Windows\Fonts\ITCKRIST.ttf` (ITC Kristen). That font is usually installed with Microsoft Office rather than with Windows itself, so update `font_path` if it is missing or if you run the script on macOS or Linux.
- The configured pages are third-party sites that may move, change, or block automated requests. Replace them with pages you are allowed to fetch.
- The mask works best with a high-contrast image: words are drawn in the non-white areas.

## Related Projects

- [Simple Selenium Scraper](../Simple%20Selenium%20Scraper/readme.md)
- [Image2Cartoon — OpenCV image effects](../Image2Cartoon/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
