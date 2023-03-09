from concurrent.futures import ProcessPoolExecutor, as_completed
import re
import csv
import sqlite3
from scrape_audubon import get_bird_urls_audubon, get_bird_data_audubon

headers = {'User-Agent': 'Mozilla/5.0'}

# print(get_bird_data_audubon(
#     'https://www.audubon.org/field-guide/bird/wood-sandpiper'
# ))
# print(get_bird_data_audubon(
#     'https://www.audubon.org/field-guide/bird/evening-grosbeak'
# ))
# get_bird_data_audubon(
#     'https://www.audubon.org/field-guide/bird/evening-grosbeak'
# )

def get_all_bird_data(urls):
    """Get information of all birds listed in the audubon website"""
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(get_bird_data_audubon, url) for url in urls]
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        return results


def write_to_csv(birds):
    """Write data of all birds to a csv file and save on disk"""
    with open(
            'bird_database_audubon.csv',
            mode='w',
            newline='',
            encoding='UTF-8'
        ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Name', 'Scientific Name', 'Description',
            'Conservation Status', 'Family', 'Habitat',
            'Feeding Behavior', 'Eggs', 'Young', 'Diet',
            'Nesting', 'Migration', 'Songs and Calls', 'URL'
        ])
        for bird in birds:
            writer.writerow(bird)

def create_birds_table():
    """Create birds SQLite table"""
    connection = sqlite3.connect('birds.db')
    cursor = connection.cursor()
    cursor.execute(
        'CREATE TABLE birds ( \
            id INTEGER PRIMARY KEY, \
            name TEXT, \
            scientific_name TEXT, \
            description TEXT, \
            conservation_status TEXT, \
            family TEXT, \
            habitat TEXT, \
            feeding_behavior TEXT, \
            eggs TEXT, \
            young TEXT, \
            diet TEXT, \
            nesting TEXT, \
            migration TEXT, \
            songs TEXT, \
            url TEXT \
        )'
    )

def write_bird_data(all_bird_data):
    """Write all bird data into birds table"""
    connection = sqlite3.connect('birds.db')
    cursor = connection.cursor()

    cursor.executemany('INSERT INTO birds( \
                        name, \
                        scientific_name, \
                        description, \
                        conservation_status, \
                        family, \
                        habitat, \
                        feeding_behavior, \
                        eggs, \
                        young, \
                        diet, \
                        nesting, \
                        migration, \
                        songs, \
                        url) \
                    VALUES( \
                       ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? \
                    )', all_bird_data)
    connection.commit()

if __name__ == '__main__':
    bird_urls = get_bird_urls_audubon()
    all_bird_data = get_all_bird_data(bird_urls)
    write_bird_data(all_bird_data)
    # write_to_csv(birds_data)