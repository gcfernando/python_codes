# Developer ::> Gehan Fernando
# import libraries
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Define the URL to be scraped
url = "https://www.espncricinfo.com/cricket-news"

# Specify the path to the chromedriver.exe file
chromedriver_path = "C:\Gehan\Projects\Python\chromedriver.exe"

# Create a ChromeOptions object to configure the browser
chrome_options = Options()
chrome_options.add_argument("--headless") # run in headless mode (without GUI)
chrome_options.add_argument("--disable-gpu") # disable GPU acceleration

# Create a webdriver object using the chromedriver and options
driver = webdriver.Chrome(chromedriver_path, options=chrome_options)

# Navigate to the URL
driver.get(url)

# Find the header element on the page
header = driver.find_element(By.CLASS_NAME, 'ds-text-title-xl')
news_feeds = driver.find_elements(By.CLASS_NAME,'ds-text-title-s.ds-font-bold.ds-text-typo')

# Clear the console
os.system('cls')

# Print the header and the news feeds
print(f"Looking for : {header.text}")
for index, news_feed in enumerate(news_feeds[2:], 1):
    print(f"\t{news_feed.text}")

# Close the browser
driver.close()
driver.quit()