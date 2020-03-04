#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC


class RawDiagnosticCard(ABC):
    """A diagnostic card."""

    def __init__(self, model, subfamily, serial_number, firmware, uptime,
                 reboot_reason, dc_list, dc_string):
        self.model = model
        self.subfamily = subfamily
        self.serial_number = serial_number
        self.firmware = firmware
        self.uptime = uptime
        self.reboot_reason = reboot_reason
        self.dc_list = dc_list
        self.dc_string = dc_string


class R5000Card(RawDiagnosticCard):
    """An R5000 diagnostic card."""

    family = 'R5000'

    def __init__(self, model, subfamily, serial_number, firmware, uptime,
                 reboot_reason, dc_list, dc_string,
                 settings, radio_status, ethernet_status):
        super().__init__(model, subfamily, serial_number, firmware, uptime,
                         reboot_reason, dc_list,
                         dc_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status


class XGCard(RawDiagnosticCard):
    """A XG diagnostic card."""

    family = 'XG'

    def __init__(self, model, subfamily, serial_number, firmware, uptime,
                 reboot_reason, dc_list, dc_string,
                 settings, radio_status, ethernet_status, panic):
        super().__init__(model, subfamily, serial_number, firmware, uptime,
                         reboot_reason, dc_list,
                         dc_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status
        self.panic = panic


class QCard(RawDiagnosticCard):
    """A Quanta diagnostic card."""

    family = 'Quanta'

    def __init__(self, model, subfamily, serial_number, firmware, uptime,
                 reboot_reason, dc_list, dc_string,
                 settings, radio_status, ethernet_status):
        super().__init__(model, subfamily, serial_number, firmware, uptime,
                         reboot_reason, dc_list,
                         dc_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status