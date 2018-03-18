from bs4 import BeautifulSoup
import requests
from config import BASE_URL

class ProfileCrawler:
    def __init__(self, username=None):
        self.base_url = BASE_URL + '/profile/viewprofile.php?username='
        if username:
            self.username = username
            self.profile_link = self.base_url + self.username
        else:
            self.username = None
            self.profile_link = None

    def get_user_profile_link(self):
        if self.profile_link:
            return self.profile_link
        else:
            raise Exception('Empty username passed')

    def get_soup(self, url):
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'html.parser')
        return soup

    def get_gender(self, soup):
        p_tag = soup.find("p", {"id": "breadcrumbs"})
        gender = ''
        # check if user is groom or bride from the tags
        for span in p_tag.find_all('span'):
            if ('grooms' in span.text.lower()):
                gender = 'Male'
                break
            elif ('brides' in span.text.lower()):
                gender = 'Female'
                break
        return gender

    def get_user_details(self):
        user = {}
        soup = self.get_soup(self.get_user_profile_link())

        # check if user is groom , bride
        gender = self.get_gender(soup)
        user['Gender'] = gender 

        user_details_types = soup.find("ul", { "class": "prfdesc f14 clearfix"})
        user_details_links = user_details_types.find_all('li')
        age_height = user_details_links[0].text.encode('ascii', 'ignore').split(',')

        user['UserName'] = self.username
        user['Age'] = age_height[0]
        user['Height'] = age_height[1].strip(' ')
        user['Education'] = user_details_links[1].text.encode('ascii', 'ignore')    
        user['Location'] = user_details_links[2].text.encode('ascii', 'ignore') 
        user['Profession'] = user_details_links[3].text.encode('ascii', 'ignore')   
        user['Religion'] = user_details_links[4].text.encode('ascii', 'ignore') 
        user['Income'] = user_details_links[5].text.encode('ascii', 'ignore')   
        user['Language'] = user_details_links[6].text.encode('ascii', 'ignore')
        user['Marital Status'] = user_details_links[7].text.encode('ascii', 'ignore')
    
        return user 

        

        


# if __name__ == "__main__":
#   print (get_user_details('SSU2561'))
