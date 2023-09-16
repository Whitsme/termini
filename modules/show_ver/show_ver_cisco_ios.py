#!/usr/bin/env python3

def show_ver_cisco_ios(output_version):
    version_info = {
        'make': '',
        'model': '',
        'model_family': '',
        'software': '',
        'software_version': ''
    }
    split_version = output_version.split("\n")
    for i in split_version:
        if "Software, Version" in i:
            split_i = (i.strip()).split(" ")
            version_info['software'] = f"Software: {split_i[1]} {split_i[2]} v{split_i[5]}"
            split_software = (split_i[5]).split('.')
            version_info['software_version'] = f"{split_i[1]} {split_i[2]} {split_software[0]}.{split_software[1]}"
    interactive_ssh(' ', ssh_channel)
    output_hardware = interactive_ssh(' ', ssh_channel)
    split_hardware = output_hardware.split("\n")
    for i in split_hardware:
        if "cisco" in i and "processor" in i:
            split_i = (i.strip()).split(" ")
            version_info['make'] = split_i[0]
            hardware[0] = make
            version_info['model'] = split_i[1]
            hardware[1] = model
            split_model = model.split('-')
            version_info['model_family'] = split_model[1]

    return version_info