# Developer ::> Gehan Fernando
# import libraries
from PIL import Image
from inscriptis import get_text
from wordcloud import WordCloud, STOPWORDS
import requests, numpy as np
import urllib.request, matplotlib.pyplot as plt

concatText = ''
font_path  = 'C:\Windows\Fonts\ITCKRIST.ttf'
background = 'https://cdn3.iconfinder.com/data/icons/popular-services-brands-vol-2/512/nike-512.png'

webPages   = ['https://en.wikipedia.org/wiki/Nike,_Inc.', 'https://www.trustpilot.com/review/www.nike.com',
              'https://www.trustpilot.com/review/www.nike.com?page=2', 'https://www.businessinsider.com/nike-colin-kaepernick-ad-sparks-boycott-2018-9',
              'https://www.cnbc.com/2018/09/04/nike-shares-tumble-after-company-reveals-new-ad-campaign-featuring-colin-kaepernick.html',
              'https://www.ig.com/en-ch/news-and-trade-ideas/shares-news/the-battle-for-sporting-goods-supremacy--nike-vs-adidas-180329',
              'http://www.researchomatic.com/Comparing-Two-Brands-Nike-And-Adidas-79623.html']

count      = len(webPages) - 1

while count >= 0:
    pageUrl = webPages[count]
    pageContent = urllib.request.urlopen(pageUrl).read().decode('utf-8')
    concatText += get_text(pageContent) + '\n'
    count -= 1

mask = np.array(Image.open(requests.get(background, stream = True).raw))
stopwords = set(STOPWORDS)
wordcloud = WordCloud(background_color = 'black', stopwords = stopwords,
                      width = 512, height = 512, font_path = font_path,
                      max_words = 500, min_font_size = 4, max_font_size = 50,
                      random_state = None, mask = mask,
                      mode = 'RGB', relative_scaling = 'auto',
                      regexp = None, collocations = True,
                      colormap = None, normalize_plurals = True).generate(str(concatText))

plt.figure(figsize = (10,8), facecolor = 'black', edgecolor = 'blue')
plt.imshow(wordcloud, interpolation = 'bilinear')
plt.axis("off")
plt.tight_layout(pad = 0)
plt.show()