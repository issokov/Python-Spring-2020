import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
from urllib.request import urlopen
from collections import Counter
def get_data(path, data_file_name):    
    try:
        file = open(data_file_name, encoding="utf-8", mode="r")
        return file.read()
    except:
        print("Loaded data not found.\nStart downloading")
        try:
            response = urlopen(path)
        except:
            print("Abort! No connection...")
            return None
        print("Server response: \nCode: {}\nReason: {}"\
              .format(response.code, response.reason))
        if response.code > 199 and response.code < 300:
            data = response.read().decode("utf-8")
            file = open(data_file_name, encoding="utf-8", mode ="w")
            file.write(data)
            print("Data was saved in '{}'".format(data_file_name))
            return data

def get_stats(string_numbers):
	counter = Counter(map(lambda x: x[0] if x else None, string_numbers))
	stats = [counter[str(i)] for i in range(1, 10)]
	return stats

def show_comparison(your_stats : list):
	summary = sum(your_stats)
	benford_stats = list(map(lambda x: x * summary / 100,
                    [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]))
	x = np.arange(1, 10)
	shift = 0.35
	fig, ax = plt.subplots()
	rects1 = ax.bar(x - shift/2, your_stats, shift, label='Распределение в данных')
	rects2 = ax.bar(x + shift/2, benford_stats, shift, label='Истинное распределение Бенфорда')
	ax.set_ylabel('Количество чисел собственно в данных')
	ax.set_title('Проверка закона Бенфорда\n для числа несовершеннолетних лиц, совершивших преступления')
	ax.set_xticks(x)
	ax.legend()
	plt.show()

