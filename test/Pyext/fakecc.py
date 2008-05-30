fakecmd = r"""
#! /usr/bin/env python

# Fake compiler : can handle posix style and windows style basic arguments, and
# filter out NOKEEP line
import sys
import re

WIN_CFLAG = re.compile('/[Cc]')
# Match any alphanumeric + .
WIN_OFLAG = re.compile('/Fo([\w\.]*)')
WIN_OPTFLAG = re.compile('/O([\w]*)')
WIN_WARNFLAG = re.compile('/W([\w]*)')

POSIX_CFLAG = re.compile('-c')
POSIX_OFLAG = re.compile('-o')
POSIX_OPTFLAG = re.compile('-O(\d*)')
POSIX_WARNFLAG = re.compile('-W([\w]*)')
POSIX_PIC = re.compile('-[\w]PIC')
POSIX_INCLUDE = re.compile('-I[\S]+')

args = sys.argv[1:]

NOKEEP = @NOKEEP@

def ignore_flag_win32(flag):
    for f in [WIN_OPTFLAG, WIN_WARNFLAG, WIN_CFLAG]:
        if f.match(flag):
            return True
    return False

def parse_win32(args):
    output = None
    input = None

    while len(args) > 0:
        a = args[0]
        if ignore_flag_win32(a):
            pass
        elif WIN_OFLAG.search(a):
            output = WIN_OFLAG.search(a).group(1)
            #output = args[1]
        elif a[0] == '/':
            raise ValueError("Option %s not understood" % a)
        else:
            input = a
        args = args[1:]

    return output, input

def parse_posix(args):
    output = None
    input = None

    while len(args) > 0:
        a = args[0]
        if ignore_flag_posix(a):
            pass
        elif POSIX_OFLAG.search(a):
            output = args[1]
            args = args[1:]
        elif a[0] == '-':
            raise ValueError("Option %s not understood" % a)
        else:
            input = a
        args = args[1:]

    if output is None:
        raise ValueError("No output ?")
    if input is None:
        raise ValueError("No input ?")
    return output, input

def ignore_flag_posix(flag):
    for f in [POSIX_OPTFLAG, POSIX_WARNFLAG, POSIX_CFLAG, POSIX_PIC, POSIX_INCLUDE]:
        if f.match(flag):
            return True
    return False

if sys.platform == 'win32':
    output, input = parse_win32(args)
else:
    output, input = parse_posix(args)

o = open(output, 'w')
for line in open(input).readlines():
    if not line[:len(NOKEEP)] == NOKEEP:
        o.write(line)

sys.exit(0)
"""
