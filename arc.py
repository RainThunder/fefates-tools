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

"""A simple tool which can be used to extract and pack the .arc files
in Fire Emblem Fates. It can also be used as a Python library. Credits
to SciresM for the original implementation.

Usage: python arc.py PATH

If PATH is an .arc file, this tool will extract that file.
If PATH is a folder, this tool will pack all files in that folder to
an .arc file.

Due to Windows' Command Prompt doesn't support Unicode file name right
out of the box, you have to use `chcp 65501` to change the code page
to UTF-8 before using this tool. Alternatively, you can create a .bat
file which contains the following lines:

```chcp 65501
python arc.py "%1"
```

After that, you can drag and drop any file or folder to that .bat file
whenever you want to use this tool.
"""

from __future__ import print_function
import os
import platform
import sys
from collections import namedtuple
from struct import unpack, pack
if sys.version_info[0] > 2:
    unicode = str
    xrange = range

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

class Arc(object):
    """An arc file object."""
    FileInfo = namedtuple('FileInfo', ['name', 'index', 'length', 'offset'])

    def __init__(self, header=None, raw=None):
        """Initialize the bin objects.

        Parameters:
        ``header``: Header
        ``raw``: Raw data
        """
        if header != None and raw != None:
            self.__init(header, raw)
        else:
            self.__init_empty()

    def __init_empty(self):
        self.__data = b''
        self.__info_table = []

    def __init(self, header, raw):
        # Header
        size, data_length, p1_count, p2_count = \
            unpack('<4I', header[0x0:0x10])
        p1_offset = data_length
        p2_offset = p1_offset + p1_count * 4
        label_offset = p2_offset + p2_count * 8

        # Pointer 1
        self.__p1_list = list(unpack('<' + str(p1_count) + 'I',\
            raw[p1_offset:p2_offset]))

        # Pointer 2
        self.__p2_list = []
        for offset in xrange(p2_offset, label_offset, 8):
            self.__p2_list.append(unpack('<II', raw[offset:offset + 8]))

        # Labels
        label_list = raw[label_offset:].rstrip(b'\0').split(b'\0')
        self.__label_dict = {}
        total_length = 0
        for label in label_list:
            self.__label_dict[label_offset + total_length] = label
            total_length += len(label) + 1

        # Critical info in pointer region 2
        for ptr in self.__p2_list:
            label = self.__label_dict[label_offset + ptr[1]]
            if label == b'Data':
                data_begin = ptr[0]
            elif label == b'Count':
                file_count = unpack('<I', raw[ptr[0]:ptr[0] + 4])[0]
                data_end = ptr[0]
            elif label == b'Info':
                info_offset = ptr[0]
            else:
                # Other ptrs are pointed to file entries in info table.
                pass

        # Data: only contains files
        self.__data = raw[data_begin:data_end]

        # File info table
        self.__info_table = []
        for file_index in xrange(file_count):
            offset = info_offset + file_index * 16
            name_offset, index, length, file_offset =\
                unpack('4I', self.__data[offset:offset + 16])
            self.__info_table.append(self.FileInfo._make((
                self.__label_dict[name_offset].decode('shift-jis'),
                index,
                length,
                file_offset
            )))

    def get_file_count(self):
        """Get the number of files in the Arc object."""
        return len(self.__info_table)

    def get_filename(self, file_index):
        """Get the file name of the file_index-th file."""
        if file_index >= len(self.__info_table):
            raise ValueError("Out-of-bound file index.")

        return self.__info_table[file_index].name

    def get_file(self, file_index):
        """Get the file data of the file_index-th file.

        Parameters:
        `file_index`: File index
        """
        if file_index >= len(self.__info_table):
            raise ValueError("Out-of-bound file index.")

        info = self.__info_table[file_index]
        return self.__data[info.offset:info.offset + info.length]

    def append_file(self, name, data):
        """Append a new file to the Arc object.

        Parameters:
        `name`: File name
        `data`: File data
        """
        if len(data) & 0xFF == 0x00:
            pad = 0
        else:
            pad = 0x100 - (len(data) & 0xFF)
        self.__info_table.append(self.FileInfo._make((
            name, len(self.__info_table), len(data), len(self.__data))))
        self.__data += data + b'\0' * pad

    def to_arc(self):
        """Export the Arc object to .arc file format."""
        output = BytesIO()
        file_count = len(self.__info_table)

        # Header
        p1_offset = 0x60 + len(self.__data) + 0x4 + len(self.__info_table) * 16
        output.write(pack('<4I', 0, p1_offset, file_count, file_count + 3))

        output.write(b'\0' * 0x70) # Padding
        output.write(self.__data) # Data
        output.write(pack('<I', file_count)) # File count

        label_offset = p1_offset + file_count * 4 + (file_count + 3) * 8 + 16
        name_length = 0
        filenames = []
        info_offsets = []

        # File info table
        for file_index in xrange(file_count):
            name_offset = label_offset + name_length
            info_offsets.append(output.tell() - 0x20)
            info = self.__info_table[file_index]
            output.write(pack('<4I', name_offset, file_index, info.length,
                              info.offset))
            filenames.append(info.name.encode('shift-jis'))
            name_length += len(filenames[file_index]) + 1

        # Pointer region 1
        for file_index in xrange(file_count):
            output.write(pack('<I', info_offsets[file_index]))

        # Pointer region 2
        output.write(pack('<2I', 0x60, 0x0))
        output.write(pack('<2I', 0x60 + len(self.__data), 0x5))
        output.write(pack('<2I', 0x60 + len(self.__data) + 0x4, 0xB))
        name_length = 16
        for file_index in xrange(file_count):
            output.write(pack('<2I', info_offsets[file_index], name_length))
            name_length += len(filenames[file_index]) + 1

        # Label region
        output.write(b'Data\0Count\0Info\0')
        for file_index in xrange(file_count):
            output.write(filenames[file_index] + b'\0')

        # File size
        size = output.tell()
        output.seek(0, os.SEEK_SET)
        output.write(pack('<I', size))

        return output.getvalue()


