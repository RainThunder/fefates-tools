# fefates-tools
A collection of Nightmare modules and small tools for Fire Emblem Fates.

# About Nightmare
Nightmare is a program that allow you to easily hex edit the data files using modules. With Nightmare, even those who don't have any knowledge in data structure and hex editing are able to edit the game's files and make some cool stuff. Nightmare is the tradition of Fire Emblem ROM hacking community.

A Nightmare module (.nmm file) is just a text file which defines structure in a data file.

Because Nightmare only allows editing fixed-size data, you can't add any new stuff into the game via these modules. However, based on the information in .nmm files, with some basic knowledge of [.bin file format](https://github.com/RainThunder/fefates-tools/wiki/BIN-(File-Format)), you definitely can add something new to the game.

# Requirements
* A way to decrypt the game and extract the game's files. Currently, any 3DS with CFW or homebrew access will be able to do this. For instructions, see below.
* Nightmare: [here](http://serenesforest.net/forums/index.php?showtopic=26737) or [here](http://www.romhacking.net/utilities/610/). Nightmare 2 is recommended.
* [FEAT](https://github.com/SciresM/FEAT/releases), for decompressing .lz files.
* [BatchLZ77](http://filetrip.net/nds-downloads/utilities/download-batchlz77-1-3-f11736.html) / [DSDecmp4](http://www.romhacking.net/utilities/789/) / [lzx](http://www.romhacking.net/utilities/826/) to recompress the edited file. I'm not sure if those tools work on other operating systems than Windows. lzx is open-source and written in C, so you might be able to compile it for other OSes.
* If you want to run .py script, you need [Python 2.7](https://www.python.org/download).

# Download
https://github.com/RainThunder/fefates-tools/archive/master.zip

# Instructions
## Decrypting
* [This guide](https://github.com/ihaveamac/3DS-rom-tools/wiki) or [this guide](http://gbatemp.net/threads/383055/) is a good start.
* Alternatively, you can download xorpads or decrypted ROMs on "that iso site", or use the provided files in this repository.

## Editing
* All .lz files can be decompressed using FEAT (there are still some error that need to be fixed soon).
  * Just drag and drop .lz file into FEAT window.
* How to use modules and tools:
  * To use Nightmare modules, you need to open certain file with its respective module file (.nmm). Please read README.md in the folder of each module for more details.
  * fst_generator.py: Drag and drop your folder that contains your DLC files to this script.
* After editing, you can use BatchLZ77 / DSDecmp4 / lzx to recompress your edited files.
  * DSDecmp4: Type `DSDecmp4 -c lz11 file.bin` in the command line (file.bin is the name of the file that need to be compressed)
  * lzx: Type `lzx -evb file.bin` in the command line.
  * BatchLZ77:
    * Click *Options* -> *LZ77 Type 11*
    * Click *File* -> *Compress Files...*
    * Choose your edited file, then click *Open*.
    * Your edited file will be compressed to *.bin.compressed. Rename it to *.bin.lz.
  
## Applying the patch
* Main game: You can use one of the following methods:
  * Use [NTR CFW](https://github.com/44670/BootNTR/releases)'s LayeredFS plugin.
  * Rebuild entire RomFS folder with [RomFS Builder](https://github.com/SciresM/RomFS-Builder/releases) to use with [HANS](https://smealum.github.io/3ds).
  * Rebuild 3DS or CIA to use with Gateway 3DS or CFW. Again, [the guide that was mentioned above](http://gbatemp.net/threads/383055/) is okay to follow.
* DLC: [Here](http://gbatemp.net/threads/397560/page-5#post-5906138).

# List of modules and tools
## Modules
* Character
* Character (A_HANDOVER): Modify character data that will be used in Birthright path.
* Character (B_HANDOVER): Modify character data that will be used in Conquest path.
* Character (C_HANDOVER): Modify character data that will be used in Revelation path.
* Class
* Item
* Chapter
* Weapon Rank
* Path Bonus
* Visit Bonus
* Battle Bonus
* Dispos

## Tools
* fst_generator.py: Generates fst.bin file for Fire Emblem Fates DLC. It is used for custom DLC (like DeathChaos25's DLC)

## Data files
* GameData.bin
* A_HANDOVER.bin
* B_HANDOVER.bin
* C_HANDOVER.bin

# Documentation
* General Fire Emblem Fates ROM hacking: https://github.com/RainThunder/fefates-tools/wiki
* Nightmare file format: http://feuniverse.us/t/nightmare-module-format-explained/267, or the text file in the Nightmare 2 download.

# Special thanks
* SciresM, for [FEAT](https://github.com/SciresM/FEAT).
* VincentASM, for his [initial data mining](http://serenesforest.net/fire-emblem-fates).
* Hextator, for Nightmare 2.
* DeathChaos25, for his contributions.
