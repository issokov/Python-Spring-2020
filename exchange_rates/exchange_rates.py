import os
import re
import time as tm
from collections import defaultdict
from urllib.request import urlopen

currency_pairs = ["CAD_RUB", "CHF_RUB", "CNY_RUB", "EUR_RUB",
                  "JPY_RUB", "TRY_RUB", "UAH_RUB", "USD_CAD",
                  "USD_CHD", "USD_JPY", "USD_INR", "USD_RUB",
                  "USD_TRY", "USD_UAH", "INR_RUB"]


def extract_data(data):
    finding_substr = "Текущее значение:"
    start_index = data.find(finding_substr)
    if start_index != -1:
        start_index += len(finding_substr)
        string = data[start_index:start_index+50]
        try:
            value =re.findall(r'\d+,*\d*\s*</b>', string)[0][:-4].replace(',', '.')
            time = re.findall(r'\d\d:\d\d:\d\d', string)[0]
            date = re.findall(r'\d\d.\d\d.\d\d\d\d', string)[0]
            return date, time, value
        except:
            print(start_index)
            print(data[start_index:start_index+50])
            print(data)
    return None, None, None

folder_name = "data"
moex_url = "https://www.moex.com/ru/derivatives/currency-rate.aspx?currency="
last_update = defaultdict(str)
updated = []
if not os.path.exists(folder_name):
    os.mkdir(folder_name)

while True:
    for pair in currency_pairs:
        try:
            response = urlopen(moex_url+pair)
        except:
            print("Abort! No connection. Sleep 59 seconds")
            tm.sleep(59)
        if response.code == 200:
            data = response.read().decode("utf-8")
            date, time, value = extract_data(data)
            if date != None:
                if not os.path.exists(folder_name+'/'+date):
                    os.mkdir(folder_name+'/'+date)
                else:
                    if last_update[pair] != time:
                        last_update[pair] = time
                        file = open("{}/{}/{}.txt".format(folder_name, date, pair), "a")
                        file.write("{} {}\n".format(time,value))
                        file.close()
                        updated.append(pair)
                        
            else:
                print("Failed: ", pair)
        else:
            print("Ooops, something gonna wrong ", response.reason)
    print("Updated: ", *updated)
    updated.clear()
    print("Sleep 59 sec")
    tm.sleep(59)
