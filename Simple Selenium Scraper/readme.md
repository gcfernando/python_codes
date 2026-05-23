# Simple Selenium Scraper

A headless web scraper that extracts cricket news headlines from ESPN Cricinfo using Selenium and Chrome.

## Overview

This script launches a headless Chrome browser, navigates to the ESPN Cricinfo news page, and extracts the page header and all news feed article titles. Results are printed to the console.

## Features

- Runs Chrome in headless mode (no visible browser window)
- Scrapes the page header and news article titles
- GPU acceleration disabled for compatibility in server environments
- Console cleared before displaying results

## Requirements

```
selenium
```

Install the dependency:

```bash
pip install selenium
```

You also need:
- **Google Chrome** installed on your system
- **ChromeDriver** matching your Chrome version — download from [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads)

## Configuration

Open `Web_Scrape.py` and update the ChromeDriver path:

```python
chromedriver_path = "path/to/chromedriver.exe"
```

The target URL is set to:
```
https://www.espncricinfo.com/cricket-news
```

You can change this to any URL and update the CSS class selectors (`ds-text-title-xl`, `ds-text-title-s`) to match the structure of your target page.

## Usage

```bash
python Web_Scrape.py
```

### Example Output

```
Looking for : Cricket News

    India beat Australia by 5 wickets in 3rd ODI
    England name squad for West Indies tour
    ...
```

## File Structure

```
Simple Selenium Scraper/
└── Console_Code/
    └── Web_Scrape.py    # Main script
```

## Notes

- The first two items from the news feed list are skipped (`news_feeds[2:]`) to avoid navigation elements.
- ChromeDriver must be version-compatible with the installed Chrome browser.
