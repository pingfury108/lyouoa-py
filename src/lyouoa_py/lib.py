import httpx
import re

from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parser_hotel_data(html_text) -> list[dict]:
    hotel_html = BeautifulSoup(html_text, 'html.parser')
    tabhotel = hotel_html.find(id='TabHotel')
    h_kw = tabhotel.find('thead').find('tr').get_text().split()

    data = []
    for tr in tabhotel.find('tbody').find_all('tr'):
        row = {
            'customerid': tr.get('customerid'),
            'groupeid': tr.get('groupeid'),
            'hotelid': tr.get('hotelid'),
            'uuid': tr.get('uuid')
        }
        for i, td in enumerate(tr.find_all('td')[1:]):
            ip = td.find('input')
            if ip:
                ip_v = ip.get('value')
                if ip_v:
                    row[h_kw[1:][i]] = ip_v.strip()
                else:
                    row[h_kw[1:][i]] = ""
            else:
                row[h_kw[i]] = " ".join(td.get_text().split()).strip()
                data.append(row)

    return data


def parser_loglist(html_text) -> list[dict]:
    loglist_html = BeautifulSoup(html_text, 'html.parser')
    h_kw = loglist_html.find('table').find('thead').get_text().split()
    data = []
    for tr in loglist_html.find('table').find('tbody').find_all('tr'):
        row = {}
        for r in zip(h_kw, map(lambda x: x.get_text(), tr.find_all('td'))):
            row[r[0]] = r[-1]
            data.append(row)

    return [x for x in data if re.search('新建', x['操作'])]


def find_ower(loglist: list, jiudian_name: str, fj_type: str) -> dict:
    row = [
        x for x in filter(lambda r: re.search(jiudian_name, r['操作']), loglist)
        if re.search(fj_type, x['操作'])
    ]
    if len(row) >= 1:
        return {'ower': row[0].get("用户"), 'opt_time': row[0].get("时间")}
    else:
        return {}


class LyouoaClient():

    def __init__(self,
                 company_code: str,
                 host: str = "http://vip.lyouoa.com") -> None:
        self.host = urljoin(host, f'/{company_code}')

        return

    @property
    def headers(self):

        return {
            "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }

    @property
    def cookies(self):

        return {'ASP.NET_SessionId': self.session}

    def set_session(self, session: str):

        self.session = session

        return

    def get_tanhao(self):

        httpx.get(url=urljoin(self.host, '/Regulate/QueryRegulateLayPage'),
                  headers=self.headers,
                  cookies=self.cookies,
                  params={})

        return
