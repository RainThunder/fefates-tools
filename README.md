# fefates-tools
A collection of Nightmare modules and small tools for Fire Emblem Fates.

# About Nightmare
Nightmare is a program that allow you to easily hex edit the data files using modules. With Nightmare, even those who don't have any knowledge in data structure and hex editing are able to edit the game's files and make some cool stuff. Nightmare is the tradition of Fire Emblem ROM hacking community.

A Nightmare module (.nmm file) is just a text file which defines structure in a data file.

Because Nightmare only allows editing fixed-size data, you can't add any new stuff into the game via these modules. However, based on the information in .nmm files, with some basic knowledge of [.bin file format](https://github.com/RainThunder/fefates-tools/wiki/BIN-(File-Format)), you definitely can add something new to the game.

# Requirements
* A way to decrypt the game and extract the game's files. Currently, any 3DS with CFW or homebrew access is able to do this. For instructions, see below.
* Nightmare: [here](http://serenesforest.net/forums/index.php?showtopic=26737) or [here](http://www.romhacking.net/utilities/610/). Nightmare 2 is recommended.
* [FEAT](https://github.com/SciresM/FEAT/releases), for decompressing .lz files.
* [BatchLZ77](http://filetrip.net/nds-downloads/utilities/download-batchlz77-1-3-f11736.html) / [DSDecmp4](http://www.romhacking.net/utilities/789/) / [lzx](http://www.romhacking.net/utilities/826/) to recompress the edited file. I'm not sure if those tools work on other operating systems than Windows. lzx is open-source and written in C, so you might be able to compile it for other OSes.
* If you want to run .py script, you need [Python](https://www.python.org/download). Both Python 2 and Python 3 are supported.

# Download
https://github.com/RainThunder/fefates-tools/archive/master.zip

# List of modules, tools and files
## Modules
* Chapter
* Character
* Character (A_HANDOVER): Modify character data that will be used in Birthright path.
* Character (B_HANDOVER): Modify character data that will be used in Conquest path.
* Character (C_HANDOVER): Modify character data that will be used in Revelation path.
* Class
* Skill
* Stat
* Army (practically useless)
* Item
* Forge
* Tutorial (practically useless)
* Weapon Rank
* Path Bonus
* Visit Bonus
* Battle Bonus
* Dispos

## Tools
* **fst_generator.py**: Generates fst.bin for Fire Emblem Fates custom DLC.
* **arc.py**: Extract and repack .arc files.
* **gamedata_module.py**: Add new data to GameData.bin and automatically update all modules to reflect the changes. This tool is a workaround for Nightmare limitations.
* **trim.py**: Trim the padding bytes caused by Nightmare 2.
* **castle_join.py**: Convert castle_join.bin to tab-delimited text file and vice versa.

## Data files
* GameData.bin
* A_HANDOVER.bin
* B_HANDOVER.bin
* C_HANDOVER.bin
* Dispos files

# Instructions
## Decrypting
* [This guide](https://github.com/ihaveamac/3DS-rom-tools/wiki) or [this guide](http://gbatemp.net/threads/383055/) is a good start.
* Alternatively, you can download xorpads or decrypted ROMs / CIAs on other sites, or use the provided files in this repository.

## Editing
* All *.lz* files can be decompressed using **FEAT** (there are still some error that need to be fixed soon).
  * Just drag and drop .lz file into FEAT window.
* How to use the modules and tools:
  * For Nightmare modules, you need to open certain .bin file with its respective module file (.nmm). Please read **README.md** in each module's folder for more details.
  * For tool usage, see [https://github.com/RainThunder/fefates-tools#using-the-tools](Using the tools)
* After editing, drag and drop your modified file(s) to **trim.py**, then run **BatchLZ77** / **DSDecmp4** / **lzx** to recompress your edited file(s).
  * **DSDecmp4**: Type `DSDecmp4 -c lz11 file.bin` in the command line (file.bin is the name of the file that need to be compressed)
  * **lzx**: Type `lzx -evb file.bin` in the command line.
  * **BatchLZ77**:
    * Click *Options* -> *LZ77 Type 11*
    * Click *File* -> *Compress Files...*
    * Choose your edited file, then click *Open*.
    * Your edited file will be compressed to *.bin.compressed. Rename it to *.bin.lz.
  
## Applying the patch
* Main game: You can use one of the following methods:
  * Use [NTR CFW](https://github.com/44670/BootNTR/releases)'s LayeredFS plugin.
  * Rebuild entire RomFS folder with [RomFS Builder](https://github.com/SciresM/RomFS-Builder/releases) to use with [HANS](https://smealum.github.io/3ds).
  * Rebuild 3DS or CIA to use with Gateway 3DS or CFW. Read one of the guide that was mentioned above for more details.
* DLC: The instructions can be found [here](http://gbatemp.net/threads/397560/page-5#post-5906138).

## Using the tools:
* **fst_generator.py**: Drag and drop your folder that contains your DLC files to this script.
* **arc.py**: Extract and repack .arc files.
  * For Windows:
    * To extract an .arc file, drag and drop it to the arc.bat script.
    * To repack a folder, drag and drop the folder to the arc.bat script.
  * For other OSes:
    * Open the Terminal.
	* Type `python arc.py file.arc` to extract a file named "file.arc".
	* Type `python arc.py folder` to pack a folder named "folder" to an .arc file with the same name.
* **gamedata_module.py**: `python gamedata_module.py [--option id name] ...`
  * Arguments:
	* `option`: "chapter", "character", "class", "item" are available options.
	* `id`: ID of the new data. Must be an integer.
	* `name`: Name of the new data, which is used for label.
  * Example:
    * `python gamedata_module.py --item 405 ABC --item 406 DEF`: Adding two items, which takes 405 and 406 as IDs and IID_ABC and IID_DEF as labels, respectively.
* **trim.py**: Drag and drop the padded files to this script, or if you prefer the command line: `python trim.py files [files ...]`.
* **castle_join.py**: Drag and drop castle_join.bin / castle_join.txt to this script.
  * Legacy tool (Python 2 only) can be found [here](https://gist.github.com/RainThunder/e547462df8bfdcc3cc5af0786a74f6ee).

# See also
* General Fire Emblem Fates ROM hacking documentation: https://github.com/RainThunder/fefates-tools/wiki
* Fire Emblem Fates ROM Hacking General Thread: https://gbatemp.net/threads/fire-emblem-fates-rom-hacking-general-thread.434509/
* Nightmare file format: http://feuniverse.us/t/nightmare-module-format-explained/267, or the text file in the Nightmare 2 zip.

# Special thanks
* SciresM, for [FEAT](https://github.com/SciresM/FEAT).
* VincentASM, for his [initial data mining](http://serenesforest.net/fire-emblem-fates).
* Hextator, for Nightmare 2.
* DeathChaos25, for his contributions.
