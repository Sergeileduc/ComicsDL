#!/usr/bin/python3
# -*-coding:utf-8 -*-

import re
from urllib.parse import unquote

from utils.tools import searchRegex, searchRegexName


# Regex to detect name, (year) (tag).extension
regex_tag = r"(.+)(\ \([1|2][9|0]\d{2}\))(.*)(\..{3})"

regex_first = r'.*?getElementById.*?href = \"(?P<first>.*?)\"'

regex_abcd = (r'.*?getElementById.*?href = \"(.*?)\"'
              r' \+ \((?P<a>\d+) \% (?P<b>\d+) \+ (?P<c>\d+) \% (?P<d>\d+)\)')

regex_rawname = r'.*?getElementById.*?href = \".*?\" \+ \(.*?\) \+ \"(.*?)\"'


def _removetag(filename):
    if re.match(regex_tag, filename):
        # print("match")
        return re.sub(regex_tag, r"\1\2\4", filename)
    else:
        return filename


def getFileUrl(url, button):
    print("Found zippyshare : " + url)
    first_part = searchRegexName(button, regex_first, 'first')
    a = int(searchRegexName(button, regex_abcd, 'a'))
    b = int(searchRegexName(button, regex_abcd, 'b'))
    c = int(searchRegexName(button, regex_abcd, 'c'))
    d = int(searchRegexName(button, regex_abcd, 'd'))

    raw_name = searchRegex(button, regex_rawname, 1)
    # temp = replace(raw_name[1:], substitutions)
    # filename = _removetag(temp)
    filename = _removetag(unquote(raw_name).strip('/'))
    # Calculating the id and forming url
    # that is an extremely dirty way, I know
    second_part = a % b + c % d
    fullURL = url[:-21] + first_part + str(second_part) + raw_name
    print(fullURL)
    return fullURL, filename
