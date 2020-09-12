import json
from os.path import basename, splitext


class Book:
    bookmark = 0
    book_buffer = None

    OK, END, PAUSE = range(3)
    pause_element = ['.', '?', '!']

    def __init__(self, name, book_path, bookmark):
        with open(book_path, encoding="utf8") as book_file:
            self.name = name
            self.book_buffer = book_file.read().split()
            self.bookmark = bookmark

    def get_word(self, shift=0):
        if len(self.book_buffer) > self.bookmark + shift:
            self.bookmark += shift
            if self.bookmark < 0:
                self.bookmark = 0
            word = self.book_buffer[self.bookmark]
            return self.PAUSE if word and word[-1] in self.pause_element else self.OK, word
        else:
            self.bookmark = len(self.book_buffer)
            return self.END, None


class Reader:
    library_file = "library.txt"
    library = dict()
    book = None

    def __init__(self):
        try:
            with open(self.library_file, encoding="utf8") as lib:
                self.library = json.loads(lib.read())
        except FileNotFoundError:
            pass

    def add_to_library(self, book_path: str):
        file_name = splitext(basename(book_path))[0]
        while file_name in self.library:
            file_name += "_copy"
        self.library[file_name] = {
            "name": file_name,
            "path": book_path,
            "bookmark": 0
        }
        self.save_library()
        return file_name

    def get_library(self):
        return list(self.library.keys())

    def pop_from_library(self, book_name):
        if self.book and self.book.name == book_name:
            self.book = None
        self.library.pop(book_name)
        self.save_library()

    def save_library(self):
        with open(self.library_file, "w", encoding="utf8") as lib:
            lib.write(json.dumps(self.library, indent=4))

    def open_book(self, book_name):
        if self.book:
            self.library[self.book.name]["bookmark"] = self.book.bookmark
        try:
            book_info = self.library[book_name]
            self.book = Book(book_info["name"], book_info["path"], book_info["bookmark"])
            return True
        except FileNotFoundError:
            return False

    def synchronize(self):
        if self.book:
            self.library[self.book.name]["bookmark"] = self.book.bookmark
        self.save_library()

r = Reader()
