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

"""castle_join.py - extract and pack data in the castle_join.bin file in Fire
Emblem Fates.

Usage:
    `python castle_join.py input [output]`

If the input file has .bin extension, this script will extract data in that
file to a tab-delimited text file. If the input file is a text file, the
script will try to pack all data to a functional .bin file. If `output`
argument is present, the output file name will be changed

This script can be used as a library. Its design makes editing data in
castle_join.bin trivial.

Example:
    >>> import castle_join
    >>> cj = castle_join.load_bin('castle_join.bin')
    >>> cj.characters[0].pid                   # Show character[0]'s PID label
    'PID_ABCD'
    >>> cj.characters.append(Character(
            pid='PID_A',
            cids=['NULL', 'NULL', 'C016'],
            building_ids=[0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF]
        )) # Add a new character
    >>> with open('castle_join.bin', 'rb') as file:
            file.write(cj.tobin()) # Write the modified data,
"""

import cStringIO
from struct import unpack, pack, pack_into

import bin

class CastleJoin(bin.BinFile):
    """A class that represent data structure in castle_join.bin.

    `characters` is a public field. It represent a list of characters.
    """

    def __init__(self, header=None, raw=None):
        """Create a new CastleJoin object."""
        super(CastleJoin, self).__init__(header, raw)
        self.characters = CharacterList()

        if raw is None:
            self._data = '\0' * 4
        else:
            self.frombin(header, raw)

    def get_data(self):
        raise NotImplementedError

    def get_pointer_1(self):
        raise NotImplementedError

    def get_pointer_2(self):
        raise NotImplementedError

    def frombin(self, header, raw):
        """Load data from bin file."""
        unit_count = unpack('<I', self._data[0x0:0x4])[0]
        if 0x4 + 0x20 * unit_count != len(self._data):
            raise ValueError('Invalid file.')

        label_dict = self.get_labels(encoding='unicode')
        for index in xrange(unit_count):
            offset = 0x4 + index * 0x20
            temp = unpack('<8I', self._data[offset:offset + 0x20])
            self.characters.append(Character(
                pid=label_dict[temp[1]],
                cids=[label_dict[ptr] for ptr in temp[2:5]],
                building_ids=list(temp[5:8])
            ))

    def totext(self):
        """Export to text file. Index number will be removed."""
        return 'PID\tCID_A\tCID_B\tCID_C\tBuilding 1\tBuilding 2\t' + \
            'Building 3\n' + '\n'.join([str(c) for c in self.characters])

    def fromtext(self, text):
        """Load data from text."""
        lines = text.split('\n')
        for i in xrange(1, len(lines)):
            cells = lines[i].split('\t')
            if len(cells) < 7:
                continue
            for j in xrange(4, 7):
                try:
                    if cells[j].startswith('0x'):
                        cells[j] = int(cells[j], 16)
                    else:
                        cells[j] = int(cells[j])
                except ValueError:
                    raise ValueError('Invalid number at line ' + str(i))
            for j in xrange(0, 4):
                cells[j] = cells[j].decode('utf-8')
            self.characters.append(Character(pid=cells[0], cids=cells[1:4],
                                   building_ids=cells[4:7]))

    def tobin(self):
        """Build a functional castle_join.bin."""
        paths = ['A', 'B', 'C']

        # Process all labels and construct label region.
        # Also create pointer 1 groups for a properly formatted .bin file
        label_offsets = {}                # Store label offsets
        raw_labels = cStringIO.StringIO() # Store labels in Shift-JIS encoding
        p1_groups = {}                    # Store pointer 1 groups
                                          # All pointer 1 that point to the
                                          # same label belong to a group
        p1_count = 0
        for i in xrange(len(self.characters)):
            # PID label
            label = self.characters[i].pid
            label_offsets[label] = raw_labels.tell()
            raw_labels.write(label.encode('shift-jis') + '\0')
            p1_groups[label] = 0x8 + i * 0x20
            p1_count += 1

            # CID labels
            for j in xrange(3):
                path = paths[j]
                if self.characters[i].cids[path] == u'NULL':
                    continue
                label = self.characters[i].cids[path]
                if label not in label_offsets:
                    label_offsets[label] = raw_labels.tell()
                    raw_labels.write(label.encode('shift-jis') + '\0')
                    p1_groups[label] = [0xC + i * 0x20 + j * 4]
                else:
                    p1_groups[label].append(0xC + i * 0x20 + j * 4)
                p1_count += 1
        self._labels = raw_labels.getvalue()

        # Data and pointer region 1
        label_offset = 0x4 + len(self.characters) * 0x20 + p1_count * 4
        raw_data = cStringIO.StringIO()
        raw_data.write(pack('<I', len(self.characters)))
        self._p1_list = []
        for i in xrange(len(self.characters)):
            # Index
            raw_data.write(pack('<I', i))

            # Character label (PID)
            label = self.characters[i].pid
            raw_data.write(pack('<I', label_offset + label_offsets[label]))
            self._p1_list.append(p1_groups[label])

            # Chapter labels (CID)
            for j in xrange(3):
                path = paths[j]
                label = self.characters[i].cids[path]
                if label == u'NULL':
                    raw_data.write(pack('<I', 0))
                    continue
                raw_data.write(pack('<I', label_offset + label_offsets[label]))
                try:
                    self._p1_list.extend(p1_groups[label])
                    del p1_groups[label]
                except KeyError:
                    pass

            # Building IDs
            for id in self.characters[i].building_ids:
                raw_data.write(pack('<I', id))

        self._data = raw_data.getvalue()
        return super(CastleJoin, self).tobin()


