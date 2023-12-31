import httpx
import re
import calendar
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def parser_hotel_data(html_text) -> list[dict]:
    hotel_html = BeautifulSoup(html_text, 'html.parser')
    tabhotel = hotel_html.find(id='TabHotel')
    h_kw = tabhotel.find('thead').find('tr').get_text().split()

    data = []
    for tr in tabhotel.find('tbody').find_all('tr'):
        row = {}
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
                data.append({
                    **row, 'customerid': tr.get('customerid'),
                    'groupeid': tr.get('groupeid'),
                    'hotelid': tr.get('hotelid'),
                    'uuid': tr.get('uuid')
                })

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
        x for x in filter(
            lambda r: re.search(re.escape(jiudian_name), r['操作']), loglist)
        if re.search(re.escape(fj_type), x['操作'])
    ]
    if len(row) >= 1:
        return {'ower': row[0].get("用户"), 'opt_time': row[0].get("时间")}

    return {'ower': '', 'opt_time': ''}


def comp_hotel_data(hotel_data: list[dict], loglist: list[dict]) -> list[dict]:

    def com_hotel(row):
        kw = find_ower(loglist, row.get('酒店名称'), row.get('房间类型'))
        return {**row, **kw}

    return [com_hotel(x) for x in hotel_data]


class LyouoaException(Exception):

    def __init__(self, code: int = 0, msg: str = "") -> None:

        self.code = code
        self.msg = msg

        return

    def __str__(self) -> str:
        return f'code: {self.code}\nmsg:\n{self.msg}\n'


