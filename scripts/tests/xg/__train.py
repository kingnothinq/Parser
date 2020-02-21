#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def check_carrier(carrier):
    if float(search(r'\(([\d\.]+)%\)', carrier['Rx Acc FER']).group(1)) > 0:
        return 'Rx Acc FER > 0'
    check_stream(carrier['Stream 0'])


def check_stream(stream):
    def check_rssi(rssi):
        rssi = int(search(r'(\d+)', rssi).group(1))
        if rssi < 40:
            return 'RSSI < 40'
        elif rssi > 80:
            return 'RSSI > 40'

    def check_cinr(cinr):
        cinr = int(search(r'(\d+)', cinr).group(1))
        if cinr < 10:
            return 'CINR < 10'
        elif cinr < 20:
            return 'CINR < 20'

    def check_crosstalk(crosstalk):
        crosstalk = int(search(r'(\d+)', crosstalk).group(1))
        if crosstalk < 20:
            return 'Crosstalk < 20'

    def check_errors_ratio(errors_ratio):
        errors_ratio = float(search(r'([\d\.]+)', errors_ratio).group(1))
        if errors_ratio > 3:
            return 'Errors Ratio > 3'

    return check_rssi(stream['RSSI']), check_cinr(stream['CINR']), check_crosstalk(
        stream['Crosstalk']), check_errors_ratio(stream['Errors Ratio'])


def check_status():
    pass


status = {'Link status': 'UP', 'Measured Distance': '228 meters', 'Master': {'Role': 'Local',
                                                                             'Carrier 0': {'Frequency': '5700',
                                                                                           'DFS': 'ENABLED',
                                                                                           'Rx Acc FER': '0e0 (1%)',
                                                                                           'Stream 0': {
                                                                                               'Tx Power': '1.5 dBm',
                                                                                               'Tx Gain': '-32 dB',
                                                                                               'MCS': 'QAM1024 8/10 (10)',
                                                                                               'CINR': '33 dB',
                                                                                               'RSSI': '-47 dBm',
                                                                                               'Crosstalk': '-21 dB',
                                                                                               'Errors Ratio': '0.01%'},
                                                                                           'Stream 1': {
                                                                                               'Tx Power': '4.75 dBm',
                                                                                               'Tx Gain': '-28 dB',
                                                                                               'MCS': 'QAM256 30/32 (9)',
                                                                                               'CINR': '30 dB',
                                                                                               'RSSI': '-44 dBm',
                                                                                               'Crosstalk': '-29 dB',
                                                                                               'Errors Ratio': '0.01%'}},
                                                                             'Carrier 1': {'Frequency': '5620',
                                                                                           'DFS': 'ENABLED',
                                                                                           'Rx Acc FER': '0e0 (0%)',
                                                                                           'Stream 0': {
                                                                                               'Tx Power': '1.75 dBm',
                                                                                               'Tx Gain': '-32 dB',
                                                                                               'MCS': 'QAM256 30/32 (9)',
                                                                                               'CINR': '31 dB',
                                                                                               'RSSI': '-50 dBm',
                                                                                               'Crosstalk': '-26 dB',
                                                                                               'Errors Ratio': '0%'},
                                                                                           'Stream 1': {
                                                                                               'Tx Power': '7 dBm',
                                                                                               'Tx Gain': '-26.75 dB',
                                                                                               'MCS': 'QAM256 30/32 (9)',
                                                                                               'CINR': '32 dB',
                                                                                               'RSSI': '-48 dBm',
                                                                                               'Crosstalk': '-27 dB',
                                                                                               'Errors Ratio': '0.01%'}}},
          'Slave': {'Role': 'Remote', 'Carrier 0': {'Frequency': '5700', 'DFS': 'ENABLED', 'Rx Acc FER': '0e0 (0.01%)',
                                                    'Stream 0': {'Tx Power': '1 dBm', 'Tx Gain': '-33.25 dB',
                                                                 'MCS': 'QAM64 4/6 (5)', 'CINR': '32 dB',
                                                                 'RSSI': '-47 dBm', 'Crosstalk': '-22 dB',
                                                                 'Errors Ratio': '2.32%'},
                                                    'Stream 1': {'Tx Power': '3.5 dBm', 'Tx Gain': '-29.25 dB',
                                                                 'MCS': 'QAM16 3/4 (4)', 'CINR': '30 dB',
                                                                 'RSSI': '-44 dBm', 'Crosstalk': '-28 dB',
                                                                 'Errors Ratio': '2.32%'}},
                    'Carrier 1': {'Frequency': '5620', 'DFS': 'ENABLED', 'Rx Acc FER': '1.33e-3 (0.13%)',
                                  'Stream 0': {'Tx Power': '1 dBm', 'Tx Gain': '-32.25 dB', 'MCS': 'QAM16 3/4 (4)',
                                               'CINR': '31 dB', 'RSSI': '-45 dBm', 'Crosstalk': '-31 dB',
                                               'Errors Ratio': '2.31%'},
                                  'Stream 1': {'Tx Power': '1 dBm', 'Tx Gain': '-32.75 dB', 'MCS': 'QAM64 4/6 (5)',
                                               'CINR': '30 dB', 'RSSI': '-49 dBm', 'Crosstalk': '-23 dB',
                                               'Errors Ratio': '2.31%'}}}}
settings = {'Role': 'master', 'Bandwidth': '40', 'DL Frequency': {'Carrier 0': '5480', 'Carrier 1': '5560'},
            'UL Frequency': {'Carrier 0': '5480', 'Carrier 1': '5560'}, 'Short CP': 'Disabled', 'Max distance': '1',
            'Frame size': '5', 'UL/DL Ratio': '39/61 (auto)', 'Tx Power': '7', 'Control Block Boost': 'Disabled',
            'ATPC': 'Enabled', 'AMC Strategy': 'aggressive', 'Max MCS': '10', 'IDFS': 'Disabled',
            'Traffic prioritization': 'Disabled',
            'Interface Status': {'Ge0': None, 'Ge1': None, 'SFP': None, 'Radio': None, 'ge0': 'up', 'ge1': 'up',
                                 'sfp': 'up', 'radio': 'up'}}

subfamily = 'XG 1000'

master = status['Master']
slave = status['Slave']
result = []

print(master['Carrier 0']['Stream 0'])

if subfamily == 'XG 500':
    pass
else:
    for carrier in ['Carrier 0', 'Carrier 1']:
        print(check_carrier(master[carrier]))
