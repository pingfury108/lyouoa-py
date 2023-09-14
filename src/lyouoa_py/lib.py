import httpx
from urllib.parse import urljoin

class LyouoaClient():

    def __init__(self, host: str = "http://vip.lyouoa.com") -> None:
        self.host = host

    def get_tanhao(self, company_code: str):

        httpx.get(url=urljoin(self.host, f'/{company_code}/Regulate/QueryRegulateLayPage'),params={})
