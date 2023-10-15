#!/usr/bin/env python3

import re

from modules.ssh import send_ssh_no_pagination

running_config_and_interfaces = {
    'running_config': '',
    'tagged_vlan': {},
    'untagged_vlan': {}
}

all_lines = []

def save_vlan(vlan_type, port_number, last_vlan) -> None:
    if len(last_vlan.split(',')) > 1:
        last_vlan = last_vlan.split(',')
        running_config_and_interfaces[vlan_type][port_number] = last_vlan
    else:
        if port_number in running_config_and_interfaces[vlan_type]:
            running_config_and_interfaces[vlan_type][port_number].append(last_vlan)
        else:
            running_config_and_interfaces[vlan_type][port_number] = [last_vlan]

def get_sub_port(port_start, port_end=None):
    sub_port = 0
    if 'A' in port_start:
        sub_port = 1
        port_start = port_start.strip('A')
        if port_end:
            port_end = port_end.strip('A')
    elif 'B' in port_start:
        sub_port = 2
        port_start = port_start.strip('B')
        if port_end:
            port_end = port_end.strip('B')
    elif 'C' in port_start:
        sub_port = 3
        port_start = port_start.strip('C')
        if port_end:
            port_end = port_end.strip('C')
    

def aruba_pre_process_vlan(vlan_type, last_vlan, port_range):
    split_range = str(port_range).split('-')
    if len(split_range) > 1: 
        port_start = split_range[0]
        port_end = split_range[1]
    else:
        port_start = str(port_range)
        port_end = None
    sub_port = 0
    if 'A' in port_start:
        sub_port = 1
        port_start = port_start.strip('A')
    elif 'B' in port_start:
        sub_port = 2
        port_start = port_start.strip('B')
    elif 'C' in port_start:
        sub_port = 3
        port_start = port_start.strip('C')
    if port_end != None: 
        port_end = port_end.strip('A').strip('B').strip('C')
        for port in range(int(port_start), int(port_end) + 1):
            port_number = f'1/{sub_port}/{port}' 
            save_vlan(vlan_type, port_number, last_vlan)
    else:
        port = port_range
        port_number = f'1/{sub_port}/{port}' 
        save_vlan(vlan_type, port_number, last_vlan)

def parse_untagged_vlan(split_line, last_vlan) -> None:
    vlan_type = 'untagged_vlan'
    if '-' in split_line[1]:
        if ',' in split_line[1]:
            split_ranges = split_line[1].split(',')
            for port_range in split_ranges:
                aruba_pre_process_vlan(vlan_type, last_vlan, port_range)
        else:
            port_range = split_line[1]
            aruba_pre_process_vlan(vlan_type, last_vlan, port_range)
    else:
        if len(split_line) == 2:
            split_line[1] = int(split_line[1])
            port_range = split_line[1]
            aruba_pre_process_vlan(vlan_type, last_vlan, port_range)

def parse_tagged_vlan(split_line, last_vlan) -> None:
    vlan_type = 'tagged_vlan'
    if '-' in split_line[1]:
        if ',' in split_line[1]:
            split_ranges = split_line[1].split(',')
            for port_range in split_ranges:
                aruba_pre_process_vlan(vlan_type, last_vlan, port_range)
        else:
            port_range = split_line[1]
            aruba_pre_process_vlan(vlan_type, last_vlan, port_range)
    else:
        if len(split_line) == 2:
            split_line[1] = int(split_line[1])
            port_number = split_line[1]
            save_vlan(vlan_type, port_number, last_vlan)

def parse_lines(output, precursor) -> None:
    last_interface = ''
    last_vlan = ''
    for line in output:
        if '-- MORE --' not in line:
            print(line)
            split_line = line.strip().split(' ')
            if precursor in line:
                return
            if 'vlan' in line:
                last_vlan = split_line[1] 
            if len(split_line) == 2:
                if 'untagged' in line:
                    parse_untagged_vlan(split_line, last_vlan)
                elif 'tagged' in line:
                    parse_tagged_vlan(split_line, last_vlan)                     
                                  
            all_lines.append(line)

def aruba_show_running_config(ssh_channel, precursor, no_pagination_cmd) -> dict:
    output = send_ssh_no_pagination(ssh_channel, 'show running-config\n', precursor, no_pagination_cmd)
    # output = send_ssh_no_pagination(ssh_channel, 'show config int\n', precursor, no_pagination_cmd)

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)

    output_lines = [line for line in output.split('\n') if line.strip()]
    parse_lines(output_lines, precursor)

    running_config_and_interfaces['running_config'] = '\n'.join(all_lines)
    print('returning running config')
    print(running_config_and_interfaces['untagged_vlan'])
    return running_config_and_interfaces
