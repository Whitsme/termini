#!/usr/bin/env python3

import time

def send_ssh_command(ssh_channel, command=None):
    
    if command:
        if command == "?":
            ssh_channel[0].send(command)
        elif "?" in command:
            ssh_channel[0].send(command)
        elif command.lower() == "exit":
            ssh_channel[0].close()
            ssh_client.close()
            port_info = ["connection terminated...","end of line."]
            return port_info
        elif command == ' ' or command == '':
            ssh_channel[0].send(command)
        else:
            ssh_channel[0].send(command + '\n')

    time.sleep(0.1) 
    while not ssh_channel[0].recv_ready():
        pass
        
    port_info = ssh_channel[0].recv(8192).decode('utf-8')
    if '\r' in port_info:
        split_info = port_info.split('\r', 1)
        port_info = split_info[1]

    return port_info

    # except Exception as e:
    #     print("An error occurred:", e)
    #     ssh_channel[0].close()
    #     ssh_client.close()