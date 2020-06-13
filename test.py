import re

pattern_s_afbitr = re.compile(r'-(auto|fixed)bitr')
pattern_s_afbitr_offset = re.compile(r'-(auto|fixed)bitr (([\-+])?([\d]+))')
profiles = [' mint rf5.0 prof 1 -band 40 -freq 5710 -bitr 300000 -sid BC03CE01 \\\r\n', '\t      -nodeid 237.240 -type slave \\\r\n', '\t      -autobitr -mimo \\\r\n', '\t      -key "sninfinet"\r\n']
profile = {}

for line in profiles:
    if pattern_s_afbitr.search(line):

        if pattern_s_afbitr.search(line).group(1) == 'auto' \
                and pattern_s_afbitr_offset.search(line):
            profile['Auto bitrate'] = f'Enabled. Modification is ' \
                                      f'{pattern_s_afbitr_offset.search(line).group(2)}'
        elif pattern_s_afbitr.search(line).group(1) == 'auto':
            profile['Auto bitrate'] = 'Enabled'
        elif pattern_s_afbitr.search(line).group(1) == 'fixed':
            profile['Auto bitrate'] = f'Disabled. Fixed bitrate is {profile["Max bitrate"]}'
