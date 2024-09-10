import json
import requests
from bs4 import BeautifulSoup


def link_gpp():
    link = "https://www.3gpp.org/3gpp-groups"
    domain = "https://www.3gpp.org"
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
                    "link": domain + subcategory_link,
                    "tree": tree,
                }
            )
    return data_return


# print(link_gpp())


def get_last_link_3pgpp(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        url = soup.select_one("a[href*='dynareport']").attrs["href"]
        print(url)
        link = "https://www.3gpp.org" + url
        return link
    except Exception as e:
        print(e)
        return False


# print(get_last_link_3pgpp("https://www.3gpp.org/3gpp-groups/radio-access-networks-ran/ran-wg2"))


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


# print(lifecycle_gpp(
#     1,
#     "https://www.3gpp.org/DynaReport/36201.htm",
# ))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
import pandas as pd
import os

TMP_FILE = "./tmp/etsi.csv"


def get_etsi_data(url):
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(10)
        url_download = driver.execute_script(
            'var url=standardssearchGetURI("csv") + "&x=" + Date.now();return url;'
        )
        response = requests.get(url_download)
        if response.status_code == 200:
            os.makedirs("./tmp", exist_ok=True)
            with open(TMP_FILE, "wb") as file:
                file.write(response.content)
        else:
            print("LOI TAI FILE")
            return []
        with open(TMP_FILE, "r") as fin:
            data = fin.read().splitlines(True)
        with open(TMP_FILE, "w") as fout:
            fout.writelines(data[1:])
        try:
            df = pd.read_csv(
                TMP_FILE,
                sep=";",
                quotechar='"',
                skiprows=1,
                usecols=[0, 1, 2, 3, 4, 5, 6],
            )
            df.columns = [
                "id",
                "code",
                "title",
                "status",
                "link",
                "file_link",
                "description",
            ]
            print(len(df))
            json_data = df.to_json(orient="records")
            std_links = json.loads(json_data)
            return std_links
        except Exception as e:
            print(e)
            return []
    except Exception as e:
        print(e)
        return []


print(
    get_etsi_data(
        "https://www.etsi.org/standards#page=1&search=&title=1&etsiNumber=1&content=1&version=0&onApproval=1&published=1&withdrawn=1&historical=1&isCurrent=1&superseded=1&startDate=1988-01-15&endDate=2024-09-10&harmonized=0&keyword=&TB=&stdType=&frequency=&mandate=&collection=&sort=1"
    )[:10]
)
