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
"""A lightweight library for .bin file format in Fire Emblem Fates."""

from struct import unpack, pack, pack_into


class InvalidFileError(Exception):
    pass


class BinFile(object):
    def __init__(self, header=None, raw=None):
        """Initialize the bin objects.

        Parameters:
        ``header``: Header
        ``raw``: Raw data
        """
        if header is None or raw is None:
            self._data = ''
            self._p1_list = []
            self._p2_list = []
            self._labels = ''

        else:
            # Header
            size, data_length, p1_count, p2_count = \
                unpack('<4I', header[0x0:0x10])
            if size != len(header) + len(raw):
                raise InvalidFileError('Invalid file.')

            p1_offset = data_length
            p2_offset = p1_offset + p1_count * 4
            label_offset = p2_offset + p2_count * 8

            # Data
            self._data = raw[:data_length]

            # Pointer 1
            self._p1_list = list(unpack('<' + str(p1_count) + 'I',\
                raw[p1_offset:p2_offset]))

            # Pointer 2
            self._p2_list = []
            for offset in xrange(p2_offset, label_offset, 8):
                self._p2_list.append(unpack('<II', raw[offset:offset + 8]))

            # Labels
            self._labels = raw[label_offset:]

    def __len__(self):
        return 0x20 + len(self._data) + len(self._p1_list) * 4 + \
            len(self._p2_list) * 8 + len(self._labels)

    def __repr__(self):
        return self.get_raw_data()

    def get_raw_data(self):
        """Return raw data, without the header."""
        pointer1 = ''.join([pack('<I', _) for _ in self._p1_list])
        pointer2 = ''.join([pack('<II', *_) for _ in self._p2_list])
        return self._data + pointer1 + pointer2 + self._labels

    def tobin(self):
        """Export to .bin file."""
        header = pack('<4I', len(self), len(self._data), len(self._p1_list),
                      len(self._p2_list))
        return header + '\0' * 16 + self.get_raw_data()

    def get_data(self):
        """Get raw bytes of the data region."""
        return self._data

    def get_pointer_1(self):
        """Return a list of all pointers in region 1."""
        return self._p1_list

    def get_pointer_2(self):
        """Return a list of all pointers in region 2."""
        return self._p2_list

    def get_label_offset(self):
        """Get base label offset."""
        return len(self._data) + len(self._p1_list) * 4 + len(self._p2_list) * 8

    def get_labels(self, encoding='shift-jis'):
        """Construct a label dictionary for the current .bin file. All labels
        are referenced in pointer region 1.

        Parameters:
        ``encoding``: Encode the output using specified code page.
        """
        label_dict = dict()
        label_dict[0] = 'NULL'
        data_length = len(self._data)
        label_base_offset = data_length + len(self._p1_list) * 4 + \
            len(self._p2_list) * 8
        for pointer1 in self._p1_list:
            ptr = unpack('<I', self._data[pointer1:pointer1 + 0x4])[0]
            if ptr < data_length:
                continue
            offset = ptr - label_base_offset
            length = 0
            while self._labels[offset + length] != '\0':
                length += 1
            if encoding == 'shift-jis':
                label_dict[ptr] = self._labels[offset:offset + length]
            elif encoding == 'unicode':
                label_dict[ptr] = self._labels[offset:offset + length].decode('shift-jis')
            else:
                label_dict[ptr] = self._labels[offset:offset + length]\
                    .decode('shift-jis').encode(encoding)
        return label_dict

    def get_label_list(self, encoding='shift-jis'):
        """Return all distinct labels in the current .bin file. Because this
        method cannot check if there are other data inside the label region,
        you should use get_label_list() with cautions.

        Parameters:
        ``encoding``: Encode the output using specified code page.
        """
        label_list = self._labels.split('\0')
        if encoding == 'shift-jis':
            return label_list
        else:
            return [label.decode('shift-jis').encode(encoding)
                    for label in label_list]

    def format(self):
        """Properly format this file.

        Important note: All unused labels will be removed immediately.
        """
        # Group all pointers that are pointed to the same thing.
        # Pointers that doesn't point to a label are belong to the first group.
        label_offset = self.get_label_offset()
        ptr_groups = {-1:[]} # First Pointer 1 -> List of Pointer 1
        ptr_p1_dict = {}     # Data pointers -> Pointer 1
        for p1_ptr in self._p1_list:
            ptr = unpack('<I', self._data[p1_ptr:p1_ptr + 4])[0]
            if ptr < label_offset:            # Non-label pointers
                ptr_groups[-1].append(p1_ptr) # to the first group
            else:
                if ptr not in ptr_p1_dict:
                    ptr_p1_dict[ptr] = p1_ptr
                    ptr_groups[p1_ptr] = []
                else:
                    ptr_groups[ptr_p1_dict[ptr]].append(p1_ptr)

        # Sort and combine
        p1_sorted = sorted(ptr_groups.keys())
        p1_list = []
        for p1_ptr in p1_sorted:
            if p1_ptr != -1:
                p1_list.append(p1_ptr)
            if len(ptr_groups[p1_ptr]) > 0:
                p1_list.extend(ptr_groups[p1_ptr])
        self._p1_list = p1_list

        # Sort pointer 2
        self._p2_list.sort(key=lambda x:x[0])

        # Sort labels
        labels = []        # Labels -> New label offsets
        label_offsets = {} # Old label offsets -> New label offsets
                           # Used for fixing pointer in data region.
        total_length = 0   # Total length of all labels in "labels" list.

        # Add pointer 2 labels and fix pointer 2
        for p2_index in xrange(len(self._p2_list)):
            p2_ptr = self._p2_list[p2_index]

            # Get label by offset (label_start)
            label_start = label_end = p2_ptr[1]
            while self._labels[label_end] != '\0':
                label_end += 1
            label = self._labels[label_start:label_end]
            labels.append(label)

            label_offsets[label_start] = total_length           # Reserve
            self._p2_list[p2_index] = (p2_ptr[0], total_length) # Fix offset
            total_length += len(label) + 1                      # Update

        # Add pointer 1 labels and fix all data pointers
        data = bytearray(self._data)
        for p1_ptr in self._p1_list:
            ptr = unpack('<I', self._data[p1_ptr:p1_ptr + 4])[0]
            label_start = ptr - label_offset
            if ptr < label_offset:
                continue
            if label_start not in label_offsets:
                label_end = label_start
                while self._labels[label_end] != '\0':
                    label_end += 1
                label = self._labels[label_start:label_end]
                labels.append(label)
                label_offsets[label_start] = total_length
                total_length += len(label) + 1
            # Fix data pointer
            pack_into('<I', data, p1_ptr, label_offset +
                      label_offsets[label_start])

        self._data = str(data)
        self._labels = '\0'.join(labels) + '\0'


def load_file(path):
    """Load a bin file to a bin object.

    Parameters:
    ``path``: Path to a bin file.
    """
    with open(path, 'rb') as file:
        header = file.read(0x20)
        raw = file.read()
    return BinFile(header, raw)

def load(raw):
    """Load data from raw bytes to a bin objects.

    Parameters:
    ``raw``: Raw data.
    """
    return BinFile(raw[:0x20], raw[0x20:])


if __name__ == '__main__':
    print 'This script is a library and does not mean to be used directly.'
