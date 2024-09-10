import json
import requests
import logging
from bs4 import BeautifulSoup
import utils

_logger = logging.getLogger(__name__)

DOMAIN = "https://www.iso.org"


def iso_get_link_tree(endpoint, tree):
    response = requests.get(DOMAIN + endpoint)
    html_content = response.content
    soup = BeautifulSoup(html_content, "html.parser")
    td_tags = soup.find_all("td", {"data-title": "ICS"})
    links = []
    if len(td_tags):
        for td in td_tags[0:1]:
            a_tag = td.find("a")
            if a_tag:
                tr_parent = td.parent
                td_field = tr_parent.find("td", {"data-title": "Field"})
                endpoint_children = a_tag["href"]
                tree.append(
                    {
                        "key": a_tag.get_text(strip=True),
                        "des": td_field.get_text(strip=True),
                    }
                )
                link = DOMAIN + endpoint_children
                links_children = iso_get_link_tree(endpoint_children, tree)
                if not len(links_children):
                    links.append(
                        {
                            "link": link,
                            "tree": tree,
                        }
                    )
                    _logger.error(
                        {
                            "link": link,
                            "tree": tree,
                        }
                    )
                else:
                    links = links.extend(links_children)
    return links


def link_iso():
    endpoint = f"/standards-catalogue/browse-by-ics.html"
    tree = [
        {
            "key": "ISO",
            "des": "ISO ROOT",
        }
    ]
    return iso_get_link_tree(endpoint, tree)


def iso(data):
    data = json.loads(data.replace("'", '"'))
    url = data["link"]
    # _logger.error(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    iso_out = []
    tr_tags = soup.find_all("tr")
    for tr in tr_tags[0:10]:
        if "ng-show" in tr.attrs and tr.attrs["ng-show"] != "wChecked":
            link = DOMAIN + tr.find_all("a")[0].get("href")
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")

            description = soup.find("div", itemprop="description")
            if description:
                description_text = description.get_text(strip=True)
            else:
                description_text = "N/A"

            number = soup.find(
                "span", class_="d-flex justify-content-between align-items-start"
            )
            if number:
                inspan = number.find("span", class_="d-block mb-3")
                if inspan:
                    number_text = inspan.get_text(strip=True)
                else:
                    number_text = "N/A"
            else:
                number_text = "N/A"
            title_span = soup.find("span", class_="lead d-block mb-3")
            if title_span:
                title = title_span.get_text(strip=True)
            else:
                title = "N/A"
            link_sample = soup.find("a", class_="btn btn-sm btn-light")
            if link_sample:
                link_sample = link_sample.get("href")
            else:
                link_sample = "N/A"
            releaseDate = soup.find("span", {"itemprop": "releaseDate"})
            try:
                releaseDate = releaseDate.get_text(strip=True)
            except Exception as e:
                _logger.error(e)
                releaseDate = False
            tree = [data["tree"]]
            # get version
            li_tags = soup.find_all("li", {"class": "time-step"})
            lifecycle = []
            for li in li_tags:
                lifecycle = [li.find("h5").get_text(strip=True)]

            iso_out.append(
                utils.data_out(
                    ten_tieng_anh=title,
                    so_hieu=number_text,
                    trees=tree,
                    link_file=link_sample,
                    duong_link=link,
                    mo_ta=description_text,
                    nam_ban_hanh=releaseDate,
                    lifecycle=lifecycle,
                )
            )
    return iso_out


def lifecycle_iso(id, link):
    DOMAIN = "https://www.iso.org"
    response = requests.get(link)
    soup = BeautifulSoup(response.content, "html.parser")
    li_tags = soup.find_all("li", {"class": "time-step"})
    lifecycle = []
    curent_link = link
    for li in li_tags:
        h5 = li.find("h5")
        a = h5.find("a")
        try:
            link = DOMAIN + a.attrs["href"]
        except:
            link = curent_link
        lifecycle.append({"name": h5.get_text(strip=True), "link": link})
    return {
        "id": id,
        "lifecycle": lifecycle,
    }
