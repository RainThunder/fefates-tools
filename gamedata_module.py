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
"""A Python script which is a workaround for Fire Emblem Fates Nightmare
modules, allows adding stuff into GameData.bin file.

Implemented features:
- Add chapters, characters, classes, items to the GameData.bin file.
- Automatically update the modules to reflect the new changes.
- Add character support, attack / defensive stance table.

Important note:
Please note that this tool doesn't automatically add text, sprites, models.

Usage:
    python gamedata_module.py [--option id name] ...

`option`: "chapter", "character", "class", "item" are available options.
`id`: ID of the new data. Must be an integer.
`name`: Name of the new data, which is used for label.

Example:
    Add two new items with their IDs are 400 and 401, and their labels is
    IID_ABC and IID_DEF, respectively:
        `python gamedata_module.py --item 400 ABC --item 401 DEF`

    Add a new character with label ABC who has support with 47 characters:
        `python gamedata_module.py --character 400 ABC 47 --support`
"""

from __future__ import print_function, unicode_literals
import os
import sys
from struct import unpack
if sys.version_info[0] > 2:
    unicode = str
    xrange = range

import gamedata


MODULE_FILES = {
    'Chapter': [
        os.path.join('Chapter', 'Chapter2.txt')
    ],
    'Character': [
        os.path.join('Character', 'CharID.txt')
    ],
    'Class': [
        os.path.join('Character', 'Class.txt'),
        os.path.join('Character_A_HANDOVER', 'Class.txt'),
        os.path.join('Character_B_HANDOVER', 'Class.txt'),
        os.path.join('Character_C_HANDOVER', 'Class.txt'),
        os.path.join('Class', 'Class2.txt')
    ],
    'Skill': [
        os.path.join('Character', 'Skill.txt'),
        os.path.join('Character_A_HANDOVER', 'Skill.txt'),
        os.path.join('Character_B_HANDOVER', 'Skill.txt'),
        os.path.join('Character_C_HANDOVER', 'Skill.txt'),
    ],
    'Army': [
        os.path.join('Character', 'Army.txt'),
        os.path.join('Character_A_HANDOVER', 'Army.txt'),
        os.path.join('Character_B_HANDOVER', 'Army.txt'),
        os.path.join('Character_C_HANDOVER', 'Army.txt'),
    ],
    'Item': [
        os.path.join('Battle Bonus', 'Item.txt'),
        os.path.join('Character', 'Item.txt'),
        os.path.join('Character_A_HANDOVER', 'Item.txt'),
        os.path.join('Character_B_HANDOVER', 'Item.txt'),
        os.path.join('Character_C_HANDOVER', 'Item.txt'),
        os.path.join('Path Bonus', 'Item.txt'),
        os.path.join('Visit Bonus', 'Item.txt')
    ]
}

MODULE_ORDER = [
    ('Chapter', os.path.join('Chapter', 'Chapter.nmm')),
    ('Character', os.path.join('Character', 'Character.nmm')),
    ('Class', os.path.join('Class', 'Class.nmm')),
    ('Skill', os.path.join('Skill', 'Skill.nmm')),
    ('Stat', os.path.join('Stat', 'Stat.nmm')),
    ('Army', os.path.join('Army', 'Army.nmm')),
    ('Weapon Rank', os.path.join('Weapon Rank', 'WeaponRank.nmm')),
    ('Item', os.path.join('Item', 'Item.nmm')),
    ('Forge', os.path.join('Forge', 'Forge.nmm')),
    ('Tutorial', os.path.join('Tutorial', 'Tutorial.nmm')),
    ('Path Bonus', os.path.join('Path Bonus', 'PathBonus.nmm')),
    ('Battle Bonus', os.path.join('Battle Bonus', 'BattleBonus.nmm')),
    ('Visit Bonus', os.path.join('Visit Bonus', 'VisitBonus.nmm'))
]

def update_modules(data_type, ids, names):
    """Update the modules."""
    # Update data counter in the .nmm file
    with open(os.path.join(data_type, data_type + '.nmm'), 'r+') as file:
        lines = file.readlines()
        lines[5] = str(int(lines[5]) + len(names)) + '\n' # Update count
        file.seek(0)
        file.writelines(lines)

    # Append the new names to the .txt file
    with open(os.path.join(data_type, data_type + '.txt'), 'r+') as file:
        lines = file.readlines()
        lines.extend(names)
        file.seek(0)
        file.writelines(lines)

    # Update other modules
    for path in MODULE_FILES[data_type]:
        with open(path, 'r+') as file:
            lines = file.readlines()
            lines[0] = str(int(lines[0]) + len(names)) + '\n'
            for index in xrange(len(ids)):
                lines.append('0x' + format(ids[index], 'X') + ' ' +
                             names[index] + '\n')
            file.seek(0)
            lines = file.writelines(lines)

def fix_module_offsets(game_data, data_type):
    """Fix the base offset of some modules.

    `game_data`: GameData object
    `data_type`: (Chapter, Character, Class, Item)
    """
    index = 0
    while MODULE_ORDER[index][0] != data_type:
        index += 1
    index += 1
    data_diff = game_data.get_table_info(data_type).size * len(ids)
    while index < len(MODULE_ORDER):
        with open(MODULE_ORDER[index][1], 'r+') as file:
            lines = file.readlines()
            lines[4] = '0x' + format(int(lines[4][2:], 16) + data_diff, 'X') + '\n'
            file.seek(0)
            file.writelines(lines)
        index += 1

