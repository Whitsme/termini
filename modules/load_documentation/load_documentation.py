#!/usr/bin/env python3

import json

def load_documentation(version_info):

    documentation = {
        'data_sheet': '',
        'cli_reference': '',
    }

    with open('static/json/devices.json', 'r') as devices_file:
        data = json.load(devices_file)
        if version_info['model_family'] in data[version_info['make'].lower()]:
            documentation['data_sheet'] = data[version_info['make'].lower()][version_info['model_family']]
        if version_info['software_version'] in data[version_info['make'].lower()]:
            documentation['cli_reference'] = data[version_info['make'].lower()][version_info['software_version']]

    return documentation