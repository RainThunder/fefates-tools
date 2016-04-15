#!/usr/bin/env python2
# Generate fst.bin file for Fire Emblem If / Fates DLC.
# It is basically a file list.

import os
import sys
from struct import pack, unpack

if not os.path.isdir(unicode(sys.argv[1])):
    print sys.argv[1] + ': No such directory.'
    sys.exit(0)
    
# List all file in the directory and calculate fst.bin file size.
file_list = []
path_length = 0
file_count = 0
root_name = unicode(sys.argv[1])
for dirpaths, dirnames, filenames in os.walk(unicode(sys.argv[1])):
    for filename in filenames:
        if filename == u'fst.bin':
            continue
        if dirpaths != root_name:
            filepath = (dirpaths.replace(root_name + os.sep, '').replace(os.sep, u'/') + u'/' + filename).encode('shift-jis')
        else:
            filepath = filename.encode('shift-jis')
        path_length = path_length + len(filepath) + 1
        file_list.append(filepath)
        file_count = file_count + 1

list_offset = 0x20 + 0x4 + file_count * 8 # File list offset
fst_size = list_offset + path_length # fst.bin file size
fst_file = open(os.path.join(unicode(sys.argv[1]), u'fst.bin'), 'wb')

fst_file.write(pack('<I', fst_size))
fst_file.write(pack('<I', file_count * 4 + 4))
fst_file.write(pack('<I', file_count))
fst_file.write(''.join(['\0'] * 20))
fst_file.write(pack('<I', file_count))
temp_offset = list_offset - 0x20
for i in xrange(file_count):
    fst_file.write(pack('<I', temp_offset))
    temp_offset = temp_offset + len(file_list[i]) + 1
for i in xrange(file_count):
    fst_file.write(pack('<I', 0x4 + i * 4))
for i in xrange(file_count):
    fst_file.write(file_list[i] + '\x00'.encode('shift-jis'))
    
fst_file.close()
print 'fst.bin generated.'