def generate_support_module(gamedata_obj, index):
    """Generate a support module for certain characters

    Arguments:
    `gamedata_obj`: GameData object
    `index`: Character index
    """
    data = gamedata_obj.data
    chinfo = gamedata_obj.get_table_info('Character')
    spinfo = gamedata_obj.get_table_info('Support')
    chcount = unpack('<H', data[chinfo.count_offset:chinfo.count_offset+2])[0]
    spcount = unpack('<H', data[spinfo.count_offset:spinfo.count_offset+2])[0]

    # Get all available support IDs and offset
    support_ids = {}
    sp_offsets = unpack('<' + str(spcount) + 'I',
        data[spinfo.offset:spinfo.offset + 4 * spcount])
    for i in xrange(spcount):
        id = unpack('<H', data[sp_offsets[i]:sp_offsets[i] + 2])[0]
        support_ids[id] = sp_offsets[i]

    # Support ID and data offset
    offset = chinfo.offset + index * chinfo.size + 0x30
    id = unpack('<H', data[offset:offset + 2])[0]
    offset = support_ids[id]
    sp_chcount = unpack('<H', data[offset + 0x2:offset + 0x4])[0]

    # Create new modules
    spdir = 'Support_' + str(id)
    if not os.path.isdir(spdir):
        os.mkdir(spdir)
    with open(os.path.join(spdir, 'Support.nmm'), 'w') as file:
        file.write('\n'.join([
            '#Fire Emblem Fates Support Editor',
            '',
            '1',
            'Fire Emblem Fates Support Editor by RainThunder',
            '0x' + format(offset + 0x4, 'X'),
            str(sp_chcount),
            '12',
            'Support.txt',
            'NULL',
            '',
            'Character ID',
            '0',
            '2',
            'NEHU',
            'NULL',
            '',
            'Support index',
            '2',
            '2',
            'NEDU',
            'NULL',
            '',
            'C support point',
            '4',
            '1',
            'NEDS',
            'NULL',
            '',
            'B support point',
            '5',
            '1',
            'NEDS',
            'NULL',
            '',
            'A support point',
            '6',
            '1',
            'NEDS',
            'NULL',
            '',
            'S support point',
            '7',
            '1',
            'NEDS',
            'NULL',
            '',
            'Unknown',
            '8',
            '2',
            'NEHU',
            'NULL',
            '',
            'Global support index',
            '10',
            '2',
            'NEDU',
            'NULL'
        ]))
    with open(os.path.join(spdir, 'Support.txt'), 'w') as file:
        file.write('\n'.join([str(i) for i in xrange(sp_chcount)]))
    return spdir


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', '--item', action='append', nargs=2,
                       help='add an item', metavar=('id', 'name'))
    group.add_argument('-p', '--character', action='append', nargs=3,
                       help=('add a character with id, name and sp number of '
                       'support characters. Attack / defense stance entry '
                       'will be added by default'),
                       metavar=('id', 'name', 'sp'))
    group.add_argument('-c', '--chapter', action='append', nargs=2,
                        help='add a chapter', metavar=('id', 'name'))
    group.add_argument('-j', '--class', action='append', dest='class_args',
                        nargs=2, help='add a class', metavar=('id', 'name'))
    parser.add_argument('-s', '--support', nargs='?', default=None,
                        help=('generate support module for character at '
                        'index i. If this argument is used with --character, '
                        'generate module for the new character (i will be '
                        'ignored)'), metavar='i')
    args = parser.parse_args()

    arg_list = None
    if args.chapter:
        arg_list = args.chapter
        data_type = 'Chapter'
    if args.character:
        arg_list = args.character
        data_type = 'Character'
    if args.class_args:
        arg_list = args.class_args
        data_type = 'Class'
    if args.item:
        arg_list = args.item
        data_type = 'Item'

    if arg_list != None: # Adding something
        # Get data IDs and names from the arguments
        ids = []
        names = []
        for data in arg_list:
            try:
                if data[0].startswith('0x'):
                    ids.append(int(data[0], 16))
                else:
                    ids.append(int(data[0]))
            except ValueError:
                print('Data ID must be an integer.')
                exit()
            names.append(data[1])

        # Add new data to GameData.bin
        game_data = gamedata.load_file('GameData.bin')
        if args.character is None:
            game_data.append(data_type, ids, names)

        else: # Add character
            supports = []
            for data in arg_list:
                supports.append(int(data[2]))
            game_data.append_character(ids, names, supports)
            if args.support: # Generate support module
                info = game_data.get_table_info('Character')
                chcount = unpack('<H', info.count_offset)[0]
                for i in xrange(1, len(names)):
                    generate_support_module(game_data, chcount - i)

        game_data.format()
        with open('GameData.bin', 'wb') as file:
            file.write(game_data.tobin())

        update_modules(data_type, ids, names) # Update some modules
        fix_module_offsets(game_data, data_type) # Fix some modules' offsets
        print('Added %d %s(s) to GameData.bin.' % (len(ids), data_type))

    elif args.support != None:
        game_data = gamedata.load_file('GameData.bin')
        try:
            spdir = generate_support_module(game_data, int(args.support))
            print('Support module "' + spdir + '" was generated.')
        except KeyError:
            print('The character at index %s has no support.' % args.support)

    else:
        exit()
