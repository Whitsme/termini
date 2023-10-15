#!/usr/bin/env python3

import re
import json
import paramiko
from flask import Flask, request, render_template, jsonify

from modules.aruba.show_commands import aruba_show_running_config, show_int_status, show_lldp_info, show_modules, show_system
from modules.ssh import send_ssh_command
from modules.show_commands import (show_interface, show_lldp_neighbors, show_running_config, show_version)

app = Flask(__name__)

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh_channel = []
precursor = [""]
more_tracker = [False]
no_pagination_cmd = ["", ""]

def ssh_invoke_shell(hostname, username, password):
    ssh_client.connect(
        hostname=hostname,
        username=username,
        password=password,
        allow_agent=False,
        look_for_keys=False
    )
    ssh_channel.append(ssh_client.invoke_shell())
    return ssh_channel[0]

def ssh_invoke_background_shell(hostname, username, password):
    ssh_client.connect(
        hostname=hostname,
        username=username,
        password=password,
        allow_agent=False,
        look_for_keys=False
    )
    ssh_channel.append(ssh_client.invoke_shell())
    return ssh_channel[1]
    # ssh_background_channel = ssh_client.get_transport().open_session()
    # ssh_background_channel.exec_command('echo "Background channel started."')
    # while ssh_background_channel.recv_ready():
    #     print(ssh_background_channel.recv(1024).decode('utf-8'))

def sanitize_output(output, precursor):
    output_lines = []
    lines = [line for line in output.split('\n') if line.strip()]
    for line in lines:
        if line != precursor[0]:
            line.replace('"', '\\"').replace('\r', '')
            output_lines.append(f"{line}")
    output = ''.join(output_lines)
    return output

@app.route('/send-command', methods=['POST'])
def send_command():
    if len(ssh_channel) > 0:
        data = request.json
        command = data['command']

        output = send_ssh_command(ssh_channel, command)
        split_output = output.split("\n")

        precursor_text = split_output[len(split_output) - 1] 
        if ">" in precursor_text:
            precursor[0] = precursor_text
            more_tracker[0] = False
        elif "#" in precursor_text:
            precursor[0] = precursor_text
            more_tracker[0] = False
        sanitized_output = sanitize_output(output, precursor)

        return jsonify({'output': sanitized_output, 'precursor': precursor[0]})

    else:
        return jsonify({'error': 'no connection found.', 'precursor': precursor[0]}) 

@app.route('/connect', methods=['POST'])
def connect_ssh():

    hardware = ''
    interfaces = ''
    # documentation = {
    #     'data_sheet': '',
    #     'cli_reference': ''
    # }
    running_config = ''
    version_info = {
        'make': '',
        'model': '',
        'model_family': '',
        'software': '',
        'software_version': ''
    }

    data = request.json
    hostname = data['hostname']
    username = data['username']
    password = data['password']
       
    ssh_channel[0] = ssh_invoke_shell(hostname, username, password)
    ssh_channel[0].set_name('user_channel')
    # ssh_channel[1] = ssh_invoke_background_shell(hostname, username, password)
    # ssh_channel[1].set_name('automated_channel')

    print(f"\n{ssh_channel[0].get_id}\n") 

    no_pagination_cmd[0] = 'terminal length 0\n'
    no_pagination_cmd[1] = 'terminal length 24\n'

    output = send_ssh_command(ssh_channel, None)
    if 'ICX' not in output:
        while '#' not in output:
            output = send_ssh_command(ssh_channel, ' ')
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            output = ansi_escape.sub('', output)

    split_output = output.split("\n")
    if 'ICX' in split_output[len(split_output) - 1].strip():
        no_pagination_cmd[0] = 'skip\n'
        no_pagination_cmd[1] = 'page\n'
        if ssh_channel[0].send_ready():
            ssh_channel[0].send('enable\n')
        while not ssh_channel[0].recv_ready():
            pass
        split_output = (ssh_channel[0].recv(8192).decode('utf-8')).split("\n")
        
    precursor[0] = split_output[len(split_output) - 1].strip() 

    print(precursor[0])
    
    if 'Aruba' not in precursor[0]:
        version_info = show_version(ssh_channel, precursor[0], no_pagination_cmd)
        hardware = f"{version_info['make']} {version_info['model']}"
    else:
        no_pagination_cmd[0] = 'no paging\n'
        no_pagination_cmd[1] = 'paging\n'
        version_info = show_system(ssh_channel, precursor[0], no_pagination_cmd)
        hardware = show_modules(ssh_channel, precursor[0], no_pagination_cmd)

    return jsonify({
        'precursor': precursor[0], 
        'hardware': hardware, 
        'software': version_info['software']
    })

@app.route('/known_hosts', methods=['GET'])
def known_hosts():
    known_hosts_path = r'C:\Users\aaron.whitaker\Documents\misc\networking\known_hosts.json'  
    try:
        with open(known_hosts_path, 'r') as known_hosts_json:
            known_hosts = json.load(known_hosts_json)
        return jsonify(known_hosts)
    except FileNotFoundError:
        print('json file not found')
        return jsonify({"known_hosts.json not found.": "JSON file not found"})
    except Exception as e:
        print('error' + str(e))
        return jsonify({"error": str(e)})

@app.route('/show_configuration', methods=['POST'])
def show_configuration():
    if "Aruba" not in precursor[0]:
        running_config = show_running_config(ssh_channel, precursor[0], no_pagination_cmd)
    else: 
        running_config = aruba_show_running_config(ssh_channel, precursor[0], no_pagination_cmd)
    if running_config:
        return jsonify({
            'running_config': str(running_config['running_config']),
            'tagged_vlan': running_config['tagged_vlan'],
            'untagged_vlan': running_config['untagged_vlan']
            })
    return jsonify({
            'running_config': 'error'
        })

@app.route('/show_interfaces', methods=['POST'])
def send_show_interfaces():
    if "Aruba" not in precursor[0]:
        interfaces = show_interface(ssh_channel, precursor[0], no_pagination_cmd)
    else:
        interfaces = show_int_status(ssh_channel, precursor[0], no_pagination_cmd)
    if interfaces:
        return jsonify({
            'interfaces': interfaces
        })
    return jsonify({
            'interfaces': 'error'
        })

@app.route('/show_lldp_neighbors', methods=['POST'])
def send_show_lldp_neighbors():
    if "Aruba" not in precursor[0]:
        lldp_neighbors = show_lldp_neighbors(ssh_channel, precursor[0], no_pagination_cmd)
    else:
        lldp_neighbors = show_lldp_info(ssh_channel, precursor[0], no_pagination_cmd)
    if lldp_neighbors:
        return jsonify({
            'lldp_neighbors': lldp_neighbors
        })
    return jsonify({
            'lldp_neighbors': 'error'
        })

# @app.route('/reset_connection', methods=['GET'])
# def reset_connection():
#     if ssh_channel:
#         ssh_channel[0].close()
#     if ssh_client:
#         ssh_client.close()
#     return jsonify({'precursor': ''})

@app.route('/')
def index():
    return render_template('termini.html')

if __name__ == '__main__':
    app.run(debug=True)
