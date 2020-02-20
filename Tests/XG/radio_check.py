#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


def test(device):
     """Check radio parameters and return conclusion"""

     def check_stream(stream):
          pass

     def check_carrier(carrier):
          if float(search(r'\(([\d\.]+)%\)', carrier['Rx Acc FER']).group(1)) > 0:
               result.append('Blabla')

     def check_radio(*args):
          if subfamily == 'XG 500':
               check_carrier(master['Carrier 0'])
               check_carrier(slave['Carrier 0'])
          else:
               check_carrier(master['Carrier 0'])
               check_carrier(slave['Carrier 0'])
               check_carrier(master['Carrier 1'])
               check_carrier(slave['Carrier 1'])

     subfamily = device.subfamily
     status = device.radio_status
     settings = device.settings
     master = status['Master']
     slave = status['Slave']
     result = []

     print(master['Carrier 0'])

     if status['Link status'] == 'DOWN':
          if settings['Interface Status']['Radio'] == 'down':
               return '* The link is not established because the radio interface is turned off. \
                Please enable the radio interface (CLI: \"ifc radio up\").\n'
          else:
               return '* The link is not established. Please check the alignment, remote side, LOS, spectrum, etc.\n'
     elif status['Link status'] == 'ERROR':
          # function_to_check_errors(args)
          return '* The link is not established and stucked in the ERROR state. \
           Please find out the cause of the error.\n'
     elif status['Link status'] == 'STARTING':
          return '* The link is establishing but this status should not be displayed. \
           Please find out the cause of this status.\n'
     elif status['Link status'] == 'STOPPED':
          return '* The link is not established. Please find out the cause of the error.\n'
     elif status['Link status'] == 'PHY':
          return '* The link is not established. Please find out the cause of the error.\n'
     else:
          check_radio(master, slave, settings, subfamily)
          print(result)
