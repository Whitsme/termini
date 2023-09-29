#!/usr/bin/env python3

from modules.ssh import send_ssh_no_pagination

lldp_neighbors_data = {}

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

def parse_lines(output, precursor, detailed=None) -> None:
    for line in output:
        if '--More--' not in line:
            clean_line = line.replace('"', '\\"').replace('\r', '')
            if precursor in clean_line:
                break
            if detailed and "Local port" in clean_line or 'Local Intf' in clean_line:
                split_line = clean_line.split(':')
                if line_counter[0] > 0 and last_interface[0] != '':
                    save_interface()
                if len(split_line) > 1:
                    split_port = split_line[1].split('/')
                    last_interface[0] = f'{split_port[0][-1]}/{split_port[1]}/{split_port[2]}'
            all_lines.append(clean_line)
            line_counter[0] += 1

def show_lldp_neighbors(ssh_channel, precursor, no_pagination_cmd) -> dict:

    lldp_details = send_ssh_no_pagination(ssh_channel, 'show lldp neighbors detail\n', precursor, no_pagination_cmd)
    if '\r' in lldp_details:
        split_info = lldp_details.split('\r', 1)
        lldp_details = split_info[1]
    lldp_details_lines = [line for line in lldp_details.split('\n') if line.strip()]    
    parse_lines(lldp_details_lines, precursor, 'detailed')
    save_interface()

    return lldp_neighbors_data
