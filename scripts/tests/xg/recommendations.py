#!/usr/bin/python
# -*- coding: utf-8 -*-

from re import search, findall

from ftplib import FTP


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
    release_firmwares = ftp.nlst('pub/Firmware/XG/H12/')
    beta_firmwares = ftp.nlst('pub/Firmware/beta/XG/')
    firmwares = release_firmwares + beta_firmwares
    current_version = search(r'v((\d+\.){2}(\d+))', device.firmware).group(1)
    latest_version = []
    for version in firmwares:
        ftp_firmware = search(r'v(\d+\.\d+\.\d+)\.bin', version)
        if ftp_firmware is not None:
            latest_version.append(ftp_firmware.group(1))
    latest_version.sort()
    latest_fw_name = 'firmware.H12S10v{}.bin'.format(latest_version[-1])
    if ('pub/Firmware/beta/XG/' + latest_fw_name) in beta_firmwares:
        ftp_path = 'ftp://ftp.infinet.ru/pub/Firmware/beta/XG/' + latest_fw_name
    else:
        ftp_path = 'ftp://ftp.infinet.ru/pub/Firmware/XG/H12/' + latest_fw_name
    if current_version != latest_version[-1]:
        result.append('* The current firmware version ({}) is old. '
                      'Please update it. '
                      'The latest version ({}) can be downloaded '
                      'from our FTP server ({}).'
                      .format(current_version, latest_version[-1], ftp_path))

    if len(result) > 0:
        return '\nRecommendations: \n' + '\n'.join(result)
    else:
        pass