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

import codecs
from collections import OrderedDict
from struct import unpack, pack, pack_into

import bin
import basetypes

class CastleJoin(bin.BinFile):
    """A class that represent data structure in castle_join.bin.

    `characters` is a public field. It represent a list of characters.
    """

    def __init__(self, header=None, raw=None):
        """Create a new CastleJoin object."""
        super(CastleJoin, self).__init__(header, raw)
        self.characters = CharacterList()

        if raw is None:
            self._data = b'\0' * 4
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

        self.characters = self.extractmultiple(CharacterList, 0x4, unit_count)

    def totext(self):
        """Export to text file. Index number will be removed."""
        return u'Index\tPID\tCID_A\tCID_B\tCID_C\tBuilding 1\tBuilding 2\t' + \
            u'Building 3\n' + u'\n'.join([c.tostring() for c in self.characters])

    def fromtext(self, text):
        """Load data from text."""
        text = u'\n'.join(text.split(u'\n')[1:])
        self.characters = CharacterList(text)

    def tobin(self):
        """Build a functional castle_join.bin."""
        super(CastleJoin, self).repack(self.characters, 0x4)
        self._data = pack('<I', len(self.characters)) + self._data[0x4:]
        return super(CastleJoin, self).tobin()


class ChapterLabelDict(basetypes.RestrictedDict):
    """A dict which store chapter labels in an elegant way."""
    type = basetypes.Label
    keys = [u'A', u'B', u'C']
    size = type.size * len(keys)
    fstring = type.fstring * len(keys)

    def __init__(self, *args, **kwargs):
        """Initialize a ChapterLabelDict object."""
        super(ChapterLabelDict, self).__init__(*args, **kwargs)


class BuildingIDs(basetypes.Array):
    """List of Building IDs."""
    type = basetypes.S32
    length = 3
    size = type.size * length
    fstring = type.fstring * length

    def __init__(self, *args, **kwargs):
        """Initialize a BuildingIDs object."""
        super(BuildingIDs, self).__init__(*args, **kwargs)


class Character(basetypes.Row):
    """Character in castle_join.bin"""
    structure = OrderedDict([
        ('index', basetypes.Structure(basetypes.U32, basetypes.Formats.STR)),
        ('pid', basetypes.Structure(basetypes.Label, basetypes.Formats.STR)),
        ('cids', basetypes.Structure(ChapterLabelDict, basetypes.Formats.STR)),
        ('building_ids', basetypes.Structure(BuildingIDs, basetypes.Formats.HEX))
    ])

    def __init__(self, *args, **kwargs):
        """Initialize a Character object.

        Positional arguments:
        `data`: raw data, cannot be used with other arguments.

        Keyword arguments:
        `pid`: character label / PID (str / unicode)
        `cids`: list of chapter labels / CID (str / unicode)
        `building_ids`: building IDs (int)
        """
        valid_args = frozenset(['data', 'pid', 'cids', 'building_ids'])
        for arg in kwargs.keys():
            if arg not in valid_args:
                raise ValueError('Unsupported keyword argument: ' + arg)

        if len(args) > 1:
            raise TypeError('expected 1 arguments, got ' + len(args))
        if len(args) == 0 and len(kwargs) == 0:
            raise ValueError('character label cannot be empty')

        if len(args) == 1:
            data = args[0]
        else:
            data = []
            if 'pid' in kwargs:
                data.append(kwargs['pid'])
            else:
                raise ValueError('character label cannot be empty')

            # Chapter labels
            if 'cids' in kwargs:
                data.append(kwargs['cids'])
            else:
                data.extend([u'NULL', u'NULL', u'NULL'])

            # Building IDs
            if 'building_ids' in kwargs:
                data.append(kwargs['building_ids'])
            else:
                data.extend([0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF])

        super(Character, self).__init__(data)


class CharacterList(basetypes.Table):
    """Represent a list of character."""
    type = Character

    def __init__(self, *args, **kwargs):
        super(CharacterList, self).__init__(*args, **kwargs)


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
    with codecs.open(path, 'r', 'utf-8') as file:
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
        with codecs.open(outname, 'w', 'utf-8') as file:
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
