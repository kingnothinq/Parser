#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import collections



# Diagnostic cards classes

class RawDiagnosticCard(ABC):
    """A diagnostic card"""

    def __init__(self, subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list, dcard_raw_text_string):
        self.subfamily = subfamily
        self.model = model
        self.serial_number = serial_number
        self.firmware = firmware
        self.uptime = uptime
        self.rebootreason = rebootreason
        self.dcard_raw_text_list = dcard_raw_text_list
        self.dcard_raw_text_string = dcard_raw_text_string


class R5000Card(RawDiagnosticCard):
    """An R5000 diagnostic card"""

    family = 'R5000'

    def __init__(self, subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list, dcard_raw_text_string, ethernet, radio):
        super().__init__(subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list, dcard_raw_text_string)
        self.ethernet = ethernet
        self.radio = radio


class XGCard(RawDiagnosticCard):
    """A XG diagnostic card"""

    family = 'XG'

    def __init__(self, subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list, dcard_raw_text_string, settings, radio_status,
                 ethernet_status, panic):
        super().__init__(subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list, dcard_raw_text_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status
        self.panic = panic


class QCard(RawDiagnosticCard):
    """A Quanta diagnostic card"""

    family = 'Quanta'

    def __init__(self, subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list, dcard_raw_text_string, settings, radio_status,
                 ethernet_status, panic):
        super().__init__(subfamily, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text_list, dcard_raw_text_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status
        self.panic = panic

# Settings classes

# Radio Status classes

# Ethernet Status classes