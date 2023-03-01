import requests
import re
import csv
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor, as_completed

headers = {'User-Agent':'Mozilla/5.0'}

def get_bird_urls_audubon():
    # Use page_num = 0 to get all birds
    page_num = 24
    bird_urls = []

    while (True):
        URL = f'https://www.audubon.org/bird-guide?page={page_num}&search_api_views_fulltext=&field_bird_family_tid=All&field_bird_region_tid=All'
        page = requests.get(URL, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        # Stop loop if there are no more birds to load
        if soup.body.find_all(string=re.compile('No birds matching')):
            break
        birds = soup.find_all('article','bird-card')

        # Delete the first bird as it is the same "Featured Bird" on every page
        del birds[0]

        for bird in birds:
            bird_urls.append(bird.a.get('href'))
        page_num += 1
    return bird_urls

def get_bird_urls_ebird():
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
        
def get_bird_data_ebird(url):
    bird_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(bird_page.content, 'html.parser')
    species_info = soup.find('div','speciesInfoCard')

    name = species_info.span.get_text()
    scientific_name = species_info.em.get_text()
    description = species_info.p.get_text()

    return [name, scientific_name, description]

def get_all_bird_data(urls):
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(get_bird_data_ebird, url) for url in urls]
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

# if __name__ == '__main__':
#     bird_urls = get_bird_urls_ebird()
#     birds_data = get_all_bird_data(bird_urls)
#     write_to_csv(birds_data)
print(get_bird_urls_audubon())
