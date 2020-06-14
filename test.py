import re

text = ["Leidos-Ramp5          ", "JAF1-Leidos             ", "Geo Chem- MOF               "]

pattern_mac = re.compile(r'(00[\dA-F]{10})')
pattern_prf = re.compile(r'(join|prf)')
pattern_name = re.compile(r'[\.\d]+\s+([\w\d\S \-]+)\s+00[\dA-F]{10}')
pattern_spaces = re.compile(r"(\s{2,})")
pattern_level = re.compile(r'00[\w\d]+\s+(\d+)/(\d+)')

for link in text:
    link_name = pattern_name.search(link).group(1)
    spaces = pattern_spaces.search(link_name)
    radio_status['Links'][mac]['Name'] = link_name.replace(spaces, '')
    print(radio_status['Links'][mac]['Name'])

"""Check
                    link_name = pattern_name.search(link).group(1)
                    spaces = pattern_spaces.search(link_name)
                    radio_status['Links'][mac]['Name'] = link_name.replace(spaces, '')
                    print(radio_status['Links'][mac]['Name'])

"""