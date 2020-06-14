import re

links_text = ['   00070 Master 2 prf                 00043504BAE9 join\r\n', '\t load 4/0, pps 6/0, cost 1\r\n', '   09455 KRIBI-SLAVE-PER_CENTR        00043514A732 15/14  104/104  1/0  /S/\r\n', '\t  load 7/24, pps 7/17, cost 51\r\n', '\t   pwr 23/23, snr 35/34, dist 13\r\n', '\t   H08v1.90.36, IP=10.10.96.237, up 00:10:25\t \r\n', ' ------- ---------------------------- ------------ -----  ------- ----- -------\r\n', ' 0 active neighbors, 1 join\r\n', ' Point-To-Point mode\r\n', ' Total nodes in area: 8\r\n', ' Links fault 2, Routes fault 0\r\n', '\r\n', '\r\n', '==============================================================================\r\n', 'Interface prf0  (parent eth0)\r\n', 'Node  00043504BAE9  "Master 2 prf", Id 00070, Nid 0, (Master)\r\n', '\r\n', ' ------- ---------------------------- ------------ -------\r\n', '   Id         Name                        Node     Options\r\n', ' ------- ---------------------------- ------------ -------\r\n', '   00050 Master 1 prf                 00043504BAEB prf\r\n', '\t load 5/0, pps 7/0, cost 23\r\n', '\t  H11v1.90.38, up 00:09:31\r\n', '   09993 2215-2                       00043524BAE9 join\r\n', '\t load 3/3, pps 4/4, cost 1\r\n']
pattern_prf = re.compile(r'(join|prf)')
pattern_mac = re.compile(r'(00[\dA-F]{10})')


slices = []
for index, line in enumerate(links_text):
    if pattern_mac.search(line):
        slices.append(index)
slices.append(len(links_text))


links = []
for index, slice in enumerate(slices):
    try:
        link_start = slices[index]
        link_end = slices[index + 1]
    except IndexError:
        link_end = slices[index]
    finally:
        links.append(links_text[link_start:link_end])
links.pop()

links = [['   00070 Master 2 prf                 00043504BAE9 join\r\n', '\t load 4/0, pps 6/0, cost 1\r\n'], ['   09455 KRIBI-SLAVE-PER_CENTR        00043514A732 15/14  104/104  1/0  /S/\r\n', '\t  load 7/24, pps 7/17, cost 51\r\n', '\t   pwr 23/23, snr 35/34, dist 13\r\n', '\t   H08v1.90.36, IP=10.10.96.237, up 00:10:25\t \r\n', ' ------- ---------------------------- ------------ -----  ------- ----- -------\r\n', ' 0 active neighbors, 1 join\r\n', ' Point-To-Point mode\r\n', ' Total nodes in area: 8\r\n', ' Links fault 2, Routes fault 0\r\n', '\r\n', '\r\n', '==============================================================================\r\n', 'Interface prf0  (parent eth0)\r\n'], ['Node  00043504BAE9  "Master 2 prf", Id 00070, Nid 0, (Master)\r\n', '\r\n', ' ------- ---------------------------- ------------ -------\r\n', '   Id         Name                        Node     Options\r\n', ' ------- ---------------------------- ------------ -------\r\n'], ['   00050 Master 1 prf                 00043504BAEB prf\r\n', '\t load 5/0, pps 7/0, cost 23\r\n', '\t  H11v1.90.38, up 00:09:31\r\n'], ['   09993 2215-2                       00043524BAE9 join\r\n', '\t load 3/3, pps 4/4, cost 1\r\n']]

temp = []
for index, link in enumerate(links):
    if not pattern_prf.search(link[0]):
        temp.append(link)
links = temp
