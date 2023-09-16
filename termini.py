#!/usr/bin/env python3

import paramiko
import re
import time
from flask import Flask, request, render_template, jsonify

from modules.load_documentation import load_documentation
from modules.sanitize_output import sanitize_output
from modules.send_ssh_command import send_ssh_command
from modules.show_running_config import show_running_config
from modules.show_ver import show_ver_cisco_ios, show_ver_ruckus_icx

app = Flask(__name__)

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh_channel = []
precursor = [""]
more_tracker = [False]

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

@app.route('/send-command', methods=['POST'])
def send_command():
    if len(ssh_channel) > 0:
        # try:
            data = request.json
            command = data['command']

            output = send_ssh_command(ssh_channel, command)
            print(output)
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

        # except Exception as e:
        #     ssh_channel[0].close()
        #     ssh_client.close()
        #     return jsonify({'error': str(e), 'precursor': precursor[0]})
    else:
        return jsonify({'error': 'no connection found.', 'precursor': precursor[0]}) 

@app.route('/connect', methods=['POST'])
def connect_ssh():

    version_info = {
        'make': '',
        'model': '',
        'model_family': '',
        'software': '',
        'software_version': ''
    }

    documentation = {
        'data_sheet': '',
        'cli_reference': '',
    }

    running_config = {
        'running_config': '',
        'interfaces': []
    }

    hardware = ''
    sanitized_output = ''

    data = request.json
    hostname = data['hostname']
    username = data['username']
    password = data['password']
    
    
    ssh_channel[0] = ssh_invoke_shell(hostname, username, password)

    output = send_ssh_command(ssh_channel, None)
    split_output = output.split("\n")
    precursor[0] = split_output[len(split_output) - 1] 

    try:   
        output_version = send_ssh_command(ssh_channel, 'show version')
        data_sheet = ""
        cli_reference = ""
        if 'ICX' in precursor[0]:
            version_info = show_ver_ruckus_icx()
        elif 'Switch' in precursor[0] and len(output) > 0:
            version_info = show_ver_cisco_ios()
        
        documentation = load_documentation(version_info)

        hardware = f"{version_info['make']} {version_info['model']}"
        send_ssh_command(ssh_channel, " ")

        output_config = send_ssh_command(ssh_channel, 'show running-config')
        running_config = show_running_config(output_config, ssh_channel)
        for i in running_config['interfaces']:
            print(i)
    except:
        print('show version -or- show running-config: failed')

        return jsonify({
            'output': sanitized_output, 
            'precursor': precursor[0], 
            'hardware': hardware, 
            'software': version_info['software'], 
            'data_sheet': documentation['data_sheet'],
            'cli_reference': documentation['cli_reference'],
            'running_config': running_config['running_config'],
            'interfaces': running_config['interfaces']
        })

    # except Exception as e:
    #     ssh_channel[0].close()
    #     ssh_client.close()
    #     return jsonify({'error': str(e), 'precursor': precursor[0]})

@app.route('/reset_connection', methods=['GET'])
def reset_connection():
    if ssh_channel:
        ssh_channel[0].close()
    if ssh_client:
        ssh_client.close()
    return jsonify({'precursor': ''})

@app.route('/')
def index():
    return render_template('termini.html')

if __name__ == '__main__':
    app.run(debug=True)