class ChapterLabelDict(dict):
    """ChapterLabelDict"""
    def __init__(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        dict.__init__(self, **kwargs)
        if len(args) == 1:
            if not isinstance(args[0], list):
                raise TypeError('argument must be a list')
            if len(args[0]) != 3:
                raise TypeError('number of chapter labels must be 3')
            self['A'] = args[0][0]
            self['B'] = args[0][1]
            self['C'] = args[0][2]

    def __setitem__(self, key, label):
        if key not in frozenset(['A', 'B', 'C']):
            raise KeyError("key must be either 'A', 'B' or 'C'")
        if label is None:
            dict.__setitem__(self, key, u'NULL')
        elif isinstance(label, str):
            dict.__setitem__(self, key, unicode(label))
        elif isinstance(label, unicode):
            dict.__setitem__(self, key, label)
        else:
            raise TypeError('chapter label must be a string or None')

    def __delitem__(self, key):
        raise NotImplementedError()


class BuildingIDs(list):
    """List of Building IDs."""
    # All method that change the list size will throw an exception

    def __init__(self, *args):
        if len(args) != 1:
            raise TypeError('expected 1 arguments, got %d' % len(args))
        if not isinstance(args[0], list):
            raise TypeError('argument must be a list')
        if len(args[0]) != 3:
            raise ValueError('number of building ID must be 3')
        for id in args[0]:
            self.__checkid(id)
        list.__init__(self, *args)

    def __checkid(self, id):
        if not isinstance(id, (int, long)):
            raise TypeError('building ID must be an integer')

    def __setitem__(self, index, id):
        if index >= 3:
            raise IndexError('list index out of range')
        self.__checkid(id)
        list.__setitem__(self, index, id)

    def __delitem__(self, index):
        raise NotImplementedError()

    def append(self, id):
        raise NotImplementedError()

    def extend(self, building_ids):
        raise NotImplementedError()

    def insert(self, index, id):
        raise NotImplementedError()

    def pop(self, index):
        raise NotImplementedError()

    def remove(self, index, id):
        raise NotImplementedError()


class Character(object):
    """Character in castle_join.bin"""
    __slots__ = ['_pid', '_cids', '_building_ids']

    def __init__(self, **kwargs):
        """Initialize a Character object.

        Keyword arguments:
        `data`: raw data, cannot be used with other arguments.
        `pid`: character label / PID (unicode)
        `cids`: list of chapter labels / CID (unicode)
        `building_ids`: building IDs (int)
        """
        valid_args = frozenset(['data', 'pid', 'cids', 'building_ids'])
        for arg in kwargs.keys():
            if arg not in valid_args:
                raise ValueError('Unsupported keyword argument: ' + arg)

        if len(kwargs) == 0:
            self._pid = None
            self._cids = ChapterLabelDict()
            self._building_ids = BuildingIDs([0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF])

        if 'data' in kwargs:
            self._pid, self._cids['A'], self._cids['B'], self._cids['C'] = \
                kwargs['data'][1:5]
            self._building_ids = BuildingIDs(kwargs['data'][5:8])
        else:
            if 'pid' in kwargs:
                self.pid = kwargs['pid']
            else:
                raise ValueError('character label cannot be empty')

            # Chapter labels
            if 'cids' in kwargs:
                self._cids = ChapterLabelDict(kwargs['cids'])
            else:
                self._cids = ChapterLabelDict()

            # Building IDs
            if 'building_ids' in kwargs:
                self._building_ids = BuildingIDs(kwargs['building_ids'])
            else:
                self._building_ids = BuildingIDs([0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF])

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, label):
        if isinstance(label, str):
            self._pid = unicode(label)
        elif isinstance(label, unicode):
            self._pid = label
        else:
            raise TypeError('character label must be a string')

    @property
    def cids(self):
        return self._cids

    @property
    def building_ids(self):
        return self._building_ids

    def get_data(self):
        return (self._pid, self._cids['A'], self._cids['B'], self._cids['C'],
                self._building_ids[0], self._building_ids[1], self._building_ids[2])

    def __str__(self):
        return '\t'.join(s.encode('utf-8') for s in [
            self._pid,
            self._cids['A'],
            self._cids['B'],
            self._cids['C'],
            '0x' + format(self._building_ids[0], 'X'),
            '0x' + format(self._building_ids[1], 'X'),
            '0x' + format(self._building_ids[2], 'X')])


