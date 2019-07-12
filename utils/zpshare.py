#!/usr/bin/python3
# -*-coding:utf-8 -*-

import re

# Subistitions for getcomics
substitutions = {'%2c': '', '%20': ' ', '%28': '(',
                 '%29': ')', '%27': '\'', '%26': '&'}

# Regex to detect name, (year) (tag).extension
regex_tag = r"(.+)(\ \([1|2][9|0]\d{2}\))(.*)(\..{3})"

regex_first = r'.*?getElementById.*?href = \"(.*?)\"'

regex_abcd = (r'.*?getElementById.*?href = \"(.*?)\"'
              r' \+ \((\d+) \% (\d+) \+ (\d+) \% (\d+)\)')

regex_rawname = r'.*?getElementById.*?href = \".*?\" \+ \(.*?\) \+ \"(.*?)\"'


# Multiple replace function
def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)


def removetag(filename):
    if re.match(regex_tag, filename):
        # print("match")
        return re.sub(regex_tag, r"\1\2\4", filename)
    else:
        return filename


# Just optimizing
def searchRegex(html, regex, n):
    try:
        urlPattern = re.compile(regex, re.MULTILINE | re.IGNORECASE)
        return urlPattern.search(str(html)).group(n)
    except Exception as e:
        print(e)
        print("Cant't regex html")


def getFileUrl(url, button):
    print("Found zippyshare : " + url)
    first_part = searchRegex(button, regex_first, 1)
    a = int(searchRegex(button, regex_abcd, 2))
    b = int(searchRegex(button, regex_abcd, 3))
    c = int(searchRegex(button, regex_abcd, 4))
    d = int(searchRegex(button, regex_abcd, 5))

    raw_name = searchRegex(button, regex_rawname, 1)
    temp = replace(raw_name[1:], substitutions)
    filename = removetag(temp)
    # Calculating the id and forming url
    # that is an extremely dirty way, I know
    try:
        second_part = a % b + c % d
        fullURL = url[:-21] + first_part + str(second_part) + raw_name
        print(fullURL)
    except Exception as e:
        print("Mon erreur")
        print(e)
        raise
    return fullURL, filename
