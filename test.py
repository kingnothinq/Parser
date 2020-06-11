import re
from copy import deepcopy
import logging


slices = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 47]
links = []
for index, slice in enumerate(slices):
    try:
        link_start = slices[index]
        link_end = slices[index + 55]
    except:
        link_end = slices[index + 55]
    finally:
        links.append(slices[link_start:link_end])

print(links)
"""
# Create a custom logger
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('parser.log')
console_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.DEBUG)

# Create formatter and add it to handlers
form = '%(asctime)s - %(levelname)s - %(pathname)s - %(message)s'
formatter = logging.Formatter(fmt=form, datefmt='%d-%b-%y %H:%M:%S')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
"""
links_text = """ ------- ---------------------------- ------------ -----  ------- ----- -------
   Id         Name                        Node     Level  Bitrate Retry Options
 ------- ---------------------------- ------------ rx/tx   rx/tx  rx/tx -------
   00074 Bolnica4                     000435227565 29/19   52/104 15/0  /S/F/
	 load 12/16, pps 9/3, cost 51
	  pwr *23/-23, snr 37/39, dist 2
	  H11v1.90.36, IP=10.111.117.226, up 02:24:24
   	00003 PRF_AR_3_2                   0004350357B3 join
	 load 41/9345, pps 39/913, cost 1	  
   00074 VCamera_Barishnikova         00043522B125 22/15   78/104  4/0  /S/
	 load 7/25, pps 6/10, cost 51
	  pwr 23/23, snr 34/37, dist 2
	  H11v1.90.37, IP=10.111.117.154, up 02:18:36
   01620 OSB_055-2                    00043520C9A4 20/16   52/104  0/0  /S/
	 load 202/223, pps 25/19, cost 51
	  pwr 23/23, snr 28/36, dist 3
	  H07v1.90.37, IP=10.111.17.234, up 02:24:20
   04146 Video_Krasina_19             000435247D02 20/21  104/104  0/0  /S/
	 load 10332/278, pps 470/29, cost 51
	  pwr 23/23, snr 39/41, dist 3
	  H11v1.90.37, IP=10.10.217.230, up 02:23:15
   04148 Torfobriketnaya_4            000435247D04 24/16   13/78  28/10 /S/
	 load 1321/50, pps 64/22, cost 51
	  pwr 23/23, snr 26/29, dist 2
	  H11v1.90.37, IP=10.10.217.242, up 02:24:24
   04149 Video_Priozer_Detsad         000435247D05 27/19   26/78  25/0  /S/
	 load 3043/133, pps 155/26, cost 51
	  pwr 23/23, snr 30/31, dist 6
	  H11v1.90.37, IP=10.111.117.138, up 02:24:24
   04154 RTR_Likino_1A                000435247D0A 20/16   52/78   7/1  /S/
	 load 4665/166, pps 215/38, cost 51
	  pwr 23/23, snr 27/30, dist 10
	  H11v1.90.37, IP=10.111.117.58, up 02:24:24
   04172 SVN_Vereja_School19          000435247D1C 17/19   78/78   6/0  /S/
	 load 5279/192, pps 256/26, cost 51
	  pwr 23/23, snr 30/31, dist 9
	  H11v1.90.37, IP=10.10.217.178, up 02:24:24
   51840 TransRemKom                  00043520CA47 18/19   78/104  1/0  /S/
	 load 3/2, pps 3/0, cost 51
	  pwr 23/23, snr 31/38, dist 7
	  H07v1.90.37, IP=10.111.17.250, up 02:24:20
   59041 RTR_Gubino                   000435226D41 12/12   13/26   4/0  /S/
	 load 3/2, pps 3/0, cost 51
	  pwr 23/23, snr 14/14, dist 17
	  H11v1.90.37, IP=10.111.17.94, up 02:24:24
   61127 Video_Snopok_Shkola          000435227567 16/12   52/78   2/1  /S/
	 load 5815/202, pps 282/29, cost 51
	  pwr 23/23, snr 24/24, dist 12
	  H11v1.90.37, IP=10.111.117.110, up 02:24:23
?   61598 Video_Snopok_Detsad          00043522773E 18/20   26/39   6/4  /S/
	 load 2840/100, pps 142/23, cost 51
	  pwr 23/23, snr 23/24, dist 12
	  H11v1.90.37, IP=10.111.117.114, up 02:24:24

 ------- ---------------------------- ------------ -----  ------- ----- -------
 12 active neighbors
 Total load: 33522/1389 (rx/tx), 34911 (sum) Kbps
 Total nodes in area: 13
"""
links_text_list = list(map(lambda x: x + '\n', links_text.split('\n')))

