import json
import requests
import logging
from bs4 import BeautifulSoup
import os
import utils
import pandas as pd

_logger = logging.getLogger(__name__)


def download_file_iec(url, output):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
        else:
            return False
    except Exception as e:
        return False


def fetch_excel_file_iec(datas, tree):
    try:
        # Sử dụng BeautifulSoup để phân tích cú pháp nội dung XML
        soup = BeautifulSoup(datas, "xml")

        # Tìm tất cả các hàng dữ liệu
        rows = soup.find_all("Row")[2:]  # Bỏ qua hàng tiêu đề và hàng mô tả
        data = []
        for row in rows:
            try:
                cells = row.find_all("Cell")
                link = False
                for cell in cells:
                    if "ss:HRef" in cell.attrs:
                        link = cell.attrs["ss:HRef"]
                # lifecycle = iec_get_version(link)
                row_data = [
                    cell.find("Data").get_text() if cell.find("Data") else False
                    for cell in cells
                ]
                row_data.append(link)
                data.append(row_data)
            except Exception as e:
                link = False
                _logger.error(e)
            _logger.error(link)

        # # Chuyển đổi dữ liệu thành DataFrame
        columns = [
            "Reference",
            "Edition",
            "Corrigenda/IS",
            "Date",
            "Title",
            "Language",
            "Description",
            "link",
        ]
        df = pd.DataFrame(data, columns=columns)
        # # Đổi tên các cột cho khớp với cấu trúc dữ liệu mong muốn
        columns_mapping = {
            "Reference": "so_hieu",
            "Edition": "edition",
            "Corrigenda/IS": "Corrigenda_IS",
            "Title": "ten_tieng_anh",
            "Language": "language",
            "Description": "mo_ta",
            "Date": "nam_ban_hanh",
            "link": "link",
        }
        df.rename(columns=columns_mapping, inplace=True)
        standard = []

        # # Duyệt qua các hàng trong DataFrame và tạo đối tượng data_out
        for _, row in df.iterrows():
            datas = utils.data_out(
                Corrigenda_IS=(
                    row["Corrigenda_IS"] if pd.notna(row["Corrigenda_IS"]) else False
                ),
                language=row["language"] if pd.notna(row["language"]) else False,
                edition=row["edition"] if pd.notna(row["edition"]) else False,
                mo_ta=row["mo_ta"] if pd.notna(row["mo_ta"]) else False,
                ten_tieng_anh=(
                    row["ten_tieng_anh"] if pd.notna(row["ten_tieng_anh"]) else False
                ),
                so_hieu=row["so_hieu"] if pd.notna(row["so_hieu"]) else False,
                nam_ban_hanh=(
                    row["nam_ban_hanh"] if pd.notna(row["nam_ban_hanh"]) else False
                ),
                duong_link=row["link"],
                trees=[tree],
                # lifecycle = lifecycle,
            )
            standard.append(datas)
        return standard

    except FileNotFoundError:
        print("Lỗi: Không tìm thấy tệp.")
    except ValueError as ve:
        print(f"Lỗi: {ve}")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

        print(f"Đã xảy ra lỗi: {e}")


def lifecycle_iec(id, link):
    BASE_URL = "https://webstore.iec.ch/en/"
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    div_tag = soup.find("div", {"x-show": "activeTab === 'lifecycle'"})
    script_tag = div_tag.find("script")
    text_script = script_tag.get_text()
    start = text_script.find("lifecycles")
    end = text_script.find("statusMapping")
    lifecycles = json.loads(
        text_script[
            start
            + len("lifecycles")
            + 2 : end
            - len(
                """,
        """
            )
        ]
    )
    try:
        versions = []
        for lifecycles_v in reversed(lifecycles.values()):
            _logger.error(lifecycles_v)
            main_version = str(lifecycles_v["main"]["reference"]).strip()
            for items in reversed(lifecycles_v["versions"]):
                versions.append(
                    {
                        "name": items["reference"],
                        "link": BASE_URL + "publication/" + items["id"],
                    }
                )
            versions.append(
                {
                    "name": main_version,
                    "link": BASE_URL + "publication/" + str(lifecycles_v["main"]["id"]),
                }
            )
        return {
            "id": id,
            "lifecycle": versions,
        }
    except Exception as e:
        _logger.error(e)
        return {
            "id": id,
            "lifecycle": [],
        }


def link_iec():
    url = "https://www.iec.ch/technical-committees-and-subcommittees#tclist"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    rows = soup.find_all("tr")
    tc_links = []
    for row in rows[0:5]:
        td_publications = row.find("td", class_="datatable-column-publications")
        if td_publications:
            a_link = td_publications.find("a")
            link = "https://www.iec.ch" + a_link["href"] if a_link else False
        else:
            link = False
        arr_tree = [
            {
                "key": "IEC",
                "des": "IEC ROOT",
            }
        ]
        if link:
            dest_dropdown = row.find("a", class_="dest-dropdown")
            if dest_dropdown:
                dest_dropdown_text = dest_dropdown.get_text(strip=True)
                # tc_links.append(f"{dest_dropdown_text.replace(' ', '_')}: {link}")
                arr_tree.append(
                    {
                        "key": dest_dropdown_text,
                        "des": row.find("td", class_="datatable-column-name").get_text(
                            strip=True
                        ),
                    }
                )
                tc_links.append(
                    {
                        "link": link,
                        "tree": arr_tree,
                    }
                )

    return tc_links


def iec(data):
    data = json.loads(data.replace("'", '"'))
    url = data["link"]
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    div_tag = soup.find("div", class_="dash-thread")

    # Nếu tìm thấy thẻ <div>, tìm thẻ <a> bên trong thẻ <div>
    if div_tag:
        a_tag = div_tag.find("a", href=True)
        if a_tag:
            # Lấy giá trị của thuộc tính href
            href_value = a_tag["href"]
            # Trích xuất chuỗi cần thiết từ href_value
            start = href_value.find("f?p=")
            if start != -1:
                end = href_value.find("'", start)
                if end != -1:
                    extracted_value = href_value[start:end]
                else:
                    extracted_value = href_value[start:]
            else:
                extracted_value = None
        else:
            extracted_value = None
    else:
        extracted_value = None

    if extracted_value:
        download_url = "https://www.iec.ch/dyn/www/" + extracted_value
        path_download = "/tmp/crawler/data/iec/"
        if not os.path.exists(path_download):
            os.makedirs(path_download)
        data_download = download_file_iec(download_url, path_download + "data.xlsx")
        standard = fetch_excel_file_iec(data_download, data["tree"])
        return standard
    else:
        print("Lỗi: Không tìm thấy giá trị hợp lệ trong thẻ href.")
        return []
