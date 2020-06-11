# -*- coding: utf-8 -*-

import logging
from time import time


def timer(function):
    """Estimate time"""
    def wrapper(dc_string, dc_list):
        time_start = time()
        created_report = function(dc_string, dc_list)
        time_end = time()
        logger.info(f'Report prepared, Elapsed Time: {time_end - time_start}')
        return created_report
    return wrapper


@timer
def jira(device, tests):
    """Prepare a report for JIRA."""

    settings = device.settings
    radio_status = device.radio_status
    downlink = radio_status['Downlink']
    uplink = radio_status['Uplink']
    ethernet_status = device.ethernet_status['ge0']
    tests = '\n'.join(tests)

    message = f'''
    *General*
    |*Serial Number*|{device.serial_number}|
    |*Model*|{device.model}|
    |*Firmware version*|{device.firmware}|

    *Settings*
    |*Role*|{str.capitalize(settings["Role"])}|
    |*Frequencies*| DL - {settings["DL Frequency"]} MHz
    UL - {settings["UL Frequency"]} MHz
    |*Bandwidth*|{settings["Bandwidth"]} MHz|
    |*Frame size*|{settings["Frame size"]} ms|
    |*Guard interval*|{settings["Guard Interval"]}|
    |*Tx Power*|{settings["Tx Power"]} dBm|
    |*ATPC*|{settings["ATPC"]}|
    |*AMC Strategy*|{str.capitalize(settings["AMC Strategy"])}|
    |*Max MCS*| DL {settings["Max DL MCS"]}
    UL - {settings["Max UL MCS"]}|
    |*DL/UL Ratio*|{settings["DL/UL Ratio"]} %|
    |*ARQ*|{settings["ARQ"]}|
    |*DFS*|{settings["DFS"]}|

    *Radio status*
    |*Link status*|{radio_status["Link status"]}| | | |
    |*Measured Distance*|{radio_status["Measured Distance"]}| | | |
    |---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|
    |*Side*|Master|*Role*|Uplink| |
    | |_Carrier 0_|_Carrier 0_| | |
    |*Tx Frequency*| {downlink["Frequency"]}| (to Slave)| | |
    | |_Stream 0_|_Stream 1_| | |
    |*Tx Power*| {uplink["Stream 0"]["Tx Power"]}| {uplink["Stream 1"]["Tx Power"]}| (to Slave)| |
    |*Rx RSSI*| {uplink["Stream 0"]["RSSI"]}| {uplink["Stream 1"]["RSSI"]}| (to Master)| |
    |*Rx EVM*| {uplink["Stream 0"]["EVM"]}| {uplink["Stream 1"]["EVM"]}| (to Master)| |
    |*Rx MCS*| {uplink["Stream 0"]["MCS"]}| {uplink["Stream 1"]["MCS"]}| (to Master)| |
    |*Rx ARQ ratio*| {uplink["Stream 0"]["ARQ ratio"]}| {uplink["Stream 1"]["ARQ ratio"]}| (to Master)| |
    |---------------------------|---------------------------|---------------------------|---------------------------|---------------------------|
    |*Side*|Slave|*Role*|Downlink| |
    | |_Carrier 0_|_Carrier 0_| | |
    |*Tx Frequency*| {uplink["Frequency"]}| (to Master)| | |
    | |_Stream 0_|_Stream 1_| | |
    |*Tx Power*| {downlink["Stream 0"]["Tx Power"]}| {downlink["Stream 1"]["Tx Power"]}| (to Master)| |
    |*Rx RSSI*| {downlink["Stream 0"]["RSSI"]}| {downlink["Stream 1"]["RSSI"]}| (to Slave)| |
    |*Rx EVM*| {downlink["Stream 0"]["EVM"]}| {downlink["Stream 1"]["EVM"]}| (to Slave)| |
    |*Rx MCS*| {downlink["Stream 0"]["MCS"]}| {downlink["Stream 1"]["MCS"]}| (to Slave)| |
    |*Rx ARQ ratio*| {downlink["Stream 0"]["ARQ ratio"]}| {downlink["Stream 1"]["ARQ ratio"]}| (to Slave)| |

    *Physical interfaces status*
    |*Ge0*|{ethernet_status["Status"]}|

    *Issues and recommendations*
    {tests}
    '''

    return device.model, device.family, device.subfamily, device.serial_number, device.firmware, message


@timer
def web():
    pass


@timer
def cli():
    pass


logger = logging.getLogger('logger.report_q5')