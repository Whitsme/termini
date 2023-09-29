#!/usr/bin/env python3

import time

def send_ssh_no_pagination(ssh_channel, command, precursor, no_pagination_cmd) -> str:
    ssh_channel[0].setblocking(0)

    # waits for channel to be send ready, then sends command to turn off pagination
    while not ssh_channel[0].send_ready():
        pass
    ssh_channel[0].sendall(no_pagination_cmd[0])
    time.sleep(0.1)
    # waits for the channel to receive ready, then requests output from command
    while not ssh_channel[0].recv_ready():
        pass
    response = ssh_channel[0].recv(65535).decode('utf-8')

    # waits for channel to be send ready, then sends 'command' argument
    while not ssh_channel[0].send_ready():
        pass
    ssh_channel[0].sendall(command)
    time.sleep(0.1)
    # waits for the channel to receive ready, then requests output from command
    while not ssh_channel[0].recv_ready():
        pass
    output = ssh_channel[0].recv(65535).decode('utf-8')

    """loop to get all output received from sending the 'command' argument"""
    while precursor not in output:
        command = ' '
        # waits for channel to be send ready, then sends command for more output:' '
        while not ssh_channel[0].send_ready():
            pass
        ssh_channel[0].sendall(command)
        time.sleep(0.1)
        # waits for the channel to receive ready, then requests output from command
        while not ssh_channel[0].recv_ready():
            pass
        output += ssh_channel[0].recv(65535).decode('utf-8')

    # waits for channel to be send ready, then sends command to turn back on pagination
    while not ssh_channel[0].send_ready():
        pass
    ssh_channel[0].sendall(no_pagination_cmd[1])
    time.sleep(0.1)
    # waits for the channel to receive ready, then requests output from command
    while not ssh_channel[0].recv_ready():
        pass
    response = ssh_channel[0].recv(65535).decode('utf-8')

    ssh_channel[0].setblocking(1)

    return output
