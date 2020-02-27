#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search, findall


def test(device):
    """Not important or not necessary recommendations."""

    result = []

    if device.settings['Traffic prioritization'] == 'Enabled':
        result.append('* Traffic prioritization is not an exact QoS feature. '
                      'It is recommended to disable it due the bug (XG-1164).')

    if search(r'Antenna Gain not found in license', device.dc_string) is not None:
        result.append('* Antenna Gain not found in the license. '
                      'Please set this parameter via CLI (xg -antenna-gain <gain_dBm>).')

    pattern = findall(r'(\d{2}):(\d{2}):(\d{2})', device.uptime)
    if int(pattern[0][0]) <= 0 and int(pattern[0][1]) < 15:
        result.append('* Uptime is too short ({}). '
                      'It is recommended to wait more in order to collect more precise statistics.'
                      .format(device.uptime))

    ftp = FTP('ftp.infinet.ru')
    ftp.login()
    firmwares = ftp.nlst('pub/Firmware/octopus/h18/')
    print(device.firmware)
    current_version = search(r'PTPv((\d+\.){2}(\d+))', device.firmware).group(1)
    latest_firmware = []
    for version in firmwares:
        ftp_firmware = findall(r'h18_((\d+)\.(\d+)\.(\d+))\.bin', version)[0]
        ftp_firmware = [ftp_firmware[1], ftp_firmware[2], ftp_firmware[3]]
        latest_firmware.append(ftp_firmware)
    latest_firmware.sort()
    latest_firmware = '.'.join(latest_firmware[-1])
    ftp_path = 'ftp://ftp.infinet.ru/pub/Firmware/octopus/h18/_{}.bin'.format(latest_firmware)
    if current_version != latest_firmware:
        result.append('* The current firmware version ({}) is too old. '
                      'Please update it. '
                      'The latest version {} can be downloaded '
                      'from our FTP server ({}).'
                      .format(current_version, latest_firmware, ftp_path))

    if len(result) > 0:
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        pass