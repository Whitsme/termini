#!/usr/bin/env python3

from modules.utilities import send_ssh_no_pagination

all_lines = []
interface_data = []
interface_counter = [0]
last_port = [0]
line_counter = [0]
found_interface = [False]

def save_interface() -> None:
    port_details = []
    for j in range(last_port[0], line_counter[0]):
        port_details.append(all_lines[j])
    interface_data[interface_counter[0]]['details'] = "\n".join(port_details)

    interface_counter[0] += 1

def parse_lines(interface_lines, precursor) -> None:
    
    for line in interface_lines:
        if '--More--' not in line:
            clean_line = line.replace('"', '\\"').replace('\r', '')
            if precursor in clean_line:
                return False
            if "line protocol" in clean_line and '/' in clean_line:
                split_interface = (clean_line.split(" "))[0].split('/')
                if len(split_interface) == 3:
                    this_port = {
                        'port': '',
                        'status': '',
                        'type': '',
                        'details': '',
                    }
                    if "GigabitEthernet" in split_interface[0]:
                        port_type = "GbE"
                    if '10' in split_interface[0] or 'Ten' in split_interface[0]:
                        port_type = "10 GbE"
                    if '40' in split_interface[0]:
                        port_type = "40 GbE"

                    this_port['port'] = f"{split_interface[0][-1]}/{split_interface[1]}/{split_interface[2]}"
                    this_port['type'] = port_type

                    split_line = clean_line.split(" ")
                    this_port['status'] = split_line[2]   

                    interface_data.append(this_port)
                    if found_interface[0] == True:
                        save_interface()
                    found_interface[0] = True
                last_port[0] = line_counter[0]    
            all_lines.append(clean_line)
            line_counter[0] += 1

# def ruckus_more_lines(ssh_channel):
#     output_one = send_ssh_command(ssh_channel, ' ')
#     output_two = send_ssh_command(ssh_channel, '\n')
#     output_three = send_ssh_command(ssh_channel, ' ')
#     output = f'{output_one}{output_two}{output_three}'
#     return output

# def parse_interface(output_interfaces, ssh_channel, precursor):
#     interface_lines = [line for line in output_interfaces.split('\n') if line.strip()]
#     while clean_lines(interface_lines, precursor) == True:
#         if 'Ruckus' in precursor:
#             output_more = ruckus_more_lines(ssh_channel)
#         else:
#             output_more = more_lines(ssh_channel)
#         interface_lines = [line for line in output_more.split('\n') if line.strip()]

def show_interface_all(ssh_channel, precursor) -> dict:
    output_interfaces = send_ssh_no_pagination(ssh_channel, 'show int all')
    interface_lines = [line for line in output_interfaces.split('\n') if line.strip()]
    parse_lines(interface_lines, precursor)

    save_interface()

    return interface_data

