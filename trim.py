#!/usr/bin/env python2
"""Trim the padding bytes which is added by Nightmare 2.

Usage:
    `python trim.py files [files ...]`
    
You can also drag and drop the modified files to this script.
"""

import argparse
from struct import unpack

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+', help='input files.')
    args = parser.parse_args()

    for file in args.files:
        with open(file, 'r+b') as f:
            size = unpack('<I', f.read(4))[0]
            f.seek(0)
            f.truncate(size)
