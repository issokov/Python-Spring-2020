import json
import pymongo
from zipfile import ZipFile
from random import shuffle
from urllib.request import urlopen


class CreateDB:
    authors = dict()
    tags = ['name', 'category', 'description', 'periodStr', 'authors', 'dimStr', 'id', 'extUrl', 'typologyDesc']

    def __init__(self, database, zipfile_name, read_n=None):
        # 2020-04-03 Ruslan Nasonov: в конструктор лучше помещать только инициализацию
        # Это специальный класс, экземпляр которого нигде не хранится, он вызывается, делает свою работу, и сразу же умирает
        # сделал рефакторинг

        self.db = database
        self._create_index()

        # 2020-04-03 Ruslan Nasonov: это видимо метод с сайд эффектом. А если вызов метода переместить на строчку выше, что будет?
        #
        self._get_museums_coords()
        self._load_data(zipfile_name, read_n)

    def _create_index(self):
        self.db.exhibits.create_index("id")
        self.db.exhibits.create_index([("authors", pymongo.TEXT)], default_language="russian")

        # 2020-04-03 Ruslan Nasonov: монга уже создает уникальный идентификатор _id. Можно записывать id музея в это поле
        # исправлено
        self.db.museums.create_index([("_id", pymongo.ASCENDING), ("location", pymongo.GEOSPHERE)], unique=True)

        # 2020-04-03 Ruslan Nasonov: а эта коллекция точно нужна? Кто ее пересчитывает? Может считать это все на лету, или сделать view?
        # исправлено: коллекция убрана

        # 2020-04-03 Ruslan Nasonov: можно искать не только в авторе, но и в названии
        # не согласуется с архитектурой: всё завязано на уникальном ай-ди автора, если его нету в списке авторов,
        # то предмет нельзя идентифицировать, по этому параметру...

        # 2020-04-03 Ruslan Nasonov: а зачем отдельная таблица для авторов? Они же вроде не размечены, прим. Александр Пушкин и А. Пушкин
        # исправлено: таблица убрана

    def _load_data(self, zipfile_name, read_n):
        with ZipFile(zipfile_name) as zip_file:
            names_list = zip_file.namelist()
            shuffle(names_list)
            for file_name in names_list:
                with zip_file.open(file_name) as file:
                    print("Start reading: {}, remain: {}".format(file_name, read_n))
                    read_n = self._read_from_zipext(file, read_n)
                    if read_n == 0:
                        break

    def _get_museums_coords(self):
        url = "https://goskatalog.ru/muzfo-rest/rest/museums/"
        museum_info = json.loads(urlopen(url).read().decode('utf-8'))
        unknown_museums = {}
        with open("geo.txt") as file_handler:
            for unknown_museum in file_handler:
                colon_pos = unknown_museum.find(': ')
                museum_id = int(unknown_museum[:colon_pos])
                lat, lon = map(float, unknown_museum[colon_pos+2:].split())
                unknown_museums[museum_id] = (lat, lon)
        result_museums = []
        for museum in museum_info['museums']:
            latitude, longitude = museum['latitude'], museum['longitude']
            museum_id = museum["id"]
            # 2020-04-03 Ruslan Nasonov: тут видимо опечатка latitude == 0 and latitude == 0
            # Исправлено
            if latitude == 0 and longitude == 0 and museum_id in unknown_museums:
                latitude, longitude = unknown_museums[museum_id]
            if latitude <= -90 or latitude >= 90 or longitude <= -180 or longitude >= 180:
                latitude, longitude = 0, 0
            result_museums.append({
                "_id": museum['id'],
                "name": museum['name'],
                "address": museum['addressString'],
                "location": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                }
            })
        # 2020-04-03 Ruslan Nasonov: можно вставлять сразу много записей
        # Исправлено
        self.db.museums.insert_many(result_museums)

    def _read_from_zipext(self, file, read_n=None):
        file_data = json.loads(file.read().decode('utf8'))
        prepared_objs = []
        for item in file_data:
            prepared_objs.append(self.prepare_item(item))
            if read_n is not None:
                read_n -= 1
                if read_n == 0:
                    break
        self.db.exhibits.insert_many(prepared_objs)
        return read_n

    def prepare_item(self, raw_object: dict):
        item = raw_object['data']
        exhibit = dict()

        for tag in self.tags:
            if tag in item:
                exhibit[tag] = item[tag]

        exhibit['museum_id'] = item['museum']['id']

        if 'authors' in item:
            exhibit["authors_id"] = []
            for author in item['authors']:
                if author not in self.authors:
                    self.authors[author] = len(self.authors)
                self.db.author_museum_id.update_one({
                    "author": self.authors[author],
                    "museum_id": exhibit['museum_id']
                }, {"$inc": {"count": 1}}, upsert=True)
                exhibit["authors_id"].append(self.authors[author])
        # 2020-04-03 Ruslan Nasonov: а тут точно лучше вставлять данные пачкой, иначе уж слишком много запросов к базе
        # исправлено
        return exhibit
