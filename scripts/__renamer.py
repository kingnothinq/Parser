#!/usr/bin/python
# -*- coding: utf-8 -*-

from pathlib import Path
from re import search
import shutil

def jira_info(path):
    with open(path / 'copy.txt', 'r') as cases:
        return cases.readlines()

def text(path):
    with open(path) as file:
        return file.read()

"""Rename attaches from JIRA"""

path = Path.cwd()
path_h08 = path / 'r5000' / 'h08'
path_h09 = path / 'r5000' / 'infimux'
path_old = path / 'r5000' / 'old'
path_h11 = path / 'r5000' / 'h11'
path_q = path / 'quanta'
path_xg = path / 'xg'
path_unk = path / 'unknown'
txt_files = list(path.glob('*.txt'))
files = list(path.glob('*[!txt]'))
cases = jira_info(path)

for file in files:
    old_name = search(r'attach\\(\d+)', str(file)).group(1)
    for case in cases:
        pattern = search(r'(DESK-\d+)/(\d+)', case)
        if pattern.group(2) == old_name:
            new_name = file.with_name(pattern.group(1)).with_suffix('.txt')
            counter = 0
            while Path.exists(new_name):
                counter += 1
                name = pattern.group(1) + '_' + str(counter)
                new_name = file.with_name(name).with_suffix('.txt')
            file.rename(new_name)

for file in txt_files:
    try:
        dcard = text(file)
        if search(r'#\sR5000\sWANFleX\sH08', dcard) is not None:
            new_path = str(path_h08) + '\\' + str(file.name)
            shutil.move(file, new_path)
        elif search(r'#\sR5000\sWANFleX\sH09', dcard) is not None:
            new_path = str(path_h09) + '\\' + str(file.name)
            shutil.move(file, new_path)
        elif search(r'#\sR5000\sWANFleX\sH11', dcard) is not None:
            new_path = str(path_h11) + '\\' + str(file.name)
            shutil.move(file, new_path)
        elif search(r'#\sR5000\sWANFleX\sH(01|02|03|04|05|06|07)', dcard) is not None:
            new_path = str(path_old) + '\\' + str(file.name)
            shutil.move(file, new_path)
        elif search(r'#\sXG\sWANFleX\sH12', dcard) is not None:
            new_path = str(path_xg) + '\\' + str(file.name)
            shutil.move(file, new_path)
        elif search(r'#\sOCTOPUS-PTP\sWANFleX\sH18', dcard) is not None:
            new_path = str(path_q) + '\\' + str(file.name)
            shutil.move(file, new_path)
        else:
            new_path = str(path_unk) + '\\' + str(file.name)
            shutil.move(file, new_path)
    except UnicodeDecodeError:
        continue









