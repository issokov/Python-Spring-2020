import json
from hashlib import md5
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime as dt


def load_from_json(urls_json_fname):
    with open(urls_json_fname, "r", encoding="utf-8") as urls_json:
        return json.loads(urls_json.read())


def get_hash(data):
    try:
        return md5(BeautifulSoup(data, 'html.parser').text.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f'Parsing error: {e}')
        return None


class WebStealer:

    timeout = 3

    def __init__(self, hash_func=get_hash, urls_json_fname=None):
        self.urls = load_from_json(urls_json_fname) if urls_json_fname else None
        self.stamps = {url: self.init_stamp() for url in self.urls} if self.urls else None
        self.hash_func = hash_func

    def init_stamp(self):
        return {
            "errors": 0,
            "success": 0,
            "updates": [],
        }

    def scrap(self, url):
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) ' \
                     'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/35.0.1916.47 Safari/537.36'
        request = Request(url, headers={'User-Agent': user_agent})
        with urlopen(request, timeout=self.timeout) as resp:
            return resp.read()

    def save_stamps(self, file_name='stamps.json'):
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.stamps, indent=2))

    def update_stamp(self, url, data):
        curr_dt = dt.now().timestamp()
        new_hash = self.hash_func(data)
        stamp = self.stamps[url]
        stamp['updates'].append((curr_dt, new_hash))
        stamp[('success' if new_hash else 'errors')] += 1

    def update(self):
        with ThreadPoolExecutor(max_workers=min(50, len(self.urls))) as executor:
            feature_dict = {executor.submit(self.scrap, url): url for url in self.urls}
            for feature in as_completed(feature_dict.keys()):
                url = feature_dict[feature]
                data = None
                try:
                    data = feature.result()
                except Exception as e:
                    print(f'Error in {url}: {e}')
                self.update_stamp(url, data)
                self.save_stamps()
