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

class RuleProcessor:
    def __init__(self, rules):
        self.rulemap = dict()
        for keyword, color, bright in rules:
            self.rulemap[keyword] = (color, bright)
        self.regex = re.compile('(' + '|'.join(self.rulemap.keys()) + ')')
    
    def process_line(self, line):
        m = self.regex.search(line)
        if m is None:
            return line
        keyword = m.group()
        color, bright = self.rulemap[keyword]
        return colorize_line(line, color, bright)
    
    def process_stream(self, input, output):
        for line in input:
            line = self.process_line(line)
            output.write(line)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-L', '--less', action='store_true', help="view output in less (pipe to 'less -R')")
    parser.add_argument('files', nargs='*', help='files to read (if empty, read standard input)')
    args = parser.parse_args()
    processor = RuleProcessor([
        ('TRACE', GRAY, False),
        ('INFO', GREEN, True),
        ('WARN', YELLOW, True),
        ('DEBUG', CYAN, True),
        ('ERROR', RED, True),
        ('FATAL', MAGENTA, True),
    ])
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
                    processor.process_stream(f, output)
        else:
            processor.process_stream(sys.stdin, output)
    except IOError as e:
        if e.errno == errno.EPIPE:
            # ignore broken pipe errors
            pass
        else:
            raise
    if process is not None:
        process.stdin.close()
        process.wait()
