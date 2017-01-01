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

Planned features:
- Add character support, attack / defensive stance table.

Important note:
Please note that this tool doesn't automatically add text, sprites, models to
other file for you. If you want a new characters, classes, etc. to work
properly, you also need to manually change other files.

Usage:
    python gamedata_module.py [--option id name] ...

``option``: "chapter", "character", "class", "item" are available options.
``id``: ID of the new data. Must be an integer.
``name``: Name of the new data, which is used for label.

Example:
    python gamedata_module.py --item 400 ABC --item 401 DEF
will add two new items which had their IDs 400 and 401, respectively. IID_ABC
and IID_DEF will be used as a label for those items.
"""


import os
import sys

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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--item', action='append', nargs=2, help='add an item')
    group.add_argument('--character', action='append', nargs=2, help='add ' +
                        'a character without support')
    group.add_argument('--chapter', action='append', nargs=2, help='add a ' +
                        'chapter')
    group.add_argument('--class', action='append', dest='class_args',
                        nargs=2, help='add a class')
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
    if arg_list == None:
        exit()

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
            print 'Data ID must be an integer.'
            exit()
        names.append(data[1])

    # Add new data to GameData.bin
    game_data = gamedata.load_file('GameData.bin')
    game_data.append(data_type, ids, names)
    game_data.format()
    with open('GameData.bin', 'wb') as file:
        file.write(game_data.tobin())

    # Update some modules
    update_modules(data_type, ids, names)
    
    # Fix some modules' offsets
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
        
    # Output
    print 'Added ' + str(len(ids)) + ' ' + data_type + '(s) to GameData.bin.'
