#!/usr/bin/env python3

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

def aruba_pre_process_vlan(vlan_type, last_vlan, split_line):
    port_start = split_line[2].split('-')[0]
    port_end = split_line[2].split('-')[1]
    if 'A' in port_start:
        sub_port = 1
        port_start = port_start.strip('A')
    elif 'B' in port_start:
        sub_port = 2
        port_start = port_start.strip('B')
    elif 'C' in port_start:
        sub_port = 3
        port_start = port_start.strip('C')
    for port in range(int(port_start), int(port_end) + 1):
        if port_start is list:
            port_number = f'{port_start[0]}/{port_start[1]}/{port}' 
        else:
            port_number = f'1/{sub_port}/{port}' 
        save_vlan(vlan_type, port_number, last_vlan)

def parse_untagged_vlan(split_line, last_vlan) -> None:
    vlan_type = 'untagged_vlan'
    if '-' in split_line:
        sub_port = 0
        if ',' in split_line:
            split_ranges = split_line[2].split(',')
            for port_range in split_ranges:
                aruba_pre_process_vlan(vlan_type, last_vlan, port_range)
        else:
            aruba_pre_process_vlan(vlan_type, last_vlan, split_line)
    else: 
        i = 0
        for word in split_line:
            if 'ethe' == word:
                port_number = split_line[i + 1]
                save_vlan(vlan_type, port_number, last_vlan)
            i +=1

def parse_tagged_vlan(split_line, last_vlan) -> None:
    vlan_type = 'tagged_vlan'
    try:
        split_line[1] = int(split_line[1])
        port_number = split_line[1]
        save_vlan(vlan_type, port_number, last_vlan)
    except:
        if '-' in split_line:
            sub_port = 0
            if ',' in split_line:
                split_ranges = split_line[2].split(',')
                for port_range in split_ranges:
                    aruba_pre_process_vlan(vlan_type, port_number, last_vlan, port_range)
            else:
                aruba_pre_process_vlan(vlan_type, port_number, last_vlan, split_line)

        if '/' in split_line[2]:
            port_start = split_line[2].split('/')
            port_end = split_line[4].split('/')
        
        for port in range(int(port_start[-1]), int(port_end[-1]) + 1):
            port_number = f'{port_start[0]}/{port_start[1]}/{port}' 
            save_vlan(vlan_type, port_number, last_vlan)

def parse_lines(output, precursor) -> None:
    last_interface = ''
    last_vlan = ''
    for line in output:
        if '--More--' not in line:
            clean_line = line.replace('"', '\\"').replace('\r', '')
            if precursor in clean_line:
                return False
            if 'interface' in clean_line:
                split_interface = clean_line.split(' ')[1].split('/')
                if len(split_interface) == 3:
                    interface = f"{split_interface[0][-1]}/{split_interface[1]}/{split_interface[2]}"
                    last_interface = interface
            if 'vlan' in clean_line:
                if 'switchport' in clean_line:
                    last_vlan = clean_line.split(' ')[-1]
                else: 
                    last_vlan = clean_line.split(' ')[1]
                if 'native' in clean_line:
                    save_vlan('untagged_vlan', last_interface, last_vlan)
                elif  'access' in clean_line or 'allowed' in clean_line:
                    save_vlan('tagged_vlan', last_interface, last_vlan)
                
            if 'untagged' in clean_line or 'tagged' in clean_line:
                split_line = clean_line.strip().split(' ')
                if 'untagged' in clean_line:
                    parse_untagged_vlan(split_line, last_vlan)
                elif 'tagged' in clean_line:
                    parse_tagged_vlan(split_line, last_vlan)                     
                                  
            all_lines.append(clean_line)

def aruba_show_running_config(ssh_channel, precursor, no_pagination_cmd) -> dict:
    output = send_ssh_no_pagination(ssh_channel, 'show running-config\n', precursor, no_pagination_cmd)
    output_lines = [line for line in output.split('\n') if line.strip()]
    parse_lines(output_lines, precursor)

    running_config_and_interfaces['running_config'] = '\n'.join(all_lines)
    return running_config_and_interfaces
