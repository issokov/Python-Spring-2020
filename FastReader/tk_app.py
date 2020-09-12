from library import Reader
from tkinter import filedialog
from tkinter import *


class TkApp:
    tk = Tk()
    library = Reader()
    word_var = StringVar(tk)
    wpm = 200
    reading, delay = False, True

    def __init__(self):
        self._construct_interface()
        self._bind_events()
        self._load_lib()
        self.tk.mainloop()

    def _construct_interface(self):
        self.tk.geometry("600x400")
        self.tk.configure(bg="white")

        self.list = Listbox(selectmode=SINGLE, justify="center")
        self.open_butt = Button(text="New", font="arial 14", bg="white")
        self.delete_butt = Button(text="Delete", font="arial 14", bg="white")
        self.wpm_label = Label(text="WPM: %i" % self.wpm, fg="red", bg="white", font="arial 10")
        self.word_label = Label(textvariable=self.word_var, font="arial 20", bg="white")
        self.back_butt = Button(text="Back", font="arial 14", bg="white")
        self.play_stop_butt = Button(text="Play", font="arial 14", bg="white")
        self.next_butt = Button(self.tk, text="Next", font="arial 14", bg="white")

        self.list.grid(row=0, column=0, rowspan=3, columnspan=2, sticky="nsew")
        self.wpm_label.grid(row=0, column=2, columnspan=3, sticky="nsew")
        self.open_butt.grid(row=3, column=0, sticky="nsew")
        self.delete_butt.grid(row=3, column=1, sticky='nsew')
        self.word_label.grid(row=1, column=2, columnspan=3, rowspan=2, sticky='nsew')
        self.back_butt.grid(row=3, column=2, sticky='nsew')
        self.play_stop_butt.grid(row=3, column=3, sticky='nsew')
        self.next_butt.grid(row=3, column=4, sticky='nsew')

        self.tk.rowconfigure(0)
        self.tk.rowconfigure(1, weight=5)
        for i in range(2, 5):
            self.tk.columnconfigure(i, weight=1)
        self.word_var.set("Пожалуйста, откройте книгу")

    def _bind_events(self):
        self.open_butt["command"] = self._add_book_from_system
        self.delete_butt["command"] = self._delete_butt
        self.list.bind("<<ListboxSelect>>", self._choose_book)
        self.back_butt["command"] = self._back
        self.next_butt["command"] = self._next
        self.play_stop_butt["command"] = self._start_stop
        self.tk.bind('<Left>', self._back)
        self.tk.bind('<Right>', self._next)
        self.tk.bind('<space>', self._start_stop)
        self.tk.bind('<Up>', self._inc_wpm)
        self.tk.bind('<Down>', self._dec_wpm)
        self.tk.protocol("WM_DELETE_WINDOW", self._quit)

    def _quit(self, event=None):
        self.library.synchronize()
        self.tk.destroy()

    def _add_book_from_system(self):
        path = filedialog.askopenfile()
        if path:
            name = self.library.add_to_library(path.name)
            self.list.insert(0, name)

    def _delete_butt(self):
        index = self.list.curselection()
        if index:
            name = self.list.get(index)
            self.list.delete(index)
            self.library.pop_from_library(name)

    def _load_lib(self):
        names = self.library.get_library()
        for name in names:
            self.list.insert(0, name)

    def update_word_label(self, code, word):
        if code == self.library.book.OK or code == self.library.book.PAUSE:
            self.word_var.set(word)
            self.delay = True if code == self.library.book.PAUSE else False
        elif code == self.library.book.END:
            self._start_stop()
            self.word_var.set("Конец!")

    def _choose_book(self, event=None):
        self.word_label.grid_configure(column=3, columnspan=2)
        self.word_label.configure(anchor="w")
        name = self.list.get(self.list.curselection())
        if self.library.open_book(name) and not self.reading:
            self.reading = False
            self.update_word_label(*self.library.book.get_word())

    def _back(self, event=None):
        self.reading = False
        if self.library.book:
            self.update_word_label(*self.library.book.get_word(-1))

    def _next(self, event=None):
        if self.library.book:
            self.update_word_label(*self.library.book.get_word(1))
            if self.reading:
                pause = int(60000/self.wpm)
                if self.delay:
                    self.delay = False
                    pause = int(3*60000/self.wpm)
                self.tk.after(ms=pause, func=self._next)

    def _start_stop(self, event=None):
        self.library.synchronize()
        if not self.reading:
            if self.library.book and self.library.book.get_word()[0] != self.library.book.END:
                self.list.grid_remove()
                self.delete_butt.grid_remove()
                self.open_butt.grid_remove()
                self.reading = self.delay = True
                self.timer_id = self.tk.after(ms=1500, func=self._next)
                self.play_stop_butt["text"] = "Stop"
        else:
            self.list.grid()
            self.delete_butt.grid()
            self.open_butt.grid()
            self.reading = False
            self.library.synchronize()
            self.play_stop_butt["text"] = "Play"

    def _inc_wpm(self, event=None):
        self.wpm += 10
        self.wpm_label["text"] = "WPM: %i" % self.wpm

    def _dec_wpm(self, event=None):
        self.wpm = max(10, self.wpm - 10)
        self.wpm_label["text"] = "WPM: %i" % self.wpm

TkApp()
