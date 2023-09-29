#!/usr/bin/env python3

import re

from modules.ssh import send_ssh_no_pagination

def parse_lines(module_lines, precursor) -> str:
    for line in module_lines:
        if '--More--' not in line:
            clean_line = line.replace('"', '\\"').replace('\r', '')
            if precursor in clean_line:
                return False
            if "Chassis" in clean_line:
                split_line = (clean_line.strip()).split(" ")
                hardware = f'Aruba {split_line[1]}'
                return hardware

def show_modules(ssh_channel, precursor, no_pagination_cmd) -> dict:
    modules_output = send_ssh_no_pagination(ssh_channel, 'show modules\n', precursor, no_pagination_cmd)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    modules_output = ansi_escape.sub('', modules_output)
    if '\r' in modules_output:
        split_info = modules_output.split('\r', 1)
        modules_output = split_info[1]
    module_lines = [line for line in modules_output.split('\n') if line.strip()]
    hardware = parse_lines(module_lines, precursor)
    
    return hardware



    