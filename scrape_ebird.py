## Note: Switched to Audubon data. Below are deprecated
## data to scrape from eBird. Saving for reference

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