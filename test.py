import re

switch_settings = {}
switch_settings['Switch Group'] = {'1': {'Order': None, 'Flood': 'Disabled', 'STP': 'Disabled', 'Management': None, 'Mode': 'Normal', 'Interfaces': None, 'Rules': None}, '2': {'Order': None, 'Flood': 'Disabled', 'STP': 'Disabled', 'Management': None, 'Mode': 'Normal', 'Interfaces': None, 'Rules': None}, '10': {'Order': None, 'Flood': 'Disabled', 'STP': 'Disabled', 'Management': None, 'Mode': 'Normal', 'Interfaces': None, 'Rules': None}, '1546': {'Order': None, 'Flood': 'Disabled', 'STP': 'Disabled', 'Management': None, 'Mode': 'Normal', 'Interfaces': None, 'Rules': None}, '575': {'Order': None, 'Flood': 'Disabled', 'STP': 'Disabled', 'Management': None, 'Mode': 'Normal', 'Interfaces': None, 'Rules': None}}
sw_settings_text = {'1': [' switch group 1 add 1 rf5.0 \r\n', ' switch group 1 igmp-snooping on\r\n', ' switch group 1 igmp-snooping router-port on\r\n', "      # group 1 attached to 'svi1'\r\n", ' switch group 1 start\r\n', ' \r\n'], '2': [' switch group 2 add 2 eth0 rf5.0 \r\n', "      # group 2 attached to 'svi2'\r\n", ' switch group 2 start\r\n', ' \r\n'], '10': [' switch group 10 add 3 vlan101 vlan35 \r\n', ' switch group 10 start\r\n', ' \r\n'], '1546': [' switch group 1546 add 4 eth1 rf5.0 \r\n', ' switch group 1546 vlan 46\r\n', ' switch group 1546 start\r\n', ' \r\n'], '575': [' switch group 575 add 5 eth1:0 rf5.0:75 \r\n', ' switch group 575 rule 10 permit match LST2\r\n', ' switch group 575 deny\r\n', ' switch group 575 start\r\n', ' \r\n', ' switch start\r\n', '   \r\n', '#Switch Virtual Interface config\r\n', ' svi 1 group 1\r\n', ' svi 2 group 2\r\n']}
rule_list = {'LST2': 'not vlan\n'}
pattern_set_sw_order = re.compile(r'switch group \d+ add (\d+)')
pattern_set_sw_ifc = re.compile(r'switch group \d+ add \d+ (.+)')
pattern_set_sw_flood = re.compile(r'flood-unicast on')
pattern_set_sw_stp = re.compile(r'stp on')
pattern_set_sw_mode_trunk = re.compile(r'trunk on')
pattern_set_sw_mode_intrunk = re.compile(r'in-trunk (\d+)')
pattern_set_sw_mode_upstream = re.compile(r'upstream')
pattern_set_sw_mode_downstream = re.compile(r'downstream')
pattern_set_sw_rule = re.compile(r'switch group \d+ rule \d+\s+(permit|deny) match (\w+)')
pattern_set_sw_rule_list = re.compile(r'switch list (\w+) match add ([\w\d\-,\s\S]+)')
pattern_set_sw_rule_default = re.compile(r'switch group \d+ (deny|permit)')
pattern_set_sw_rule_vlan = re.compile(r'switch group \d+ (vlan [\d\-,]+)')
pattern_set_sw_mngt = re.compile(r'svi (\d+) group (\d+)')

for key in switch_settings['Switch Group']:
    group = switch_settings['Switch Group'][key]
    check_rule = False
    for line in sw_settings_text[key]:
        if pattern_set_sw_order.search(line):
            group['Order'] = pattern_set_sw_order.search(line).group(1)

        if pattern_set_sw_ifc.search(line):
            group['Interfaces'] = pattern_set_sw_ifc.search(line).group(1).split(' ')
            # Drop '\r'
            group['Interfaces'].pop()
            group['Interfaces'] = ', '.join(group['Interfaces'])

        if pattern_set_sw_flood.search(line):
            group['Flood'] = 'Enabled'

        if pattern_set_sw_stp.search(line):
            group['STP'] = 'Enabled'

        if pattern_set_sw_mode_trunk.search(line):
            group['Mode'] = 'Trunk'
        elif pattern_set_sw_mode_intrunk.search(line):
            group['Mode'] = f'In-Trunk {pattern_set_sw_mode_intrunk.search(line).group(1)}'
        elif pattern_set_sw_mode_upstream.search(line):
            group['Mode'] = 'Upstream'
        elif pattern_set_sw_mode_downstream.search(line):
            group['Mode'] = 'Downstream'

        if pattern_set_sw_rule_vlan.search(line):
            group['Rules'] = f'permit: {pattern_set_sw_rule_vlan.search(line).group(1)}; deny: any any'

        if pattern_set_sw_rule.search(line):
            rule_action = pattern_set_sw_rule.search(line).group(1)
            rule = pattern_set_sw_rule.search(line).group(2)
            check_rule = True

        if pattern_set_sw_rule_default.search(line):
            rule_default = pattern_set_sw_rule_default.search(line).group(1)

    if check_rule:
        print(rule_action)
        print(rule)
        print(rule_default)