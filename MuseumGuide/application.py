from pymongo import MongoClient
from database_builder import CreateDB
from console_handler import ConsoleHandler
from museum_guide import MuseumGuide

class Application:
    db_name = "museum-guide"
    client = MongoClient()
    db = client[db_name]

    user = ConsoleHandler(db)
    guide = MuseumGuide(db)

    # 2020-04-03 Ruslan Nasonov: в конструкторе по возможности не должно быть никакой работы, только инициализация
    ## конструктор убран

    def create_db(self, zip_file_name, read_n=None):
        self.client.drop_database(self.db_name)
        CreateDB(database=self.db, zipfile_name=zip_file_name, read_n=read_n)

    def start(self):
        # 2020-04-03 Ruslan Nasonov: из этого цикла нет break, он работает бесконечно?
        # исправлено
        while True:
            authors_ids = self.user.ask_about_author(self.guide)
            if not authors_ids:
                break # break добавлен
            museums_and_counts = self.guide.find_museums(authors_ids)
            while True:
                museum_id = self.user.report_and_ask_exhibits(museums_and_counts)
                if museum_id:
                    exhibits_gen = self.guide.get_exhibits_gen(museum_id, authors_ids)
                    self.user.show_exhibits(exhibits_gen)
                else:
                    break
            tour_museums_counts = self.user.ask_about_tour(museums_and_counts)
            if tour_museums_counts:
                museums_buckets = self.guide.create_tour(tour_museums_counts)
                self.user.show_buckets(museums_buckets, len(tour_museums_counts))


app = Application()
app.create_db("data-4-structure-3.json.zip", read_n=100000)
app.start()
