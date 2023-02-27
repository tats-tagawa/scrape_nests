import requests
from bs4 import BeautifulSoup

URL = 'https://www.allaboutbirds.org/guide/browse/taxonomy/'
headers = {'User-Agent':'Mozilla/5.0'}

page = requests.get(URL, headers=headers)

soup = BeautifulSoup(page.content, 'html.parser')
birds = soup.find_all('div','species-info')

for bird in birds:
  print(bird.a.get_text())
  print(bird.em.get_text())
  print('https://www.allaboutbirds.org' + bird.a.get('href'))