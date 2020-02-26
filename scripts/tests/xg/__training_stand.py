#!/usr/bin/python
# -*- coding: utf-8 -*-

radio_status = {'Link status':'UP', 'Measured Distance':'---', 'Master':{'Role'     :'Local',
                                                                         'Carrier 0':{'Frequency' :'5800',
                                                                                      'DFS'       :'BG_RSSI_V',
                                                                                      'Rx Acc FER':'1.04e-4 (0.01%)',
                                                                                      'Stream 0'  :{'Tx Power'    :'20 dBm',
                                                                                                    'Tx Gain'     :'-15.75 dB',
                                                                                                    'MCS'         :'QAM256 7/8 (8)',
                                                                                                    'CINR'        :'27 dB',
                                                                                                    'RSSI'        :'-66 dBm',
                                                                                                    'Crosstalk'   :'-25 dB',
                                                                                                    'Errors Ratio':'0.01%'},
                                                                                      'Stream 1'  :{'Tx Power'    :'20 dBm',
                                                                                                    'Tx Gain'     :'-17.75 dB',
                                                                                                    'MCS'         :'QAM256 6/8 (7)',
                                                                                                    'CINR'        :'25 dB',
                                                                                                    'RSSI'        :'-73 dBm',
                                                                                                    'Crosstalk'   :'-25 dB',
                                                                                                    'Errors Ratio':'0.02%'}},
                                                                         'Carrier 1':{'Frequency' :None,
                                                                                      'DFS'       :'BG_RSSI_V',
                                                                                      'Rx Acc FER':None,
                                                                                      'Stream 0'  :{'Tx Power'    :None,
                                                                                                    'Tx Gain'     :None,
                                                                                                    'MCS'         :None,
                                                                                                    'CINR'        :None,
                                                                                                    'RSSI'        :None,
                                                                                                    'Crosstalk'   :None,
                                                                                                    'Errors Ratio':None},
                                                                                      'Stream 1'  :{'Tx Power'    :None,
                                                                                                    'Tx Gain'     :None,
                                                                                                    'MCS'         :None,
                                                                                                    'CINR'        :None,
                                                                                                    'RSSI'        :None,
                                                                                                    'Crosstalk'   :None,
                                                                                                    'Errors Ratio':None}}},
                'Slave'      :{'Role'     :'Remote', 'Carrier 0':{'Frequency':'', 'DFS':'BG_RSSI_V', 'Rx Acc FER':'',
                                                                  'Stream 0' :{'Tx Power'    :'', 'Tx Gain':'',
                                                                               'MCS'         :'', 'CINR':'', 'RSSI':'',
                                                                               'Crosstalk'   :'', 'Errors Ratio':''},
                                                                  'Stream 1' :{'Tx Power'    :'', 'Tx Gain':'',
                                                                               'MCS'         :'', 'CINR':'', 'RSSI':'',
                                                                               'Crosstalk'   :'', 'Errors Ratio':''}},
                               'Carrier 1':{'Frequency':None, 'DFS':'BG_RSSI_V', 'Rx Acc FER':None,
                                            'Stream 0' :{'Tx Power':None, 'Tx Gain':None, 'MCS':None, 'CINR':None,
                                                         'RSSI'    :None, 'Crosstalk':None, 'Errors Ratio':None},
                                            'Stream 1' :{'Tx Power':None, 'Tx Gain':None, 'MCS':None, 'CINR':None,
                                                         'RSSI'    :None, 'Crosstalk':None, 'Errors Ratio':None}}}}


#print(radio_status['Slave'])


def no_empty(a):
    for key_1, value_1 in enumerate(a):
        a[key_1] = list(value_1)
        for key_2, value_2 in enumerate(a[key_1]):
            if value_2 == '':
                a[key_1][key_2] = None
        a[key_1] = tuple(a[key_1])


a = [('5800', '', ''), ('4000', '', '')]

no_empty(a)

print(a)