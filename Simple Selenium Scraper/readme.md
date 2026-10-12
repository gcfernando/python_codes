# Python Selenium Web Scraping Example — Headless Chrome Headline Scraper

A short **Selenium web scraping example in Python** that runs Chrome in headless mode, opens the ESPN Cricinfo news page, and prints the page header and news headlines found by CSS class.

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
- **ChromeDriver** matching your Chrome version — available from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)

> **Selenium version:** the script passes the driver path as the first positional argument, `webdriver.Chrome(chromedriver_path, options=chrome_options)`. That form was removed in Selenium 4.10, so with current Selenium versions the call fails. Either install an older release (`pip install "selenium<4.10"`) or update the call to use a `Service`:
>
> ```python
> from selenium.webdriver.chrome.service import Service
> driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
> ```
>
> With Selenium 4.6 or later you can also omit the path entirely and let Selenium Manager download a matching driver: `webdriver.Chrome(options=chrome_options)`.

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

From the `Console_Code` folder:

```bash
python Web_Scrape.py
```

### Output Format

```
Looking for : <page header text>
	<headline 1>
	<headline 2>
	...
```

Headlines change daily, and the CSS classes used by the site can change at any time; if nothing is printed, inspect the page and update the selectors.

## File Structure

```
Simple Selenium Scraper/
└── Console_Code/
    └── Web_Scrape.py    # Main script
```

## Notes

- The first two items from the news feed list are skipped (`news_feeds[2:]`) to avoid navigation elements.
- ChromeDriver must be version-compatible with the installed Chrome browser.
- The console is cleared with `os.system('cls')`, which is Windows-specific; use `clear` on macOS or Linux.
- Check a website's terms of use and `robots.txt` before scraping it, and keep request rates low.

## Related Projects

- [Tag Clouds — word cloud from scraped web pages](../TagClouds/readme.md)
- [Simple WhatsApp Sender — browser automation](../Simple%20WhatApp%20Sender/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
