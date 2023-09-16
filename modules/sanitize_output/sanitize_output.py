#!/usr/bin/env python3

def sanitize_output(output, precursor):
    output_lines = []
    lines = [line for line in output.split('\n') if line.strip()]
    for line in lines:
        if line != precursor[0]:
            line.replace('"', '\\"').replace('\r', '')
            output_lines.append(f"{line}")
    output = ''.join(output_lines)
    return output