#!/usr/bin/env python3

from modules.ssh import send_ssh_no_pagination

version_info = {
    'make': '',
    'model': '',
    'model_family': '',
    'software': '',
    'software_version': ''
}

def parse_lines(version_lines, precursor) -> None:
    for line in version_lines:
        if '--More--' not in line:
            clean_line = line.replace('"', '\\"').replace('\r', '')
            if precursor in clean_line:
                return False
            if 'ICX' in precursor:
                if "(c)" in clean_line:
                    split_line = (clean_line.strip()).split(" ")
                    make = split_line[2]
                    version_info['make'] = make
                if "HW: " in clean_line:
                    split_line = (clean_line.strip()).split(" ")
                    model = split_line[2]
                    version_info['model'] = model
                    split_model = model.split('-')
                    version_info['model_family'] = split_model[0]
                if "SW: " in clean_line:
                    split_line = (clean_line.strip()).split(" ")
                    version_info['software'] = f"{split_line[2]}"
                    split_software = (split_line[2]).split('-')
                    version_info['software_version'] = split_software[0]
            else:
                if "Software, Version" in clean_line:
                    split_line = (clean_line.strip()).split(" ")
                    version_info['software'] = f"Software: {split_line[1]} {split_line[2]} v{split_line[5]}"
                    split_software = (split_line[5]).split('.')
                    version_info['software_version'] = f"{split_line[1]} {split_line[2]} {split_software[0]}.{split_software[1]}"
                if "cisco" in clean_line and "processor" in clean_line:
                    split_line = (clean_line.strip()).split(" ")
                    version_info['make'] = split_line[0]
                    version_info['model'] = split_line[1]
                    split_model = split_line[1].split('-')
                    version_info['model_family'] = split_model[1]

def show_version(ssh_channel, precursor, no_pagination_cmd):
    version_output = send_ssh_no_pagination(ssh_channel, 'show version\n', precursor, no_pagination_cmd)
    if '\r' in version_output:
        split_info = version_output.split('\r', 1)
        version_output = split_info[1]
    version_lines = [line for line in version_output.split('\n') if line.strip()]
    parse_lines(version_lines, precursor)

    print(f'returning version info: \n{version_info}')
    return version_info