class LyouoaClient():

    def __init__(self,
                 company_code: str,
                 session_id: str,
                 usercode: str,
                 host: str = "http://vip.lyouoa.com"):
        self._host = host
        self._company_code = company_code
        self._usercode = usercode
        self.set_session(session_id)

        return

    @property
    def host(self):
        return str(urljoin(self._host, f'/{self._company_code}'))

    @property
    def headers(self):

        return {
            "User-Agent":
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
        }

    @property
    def cookies(self):

        return {
            'ASP.NET_SessionId': self.session,
            'companyuid_sso': self._company_code,
            'companyuid': self._company_code,
            'usercode': self._usercode,
        }

    def set_session(self, session: str):

        self.session = session

        return

    @property
    def fields(self):
        return 'EID,GroupCode,GroupStartTimeFormatMMdd,GroupEndTimeFormatMMdd,CustomerName,LineName,PersonCountDisplay,PersonCountDisplay,PersonConfirmDisplay,MeetingPlate,RegulateName,ExternalName,RegulateOperatorName,StatusText,RegulateGuideNames,RegulateFoodSumPrice,RegulateTicketSumPrice,RegulateHotelSumPrice,RegulateVehicleSumPrice,RegulateTrafficTicketSumPrice,RegulateInsuranceSumPrice,RegulateShoppingNames,RegulateSelfShoppingNames,RegulateIncomeSumPrice,RegulateOutgoSumPrice,RegulateConnectionNames,RegulateTeamSync,RegulateStatus,IsActive,IsGuideChecked,IsFoodChecked,IsTicketChecked,IsHotelChecked,IsVehicleChecked,IsTrafficTicketChecked,IsInsuranceChecked,IsShoppingChecked,IsSelfShoppingChecked,IsIncomeChecked,IsOutgoChecked,IsConnectionChecked,InsertUserID,IsConnectionOpen,RegulateOperatorID,IsGuideProcess,IsTicketProcess,IsHotelProcess,IsFoodProcess,IsVehicleProcess,IsTrafficTicketProcess,IsInsuranceProcess,IsShoppingProcess,IsSelfShoppingProcess,IsIncomeProcess,IsOutgoProcess,IsConnectionProcess,IsTeamSyncChecked,IsTeamSyncProcess,AdultCount,ChildrenCount,CompanionCount,SignUpAdultCountConfirm,SignUpChildrenCountConfirm,SignUpCompanionCountConfirm,SignUpAdultCountTransfer,SignUpChildrenCountTransfer,SignUpCompanionCountTransfer,GroupStatus,IsCancel,InsertLastLogDay,UpdateLastLogDay'

    def get_eid_count(self, start_time='2022-01-01', end_time=None):

        if end_time is None:
            end_time = self.endTime()
        #
        u = urljoin(self._host,
                    f'/{self._company_code}/Regulate/QueryRegulateLayPage')
        r = httpx.post(url=u,
                       headers=self.headers,
                       cookies=self.cookies,
                       params={
                           'page': ['1'],
                           'limit': ['20'],
                           'RegulateStatus': ['0,1,2,3'],
                           'Classify': ['1'],
                           'StartTime': [start_time],
                           'EndTime': [end_time],
                           'BusinessClassify': ['0'],
                           'searchKey': ['GroupCode'],
                           'OrgID': ['0'],
                           'OrgName': ['选择部门'],
                           'GroupTimeKey': ['GroupStartTime'],
                           'Category1': ['0'],
                           'Category2': ['0'],
                           'Category3': ['0'],
                           'fields': [self.fields]
                       })

        if r.status_code != 200:
            raise LyouoaException(code=r.status_code, msg=r.text)

        try:
            count = r.json().get("count", 0)
            return count
        except Exception:
            raise LyouoaException(code=r.status_code, msg=r.text)

    def get_tanhao(self,
                   count: int,
                   limit: int = 100,
                   start_time='2022-01-01',
                   end_time=None):

        if end_time is None:
            end_time = self.endTime()

        all_data = []

        if (count % limit) != 0:
            pages = (count // limit) + 1
        else:
            pages = count // limit

        for page in range(pages):
            u = urljoin(
                self._host,
                f'/{self._company_code}/Regulate/QueryRegulateLayPage')
            r = httpx.post(url=u,
                           headers=self.headers,
                           cookies=self.cookies,
                           params={
                               'page': [page + 1],
                               'limit': [limit],
                               'RegulateStatus': ['0,1,2,3'],
                               'Classify': ['1'],
                               'StartTime': [start_time],
                               'EndTime': [end_time],
                               'BusinessClassify': ['0'],
                               'searchKey': ['GroupCode'],
                               'OrgID': ['0'],
                               'OrgName': ['选择部门'],
                               'GroupTimeKey': ['GroupStartTime'],
                               'Category1': ['0'],
                               'Category2': ['0'],
                               'Category3': ['0'],
                               'fields': [self.fields]
                           })

            if r.status_code != 200:
                raise LyouoaException(code=r.status_code, msg=r.text)

            try:
                data = r.json().get("data", [])
                all_data = [*all_data, *data]
            except Exception:
                raise LyouoaException(code=r.status_code, msg=r.text)

        return [(d["EID"], d["GroupCode"]) for d in all_data]

    def endTime(self) -> str:
        t = datetime.now()
        _, d = calendar.monthrange(t.year, t.month)

        return f'{t.year-t.month-d}'

    def get_Regulate_Hotel(
            self,
            groupEID: str,
            #start_time: str = datetime.now().strftime("%Y-%m-%d"),
            end_time=None):

        if end_time is None:
            end_time = self.endTime()
            u = urljoin(self._host,
                        f'/{self._company_code}/Regulate/Regulate_Hotel')
            r = httpx.get(
                url=u,
                headers=self.headers,
                cookies=self.cookies,
                params={
                    'Classify': ['1'],
                    'GroupEID': [groupEID],
                    'Index': ['4'],
                    'RegulateStatus': ['0,1,2,3'],
                    #'StartTime': [start_time],
                    'EndTime': [end_time],
                    'SearchKey': ['GroupCode'],
                    'OrgID': ['0'],
                    'OrgName': ['选择部门'],
                    'HasChange': ['false']
                })

        if r.status_code != 200:
            raise LyouoaException(code=r.status_code, msg=r.text)

        return r.text

    def get_RegulateLogList(self, groupEID: str):
        u = urljoin(self._host, f'{self._company_code}/Group/RegulateLogList')
        r = httpx.get(url=u,
                      headers=self.headers,
                      cookies=self.cookies,
                      params={
                          'RegulateClassify': ['6'],
                          'GroupEID': [groupEID]
                      })

        if r.status_code != 200:
            raise LyouoaException(code=r.status_code, msg=r.text)

        return r.text
