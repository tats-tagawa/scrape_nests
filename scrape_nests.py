import requests
import re
import csv
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor, as_completed

headers = {'User-Agent':'Mozilla/5.0'}

def get_bird_urls_audubon():
    # Use page_num = 0 to get all birds
    page_num = 25
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

def get_bird_data_audubon(url):
    bird_page = requests.get(url, headers=headers)
    soup = BeautifulSoup(bird_page.content, 'html.parser')

    name = soup.find('h1','common-name').get_text(strip=True)
    scientific_name = soup.find('p','scientific-name').get_text(strip=True)
    description = soup.find('section','bird-guide-section').find('div','columns').get_text(strip=True)
    print('* * * * * * * * * * *')
    print(url)
    print(name)
    # Get table with conservation status, family, and habitat information
    # FIX: SOME BIRDS DON'T HAVE ALL THREE INFO
    info_table = soup.find('table','collapse')
    bird_infos = info_table.find_all('td')
    [conservation, family, habitat] = [info.get_text(strip=True) for info in bird_infos]
    return [name, scientific_name, description, conservation, family, habitat]
    # return [name, scientific_name, description]

def soup_test():
    URL = 'https://www.audubon.org/field-guide/bird/evening-grosbeak'
    page = requests.get(URL, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table','collapse')
    bird_infos = table.find_all('td')
    [conservation, family, habitat] = [bird.get_text(strip=True) for bird in bird_infos]
    print(f'conservation: {conservation} | family: {family} | habitat: {habitat}')
    
# soup_test()

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
        futures = [executor.submit(get_bird_data_audubon, url) for url in urls]
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        return results

def write_to_csv(birds):
    with open('bird_database_audubon.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Scientific Name', 'Description'])
        for bird in birds:
            writer.writerow(bird)

if __name__ == '__main__':
    bird_urls = get_bird_urls_audubon()
    birds_data = get_all_bird_data(bird_urls)
    write_to_csv(birds_data)
