# fefates-tools
A collection of Nightmare modules and small tools for Fire Emblem Fates. It is a compilation of my own research along with data from various source.

# About Nightmare
It's a program that allow you to easily hex edit data files using modules. This is the traditional of Fire Emblem ROM hacking community.
Because Nightmare only allow editing fixed byte array, you can't add stuff to the game or change pointers in data files with this method. To add stuff to the game, you need basic knowledge of pointers in the data files.
A Nightmare module (.nmm file) is just a text file that determine data structure and where to edit in the data files. To understand .nmm file format, please read the README.txt file in Nightmare 2 zip.

# Requirements
* A way to decrypt the game and extract the game's files.
* Nightmare: [here](http://serenesforest.net/forums/index.php?showtopic=26737) or [here](http://www.romhacking.net/utilities/610/)
* [Python 2.7](https://www.python.org/download).

# Instructions
## Decrypting
* Main game: [This guide](http://gbatemp.net/threads/383055/) is a good start.
* DLC: [Here](http://gbatemp.net/threads/397560/page-5#post-5906138).

## Editing
* All .lz files can be decompressed using [FEAT](https://github.com/SciresM/FEAT/releases).
* How to use modules and tools:
  * To use Nightmare modules, you need to open certain file with its respective module file (.nmm). Please read README.md in the folder of each module for more details.
  * fst_generator.py: Drag and drop your folder that contains your files in DLC to this folder.
* After editing, you can use BatchLZ77, DSDecmp4, or lzx to recompress the edited file.

## Applying the patch
You can use one of the following methods:
* Use [NTR CFW](https://github.com/44670/BootNTR/releases)'s LayeredFS plugin.
* Rebuild RomFS with [RomFS Builder](https://github.com/SciresM/RomFS-Builder/releases) to use with [HANS](https://smealum.github.io/3ds).
* Rebuild 3DS or CIA to use with Gateway 3DS or CFW.

# List of modules and tools
## Modules
* Character
* Class
* Item
## Tools
* fst_generator.py: Generates fst.bin file for Fire Emblem Fates DLC. It is used for custom DLC (like DeathChaos25's DLC)
## Data files
* GameData.bin

# Special thanks
* SciresM, for [FEAT](https://github.com/SciresM/FEAT).
* VincentASM, for his [awesome website](http//serenesforest.net).
* Hextator, for Nightmare 2.
