#!/usr/bin/python
# -*- coding: utf-8 -*-

def test(device):
     """Check radio parameters and return conclusion"""

     if device.radio_status['Link status'] == 'DOWN':
          if device.settings['Interface Status']['Radio'] == 'down':
               return '* The link is not established. Please enable the radio interface (CLI: \"ifc radio up\").\n'
          else:
               return '* The link is not established. Please check the alignment, remote side, LOS, spectrum, etc.\n'
     elif device.radio_status['Link status'] == 'ERROR':
          #function_to_check_errors(args)
          return '* The link is not established. Please find out the cause of the error.\n'
     elif device.radio_status['Link status'] == 'STARTING':
          return '* The link is establishing but this status should not be displayed. \
           Please find out the cause of this status.\n'
     elif device.radio_status['Link status'] == 'STOPPED':
          return '* The link is not established. Please find out the cause of the error.\n'
     elif device.radio_status['Link status'] == 'PHY':
          return '* The link is not established. Please find out the cause of the error.\n'
     else:
          pass