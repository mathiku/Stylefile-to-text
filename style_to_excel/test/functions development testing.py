import os
import xml.etree.ElementTree as ET
import re
import csv

class QMLFileIterator:
    def __init__(self, directory):
        self.directory = directory
        self.file_iterator = iter(os.listdir(directory))

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            file = next(self.file_iterator)
            if file.endswith('.qml'):
                return os.path.join(self.directory, file)

    def get_rasterrendderer_from_xml(self, file_path):
        with open(file_path, 'r') as file:
            xml_data = file.read()        
        # Replace escape characters
        regexp = re.compile(r'&lt;|&gt;|&amp;|&quot;|&apos;')  # regex to catch the characters '&lt;', '&gt;', '&amp;', '&quot;', '&apos;'
        replacement_map = {'&lt;': 'less than', '&gt;': 'greater than', '&amp;': 'and', '&quot;': 'quote', '&apos;': 'apostrophe'}  # map a character to the replacement value.
        fixed_xml = regexp.sub(lambda match: replacement_map[match.group(0)], xml_data)  # do the replacement
        # Parse the fixed XML data
        root = ET.fromstring(fixed_xml)
        categories = root.findall('./pipe/rasterrenderer')
        symbols = root.findall('./pipe/rasterrenderer/rastershader/colorrampshader/item')
        # for symbol in symbols:
        #     print(f"Symbols attrib.: {symbol.attrib}")
        #     print(f"Symbols attrib. label: {symbol.attrib['label']}")
        #     print(f"Symbols text.: {symbol.text}")
        #     print(f"symbol get name: {symbol.get('name')}")
        #setup the lists
        rasterr_type = [category.get('type') for category in categories]
        cMax = [category.get('classificationMax') for category in categories]
        cMin = [category.get('classificationMin') for category in categories]
        label = [symbol.attrib['label'] for symbol in symbols]
        color = [symbol.attrib['color'] for symbol in symbols]
        value = [symbol.attrib['value'] for symbol in symbols]
        #logthelists
        # print(f"rasterr_type: {rasterr_type}")
        # print(f"cMax: {cMax}")
        # print(f"cMin: {cMin}")
        # print(f"label: {label}")
        # print(f"color: {color}")
        # print(f"value: {value}")
        #print(f"Outline_width: {outline_width}")
        #lists to dicts
        dict_to_print = {'Rasterrenderer type': rasterr_type, 
                    'cMax': cMax, 
                    'cMin': cMin, 
                    'label': label,
                    'color': color,
                    'value': value
                    #'outline_width': outline_width[i],
                    }
        print(f"Dictionary for categories: {dict_to_print}")
        self.dict_forcsv = dict_to_print
        #self.write_to_file(dict_to_print)

    def write_to_file(self,dict_to_csv):
        # Get the maximum length of the lists in the dictionary
        max_len = max(len(lst) for lst in dict_to_csv.values())

        # Write the dictionary to a CSV file
        with open(r"C:\Users\DKMK01256\Downloads\stylefiletest\test output.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(dict_to_csv.keys())
            for i in range(max_len):
                writer.writerow([dict_to_csv[key][i] if i < len(dict_to_csv[key]) else '' for key in dict_to_csv])

    def determine_style_type(self, file_path):
        #Styletype is found by XML-lookups
        tree = ET.parse(file_path)
        root = tree.getroot()
        try:
            rasterrenderer = root.find('pipe')
        except:
            pass
        try:
            renderer_v2 = root.find('renderer-v2')
        except:
            pass
        if renderer_v2 is not None:
            first_child = list(renderer_v2)[0]
        elif rasterrenderer is not None:
            first_child = list(rasterrenderer)[0]
        else:
            print(f"Sorry. This type of stylefile will only be supported in a future release.")
            print(f"\n--------------------------------------------------\n")
            return
        if first_child.tag == 'ranges':
            print(f"This is vector with ranges")
            return
        if first_child.tag == 'categories':
            print(f"This is vector with categories")
            return
        if first_child.tag == 'rasterrenderer':
            print(f"This is raster with categories")
            self.get_rasterrendderer_from_xml(file)
            return
        else:
            print(f"Sorry - you tried parsing {first_child.tag}. This version only supports categories and graduated/ranges.\n The update is in the making. \n If you wanna contribute please reach out.")
            print(f"\n--------------------------------------------------\n")

iterator = QMLFileIterator(r'C:\Users\DKMK01256\Downloads\stylefiletest')
for file in iterator:
    print(f"\n--------------------------------------------------\n")
    print(file)
    iterator.determine_style_type(file)