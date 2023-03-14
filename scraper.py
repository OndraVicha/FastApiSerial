import requests
from bs4 import BeautifulSoup
import json
URL = 'https://www.imdb.com/list/ls025873927/'

page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

series_links = soup.select('div.lister-item-content>h3>a')
year_links = soup.select('div.lister-item-content>h3>span.lister-item-year')
rating_links = soup.select('div.ipl-rating-widget>div.ipl-rating-star>span.ipl-rating-star__rating')
length_links = soup.select('div.lister-item-content>p.text-muted>span.runtime')

years = [str(tag.text[1:-1]) for tag in year_links]
ratings = [float(tag.text) for tag in rating_links]
urls = [f'https://www.imdb.com{tag["href"]}' for tag in series_links]
titles = [tag.text for tag in series_links]
length = [tag.text for tag in length_links]

with open("serials.json",  "w", encoding='utf-8') as file:
    file.write('[')
    for i in range(0, 50):
        detail_page = requests.get(urls[i], headers={'User-agent': 'Mozilla/5.0'})
        dsoup = BeautifulSoup(detail_page.content, 'html.parser')
        content = dsoup.select('[data-testid=plot]>span[data-testid=plot-xs_to_m]')
        genre_links = dsoup.select('[data-testid=genres] a')
        genres = [genre.text for genre in genre_links]
        row = f'"title": "{titles[i]}", "description": "{content[0].text}", "year": "{years[i]}", "rating": "{ratings[i]}", "episode_length": "{length[i]}", "genres": {json.dumps(genres)}'
        row = '{' + row + '} '
        row = row + ',\n' if i != 49 else row + "\n"
        print(row)
        file.write(row)
    file.write(']')