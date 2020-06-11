# -*- coding: utf-8 -*-

from abc import ABC
from importlib import import_module
import logging
from pathlib import Path
from re import search


class RawDiagnosticCard(ABC):
    """A diagnostic card."""

    def __init__(self, model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string):
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

    def __init__(self, model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string, settings,
                 radio_status, ethernet_status, switch_status, qos_status):
        super().__init__(model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status
        self.switch_status = switch_status
        self.qos_status = qos_status


class XGCard(RawDiagnosticCard):
    """A XG diagnostic card."""

    family = 'XG'

    def __init__(self, model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string, settings,
                 radio_status, ethernet_status, panic):
        super().__init__(model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status
        self.panic = panic


class Q5Card(RawDiagnosticCard):
    """A Quanta diagnostic card."""

    family = 'Q5'

    def __init__(self, model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string, settings,
                 radio_status, ethernet_status):
        super().__init__(model, subfamily, serial_number, firmware, uptime, reboot_reason, dc_list, dc_string)
        self.settings = settings
        self.radio_status = radio_status
        self.ethernet_status = ethernet_status


def get_result(dc_string, dc_list, dc_name, dc_source):
    """Look for all available parsers for the requested device and run them.
    Return a class with filled arguments or an error.
    """

    def import_parser(dc_string, dc_list, dc_model):
        """Dynamic modules (parsers) import. Import only modules starts from "parser_*"

                A module must follow the next template:
                def parse(dc_string, dc_list):
                    #parse settings
                    #parse radio
                    #parse ethernet
                    #etc...
                    return tuple of objects
        """

        try:
            module = import_module(f'.parser_{dc_model}', 'scripts.parsers')
            logger.info(f'{module} was imported to parse the diagnostic card')
        except:
            logger.critical(f'Parsing script cannot be imported')

        return module.parse(dc_string, dc_list)


    def save_file(dc_list, dc_name, dc_source):
        """Save unparsed file"""

        file_name = f'{dc_name}.txt'
        file_storage = Path.joinpath(Path.cwd() / 'scripts' / 'dcards' / 'unknown', dc_source[1])
        file_path = Path.joinpath(file_storage, file_name)

        # Create a folder if it does not exist
        if Path.is_dir(file_storage) is False:
            Path.mkdir(file_storage)

        #Rename the file if the name is occupied
        file_name_counter = 0
        while Path.exists(file_path):
            file_name_counter += 1
            file_name = f'{dc_name}_{file_name_counter}.txt'
            file_path = Path.joinpath(file_storage, file_name)

        #Write text in the file
        with open(file_path, 'w') as file:
            for line in dc_list:
                file.write(line)

        logger.info(f'The unparsed file ({file_name}) was saved here: {file_storage}')


    try:
        #R5000 series
        if search(r'#\sR5000\sWANFleX\sH(01|02|03|04|05|06|07|08|11)', dc_string) is not None:
            logger.debug('This is R5000')
            dc_parsed = import_parser(dc_string, dc_list, 'r5000')
            device = R5000Card(*dc_parsed)

        #InfiMux (not supported)
        elif search(r'#\sR5000\sWANFleX\sH09', dc_string) is not None:
            logger.debug('This is InfiMUX')
            pass

        #E5000 series (not supported)
        elif search(r'#\sR5000\sWANFleX\sH(16|22)', dc_string) is not None:
            logger.debug('This is E5000')
            pass

        #XG series
        elif search(r'#\sXG\sWANFleX\sH12', dc_string) is not None:
            logger.debug('This is XG')
            dc_parsed = import_parser(dc_string, dc_list, 'xg')
            device = XGCard(*dc_parsed)

        #Quanta 5 series
        elif search(r'#\sOCTOPUS-PTP\sWANFleX\sH18', dc_string) is not None:
            logger.debug('This is Quanta 5')
            dc_parsed = import_parser(dc_string, dc_list, 'q5')
            device = Q5Card(*dc_parsed)

        #Quanta 70 series (not supported)
        elif search(r'#\sOCTOPUS-PTP\sWANFleX\sH21', dc_string) is not None:
            logger.debug('This is Quanta 70')
            pass

        #Axion 28 series (not supported)
        elif search(r'#\sOCTOPUS-PTP\sWANFleX\sH(19|20)', dc_string) is not None:
            logger.debug('This is Axion 28')
            pass

        else:
            raise

        return device

    except:
        logger.critical('The uploaded file cannot be parsed')
        save_file(dc_string, dc_name, dc_source)


logger = logging.getLogger('logger.dc_parser')