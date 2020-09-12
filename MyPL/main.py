from interpreter import Interpreter

with open("script", "r", encoding="utf-8") as file:
    Interpreter().run(file.read())