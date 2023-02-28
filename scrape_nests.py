import requests
import csv
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor, as_completed

headers = {'User-Agent':'Mozilla/5.0'}

def get_bird_urls():
    # Use second URL when testing, as it is much smaller list
    URL = 'https://www.allaboutbirds.org/guide/browse/taxonomy'
    # URL = 'https://www.allaboutbirds.org/guide/browse/taxonomy/Podicipedidae'
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
    species_info = soup.find('div','speciesInfoCard')

    name = species_info.span.get_text()
    scientific_name = species_info.em.get_text()
    description = species_info.p.get_text()

    return [name, scientific_name, description]

def get_all_bird_data(urls):
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(get_bird_data, url) for url in urls]
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        return results

def write_to_csv(birds):
    with open('bird_database.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Scientific Name', 'Description'])
        for bird in birds:
            writer.writerow(bird)

if __name__ == '__main__':
    bird_urls = get_bird_urls()
    birds_data = get_all_bird_data(bird_urls)
    write_to_csv(birds_data)

