import re
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.error import HTTPError


class RateStealer:
    cbr_usd_url = "http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/1999&date_req2=20/03/2020&VAL_NM_RQ=R01235"
    cbr_eur_url = "http://www.cbr.ru/scripts/XML_dynamic.asp?date_req1=01/01/1999&date_req2=20/03/2020&VAL_NM_RQ=R01239"
    moex_url = "https://www.moex.com/ru/derivatives/currency-rate.aspx?currency="
    currency_pairs = ["CAD_RUB", "CHF_RUB", "CNY_RUB", "EUR_RUB",
                      "JPY_RUB", "TRY_RUB", "UAH_RUB", "USD_CAD",
                      "USD_CHD", "USD_JPY", "USD_INR", "USD_RUB",
                      "USD_TRY", "USD_UAH", "INR_RUB"]
    cbr_usd_rate = {}
    cbr_eur_rate = {}

    def __init__(self):
        def extract_cbr(target_dict, url):
            while True:
                try:
                    response = urlopen(url)
                    break
                except HTTPError as err:
                    print(err.reason, err.code)

            data = response.read().decode("utf-8")
            root = ET.fromstring(data)
            for child in root.findall("Record"):
                target_dict[child.attrib['Date']] = child[1].text
        extract_cbr(self.cbr_usd_rate, self.cbr_usd_url)
        extract_cbr(self.cbr_eur_rate, self.cbr_eur_url)

    def get_cbr_rate(self, is_usd, day, month, year):
        cy_rate = self.cbr_usd_rate if is_usd else self.cbr_eur_rate
        for yyyy in range(year, 1998, -1):
            for mm in range(month, 0, -1):
                for dd in range(day, 0, -1):
                    str_day = ("0" if dd < 10 else "") + str(dd)
                    str_month = ("0" if mm < 10 else "") + str(mm)
                    date = "{}.{}.{}".format(str_day, str_month, str(year))
                    if date in cy_rate:
                        return cy_rate[date].replace(',', '.')
                day = 31
            month = 12
        return 30 if is_usd else 40

    def get_moex_rates_now(self, choosen_pairs : list):
        answer = {}
        for pair in choosen_pairs:
            if pair in self.currency_pairs:
                url = self.moex_url + pair
                try:
                    response = urlopen(url)
                    data = response.read().decode("utf-8")
                except:
                    raise RuntimeError("Server request failed.")
                date, time, value = self.__extract_data(data)
                answer["date"] = date
                answer["time"] = time
                answer[pair] = value

            else:
                raise ValueError("We don't have information about {}"
                                 " currency pair.\n Try one of these: {}"
                                 .format(pair,", ".join(map(str, self.currency_pairs))))
        return answer

    def __extract_data(self, data):
        finding_substr = "Текущее значение:"
        start_index = data.find(finding_substr)
        if start_index != -1:
            start_index += len(finding_substr)
            string = data[start_index:start_index + 50]
            try:
                value = re.findall(r'\d+,*\d*\s*</b>', string)[0][:-4].replace(',', '.')
                time = re.findall(r'\d\d:\d\d:\d\d', string)[0]
                date = re.findall(r'\d\d.\d\d.\d\d\d\d', string)[0]
                return date, time, value
            except:
                raise RuntimeError("Unable to retrieve data from the page.")