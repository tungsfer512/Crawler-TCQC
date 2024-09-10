from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By
import pandas as pd
import json
import requests
import os


def get_etsi_link():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    url = "https://www.etsi.org/standards#Pre-defined%20Collections"
    driver.get(url)
    time.sleep(5)
    tree_root = {
        "key": "ETSI",
        "des": "ETSI ROOT",
    }
    return_data = []
    categories = driver.find_elements(By.CSS_SELECTOR, "li[id*='panel-item-']")
    for category in categories:
        tree = []
        if category.get_attribute("class") != "Pre-defined Collections":
            sector_name = category.get_attribute("class")
            tree_sector = {
                "key": sector_name,
                "des": sector_name,
            }
            tree.append(tree_root)
            tree.append(tree_sector)
            link_tag = category.find_element(By.CSS_SELECTOR, "a")
            tree.append(
                {
                    "key": link_tag.text,
                    "des": link_tag.text,
                }
            )
            return_data.append({
                "link": link_tag.get_attribute("href"),
                "tree": tree,
            })
    return return_data


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
            with open("./tmp/etsi.csv", "wb") as file:
                file.write(response.content)
        else:
            return []
        try:
            df = pd.read_csv(
                "./tmp/etsi.csv",
                sep=";",
                quotechar='"',
                # skiprows=1,
                usecols=[0, 1, 2, 3, 4, 5, 6, 7]
            )
            print(df)
            df.columns = [
                "id",
                "code",
                "name",
                "status",
                "link",
                "file_link",
                "description",
                "keywords",
            ]
            new_data = []
            # json_data = df.to_json(orient="records")
            # all_data = json.loads(json_data)
            # for data in all_data:
            #     data["nam_ban_hanh"] = int(data["so_hieu"][-8:-4])
            #     new_data.append(data)
            # os.remove("./tmp/etsi.csv")
            return new_data
        except Exception as e:
            return []
    except Exception as e:
        return []

def get_data_from_link(link):
    csv_url = get_etsi_data(link["link"])
    if csv_url != None:
        data = get_url(csv_url)
        for i in data:
            arr_res = []
            arr_tree = [
                {
                    "key": "ETSI",
                    "des": "ETSI - Producing globally applicable standards for ICT-enabled systems, applications & services deployed across all sectors of industry and society.",
                }
            ]
            arr_tree.append({"key": link["sector"], "des": ""})
            arr_tree.append({"key": link["type"], "des": ""})
            arr_res.append(arr_tree)
            i["tree"] = arr_res
        return data
    return []


def get_all(linh_vuc, phan_nhom):
    data_link = get_etsi_link()
    all_data = []
    for link in data_link:
        if link["sector"] == linh_vuc and link["type"] == phan_nhom:
            all_data.extend(get_data_from_link(link))
    return all_data


def get_data(link):
    all_data = []
    link = json.loads(link.replace("'", '"'))
    all_data.extend(get_data_from_link(link))
    return all_data


def get_all_link():
    return get_etsi_link()
