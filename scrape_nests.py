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

    name = None
    scientific_name = None
    description = None
    conservation_status = None
    family = None
    habitat = None
    feeding_behavior = None
    eggs = None
    young = None
    diet = None
    nesting = None

    # Get div with all bird info
    bird_card = soup.find('div','bird-guide-card')

    # Some birds do not have all info. Check if data is available before assigning.

    name_el = bird_card.find('h1','common-name')
    if name_el:
        name = name_el.get_text(strip=True)

    scientific_name_el = bird_card.find('p','scientific-name')
    if scientific_name_el:
        scientific_name = scientific_name_el.get_text(strip=True)
    
    description_el = bird_card.find('section','bird-guide-section').find('div','columns')
    if description_el:
        description = description_el.get_text(strip=True)

    conservation_el = bird_card.find('th',string='Conservation status')
    if conservation_el:
        conservation_status = conservation_el.find_next_sibling().get_text(strip=True)

    family_el = bird_card.find('th',string='Family')
    if family_el:
        family = family_el.find_next_sibling().get_text(strip=True)

    habitat_el = bird_card.find('th', string='Habitat')
    if habitat_el:
        habitat = habitat_el.find_next_sibling().get_text(strip=True)
    
    feeding_el = bird_card.find('h2',string='Feeding Behavior')
    if feeding_el:
        feeding_behavior = feeding_el.find_next_sibling().get_text(strip=True)

    eggs_el = bird_card.find('h2',string='Eggs')
    if eggs_el:
        eggs = eggs_el.find_next_sibling().get_text(strip=True)
    
    young_el = bird_card.find('h2',string='Young')
    if young_el:
        young = young_el.find_next_sibling().get_text(strip=True)

    diet_el = bird_card.find('h2',string='Diet')
    if diet_el:
        diet = diet_el.find_next_sibling().get_text(strip=True)
    
    nesting_el = bird_card.find('h2',string='Nesting')
    if nesting_el:
        nesting = nesting_el.find_next_sibling().get_text(strip=True)

    return [name, scientific_name, description, conservation_status, family, habitat, feeding_behavior, eggs, young, diet, nesting, url]

# print(get_bird_data_audubon('https://www.audubon.org/field-guide/bird/wood-sandpiper'))
print(get_bird_data_audubon('https://www.audubon.org/field-guide/bird/evening-grosbeak'))
# get_bird_data_audubon('https://www.audubon.org/field-guide/bird/evening-grosbeak')

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
        writer.writerow(['Name', 'Scientific Name', 'Description', 'Conservation Status', 'Family', 'Habitat', 'Feeding Behavior', 'Eggs', 'Young', 'Diet', 'Nesting', 'URL'])
        for bird in birds:
            writer.writerow(bird)

# if __name__ == '__main__':
#     bird_urls = get_bird_urls_audubon()
#     birds_data = get_all_bird_data(bird_urls)
#     write_to_csv(birds_data)
