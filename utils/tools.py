#!/usr/bin/python3
# -*-coding:utf-8 -*-
"""Module for various tools."""

import re

defs = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}


# Convert to bytes
def convert2bytes(size):
    """Convert size string with unit into bytes."""
    parts = size.split()
    size = parts[0]
    unit = parts[1]
    return int(size) * defs[unit]


# Convert with corret unit
def bytes_2_human_readable(number_of_bytes):
    """Convert bytes (int) into readable string with unit."""
    if number_of_bytes < 0:
        raise ValueError("!!! number_of_bytes can't be smaller than 0 !!!")

    step_to_greater_unit = 1024.

    number_of_bytes = float(number_of_bytes)
    unit = 'bytes'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'KB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'MB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'GB'

    if (number_of_bytes / step_to_greater_unit) >= 1:
        number_of_bytes /= step_to_greater_unit
        unit = 'TB'

    precision = 1
    number_of_bytes = round(number_of_bytes, precision)

    return f'{number_of_bytes} {unit}'


def search_regex(html, regex, n):
    """Regex search."""
    url_pattern = re.compile(regex, re.MULTILINE | re.IGNORECASE)
    return url_pattern.search(str(html)).group(n)


def search_regex_name(html, regex, name):
    """Regex search with group name."""
    url_pattern = re.compile(regex, re.MULTILINE | re.IGNORECASE)
    return url_pattern.search(str(html)).group(name)