print(links_text_list)

link_status = {'Name': None, 'Level Rx': None, 'Level Tx': None, 'Bitrate Rx': None, 'Bitrate Tx': None,
                   'Load Rx': None, 'Load Tx': None, 'PPS Rx': None, 'PPS Tx': None, 'Cost': None, 'Retry Rx': None,
                   'Retry Tx': None, 'Power Rx': None, 'Power Tx': None, 'RSSI Rx': None, 'RSSI Tx': None,
                   'SNR Rx': None, 'SNR Tx': None, 'Distance': None, 'Firmware': None, 'Uptime': None}
radio_status = {'Links': None}
pattern_mac = re.compile(r'(00[\dA-F]{10})')
pattern_name = re.compile(r'[\.\d]+\s+([\w\d\S]+)\s+00[\w\d]+')
pattern_level = re.compile(r'00[\w\d]+\s+(\d+)/(\d+)')
pattern_bitrate = re.compile(r'00[\w\d]+\s+\d+/\d+\s+(\d+)/(\d+)')
pattern_retry = re.compile(r'00[\w\d]+\s+\d+/\d+\s+\d+/\d+\s+(\d+)/(\d+)')
pattern_flags = re.compile(r'/S')
pattern_load = re.compile(r'load (\d+)/(\d+)')
pattern_pps = re.compile(r'pps (\d+)/(\d+)')
pattern_cost = re.compile(r'cost ([\-\d+\.]+)')
pattern_pwr = re.compile(r'pwr ([\*\-\d+\.]+)/([\*\-\d+\.]+)')
pattern_rssi = re.compile(r'rssi ([\*\-\d+\.]+)/([\*\-\d+\.]+)')
pattern_snr = re.compile(r'snr (\d+)/(\d+)')
pattern_distance = re.compile(r'dist ([\.\d+]+)')
pattern_firmware = re.compile(r'(H\d{2}v[v\d.]+)')
pattern_uptime = re.compile(r'up ([\d\w :]*)')

slice = 0
links = []
for index, line in enumerate(links_text_list):
    if pattern_mac.search(line):
        links.append(links_text_list[slice:index])
        slice = index
links.pop(0)


radio_status['Links'] = {mac: deepcopy(link_status) for mac in [pattern_mac.search(link[0]).group(1) for link in links]}
firmware = 'MINT'

