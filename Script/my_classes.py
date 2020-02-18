#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC


class RawDiagnosticCard(ABC):
    """A diagnostic card"""

    def __init__(self, model, subfamily, serial_number, firmware, uptime,
                 reboot_reason, dcard_raw_text_list, dcard_raw_text_string):
        self.model = model
        self.subfamily = subfamily
        self.serial_number = serial_number
        self.firmware = firmware
        self.uptime = uptime
        self.reboot_reason = reboot_reason
        self.dcard_raw_text_list = dcard_raw_text_list
        self.dcard_raw_text_string = dcard_raw_text_string


class R5000Card(RawDiagnosticCard):
    """An R5000 diagnostic card"""

    family = 'R5000'

    def __init__(self, model, subfamily, serial_number, firmware, uptime,
                 reboot_reason, dcard_raw_text_list, dcard_raw_text_string,
                 settings, radio_status, ethernet_status):
        super().__init__(model, subfamily, serial_number, firmware, uptime,
                         reboot_reason, dcard_raw_text_list,
                         dcard_raw_text_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status


class XGCard(RawDiagnosticCard):
    """A XG diagnostic card"""

    family = 'XG'

    def __init__(self, model, subfamily, serial_number, firmware, uptime,
                 reboot_reason, dcard_raw_text_list, dcard_raw_text_string,
                 settings, radio_status, ethernet_status, panic):
        super().__init__(model, subfamily, serial_number, firmware, uptime,
                         reboot_reason, dcard_raw_text_list,
                         dcard_raw_text_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status
        self.panic = panic


class QCard(RawDiagnosticCard):
    """A Quanta diagnostic card"""

    family = 'Quanta'

    def __init__(self, model, subfamily, serial_number, firmware, uptime,
                 reboot_reason, dcard_raw_text_list, dcard_raw_text_string,
                 settings, radio_status, ethernet_status):
        super().__init__(model, subfamily, serial_number, firmware, uptime,
                         reboot_reason, dcard_raw_text_list,
                         dcard_raw_text_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status

# Settings classes

# Radio Status classes

# Ethernet Status classes
