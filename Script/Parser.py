#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


class RawCard():

    def __init__(self, model, serial_number, firmware, uptime, rebootreason, rawdcard):
        self.model = model
        self.serial_number = serial_number
        self.firmware = firmware
        self.uptime = uptime
        self.rebootreason = rebootreason
        self.rawdcard = rawdcard


class R5000Card(RawCard):

    def __init__(self, model, serial_number, firmware, uptime, rebootreason, rawdcard, ethernet, radio):
        super().__init__(model, serial_number, firmware, uptime, rebootreason, rawdcard)
        self.ethernet = ethernet
        self.radio = radio


class XGCard(RawCard):

    def __init__(self, model, serial_number, firmware, uptime, rebootreason, rawdcard, rssi, cinr, modulation,
                 crosstalk, etherrors, radioerrors):
        super().__init__(model, serial_number, firmware, uptime, rebootreason, rawdcard)
        self.rssi = rssi
        self.cinr = cinr
        self.modulation = modulation
        self.crosstalk = crosstalk
        self.etherrors = etherrors
        self.radioerrors = radioerrors


class QCard(RawCard):

    def __init__(self, model, serial_number, firmware, uptime, rebootreason, rawdcard, rssi, evm, modulation, crosstalk,
                 etherrors, radioerrors):
        super().__init__(model, serial_number, firmware, uptime, rebootreason, rawdcard)
        self.rssi = rssi
        self.evm = evm
        self.modulation = modulation
        self.crosstalk = crosstalk
        self.etherrors = etherrors
        self.radioerrors = radioerrors


def parse_R5000(rawdcard):

    for line in rawdcard:

        # Model (Part Number)
        if re.search(r"\b(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]{1,3}.300.2x\d{3})(.2x\d{2})?\b", line) is not None:
            model = re.search(r"\b(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]{1,3}.300.2x\d{3})(.2x\d{2})?\b", line).group()

        # Serial number
        if re.search(r"\bSN:\d{6}\b", line) is not None:
            serial_number = re.search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware
        if re.search(r"\bH\d{2}S\d{2}-(MINT|TDMA)[v\d.]+\b", line) is not None:
            firmware = re.search(r"\bH\d{2}S\d{2}-(MINT|TDMA)[v\d.]+\b", line).group()

        # Uptime
        if re.search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = re.search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason
        if re.search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = re.search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    ethernet = {'eth0': 0, 'eth1': 1}
    radio = {'link1': {'rssi': 1, 'cinr': 2}, 'link2': {'rssi': 1, 'cinr': 2}}

    result = R5000Card(model, serial_number, firmware, uptime, rebootreason, rawdcard, str(ethernet), str(radio))

    return result


def parse_XG(rawdcard):

    for line in rawdcard:
        # Model (Part Number)
        if re.search(r"[XU]m/\dX?.\d{3,4}.\dx\d{3}(.2x\d{2})?", line) is not None:
            model = re.search(r"[XU]m/\dX?.\d{3,4}.\dx\d{3}(.2x\d{2})?", line).group()

        # Serial number
        if re.search(r"\bSN:\d{6}\b", line) is not None:
            serial_number = re.search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware
        if re.search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line) is not None:
            firmware = re.search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line).group()

        # Uptime
        if re.search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = re.search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason
        if re.search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = re.search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    result = XGCard(model, serial_number, firmware, uptime, rebootreason, rawdcard, '1', '1', '1', '1', '1','1')

    return result

def parse_Quanta(rawdcard):

    for line in rawdcard:
        # Model (Part Number)
        if re.search(r"Q5-[\dE]+", line) is not None:
            model = re.search(r"Q5-[\dE]+", line).group()

        # Serial number
        if re.search(r"\bSN:\d{6}\b", line) is not None:
            serial_number = re.search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware
        if re.search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line) is not None:
            firmware = re.search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line).group()

        # Uptime
        if re.search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = re.search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason
        if re.search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = re.search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    result = QCard(model, serial_number, firmware, uptime, rebootreason, rawdcard, '1', '1', '1', '1', '1','1')

    return result