for mac in radio_status['Links']:
    for index, link in enumerate(links):
        if mac == pattern_mac.search(link[0]).group(1):
            link = ''.join(link)

            radio_status['Links'][mac]['Name'] = pattern_name.search(link).group(1)

            if pattern_level.search(link) is not None:
                radio_status['Links'][mac]['Level Rx'] = int(pattern_level.search(link).group(1))
                radio_status['Links'][mac]['Level Tx'] = int(pattern_level.search(link).group(2))
            else:
                logger.debug(f'Link {mac}: Level was not parsed')

            if pattern_bitrate.search(link) is not None:
                radio_status['Links'][mac]['Bitrate Rx'] = int(pattern_bitrate.search(link).group(1))
                radio_status['Links'][mac]['Bitrate Tx'] = int(pattern_bitrate.search(link).group(2))
            else:
                logger.debug(f'Link {mac}: Bitrate was not parsed')

            if pattern_retry.search(link) is not None:
                radio_status['Links'][mac]['Retry Rx'] = int(pattern_retry.search(link).group(1))
                radio_status['Links'][mac]['Retry Tx'] = int(pattern_retry.search(link).group(2))
            else:
                logger.debug(f'Link {mac}: Retry was not parsed')

            if pattern_load.search(link) is not None:
                radio_status['Links'][mac]['Load Rx'] = int(pattern_load.search(link).group(1))
                radio_status['Links'][mac]['Load Tx'] = int(pattern_load.search(link).group(2))
            else:
                logger.debug(f'Link {mac}: Load was not parsed')

            if pattern_pps.search(link) is not None:
                radio_status['Links'][mac]['PPS Rx'] = int(pattern_pps.search(link).group(1))
                radio_status['Links'][mac]['PPS Tx'] = int(pattern_pps.search(link).group(2))
            else:
                logger.debug(f'Link {mac}: PPS was not parsed')

            if pattern_cost.search(link) is not None:
                radio_status['Links'][mac]['Cost'] = int(pattern_cost.search(link).group(1))
            else:
                logger.debug(f'Link {mac}: Cost was not parsed')

            if pattern_pwr.search(link) is not None:
                radio_status['Links'][mac]['Power Rx'] = pattern_pwr.search(link).group(1)
                radio_status['Links'][mac]['Power Tx'] = pattern_pwr.search(link).group(2)
            else:
                logger.debug(f'Link {mac}: Power was not parsed')

            if pattern_snr.search(link) is not None:
                radio_status['Links'][mac]['SNR Rx'] = int(pattern_snr.search(link).group(1))
                radio_status['Links'][mac]['SNR Tx'] = int(pattern_snr.search(link).group(2))
            else:
                logger.debug(f'Link {mac}: SNR was not parsed')

            if pattern_distance.search(link) is not None:
                radio_status['Links'][mac]['Distance'] = int(pattern_distance.search(link).group(1))
            else:
                logger.debug(f'Link {mac}: Distance was not parsed')

            if pattern_firmware.search(link) is not None:
                radio_status['Links'][mac]['Firmware'] = pattern_firmware.search(link).group(1)
            else:
                logger.debug(f'Link {mac}: Firmware was not parsed')

            if pattern_uptime.search(link) is not None:
                radio_status['Links'][mac]['Uptime'] = pattern_uptime.search(link).group(1)
            else:
                logger.debug(f'Link {mac}: Uptime was not parsed')

            if 'TDMA' in firmware and pattern_rssi.search(link) is not None:
                radio_status['Links'][mac]['RSSI Rx'] = pattern_rssi.search(link).group(1)
                radio_status['Links'][mac]['RSSI Tx'] = pattern_rssi.search(link).group(2)
            if 'TDMA' in firmware and pattern_rssi.search(link) is None:
                logger.debug(f'Link {mac}: RSSI was not parsed')

print(radio_status['Links']['00043522773E'])


"""
pattern_flag = [re.compile(r'/S'), re.compile(r'/M'), re.compile(r'/TM'),
                re.compile(r'/L'), re.compile(r'/P'), re.compile(r'/F'),
                re.compile(r'(\?)?\s+[\.\d]+\s+([\w\d\S]+)\s+(00[\w\d]+)\s+[^join]')]

pattern_flag_s = re.compile(r'/(S)')
pattern_flag_m = re.compile(r'/(M)')
pattern_flag_tm = re.compile(r'/(TM)')
pattern_flag_l = re.compile(r'/(L)')
pattern_flag_p = re.compile(r'/(P)')
pattern_flag_f = re.compile(r'/(F)')
pattern_flag_qm = re.compile(r'(\?)?\s+[\.\d]+\s+[\w\d\S]+\s+00[\w\d]+\s+[^join]')

print(pattern_flag_s.findall(links_text))
print(pattern_flag_m.findall(links_text))
print(pattern_flag_tm.findall(links_text))
print(pattern_flag_l.findall(links_text))
print(pattern_flag_p.findall(links_text))
print(pattern_flag_f.findall(links_text))
print(pattern_flag_qm.findall(links_text))
"""

