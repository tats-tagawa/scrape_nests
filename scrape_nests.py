import requests
import csv
from bs4 import BeautifulSoup

URL = 'https://www.allaboutbirds.org/guide/browse/taxonomy/'
headers = {'User-Agent':'Mozilla/5.0'}

page = requests.get(URL, headers=headers)

soup = BeautifulSoup(page.content, 'html.parser')
birds = soup.find_all('div','species-info')

with open('bird_database.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Name', 'Scientific Name'])
    for bird in birds:
        name = bird.a.get_text()
        scientific_name = bird.em.get_text()
        writer.writerow([name, scientific_name])
