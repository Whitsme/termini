#!/usr/bin/env python3

import re

from modules.ssh import send_ssh_no_pagination

interface_data = []
details_header = "Port     Name       Status  Config-mode   Speed    Type       Tagged Untagged\n-------- ---------- ------- ------------- -------- ---------- ------ --------\n"

def parse_lines(interface_lines, precursor) -> None:
    for line in interface_lines:
        if precursor in line:
            break
        clean_line = line.replace('"', '\\"').replace('\r', '').strip()
        split_line = clean_line.split()
        if '--' != split_line[0]:
            this_port = {}
            try:
                split_line[0] == int(split_line[0])
                print(split_line)
                this_port = {}
                this_port['port'] = f"1/0/{split_line[0]}"
                this_port['type'] = "GbE"
                this_port['status'] = split_line[1]
                this_port['details'] = f"{details_header}{clean_line}"

            except:
                if len(str(split_line[0])) < 4:
                    print(split_line)
                    this_port = {}
                    this_port['port'] = f"1/1/{split_line[0]}"
                    this_port['type'] = "10 GbE"
                    this_port['status'] = split_line[1]
                    this_port['details'] = f"{details_header}{clean_line}"

            if len(this_port) > 0:
                interface_data.append(this_port)


def show_int_status(ssh_channel, precursor, no_pagination_cmd) -> dict:
    output_interfaces = send_ssh_no_pagination(ssh_channel, 'show int status\n', precursor, no_pagination_cmd)

    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output_interfaces = ansi_escape.sub('', output_interfaces)

    interface_lines = [line for line in output_interfaces.split('\n') if line.strip()]
    parse_lines(interface_lines, precursor)

    return interface_data