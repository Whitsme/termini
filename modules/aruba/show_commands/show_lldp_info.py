#!/usr/bin/env python3

import re

from modules.ssh import send_ssh_no_pagination

lldp_neighbors_data = {}

# show lldp info remote-device detail

all_lines = []
interface_counter = [0]
last_interface = ['']
last_port = [0]
line_counter = [0]

def save_interface() -> None:
    this_port = {}
    key = ''
    get_description = False

    for j in range(last_port[0], line_counter[0]):
        line = all_lines[j]
        split_line = line.split(':', 1)
        if 'System description' in line and len(split_line) > 1:
            key = split_line[0].strip().replace('+ ', '')
            value = split_line[1].strip().replace('\\', '')
            this_port[key] = value
            get_description = True
        elif get_description == True:     
            line = line.strip().replace('\\', '')
            this_port[key] = f"{this_port[key]}{line}"
            if '"' in line:
                get_description = False
        else:
            split_all_line = line.split(':')
            if len(split_all_line) == 2: 
                key = split_all_line[0].strip().replace('+ ', '')
                value = split_all_line[1].strip().replace('\\', '')
                this_port[key] = value
            elif len(split_all_line) == 1 and '+' not in line and '---' not in line:
                line = line.strip().replace('\\', '')
                this_port[key] = f"{this_port[key]}{line}"

    lldp_neighbors_data[last_interface[0]] = this_port
    interface_counter[0] += 1
    last_port[0] = line_counter[0]

def parse_lines(output, precursor) -> None:
    for line in output:
        if '--More--' not in line:
            if precursor in line:
                break
            if "Local port" in line:
                port = line.split(':')[1]
                if line_counter[0] > 0 and last_interface[0] != '':
                    save_interface()
                sub_port = 0
                if 'A' in port:
                    sub_port = 1
                    port = port.strip('A')
                elif 'B' in port:
                    sub_port = 2
                    port = port.strip('B')
                elif 'C' in port:
                    sub_port = 3
                    port = port.strip('C')
                last_interface[0] = f'1/{sub_port}/{port}'
            all_lines.append(line)
            line_counter[0] += 1

def show_lldp_info(ssh_channel, precursor, no_pagination_cmd) -> dict:

    lldp_details = send_ssh_no_pagination(ssh_channel, 'show lldp info remote-device detail\n', precursor, no_pagination_cmd)

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    lldp_details = ansi_escape.sub('', lldp_details)

    lldp_details_lines = [line for line in lldp_details.split('\n') if line.strip()] 
    parse_lines(lldp_details_lines, precursor)
    save_interface()

    return lldp_neighbors_data