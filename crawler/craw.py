import json
import requests
import logging
from bs4 import BeautifulSoup
import time
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import crawler.crawl.etsi as etsi

_logger = logging.getLogger(__name__)


# ITU
def download_and_identify_file_itu(url, download_dir=os.getcwd(), timeout=60):
    """
    Tải tệp từ trang web và xác định tên tệp vừa tải về.

    Parameters:
    url (str): Đường dẫn đến trang web chứa tệp cần tải.
    download_dir (str): Thư mục lưu tệp tải về. Mặc định là thư mục hiện tại.
    timeout (int): Thời gian chờ tối đa để tệp tải về (giây). Mặc định là 60 giây.

    Returns:
    str: Tên tệp vừa tải về hoặc None nếu quá thời gian chờ.
    """
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    # Thiết lập tùy chọn Chrome
    options = Options()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        },
    )
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-in-process-stack-traces")
    options.add_argument("--disable-logging")
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(url)
    bttn = driver.find_element(By.XPATH, '//*[@id="ctl00_content_result_ibtnExcel"]')
    bttn.click()
    wait_for_downloads(download_dir)
    path_file_download = False
    for filename in os.listdir(download_dir):
        path_file_download = f"{download_dir}/{filename}"
    driver.quit()

    return path_file_download


def get_infor_itu(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    span = soup.find(
        "span", id="ctl00_content_main_uc_rec_main_info1_rpt_main_ctl00_Label6"
    )
    text = span.get_text(separator="\n") if span else ""
    lines = text.split("\n")

    tree_tmp = [
        {
            "key": "ITU",
            "des": "The International Telecommunication Union (ITU) is the United Nations specialized agency for information and communication technologies – ICTs.",
        },
        {
            "key": "ITU-T",
            "des": "The ITU-T Recommendations constitute a set of international technical standards developed by the Telecommunication Standardization Sector (formerly CCITT) of the ITU.",
        },
    ]
    trees = []
    for line in lines:
        tree = tree_tmp
        line = line.strip()
        if line:
            parts = line.split(":", 1)
            if len(parts) > 1:
                sub_parts = parts[0].strip().split()
                if sub_parts:
                    key = sub_parts[0]
                    des = parts[1].strip()
                    # series_data[s].append()
                    tree.append(
                        {
                            "key": key,
                            "des": des,
                        }
                    )
        trees.append(tree)
    return trees


def itu_fetch_standard_from_file(file_path, tree):
    # Đọc nội dung HTML từ tệp với xử lý lỗi mã hóa
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        html_content = file.read()

    # Phân tích cú pháp HTML
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", id="ctl00_content_result_grd_result")
    standards = []

    for row in table.find_all("tr")[1:]:  # Bỏ qua hàng tiêu đề
        cells = row.find_all("td")
        _logger.error(row)
        if len(cells) == 3:
            so_hieu = cells[0].text.strip()
            title = cells[1].text.strip()
            status = cells[2].text.strip()
            link = cells[0].find("a")["href"] if cells[0].find("a") else ""
            standard_data = data_out(
                so_hieu=so_hieu,
                ten_tieng_anh=title,
                trang_thai="con_hieu_luc" if status == "In force" else "het_hieu_luc",
                duong_link=link,
                trees=tree,
            )
            standards.append(standard_data)
    os.remove(file_path)
    return standards


def lifecycle_itu(id, link):
    if "itu-t" in link:
        domain = "https://www.itu.int/itu-t/recommendations"
        lifecycle = []
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        div_tag = soup.find(
            "div",
            {
                "id": "ctl00_content_main_TabContainer1_tab_edition_uc_rec_details1_div_rec_details"
            },
        )
        tr_tags = div_tag.find_all("tr")
        for tr in tr_tags:
            td_tags = tr.find_all("td")
            a_tag = td_tags[1].find("a")
            if a_tag:
                lifecycle.append(
                    {"name": a_tag.get_text(), "link": domain + a_tag.attrs["href"][1:]}
                )
        return {
            "id": id,
            "lifecycle": lifecycle,
        }
    else:
        lifecycle = []
        return {
            "id": id,
            "lifecycle": lifecycle,
        }


def itu(data):
    data = json.loads(data.replace("'", '"'))
    if data["type"] == "itu-t":
        tree = [
            [
                {
                    "key": "ITU",
                    "des": "The International Telecommunication Union (ITU) is the United Nations specialized agency for information and communication technologies – ICTs.",
                },
                {
                    "key": "ITU-T",
                    "des": "The ITU-T Recommendations constitute a set of international technical standards developed by the Telecommunication Standardization Sector (formerly CCITT) of the ITU.",
                },
                {"key": data["key"], "des": data["des"]},
            ]
        ]
        download_dir = "/tmp/crawler/data/itu"
        file_path = download_and_identify_file_itu(
            data["link"], "/tmp/crawler/data/itu"
        )
        standard = []
        if len(os.listdir(download_dir)):
            standard = itu_fetch_standard_from_file(file_path, tree)
        return standard
    else:
        data = itu_r(data)
        return data


def itu_r(data):
    tree = [
        [
            {
                "key": "ITU",
                "des": "The International Telecommunication Union (ITU) is the United Nations specialized agency for information and communication technologies – ICTs.",
            },
            {
                "key": "ITU-R",
                "des": "The ITU-R Recommendations constitute a set of international technical standards developed by the Radiocommunication Sector (formerly CCIR) of the ITU.",
            },
            {"key": data["key"], "des": data["des"]},
        ]
    ]
    all_link_standard = get_all_link_standard_itu_r(data["link"])
    data = []
    for link in all_link_standard:
        data.append(get_data_itu_r(link, tree))
    return data


def get_all_link_standard_itu_r(link):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(link)
    all_link = []
    td_tag = driver.find_element(By.XPATH, "/html/body/div[13]/table[1]/tbody/tr[5]/td")
    a_tag = td_tag.find_elements(By.TAG_NAME, "a")
    for a in a_tag[3:]:
        link = a.get_attribute("href")
        all_link.append(link)
    return all_link


def get_data_itu_r(link, tree):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize the Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(link)
    title = driver.find_element(
        By.XPATH, "/html/body/div[13]/table[1]/tbody/tr[4]/td/strong"
    ).text
    so_hieu = title.split(":")[0]
    data = data_out(ten_tieng_anh=title, so_hieu=so_hieu, trees=tree, duong_link=link)
    return data


# ANSI
def standard(url):
    standard = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    arr_link = []
    all_link = soup.find_all(
        "h1", class_="h4 mb-2 Oswald text-capitalize tracking-tight"
    )
    for link in all_link:
        arr_link.append("https://webstore.ansi.org" + link.find("a").get("href"))
    for link in arr_link:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")
        all_tieu_de = soup.find(
            "h1", class_="h4 Oswald text-capitalize tracking-tight mt-0"
        )
        if all_tieu_de != None:
            all_tieu_de = all_tieu_de.get_text(strip=True).split("-")
            so_hieu = all_tieu_de[0]
            ten_tieng_anh = all_tieu_de[1] if len(all_tieu_de) > 1 else all_tieu_de[0]
        else:
            so_hieu = "0"
            ten_tieng_anh = "0"
        prices = soup.find("a", class_="u-link-v5 text-dark text-uppercase")
        if prices != None:
            price = prices.get_text(strip=True)
        else:
            price = "0"
        abstract = soup.find("p", class_="font-16")
        if abstract != None:
            abstract = abstract.get_text(strip=True)
        else:
            abstract = "0"
        duong_link = link
        author = soup.find("span", class_="font-20 text-dark")
        if author != None:
            author = author.get_text(strip=True)
        else:
            author = "0"
        standard.append(
            data_out(
                so_hieu=so_hieu,
                ten_tieng_anh=ten_tieng_anh,
                mo_ta=abstract,
                duong_link=duong_link,
                tac_gia=author,
            )
        )
    return standard


# EN
def get_all_level_1(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        return [
            element.get("href")
            for element in soup.find_all("a", class_="kat level1 selected open0")
        ]
    except requests.RequestException as e:
        print(f"Error fetching level 1 links: {e}")
        return []


def check_level_and_get_standard(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        level_2 = [
            element.get("href")
            for element in soup.find_all("a", class_="kat level2 selected open0")
        ]

        standards = []
        if level_2:
            for level in level_2:
                standards += process_level(level)
        else:
            standards += fetch_standard_data(url)

        return standards
    except requests.RequestException as e:
        print(f"Error checking level: {e}")
        return []


def process_level(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        level_3 = [
            element.get("href")
            for element in soup.find_all("a", class_="kat level3 selected open0")
        ]

        standards = []
        if level_3:
            for lev in level_3:
                standards += fetch_standard_data(lev)
        else:
            standards += fetch_standard_data(url)

        return standards
    except requests.RequestException as e:
        print(f"Error processing level: {e}")
        return []


def get_page_count(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        pages_span = soup.find("span", class_="pages")
        links = pages_span.find_all("a") if pages_span else []
        return len(links) - 1  # Adjust as needed
    except requests.RequestException as e:
        print(f"Error getting page count: {e}")
        return 0


def fetch_standard(page, url):
    if page <= 0:
        return fetch_standard_data(url)
    else:
        url = url[:-1]
        new_url = f"{url}-page-{page}/"
        return fetch_standard_data(new_url)


def fetch_standard_data(url):
    standards = []
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        all_links = [link["href"] for link in soup.select("a.katalogProduct__name")]

        for link in all_links:
            try:
                response = requests.get(link)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                title = soup.select_one("div.fleft.detail_right_side").get_text(
                    strip=True
                )
                description = soup.find_all("div", class_="textFormat")
                descriptions = (
                    description[2].get_text(strip=True)
                    if len(description) > 2
                    else "n/a"
                )
                date_pub = soup.select_one(".released").get_text(strip=True)

                standards.append(data_out(ten_tieng_anh=title, mo_ta=descriptions))
                time.sleep(3)
            except requests.RequestException as e:
                print(f"Error fetching standard data for link {link}: {e}")
    except requests.RequestException as e:
        print(f"Error fetching standard data: {e}")

    return standards

# ETSI

def download_pdf(url, file_name):
    pass
    response = requests.get(url)
    with open(file_name, "wb") as file:
        file.write(response.content)


def fetch_standards_etsi(page, url_template):

    standard = []
    url = url_template.format(page=page)
    try:

        response = requests.get(url)

        if response.status_code == 200:
            datas = response.json()
            for data in datas:
                link_data = (
                    "https://www.etsi.org/deliver/"
                    + data["EDSpathname"].replace("\\", "")
                    + data["EDSPDFfilename"]
                )
                # download_pdf(link_data, data["ETSI_DELIVERABLE"])
                standard.append(
                    data_out(
                        ten_tieng_anh=data["TITLE"],
                        so_hieu=data["ETSI_DELIVERABLE"],
                        linh_vuc=data["TB"],
                        tu_khoa=data["Keywords"],
                        action_type=data["ACTION_TYPE"],
                        link_file=link_data,
                        name_file=data["EDSPDFfilename"],
                    )
                )

            return standard
        else:
            return []
    except Exception as e:
        print(e)
        return standard


# NIST
def NIST(page):
    a = page
    url = "https://csrc.nist.gov/publications/fips"
    resonpse = requests.get(url)
    link_arr_standard = []
    standard = []
    if resonpse.status_code == 200:
        soup = BeautifulSoup(resonpse.text, "html.parser")
        table = soup.find(id="publications-results-table")
        links = [a.get("href") for a in table.find_all("a", href=True)]

        # Hiển thị các liên kết đã trích xuất
        for link in links:
            link_arr_standard.append("https://csrc.nist.gov/" + link)
    for link in link_arr_standard:
        resonpse = requests.get(link)
        soup = BeautifulSoup(resonpse.text, "html.parser")
        header_text = soup.find(id="pub-header-display-container").get_text(strip=True)
        date_pub = soup.find(id="pub-release-date").get_text(strip=True)
        abstract = soup.find(id="pub-detail-abstract-info").get_text(strip=True)
        keyword = soup.find(id="pub-keywords-container").get_text(strip=True)
        statuss = soup.find_all("small")
        status = statuss[len(statuss) - 1].get_text(strip=True)
        links_download = soup.find(id="pub-local-download-link").get("href")
        author = soup.find(id="pub-authors-container").get_text(strip=True)
        tenfile = links_download.split("/")[-1]
        standard.append(
            data_out(
                ten_tieng_anh=header_text,
                so_hieu=False,
                link_file=links_download,
                name_file=tenfile,
                tac_gia=author,
                nam_ban_hanh=date_pub,
                tu_khoa=keyword,
                mo_ta=abstract,
            )
        )
    return standard


def etsi(link):
    return etsi.get_data(link)


# ham lay tong cac link


def link_itu():
    data_return = []
    link_itu_t = "https://www.itu.int/ITU-T/recommendations/index.aspx"
    response = requests.get(link_itu_t)
    soup = BeautifulSoup(response.text, "html.parser")
    select = soup.find("select", {"id": "ctl00_content_main_lst_series"})
    options = select.find_all("option")
    for option in options:
        value = option.attrs["value"]
        if value != "-1":
            data_return.append(
                {
                    "type": "itu-t",
                    "key": value,
                    "des": option.get_text(),
                    "link": f"https://www.itu.int/itu-t/recommendations/search.aspx?ser={value}&type=30&status=F&pg_size=20",
                }
            )
    link_itu_r = "https://www.itu.int/pub/R-REC"
    url_itu_r = "https://www.itu.int"
    response = requests.get(link_itu_r)
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    tr_tags = tables[-1].find_all("tr")
    for tr in tr_tags:
        tds = tr.find_all("td")
        link = url_itu_r + tds[0].find("a").attrs["href"]
        key = tds[0].find("a").get_text()
        des = tds[1].get_text()
        data_return.append({"type": "itu-r", "key": key, "des": des, "link": link})

    return data_return


def link_etsi():
    return etsi.get_all_link()
