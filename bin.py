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

import sys
from struct import unpack, pack, pack_into
if sys.version_info[0] > 2:
    xrange = range
    unicode = str

import basetypes


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
            self._data = b''
            self._p1_list = []
            self._p2_list = []
            self._labels = b''

        else:
            # Header
            size, data_length, p1_count, p2_count = \
                unpack('<4I', header[0x0:0x10])
            if size != len(header) + len(raw):
                raise InvalidFileError('Invalid file.')

            p1_offset = data_length
            p2_offset = p1_offset + p1_count * 4
            label0_offset = p2_offset + p2_count * 8

            # Data
            self._data = raw[:data_length]

            # Pointer 1
            self._p1_list = list(unpack('<' + str(p1_count) + 'I',\
                raw[p1_offset:p2_offset]))

            # Pointer 2
            self._p2_list = []
            for offset in xrange(p2_offset, label0_offset, 8):
                self._p2_list.append(unpack('<II', raw[offset:offset + 8]))

            # Labels
            self._labels = raw[label0_offset:]

    def __len__(self):
        return 0x20 + len(self._data) + len(self._p1_list) * 4 + \
            len(self._p2_list) * 8 + len(self._labels)

    def __repr__(self):
        return self.raw_data

    @property
    def raw_data(self):
        """Return raw data, without the header."""
        pointer1 = b''.join([pack('<I', _) for _ in self._p1_list])
        pointer2 = b''.join([pack('<II', *_) for _ in self._p2_list])
        return self._data + pointer1 + pointer2 + self._labels

    def tobin(self):
        """Export to .bin file."""
        header = pack('<4I', len(self), len(self._data), len(self._p1_list),
                      len(self._p2_list))
        return header + b'\0' * 16 + self.raw_data

    @property
    def data(self):
        """Get raw bytes of the data region."""
        return self._data

    @property
    def ptr1_list(self):
        """Return a list of all pointers in region 1."""
        return self._p1_list

    @property
    def ptr2_list(self):
        """Return a list of all pointers in region 2."""
        return self._p2_list

    @property
    def label0_offset(self):
        """Get base label offset."""
        return len(self._data) + len(self._p1_list) * 4 + len(self._p2_list) * 8

    def get_label(self, offset, encoding='unicode'):
        """Get a single label."""
        if offset == 0:
            if encoding == 'unicode':
                return u'NULL'
            else:
                return b'NULL'
        offset -= self.label0_offset
        length = 0
        while self._labels[offset + length:offset + length + 1] != b'\0':
            length += 1
        if encoding == 'shift-jis':
            return self._labels[offset:offset + length]
        elif encoding == 'unicode':
            return self._labels[offset:offset + length].decode('shift-jis')
        else:
            return self._labels[offset:offset + length]\
                .decode('shift-jis').encode(encoding)

    def get_labels(self, encoding='unicode'):
        """Construct a label dictionary for the current .bin file. All labels
        are referenced in pointer region 1.

        Parameters:
        ``encoding``: Encode the output using specified code page.
        """
        label_dict = dict()
        data_length = len(self._data)
        for pointer1 in self._p1_list:
            ptr = unpack('<I', self._data[pointer1:pointer1 + 0x4])[0]
            if ptr < data_length:
                continue
            label_dict[ptr] = self.get_label(ptr, encoding)

        return label_dict

    def get_label_list(self, encoding='shift-jis'):
        """Return all distinct labels in the current .bin file.

        Because this method cannot check if there are other data inside the
        label region, you should use get_label_list() with cautions.

        Parameters:
        ``encoding``: Encode the output using specified code page.
        """
        label_list = self._labels.split(b'\0')
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
        label0_offset = self.label0_offset
        ptr_groups = {-1:[]}            # First Pointer 1 -> List of Pointer 1
        ptr_p1_dict = {}                # Data pointers -> Pointer 1
        for p1_ptr in self._p1_list:
            ptr = unpack('<I', self._data[p1_ptr:p1_ptr + 4])[0]
            if ptr < label0_offset:           # Non-label pointers
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

            # Get label by offset
            label = self.get_label(label0_offset + p2_ptr[1],
                encoding='shift-jis')
            labels.append(label)

            label_offsets[label0_offset + p2_ptr[1]] = total_length # Reserve
            self._p2_list[p2_index] = (p2_ptr[0], total_length)     # Fix offset
            total_length += len(label) + 1                          # Update

        # Add pointer 1 labels and fix all data pointers
        data = bytearray(self._data)
        for p1_ptr in self._p1_list:
            ptr = unpack('<I', self._data[p1_ptr:p1_ptr + 4])[0]
            label_start = ptr - label0_offset
            if ptr < label0_offset:
                continue
            if label_start not in label_offsets:
                label = self.get_label(ptr, encoding='shift-jis')
                labels.append(label)
                label_offsets[label_start] = total_length
                total_length += len(label) + 1
            # Fix data pointer
            pack_into('<I', data, p1_ptr, label0_offset +
                      label_offsets[label_start])

        self._data = bytes(data)
        self._labels = b'\0'.join(labels) + b'\0'

    ##########################################################################
    # Table methods
    ##########################################################################
    def extract(self, rowclass, offset, size=None, fstring=None, lbdict=None):
        """Extract a row based on structure.

        `rowclass`: A subclass of basetypes.Row, represent data structure.
        `offset`: Offset

        Child class can override this method if the file must be read in a
        different way (like asset files).
        """
        if not issubclass(rowclass, basetypes.Row):
            raise TypeError('expected Row class')

        # Calculate size and format strings
        if size == None:
            size = rowclass.true_size()
        if fstring == None:
            fstring = rowclass.true_fstring()

        # Unpack
        cells = list(unpack(fstring, self._data[offset:offset + size]))

        # Process
        i = 0
        temp_data = []
        structure = rowclass.structure
        for attr in structure:
            t = structure[attr].type
            if issubclass(t, basetypes.Row):
                temp_data.append(self.extract(t, cells[i]))
                i += 1

            elif issubclass(t, basetypes.Array):
                if t.type == basetypes.Label:
                    for j in xrange(i, i + t.length):
                        if lbdict is None:
                            cells[j] = self.get_label(cells[j])
                        else:
                            cells[j] = lbdict[cells[j]]
                temp_data.append(cells[i:i + t.length])
                i += t.length

            elif issubclass(t, basetypes.RestrictedDict):
                if t.type == basetypes.Label:
                    for j in xrange(i, i + len(t.keys)):
                        if lbdict is None:
                            cells[j] = self.get_label(cells[j])
                        else:
                            cells[j] = lbdict[cells[j]]
                temp_data.append(cells[i:i + len(t.keys)])
                i += len(t.keys)

            elif t == basetypes.Label:
                temp_data.append(self.get_label(cells[i]))
                i += 1

            else:
                temp_data.append(cells[i])
                i += 1

        return rowclass(temp_data)

    def extractmultiple(self, tableclass, offset, count):
        """Extract multiple rows.

        `tableclass`: A subclass of basetypes.Table
        `offset`: Offset
        `count`: Number of rows
        """
        if not issubclass(tableclass, basetypes.Table):
            raise TypeError('expected Table class')
        table = tableclass()
        rowclass = tableclass.type
        structure = rowclass.structure
        size = rowclass.true_size()
        fstring = rowclass.true_fstring()
        label_dict = self.get_labels()
        for i in xrange(count):
            table.append(self.extract(rowclass, offset, size, fstring,
                                      label_dict))
            offset += size
        return table

    def repack(self, table, offset):
        """Repack the table back to binary.

        This method does not support table with sub-row or file with multiple
        tables (i.e. GameData.bin).

        `table`: A table object
        `offset`: Offset
        """
        if not isinstance(table, basetypes.Table):
            raise TypeError('input table must be a Table type.')

        # Process all labels and construct the label region.
        # Also create pointer 1 groups for a properly formatted .bin file
        label_offsets = {}  # Store label offsets
        raw_labels = []     # Store labels in Shift-JIS encoding
        total_length = 0    # Keep track of total label length
        p1_groups = {}      # Store pointer 1 groups: all pointer 1 that point
                            # to the same label belong to a group
        p1_count = 0        # Number of pointer 1
        rowclass = table.__class__.type
        structure = rowclass.structure
        size = rowclass.true_size()
        table = table.flatten() # Convert the table to a list of list
        for i in xrange(len(table)):
            sub_offset = 0
            for cell in table[i]:
                if isinstance(cell, basetypes.Label) and cell != u'NULL':
                    label = cell
                    p1_count += 1
                    if label in label_offsets:
                        p1_groups[label].append(offset + i * size + sub_offset)
                    else:
                        label_offsets[label] = total_length
                        raw_labels.append(label.encode('shift-jis'))
                        total_length += len(raw_labels[len(raw_labels) - 1]) +1
                        p1_groups[label] = [offset + i * size + sub_offset]
                sub_offset += cell.__class__.size
        self._labels = b'\0'.join(raw_labels) + b'\0'
        del raw_labels

        # Data and pointer region 1
        # Reminder: Doesn't support file with multiple table
        label0_offset = offset + len(table) * rowclass.true_size() + \
            p1_count * 4
        label_offsets[u'NULL'] = 0 - label0_offset
        raw_data = []
        self._p1_list = []
        fstring = rowclass.true_fstring()
        for i in xrange(len(table)):
            temp_data = table[i]
            for j in xrange(len(temp_data)):
                if isinstance(temp_data[j], basetypes.Label):
                    label = temp_data[j]
                    temp_data[j] = label0_offset + label_offsets[label]
                    if label in p1_groups:
                        self._p1_list.extend(p1_groups[label])
                        del p1_groups[label]
            raw_data.append(pack(fstring, *temp_data))

        self._data = self._data[:offset] + b''.join(raw_data)


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
    print('This script is a library and does not mean to be used directly.')
