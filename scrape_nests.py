import requests
import csv
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor, as_completed

headers = {'User-Agent':'Mozilla/5.0'}

def get_bird_urls():
    URL = 'https://www.allaboutbirds.org/guide/browse/taxonomy'
    page = requests.get(URL, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')
    birds = soup.find_all('div','species-info')
    bird_urls = []
    for bird in birds:
        bird_url = 'https://www.allaboutbirds.org' + bird.a.get('href')
        bird_urls.append(bird_url)
    return bird_urls
        
def get_bird_data(url):
    bird_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(bird_page.content, 'html.parser')
    description = soup.find('p').get_text()
    return description

def get_all_bird_data(urls):
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(get_bird_data, url) for url in urls]
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        return results

if __name__ == '__main__':
    results = get_all_bird_data(get_bird_urls())
    for result in results:
        print(result)

with open('bird_database.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Name', 'Scientific Name', 'Description'])
    for bird in birds:
        name = bird.a.get_text()
        scientific_name = bird.em.get_text()

        bird_url = 'https://www.allaboutbirds.org' + bird.a.get('href')
        bird_page = requests.get(bird_url, headers=headers)
        # Bird soup sounds a bit..... violent?
        bird_soup = BeautifulSoup(bird_page.content, 'html.parser')
        description = bird_soup.find('p').get_text()
        writer.writerow([name, scientific_name, description])

