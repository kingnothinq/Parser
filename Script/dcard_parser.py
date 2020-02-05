#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search


class RawDiagnosticCard():
    """A diagnostic card"""

    def __init__(self, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text):
        self.model = model
        self.serial_number = serial_number
        self.firmware = firmware
        self.uptime = uptime
        self.rebootreason = rebootreason
        self.dcard_raw_text = dcard_raw_text


class R5000Card(RawDiagnosticCard):
    """An R5000 diagnostic card"""

    family = 'R5000'

    def __init__(self, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text, ethernet, radio):
        super().__init__(model, serial_number, firmware, uptime, rebootreason, dcard_raw_text)
        self.ethernet = ethernet
        self.radio = radio


class XGCard(RawDiagnosticCard):
    """A XG diagnostic card"""

    family = 'XG'

    def __init__(self, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text, rssi, cinr, modulation,
                 crosstalk, etherrors, radioerrors):
        super().__init__(model, serial_number, firmware, uptime, rebootreason, dcard_raw_text)
        self.rssi = rssi
        self.cinr = cinr
        self.modulation = modulation
        self.crosstalk = crosstalk
        self.etherrors = etherrors
        self.radioerrors = radioerrors


class QCard(RawDiagnosticCard):
    """A Quanta diagnostic card"""

    family = 'Quanta'

    def __init__(self, model, serial_number, firmware, uptime, rebootreason, dcard_raw_text, rssi, evm, modulation,
                 crosstalk,
                 etherrors, radioerrors):
        super().__init__(model, serial_number, firmware, uptime, rebootreason, dcard_raw_text)
        self.rssi = rssi
        self.evm = evm
        self.modulation = modulation
        self.crosstalk = crosstalk
        self.etherrors = etherrors
        self.radioerrors = radioerrors


def parse_R5000(dcard_raw_text):
    """Parse an R5000 diagnostic card and fill the class instance in"""

    for line in dcard_raw_text:

        # Model (Part Number)
        if search(r"\b(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]{1,3}.300.2x\d{3})(.2x\d{2})?\b", line) is not None:
            model = search(r"\b(R5000-[QMOSL][mxnbtcs]{2,5}/[\dX\*]{1,3}.300.2x\d{3})(.2x\d{2})?\b", line).group()

        # Serial number
        if search(r"\bSN:\d{6}\b", line) is not None:
            serial_number = search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware
        if search(r"\bH\d{2}S\d{2}-(MINT|TDMA)[v\d.]+\b", line) is not None:
            firmware = search(r"\bH\d{2}S\d{2}-(MINT|TDMA)[v\d.]+\b", line).group()

        # Uptime
        if search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason
        if search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    ethernet = {'eth0': 0, 'eth1': 1}
    radio = {'link1': {'rssi': 1, 'cinr': 2}, 'link2': {'rssi': 1, 'cinr': 2}}

    result = R5000Card(model, serial_number, firmware, uptime, rebootreason, dcard_raw_text, str(ethernet), str(radio))

    return result


def parse_XG(dcard_raw_text):
    """Parse a XG diagnostic card and fill the class instance in"""

    for line in dcard_raw_text:
        # Model (Part Number)
        if search(r"[XU]m/\dX?.\d{3,4}.\dx\d{3}(.2x\d{2})?", line) is not None:
            model = search(r"[XU]m/\dX?.\d{3,4}.\dx\d{3}(.2x\d{2})?", line).group()

        # Serial number
        if search(r"\bSN:\d{6}\b", line) is not None:
            serial_number = search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware
        if search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line) is not None:
            firmware = search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line).group()

        # Uptime
        if search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason
        if search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    result = XGCard(model, serial_number, firmware, uptime, rebootreason, dcard_raw_text, '1', '1', '1', '1', '1', '1')

    return result


def parse_Quanta(dcard_raw_text):
    """Parse a Quanta 5 diagnostic card and fill the class instance in"""

    for line in dcard_raw_text:
        # Model (Part Number)
        if search(r"Q5-[\dE]+", line) is not None:
            model = search(r"Q5-[\dE]+", line).group()

        # Serial number
        if search(r"\bSN:\d{6}\b", line) is not None:
            serial_number = search(r"\bSN:(\d{6})\b", line).group(1)

        # Firmware
        if search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line) is not None:
            firmware = search(r"\bH\d{2}S\d{2}[v\d.-]+\b", line).group()

        # Uptime
        if search(r"^Uptime: ([\d\w :]*)$", line) is not None:
            uptime = search(r"^Uptime: ([\d\w :]*)$", line).group(1)

        # Last Reboot Reason
        if search(r"^Last reboot reason: ([\w ]*)$", line) is not None:
            rebootreason = search(r"^Last reboot reason: ([\w ]*)$", line).group(1)

    result = QCard(model, serial_number, firmware, uptime, rebootreason, dcard_raw_text, '1', '1', '1', '1', '1', '1')

    return result
