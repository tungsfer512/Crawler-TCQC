import requests
import logging
from bs4 import BeautifulSoup 

_logger = logging.getLogger(__name__)

def link_mic():
    arr = ["https://mic.gov.vn/khoa-hoc-va-cong-nghe.htm"]
    return arr

def mic(link):
    data = get_data_mic(link)
    return data

def get_data_mic(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = []
    list_news = soup.find('div', class_= 'list__news').find_all('div', class_='box-category-item')
    list_focus = soup.find('div', class_= 'list__focus').find_all('div', class_='box-category-item')
    for category in list_news + list_focus:
        link = category.find('a').get('href')
        name = category.find('a').get('title')
        mo_ta = category.find('p').text.strip().replace("\n", "").replace("-", "").replace("  ", " ")
        data.append({
            "link" : 'https://mic.gov.vn' + link,
            "name" : name,
            "mo_ta" : mo_ta
        })
    return data