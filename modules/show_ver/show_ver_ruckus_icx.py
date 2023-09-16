#!/usr/bin/env python3

def show_ver_ruckus_icx(output_version):
    version_info = {
        'make': '',
        'model': '',
        'model_family': '',
        'software': '',
        'software_version': ''
    }
    split_version = output_version.split("\n")
    for i in split_version:
        if "(c)" in i:
            split_i = (i.strip()).split(" ")
            make = split_i[2]
            version_info['make'] = make
        if "HW: " in i:
            split_i = (i.strip()).split(" ")
            model = split_i[2]
            version_info['model'] = model
            split_model = model.split('-')
            version_info['model_family'] = split_model[0]
        if "SW: " in i:
            split_i = (i.strip()).split(" ")
            version_info['software'] = f"Software: {split_i[2]}"
            split_software = (split_i[2]).split('-')
            version_info['software_version'] = split_software[0]
    
    return version_info