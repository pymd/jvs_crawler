from bs4 import BeautifulSoup
import requests
import logging
import os
import sys

from config import BASE_URL
from tasks import save_urls_to_db

from jvs_crawler import get_celery_status

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
logger = logging.getLogger('')


class UrlCrawler:
    """
        Entry point into the crawler
    """
    def __init__(self):
        self.url = BASE_URL
        self.top_level_bride_urls = list()
        self.top_level_groom_urls = list()
        self.bride_urls = list()
        self.groom_urls = list()

    def crawl(self):
        # Fetch all the links from the footer navigation bar
        print('Starting crawler for url: ' + self.url)
        try:
            resp = requests.get(self.url)
            html = resp.text
        except Exception as e:
            logging.error(str(e))
            raise Exception('Error in crawling the base url: %s' % self.url)

        soup = BeautifulSoup(html, 'html.parser')
        categories = soup.find_all('div', class_='subhobver')

        for category in categories:
            links = category.find('div', class_='hpbg5 wr1 pos-rel')
            links_list = links.find_all('a')
            bride_element = links_list[0]
            groom_element = links_list[1]

            self.top_level_bride_urls.append(bride_element['href'])
            self.top_level_groom_urls.append(groom_element['href'])

        print('Found %s top level bride urls' %
              str(len(self.top_level_bride_urls)))
        print('Saving them to database ...')
        save_urls_to_db.delay(self.top_level_bride_urls)

        print('Found %s top level groom urls' %
              str(len(self.top_level_groom_urls)))
        print('Saving them to database ...')
        save_urls_to_db.delay(self.top_level_groom_urls)

        print('Finding more bride urls ...')
        self.fetch_all_bride_urls()
        print('Done')

        print('Finding more groom urls ...')
        self.fetch_all_groom_urls()
        print('Done')

    def fetch_all_bride_urls(self):
        count = 0
        for brides_url in self.top_level_bride_urls:
            try:
                resp = requests.get(brides_url)
                html = resp.text
            except Exception as e:
                print('Error: ' + str(e))

            soup = BeautifulSoup(html, 'html.parser')
            cells = soup.find_all('td', class_='cells')

            for cell in cells:
                self.bride_urls.append(cell.a['href'])

            count += len(set(self.bride_urls))
            save_urls_to_db.delay(self.bride_urls)
            self.bride_urls = list()

        logger.debug('Total len of bride urls: ' + str(count))

    def fetch_all_groom_urls(self):
        count = 0
        for grooms_url in self.top_level_groom_urls:
            try:
                resp = requests.get(grooms_url)
                html = resp.text
            except Exception as e:
                print('Error: ' + str(e))

            soup = BeautifulSoup(html, 'html.parser')
            cells = soup.find_all('td', class_='cells')

            for cell in cells:
                self.groom_urls.append(cell.a['href'])

            count += len(set(self.groom_urls))
            save_urls_to_db.delay(self.groom_urls)
            self.groom_urls = list()

        print('Total len of groom urls: ' + str(count))


if __name__ == '__main__':
    # Setup logging (__init__.py)
    # Setup DB Connections; If not raise exception; halt (__init__.py)
    # Create Database tables if not present
    # Check if Celery is working; If not throw exception; halt (__init__.py)
    # Create Crawler Object
    # Call crawler.crawl() method to start crawling
    print(get_celery_status())
    crawler = UrlCrawler()
    crawler.crawl()
