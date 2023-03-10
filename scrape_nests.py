from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import sqlite3
from scrape_audubon import get_bird_urls_audubon, get_bird_data_audubon

headers = {'User-Agent': 'Mozilla/5.0'}

def scrape_all_bird_data(urls):
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
    connection.commit()
    connection.close()

def clear_birds_table():
    """Clear all bird data from table"""
    connection = sqlite3.connect('birds.db')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM birds')
    connection.commit()
    connection.close()

def reset_bird_table_sequence():
    """Resets auto-increment sequence for birds.db to 0"""
    connection = sqlite3.connect('birds.db')
    cursor = connection.cursor()
    table_name = 'birds'
    cursor.execute('UPDATE sqlite_sequence SET seq=0 WHERE name=?',(table_name,))
    connection.commit()
    connection.close()

def write_bird_data():
    """Write all bird data into birds table"""
    bird_urls = get_bird_urls_audubon()
    all_bird_data = scrape_all_bird_data(bird_urls)

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
    connection.close()

if __name__ == '__main__':
    write_bird_data()
    # write_to_csv(birds_data)