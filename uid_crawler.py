from bs4 import BeautifulSoup
import requests
import logging

# from config import BASE_URL

logger = logging.getLogger(__file__)


class UidCrawler:
    def __init__(self):
        pass

    @staticmethod
    def get_usernames(url=None):
        usernames = list()
        try:
            resp = requests.get(url)
            html = resp.text
        except Exception as e:
            print('Error: ' + str(e))

        soup = BeautifulSoup(html, 'html.parser')
        users = soup.find_all('p', class_='f16 color11')
        for user in users:
            username = user.find('a').text
            usernames.append(username)

        print(len(usernames))
        return usernames