def load_file(path):
    """Load an archive file to an Arc object.

    Parameters:
    ``path``: Path to an archive file.
    """
    with open(path, 'rb') as arc_file:
        header = arc_file.read(0x20)
        raw = arc_file.read()
    return Arc(header, raw)

def load(raw):
    """Load data from raw bytes to an Arc objects.

    Parameters:
    ``raw``: Raw data.
    """
    return Arc(raw[:0x20], raw[0x20:])

def win32_unicode_argv():
    """Uses shell32.GetCommandLineArgvW to get sys.argv as a list of Unicode
    strings.

    Versions 2.x of Python don't support Unicode in sys.argv on
    Windows, with the underlying Windows API instead replacing multi-byte
    characters with '?'.

    Source:
    https://stackoverflow.com/questions/846850/
    https://code.activestate.com/recipes/572200/
    """

    from ctypes import POINTER, byref, cdll, c_int, windll
    from ctypes.wintypes import LPCWSTR, LPWSTR

    GetCommandLineW = cdll.kernel32.GetCommandLineW
    GetCommandLineW.argtypes = []
    GetCommandLineW.restype = LPCWSTR

    CommandLineToArgvW = windll.shell32.CommandLineToArgvW
    CommandLineToArgvW.argtypes = [LPCWSTR, POINTER(c_int)]
    CommandLineToArgvW.restype = POINTER(LPWSTR)

    cmd = GetCommandLineW()
    argc = c_int(0)
    argv = CommandLineToArgvW(cmd, byref(argc))
    if argc.value > 0:
        # Remove Python executable and commands if present
        start = argc.value - len(sys.argv)
        return [argv[i] for i in
                xrange(start, argc.value)]


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage: python arc.py PATH')
        print('If PATH is an .arc file, this tool will extract it to a' + \
            'folder with the same name.')
        print('If PATH is a folder, this tool will pack all files in that' + \
            'folder to an .arc file.')

    if platform.system() == 'Windows' and sys.version_info[0] == 2:
        path = win32_unicode_argv()[1]
    else:
        path = sys.argv[1]

    if os.path.isfile(path):
        arc = load_file(path)
        dir_name = os.path.join(os.path.dirname(path),
                                os.path.splitext(os.path.basename(path))[0])
        if not os.path.isdir(os.path.splitext(path)[0]):
            os.mkdir(dir_name)
        for file_index in xrange(arc.get_file_count()):
            out_file_name = os.path.join(dir_name, arc.get_filename(file_index))
            with open(out_file_name, 'wb') as outfile:
                outfile.write(arc.get_file(file_index))
        print(path + ' was successfully extracted.')
    elif os.path.isdir(path):
        arc = Arc()
        for dirpaths, dirnames, filenames in os.walk(path):
            for filename in filenames:
                with open(os.path.join(dirpaths, filename), 'rb') as infile:
                    data = infile.read()
                arc.append_file(filename, data)
        with open(path + u'.arc', 'wb') as outfile:
            outfile.write(arc.to_arc())
        print(repr(path) + '.arc was created.')
    else:
        print('Invalid path.')
