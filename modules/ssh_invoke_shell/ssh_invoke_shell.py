#!/usr/bin/env python3

def ssh_invoke_shell(hostname, username, password, ssh_client):
    ssh_client.connect(
        hostname=hostname,
        username=username,
        password=password,
        allow_agent=False,
        look_for_keys=False
    )
    ssh_channel = ssh_client.invoke_shell()
    return ssh_channel