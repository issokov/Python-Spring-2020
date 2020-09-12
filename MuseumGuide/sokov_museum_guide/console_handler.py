from museum_guide import MuseumGuide
from pprint import pprint


def read_one_from_list(str_list: list):
    while True:
        value = input()
        if value in str_list:
            return value
        else:
            print(f"Ooops incorrect input. Try one of this: {str_list}")


def read_many_from_list(question: str, variants, quit_key, error: str):
    while True:
        print(question)
        answers = list(input().split())
        if answers == [quit_key]:
            return [quit_key]
        if not all(map(lambda x: x in variants, answers)):
            print(error)
        else:
            return answers



class ConsoleHandler:
    def __init__(self, db):
        self.db = db

    def ask_about_author(self, guide: MuseumGuide):
        while True:
            print("Which author are you interested in? Press enter for exit.")
            author = input()
            if not author:
                return None
            result = guide.find_authors(author)
            if result:
                return result
            print("Author not found.")

    def show_museums_list(self, museums):
        for num, (museum, count) in enumerate(museums, 1):
            name = self.db.museums.find_one({"_id": museum})["name"]
            print(f"{num}({count}). {name}")

    def report_and_ask_exhibits(self, museums_counts):
        # 2020-04-03 Ruslan Nasonov: есть f-строки, они поудобнее.
        # Везде Исправлено
        print(f"We found {len(museums_counts)} museums with total {sum(museums_counts.values())} exhibits",
              "\nPrinted top 50\n",
              "Please select a museum NUMBER to view its exhibits\n"
              "Or <ENTER> to create an excursion of the best museums\n"
              "NUMBER(Exhibits COUNT): Museum NAME\n",
              "__________________________________")
        items = list(museums_counts.items())[:50]
        self.show_museums_list(items)
        print("Your choose:", end=" ")
        answer = read_one_from_list([str(i) for i in range(1, len(museums_counts) + 1)] + [''])
        return items[int(answer) - 1][0] if answer else []

    def show_exhibits(self, exhibits_gen):
        def pretty_print(ex):
            print("__________________________________")
            targets = [("name", "Name"),
                       ("description", "Description"),
                       ("periodStr", "Creation period"),
                       ("dimStr", "Dimensions")]
            pprint({tag: (ex[target] if target in ex else "No info") for target, tag in targets})

        pretty_print(next(exhibits_gen.__iter__()))
        for exhibit in exhibits_gen:
            print("More: <ENTER>. Back<: <B>")
            answer = read_one_from_list(["", "b", "B"])
            if answer.lower() == "b":
                return
            pretty_print(exhibit)
        print("That`s all..")
        print("__________________________________")

    def ask_about_tour(self, museums_counts):
        print("__________________________________")
        items = list(museums_counts.items())[:50]
        self.show_museums_list(items)
        print("It was top 50 museums")
        answer = read_many_from_list(question="Choose museums which you are interesting\n"
                                     "<ENTER> for select all, 0 for back",
                                     variants=[str(i) for i in range(1, len(items) + 1)],
                                     quit_key="0",
                                     error="Oops. Incorrect input. Try again.")
        if not answer:
            return items
        elif answer == ['0']:
            return []
        return [items[int(i) - 1] for i in answer]

    def show_buckets(self, museums_buckets, how_much_to_show=None):
        if how_much_to_show:
            museums_buckets = museums_buckets[:how_much_to_show]
        for num, (bucket, count) in enumerate(museums_buckets, 1):
            print("############################################################")
            print(f"Bucket {num} -> {count} exhibits")
            targets = ["name", "count", "address"]
            for museum in bucket:
                print("____________________")
                for tag in targets:
                    if tag in museum:
                        print(tag, ":", museum[tag])
