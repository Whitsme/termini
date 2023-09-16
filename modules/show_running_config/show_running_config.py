#!/usr/bin/env python3

from modules.send_ssh_command import send_ssh_command

def show_running_config(output_config, ssh_channel):

    running_config_and_interfaces = {
        'running_config': '',
        'interfaces': []
    }

    temp_config = []

    
    config_lines = [line for line in output_config.split('\n') if line.strip()]

    for line in config_lines:
        if '--More--' not in line:
            clean_line = line.replace('"', '\\"').replace('\r', '')
            temp_config.append(clean_line)

    more_found = 1
    saved_output = 0
    while saved_output < more_found:
        found_interface = ''
        end_interface = 1
        saved_interface = 1
        output_more = send_ssh_command(ssh_channel, ' ')
        more_lines = [line for line in output_more.split('\n') if line.strip()]
        for line in more_lines:
            if 'end' == line.strip():
                saved_output += 1
                break
            if '--More--' not in line:
                clean_line = line.replace('"', '\\"').replace('\r', '')
                temp_config.append(clean_line)
            if saved_interface < end_interface:
                if '!' in line:
                    saved_interface += 1
                    interfaces.append(found_interface)
                    found_interface = '' 
                else:  
                    clean_line = line.replace('"', '\\"').replace('\r', '')
                    found_interface = found_interface + clean_line     
            if 'interface' in line and saved_interface > 0:
                clean_line = line.replace('"', '\\"').replace('\r', '')
                if int(clean_line[-1]) > 0:
                    split_clean = (clean_line.split(" "))[1].split('/')
                    if "GigabitEthernet" in split_clean[0]:
                        port_type = "GbE"
                        if 'Ten' in split_clean[0]:
                            port_type = "10 GbE"
                        clean_interface = f"{port_type}: {split_clean[0][-1]}/{split_clean[1]}/{split_clean[2]}"
                        found_interface = clean_interface
                        saved_interface -= 1        
        more_found += 1
        saved_output += 1
    running_config_and_interfaces['running_config'] = '\n'.join(temp_config)

    return running_config