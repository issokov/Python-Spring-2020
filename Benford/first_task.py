import benford
import xml.etree.ElementTree as ET
from collections import defaultdict

data_file_name = "data_1.txt"
path = "http://crimestat.ru/loadXml/21034321"
    
data = benford.get_data(path, data_file_name)
root = ET.fromstring(data)
stats = benford.get_stats(map(lambda x: x.text, root.iter('value')))
benford.show_comparison(stats)
