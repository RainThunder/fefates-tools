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
"""A library for manipulating GameData.bin file in Fire Emblem Fates."""

from __future__ import print_function, unicode_literals
import sys
from collections import namedtuple
from struct import unpack, pack, pack_into
if sys.version_info[0] > 2:
    unicode = str
    xrange = range

import bin


class GameData(bin.BinFile):
    """GameData class."""

    __ptr_info = {
        'Chapter': [(0x0, 'CID')], # No map model (Btl_) support.
        'Character': [(0x8, 'PID'), (0xC, 'FID'), (0x10, 'AID'), (0x14, 'MPID'),
            (0x18, 'MPID_H')],
        'Class': [(0x8, 'JID'), (0xC, 'FID'), (0x10, 'MJID'), (0x14, 'MJID_H')],
        'Skill': [(0x0, 'SEID'), (0x4, 'MSEID'), (0x8, 'MSEID_H')],
        'Stat': [(0x0, 'MID'), (0x4, 'MID_H')],
        'Army': [(0x4, 'BID'), (0x8, 'BID_H')],
        'Item': [(0x8, 'IID'), (0xC, 'MIID'), (0x10, 'MIID_H')],
        'Tutorial': [(0x0, 'TUTID'), (0x8, 'MTUTID'), (0xC, 'MTUTID_H')]
    }

    def __init__(self, header, raw):
        super(GameData, self).__init__(header, raw)

    def get_table_info(self, table_name):
        """Get info of the table_name."""
        TableInfo = namedtuple('TableInfo', ['offset', 'count_offset', 'size',
                                             'id_offset', 'id_size'])
        if table_name == 'Chapter':
            offset = unpack('<I', self._data[:0x4])[0]
            return TableInfo._make((offset, 0x8, 0x1C, 0x4, 1, 0))
        elif table_name == 'Character':
            offset = unpack('<I', self._data[0x8:0xC])[0]
            return TableInfo._make((offset + 0x10, offset + 0x4, 0x98, 0x24, 2))
        elif table_name == 'Support':
            offset = unpack('<I', self._data[0x8:0xC])[0]
            offset = unpack('<H', self._data[offset + 0x8:offset + 0xA])[0]
            return TableInfo_make((offset, None, None, None, None))
        elif table_name == 'Class':
            offset = unpack('<I', self._data[0xC:0x10])[0]
            return TableInfo._make((offset + 0x8, offset + 0x6, 0x80, 0x18, 2))
        elif table_name == 'Skill':
            offset = unpack('<I', self._data[0x10:0x14])[0]
            return TableInfo._make((offset + 0x10, 0x18, 0x20, 0x10, 2))
        elif table_name == 'Stat':
            offset = unpack('<I', self._data[0x1C:0x20])[0]
            return TableInfo._make((offset, 0x20, 0x40, 0x0, 1))
        elif table_name == 'Army':
            offset = unpack('<I', self._data[0x24:0x28])[0]
            return TableInfo._make((offset, 0x28, 0x10, 0x0, 1))
        elif table_name == 'Item':
            offset = unpack('<I', self._data[0x2C:0x30])[0]
            return TableInfo._make((offset + 0x8, offset + 0x6, 0x68, 0x14, 2))
        elif table_name == 'Tutorial':
            offset = unpack('<I', self._data[0x8:0xC])[0]
            return TableInfo._make((offset + 0x10, offset + 0x6, 0x14, 0x0, 1))
        else:
            raise ValueError('Unsupported table name.')

    def append(self, data_type, ids, names):
        """Create and append new data to this file.

        Parameters:
        ``data_type``: 'Chapter', 'Character', 'Class', 'Item', etc.
        ``ids``: A list of new IDs for the new data.
        ``names``: A list of new names for the new data. Unicode strings are
            supported.
        """
        if not isinstance(names, list):
            raise ValueError('names must be a list.')
        if len(names) == 0:
            raise ValueError('names must not be empty.')

        info = self.get_table_info(data_type)
        count = len(names)
        old_count = unpack('<H', self._data[info.count_offset:
                                            info.count_offset + 2])[0]
        end_offset = info.offset + info.size * old_count  # Insert position
        data_diff = info.size * count                     # Data diff
        ptr_info = self.__ptr_info[data_type]                  # Get pointer info
        p1_diff = len(ptr_info) * count                   # Pointer 1 diff
        p2_diff = data_diff + p1_diff * 4 + count * 8     # Label offset diff
        old_label0_offset = self.label0_offset            # Old label offset
        label0_offset = old_label0_offset + p2_diff       # New label offset

        # Create new data
        new_data = bytearray(b'\0' * data_diff)
        new_labels = []         # List of new labels, in Shift-JIS encoding
        total_length = 0
        label_end_offset = len(self._labels)
        main_label_offsets = [] # Used for adding pointers to pointer region 2

        for i in xrange(count):
            # Label and pointers
            main_label_offsets.append(label_end_offset)
            for j in xrange(len(ptr_info)):
                label_ptr = label0_offset + len(self._labels) + len(new_labels)
                offset = info.size * i + ptr_info[j][0]
                pack_into('<I', new_data, offset, label_ptr)
                new_labels.append((ptr_info[j][1] + '_' + names[i])
                                   .encode('shift-jis'))
                total_length += len(new_labels[j]) + 1
            label_end_offset += total_length # Update

            # Assign a new ID
            offset = info.size * i + info.id_offset
            if info.id_size == 1:
                new_data[offset] = ids[i]
            elif info.id_size == 2:
                pack_into('<H', new_data, offset, ids[i])

        # Fix pointer region 1
        data = bytearray(self._data)
        for ptr_index in xrange(len(self._p1_list)):
            p1_ptr = self._p1_list[ptr_index]
            if p1_ptr > end_offset:
                self._p1_list[ptr_index] += data_diff
            ptr = unpack('<I', self._data[p1_ptr:p1_ptr + 4])[0]
            if ptr > end_offset and ptr < old_label0_offset:        # Sub-table
                pack_into('<I', data, p1_ptr, ptr + data_diff)
            elif ptr > old_label0_offset:                           # Label
                pack_into('<I', data, p1_ptr, ptr + p2_diff)

        # Append data
        pack_into('<H', data, info.count_offset, old_count + count)
        self._data = bytes(data[:end_offset]) + bytes(new_data) + \
            bytes(data[end_offset:])

        # Append pointer 1
        for i in xrange(count):
            for ptr in ptr_info:
                self._p1_list.append(end_offset + info.size * i + ptr[0])

        # Fix pointer region 2
        for ptr_index in xrange(len(self._p2_list)):
            data_ptr, label_ptr = self._p2_list[ptr_index]
            if data_ptr > end_offset:
                self._p2_list[ptr_index] = (data_ptr + data_diff, label_ptr)
            else:
                self._p2_list[ptr_index] = (data_ptr, label_ptr)

        # Append pointer region 2
        # The second part of pointer 2 is always pointed to the "main" label.
        for i in xrange(count):
            self._p2_list.append((end_offset + info.size * i, main_label_offsets[i]))

        # Append labels
        self._labels += b'\0'.join([l for l in new_labels]) + b'\0'

        # At this point, the file is already usable, but we would like to make
        # it properly just like the original.
        # self.format()


def load_file(path):
    """Load a bin file to a bin object.

    Parameters,
    ``path``, Path to a bin file.
    """
    with open(path, 'rb') as file:
        header = file.read(0x20)
        raw = file.read()
    return GameData(header, raw)


if __name__ == '__main__':
    print('This script is a library and does not mean to be used directly.')
