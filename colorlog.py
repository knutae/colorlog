#!/usr/bin/env python

import re, sys, argparse, subprocess, errno

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

def colorize_stream(rules, input, output):
    for line in input:
        for regex, col, bright in rules:
            if regex.search(line) is not None:
                line = colorize_line(line, col, bright)
                break
        output.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-L', '--less', action='store_true', help="view output in less (pipe to 'less -R')")
    parser.add_argument('files', nargs='*', help='files to read (if empty, read standard input)')
    args = parser.parse_args()
    rules = [
        (re.compile('TRACE'), GRAY, False),
        (re.compile('INFO'), GREEN, True),
        (re.compile('WARN'), YELLOW, True),
        (re.compile('DEBUG'), CYAN, True),
        (re.compile('ERROR'), RED, True),
        (re.compile('FATAL'), MAGENTA, True),
    ]
    process = None
    if args.less:
        process = subprocess.Popen(['less', '-R'], stdin=subprocess.PIPE)
        output = process.stdin
    else:
        output = sys.stdout
    try:
        if len(args.files) > 0:
            for fname in args.files:
                with open(fname) as f:
                    colorize_stream(rules, f, output)
        else:
            colorize_stream(rules, sys.stdin, output)
    except IOError as e:
        if e.errno == errno.EPIPE:
            # ignore broken pipe errors
            pass
        else:
            raise
    if process is not None:
        process.stdin.close()
        process.wait()
