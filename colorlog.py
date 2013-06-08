#!/usr/bin/env python

import re, sys

BLACK = '30'
RED = '31'
GREEN = '32'
YELLOW = '33'
BLUE = '34'
MAGENTA = '35'
CYAN = '36'
GRAY = '37'

def colorize_line(line, fg_color, bright):
    prefix = '\x1b['
    suffix = 'm'
    brightness = '1' if bright else '0'
    return prefix + brightness + ';' + str(fg_color) + suffix + line + prefix + suffix

if __name__ == '__main__':
    rules = [
        (re.compile('TRACE'), GRAY, False),
        (re.compile('INFO'), GREEN, True),
        (re.compile('WARN'), YELLOW, True),
        (re.compile('DEBUG'), CYAN, True),
        (re.compile('ERROR'), RED, True),
        (re.compile('FATAL'), MAGENTA, True),
    ]
    for line in sys.stdin:
        for regex, col, bright in rules:
            if regex.search(line) is not None:
                line = colorize_line(line, col, bright)
                break
        sys.stdout.write(line)
