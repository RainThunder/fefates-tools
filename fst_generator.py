#!/usr/bin/env python2
#
# The MIT License
#
# Copyright (c) 2016 RainThunder.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

"""Generate fst.bin for Fire Emblem If / Fates DLC. fst.bin basically is
a file list, contains the paths of all files except itself in a DLC's RomFS.

Usage:
    python fst_generator.py dir

with `dir` is path to the DLC's RomFS folder. Alternatively, you can drag and
drop that folder to this script. A new fst.bin file will automatically be
generated inside that folder.
"""

import os
import sys
from struct import pack, unpack, pack_into
if sys.version_info[0] > 2:
    xrange = range
    unicode = str

try:
    import bin
    standalone = False
except ImportError:
    standalone = True


class Fst(bin.BinFile):
    """Fst.bin file class."""
    def __init__(self, header=None, raw=None):
        super(Fst, self).__init__(header, raw)

    def construct(self, file_list):
        """Construct fst.bin file."""
        # Add file names to label region.
        offsets = []
        total_length = 0
        for filename in file_list:
            offsets.append(total_length)
            total_length += len(filename) + 1
        self._labels = b'\0'.join([f.encode('shift-jis') for f in file_list])\
            + b'\0'

        # Data and pointer 1
        data_length = 4 + len(file_list) * 4 # = p1_offset
        label_offset = data_length + len(file_list) * 4
        data = bytearray(b'\0' * data_length)
        self._p1_list = []
        pack_into('<I', data, 0, len(file_list))
        for i in xrange(len(file_list)):
            pack_into('<I', data, 0x4 + i * 4, label_offset + offsets[i])
            self._p1_list.append(0x4 + i * 4)
        self._data = bytes(data)


def generate(path):
    """Generate fst.bin file using bin module."""
    # List all file in the directory
    file_list = []
    root_name = unicode(path)
    for dirpaths, dirnames, filenames in os.walk(unicode(path)):
        for filename in filenames:
            if filename == u'fst.bin':
                continue
            if dirpaths != root_name:
                label = dirpaths.replace(root_name + os.sep, '').replace(os.sep, u'/') + u'/' + filename
            else:
                label = filename
            file_list.append(label)

    # Construct the file/
    fst = Fst()
    fst.construct(file_list)
    fst_file = open(os.path.join(unicode(path), u'fst.bin'), 'wb')
    fst_file.write(fst.tobin())
    fst_file.close()

def generate_standalone(path):
    """Generate fst.bin file. No module import needed."""
    labels = []
    name_offsets = []
    total_length = 0
    root_name = unicode(path)
    for dirpaths, dirnames, filenames in os.walk(unicode(path)):
        for filename in filenames:
            if filename == u'fst.bin':
                continue
            if dirpaths != root_name:
                label = (dirpaths.replace(root_name + os.sep, '')\
                    .replace(os.sep, u'/') + u'/' + filename)\
                    .encode('shift-jis')
            else:
                label = filename.encode('shift-jis')
            name_offsets.append(total_length)
            labels.append(label)
            total_length += len(filepath) + 1

    file_count = len(name_offsets)
    label0_offset = 4 + file_count * 8
    with open(os.path.join(unicode(path), u'fst.bin'), 'wb') as fst_file:
        fst_file.write(
            # Header
            pack('<4I', 0x24 + file_count * 8 + len(labels),
                 4 + file_count * 4, file_count, 0) +
            '\0' * 16 + # padding

            # Data
            pack('<I', file_count) +
            b''.join([pack('<I', label0_offset + offset) for offset in name_offsets]) +

            # Pointer 1
            b''.join([pack('<I', ptr) for ptr in xrange(4, 4 + file_count * 4, 4)]) +

            # Labels
            b'\0'.join(labels) + b'\0'
        )


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='input folder')
    args = parser.parse_args()

    if not os.path.isdir(unicode(args.path)):
        print(args.path + ': No such directory.')
        exit()

    if standalone:
        generate_standalone(args.path)
    else:
        generate(args.path)
    print('fst.bin generated.')
