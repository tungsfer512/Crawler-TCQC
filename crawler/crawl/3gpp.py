import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import utils

BASE_URL = "https://www.3gpp.org"


def link_gpp():
    link = f"{BASE_URL}/3gpp-groups"
    data_return = []
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    category_tags = soup.select("div.sppb-addon-content.sppb-text-center")
    for category_tag in category_tags:
        parent_tag = category_tag.find_parents(limit=4)[-1]
        subcategory_tags = parent_tag.select("div.sppb-addon-content.sppb-text-left")
        category_text = category_tag.text
        tree_tmp = {
            "key": category_text[: str(category_text).index(" ", 4, 10)],
            "des": category_text[str(category_text).index(" ", 4, 10) + 1 :],
        }
        for subcategory_tag in subcategory_tags[0:1]:
            subcategory_key = subcategory_tag.select_one("h5.sppb-addon-title a")
            subcategory_des = subcategory_tag.select_one("div.sppb-addon-text a")
            subcategory_link = subcategory_key.attrs["href"]
            tree = [
                {
                    "key": "3GPP",
                    "des": "3GPP ROOT",
                },
                tree_tmp,
            ]
            tree.append(
                {
                    "key": subcategory_key.text,
                    "des": subcategory_des.text,
                }
            )
            data_return.append(
                {
                    "link": BASE_URL + subcategory_link,
                    "tree": tree,
                }
            )
    return data_return


def get_data_3pgpp(arr_link, tree):
    data_arr = []
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    for link in arr_link:
        driver.get(link)
        title = driver.find_element(By.ID, "titleVal").text
        so_hieu = driver.find_element(By.ID, "referenceVal").text
        trang_thai = driver.find_element(By.ID, "statusVal").text
        loai = driver.find_element(By.ID, "typeVal").text
        data = utils.data_out(
            so_hieu=so_hieu, ten_tieng_anh=title, trees=[tree], duong_link=link
        )
        data_arr.append(data)
    return data_arr


def get_last_link_3pgpp(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        url = soup.select_one("a[href*='dynareport']").attrs["href"]
        print(url)
        link = BASE_URL + url
        return link
    except Exception as e:
        print(e)
        return False


def get_all_link_3pgpp(link):
    link_all = []
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    div_tag = soup.find_all("div", class_="sppb-media-body")
    for div in div_tag:
        if div.find("h5"):
            link = div.find("h5").find("a")["href"]
            tree = {
                "key": div.find("h5").find("a").get_text(),
                "des": div.find("div", class_="sppb-addon-text").get_text(),
                "link": BASE_URL + link,
            }
            link_all.append(tree)
    return link_all


def get_all_link_standard_3pgpp(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    arr_link = []
    table = soup.find(
        "table",
        class_="dsptab adynspec dsp-tsgwg table table-sm table-bordered table-striped",
    )
    tr_tag = table.find_all("tr")
    for tr in tr_tag:
        link = tr.find_all("td")[0].find("a").get("href")
        arr_link.append(BASE_URL + link)
    return arr_link


def gpp(data):
    data = json.loads(data.replace("'", '"'))
    link = data["link"]
    last_link = get_last_link_3pgpp(link)
    if last_link:
        all_link_standard = get_all_link_standard_3pgpp(last_link)
    else:
        return []
    tree = data["tree"]
    data = get_data_3pgpp(all_link_standard, tree)
    return data


def lifecycle_gpp(id, link):
    response = requests.get(
        link,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        },
    )
    soup = BeautifulSoup(response.text, "html.parser")
    version_tab_content = soup.select_one("#RadPageReleases")
    versions = version_tab_content.select(".rgRow, .rgAltRow")
    print(len(versions))
    lifecycle = []
    for version in versions:
        version_tag = version.select_one("a[id$='_lnkFtpDownload']")
        version_name = version_tag.text
        version_link = version_tag.attrs.get("href", False)
        lifecycle.append(
            {
                "name": version_name,
                "link": version_link,
            }
        )
    return {
        "id": id,
        "lifecycle": lifecycle,
    }