class CharacterList(list):
    """Represent a list of character."""

    def __init__(self, *args):
        list.__init__(self, *args)

    def __setitem__(self, index, character):
        if not isinstance(character, Character):
            raise TypeError('Character object is required')
        list.__setitem__(self, index, character)

    def append(self, character):
        """Add a new character to the end of the list."""
        if not isinstance(character, Character):
            raise TypeError('Character object is required')
        list.append(self, character)

    def extend(self, character_list):
        """Extend the list by appending all the items in the given list."""
        if not isinstance(character_list, CharacterList):
            raise TypeError('CharacterList object is required')
        list.extend(self, character_list)

    def insert(self, index, character):
        """Insert an item at a given position."""
        if not isinstance(character, Character):
            raise TypeError('Character object is required')
        list.insert(self, index, character)


def load_bin(path):
    """Load a bin file to a CastleJoin object.

    Parameters:
    ``path``: Path to a bin file.
    """
    with open(path, 'rb') as file:
        header = file.read(0x20)
        raw = file.read()
    return CastleJoin(header, raw)

def load_text(path):
    """Load a txt file to a CastleJoin object.

    Parameters:
    ``path``: Path to a bin file.
    """
    with open(path, 'r') as file:
        text = file.read()
    cj = CastleJoin()
    cj.fromtext(text)
    return cj


if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input file name')
    parser.add_argument('output', nargs='?', default=None,
                        help='output file name (optional)')
    args = parser.parse_args()

    if os.path.splitext(args.input)[1] == '.bin':
        castle_join = load_bin(args.input)
        outname = args.output
        if args.output is None:
            outname = 'castle_join.txt'
        with open(outname, 'w') as file:
            file.write(castle_join.totext())
        print('Data was extracted to ' + outname + '.')

    elif os.path.splitext(args.input)[1] == '.txt':
        castle_join = load_text(args.input)
        outname = args.output
        if args.output is None:
            outname = 'castle_join.bin'
        with open(outname, 'wb') as file:
            file.write(castle_join.tobin())
        print('Data was packed to ' + outname + '.')
