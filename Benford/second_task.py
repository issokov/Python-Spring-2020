import benford
import xml.etree.ElementTree as ET


data_file_name = "data_2.txt"
path = "https://data.gov.ru/opendata/7708234640-vpn2010-pub-05-02-52-v01/data-20130912T1248-structure-20130912T1248.xml?encoding=UTF-8"
data = benford.get_data(path, data_file_name)
root = ET.fromstring(data)
stats = benford.get_stats(map(lambda x: x.attrib['measure52']
            if 'measure52' in x.attrib else None, root.iter('cell')))
benford.show_comparison(stats)
