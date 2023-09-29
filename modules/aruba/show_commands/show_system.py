#!/usr/bin/env python3

import re

from modules.ssh import send_ssh_no_pagination

version_info = {
    'make': '',
    'model': '',
    'model_family': '',
    'software': '',
    'software_version': ''
}

def parse_lines(system_lines, precursor) -> None:
    for line in system_lines:
        if '--More--' not in line:
            clean_line = line.replace('"', '\\"').replace('\r', '')
            if precursor in clean_line:
                return False
            if "Software revision" in clean_line:
                split_line = clean_line.split(':')[1].strip().split(' ')
                version_info['software'] = f"{split_line[0].strip()}"
                version_info['software_version'] = f"{split_line[0].strip()}"

def show_system(ssh_channel, precursor, no_pagination_cmd) -> dict:
    system_output = send_ssh_no_pagination(ssh_channel, 'show system\n', precursor, no_pagination_cmd)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    system_output = ansi_escape.sub('', system_output)
    if '\r' in system_output:
        split_info = system_output.split('\r', 1)
        system_output = split_info[1]
    system_lines = [line for line in system_output.split('\n') if line.strip()]
    parse_lines(system_lines, precursor)

    return version_info