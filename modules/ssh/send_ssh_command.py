#!/usr/bin/env python3

import time

def send_ssh_command(ssh_channel, command=None):
    
    if command:
        while not ssh_channel[0].send_ready():
            pass
        if command == "?":
            ssh_channel[0].send(command)
        elif "?" in command:
            ssh_channel[0].send(command)
        elif command.lower() == "exit":
            ssh_channel[0].close()
            output = ["connection terminated...","end of line."]
            return output
        elif command == ' ' or command == '' or command == '\n':
            ssh_channel[0].send(command)
        else:
            ssh_channel[0].send(command + '\n')

    time.sleep(0.1) 
    while not ssh_channel[0].recv_ready():
        pass
        
    output = ssh_channel[0].recv(65535).decode('utf-8')
    if '\r' in output:
        split_info = output.split('\r', 1)
        output = split_info[1]

    return output

    # except Exception as e:
    #     print("An error occurred:", e)
    #     ssh_channel[0].close()
    #     ssh_client.close()