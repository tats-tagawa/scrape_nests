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

    conservation_status = None
    family = None
    habitat = None
    feeding_behavior = None
    Eggs = None
    Young = None

    # Get table with conservation_status status, family, and habitat information
    bird_card = soup.find('div','bird-guide-card')

    conservation_info = bird_card.find('th',string='Conservation status')
    if conservation_info:
        conservation_status = conservation_info.find_next_sibling().get_text(strip=True)

    family_info = bird_card.find('th',string='Family')
    if family_info:
        family = family_info.find_next_sibling().get_text(strip=True)

    habitat_info = bird_card.find('th', string='Habitat')
    if habitat_info:
        habitat = habitat_info.find_next_sibling().get_text(strip=True)
    
    feeding_info = bird_card.find('h2',string='Feeding Behavior')
    if feeding_info:
        feeding_behavior = feeding_info.find_next_sibling().get_text(strip=True)

    print(feeding_behavior)
    return [name, scientific_name, description, conservation_status, family, habitat]

# print(get_bird_data_audubon('https://www.audubon.org/field-guide/bird/evening-grosbeak'))
get_bird_data_audubon('https://www.audubon.org/field-guide/bird/evening-grosbeak')

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
        writer.writerow(['Name', 'Scientific Name', 'Description', 'Conservation Status', 'Family', 'Habitat'])
        for bird in birds:
            writer.writerow(bird)

# if __name__ == '__main__':
#     bird_urls = get_bird_urls_audubon()
#     birds_data = get_all_bird_data(bird_urls)
#     write_to_csv(birds_data)
