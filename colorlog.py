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

LINE_SUFFIX = '\x1b[m'

def line_prefix(fg_color, bright):
    brightness = '1' if bright else '0'
    return '\x1b[' + brightness + ';' + str(fg_color) + 'm'

class RuleProcessor:
    def __init__(self, rules):
        self.prefixmap = dict()
        for keyword, color, bright in rules:
            self.prefixmap[keyword] = line_prefix(color, bright)
        self.regex = re.compile('(' + '|'.join(self.prefixmap.keys()) + ')')
    
    def process_line(self, line, output):
        m = self.regex.search(line)
        if m is None:
            output.write(line)
            return
        keyword = m.group()
        output.write(self.prefixmap[keyword] + line + LINE_SUFFIX)
    
    def process_stream(self, input, output):
        # the following provides better streaming behavior (less buffering) than "for line in input"
        for line in iter(input.readline, ''):
            self.process_line(line, output)

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
