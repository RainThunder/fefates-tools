# About Dispos directory
In Fire Emblem Fates, GameData/Dispos directory contains unit distribution on every map. All maps are named after the following pattern: `<map-prefix><index><map-suffix>`.

| Map prefix | Description |
| --- | --- |
| A | Birthright |
| B | Conquest |
| C | Revelation |
| X | Paralogue |
| E | DLC |
| P | Branch chapter |
| Y | Castle invasion |
| Z | Debug |

| Map suffix | Description |
| --- | --- |
| E | Scout |
| V | Versus |

For example, B025 is Conquest chapter 25.

# How to use these modules
Open the .bin file with its respective .nmm file.

# Flag guide
## Unit flags

| Flags | Description |
| --- | --- |
| 1 | |
| 2 | |
| 3 | |
| 4 | This unit must participate the map |
| 5 | |
| 6 | |
| 7 | |
| 8 | Preset unit |
| 9 | Normal difficulty |
| 10 | Hard difficulty |
| 11 | Lunatic difficulty |
| 12 | |
| 13 | |
| 14 | |
| 15 | |
| 16 | |

## Item flags

| Flags | Description |
| --- | --- |
| 1 | Droppable |
| 2 | |
| 3 | |
| 4 | |
| 5 | |
| 6 | |
| 7 | |
| 8 | |
| 9 | |
| 10 | |
| 11 | |
| 12 | |
| 13 | |
| 14 | |
| 15 | |
| 16 | |

## Skill flags

| Flags | Description |
| --- | --- |
| 1 | Skill 1 is available on Normal difficulty |
| 2 | Skill 1 is available on Hard difficulty |
| 3 | Skill 1 is available on Lunatic difficulty |
| 4 | Skill 2 is available on Normal difficulty |
| 5 | Skill 2 is available on Hard difficulty |
| 6 | Skill 2 is available on Lunatic difficulty |
| 7 | Skill 3 is available on Normal difficulty |
| 8 | Skill 3 is available on Hard difficulty |
| 9 | Skill 3 is available on Lunatic difficulty |
| 10 | Skill 4 is available on Normal difficulty |
| 11 | Skill 4 is available on Hard difficulty |
| 12 | Skill 4 is available on Lunatic difficulty |
| 13 | Skill 5 is available on Normal difficulty |
| 14 | Skill 5 is available on Hard difficulty |
| 15 | Skill 5 is available on Lunatic difficulty |

# AI labels
AI labels are used in dispos file to indicate AI behavior. Here is all labels available throughout all the dispos files:

* AI_AC: AI_AC_Area, AI_AC_AttackRange, AI_AC_AttackRangeExcludePerson, AI_AC_BandRange, AI_AC_Everytime, AI_AC_Null, AI_AC_Turn, AI_AC_TurnAttackRange.  
* AI_MI: AI_MI_BreakDown, AI_MI_Escape, AI_MI_Null, AI_MI_Talk, AI_MI_Transform, AI_MI_Treasure, AI_MI_Village.
* AI_AT: AI_AT_Attack, AI_AT_AttackToHeal, AI_AT_B025, AI_AT_CastleDestroy, AI_AT_CastleOffense, AI_AT_ExcludeBand, AI_AT_ExcludePerson, AI_AT_Heal, AI_AT_HealToAttack, AI_AT_Hero, AI_AT_HeroOnly, AI_AT_Idle, AI_AT_MustAttack, AI_AT_Null, AI_AT_Person, AI_AT_PersonOnly, AI_AT_TrapRelease.
* AI_MV: AI_MV_B009, AI_MV_B028, AI_MV_BreakDown, AI_MV_CastleOffense, AI_MV_Escape, AI_MV_Force, AI_MV_ForceExcludePerson, AI_MV_Hero, AI_MV_HeroOnly, AI_MV_NearestEnemy, AI_MV_NearestEnemyExcludePerson, AI_MV_NearestHeal, AI_MV_Null, AI_MV_Person, AI_MV_Position, AI_MV_TrapRelease, AI_MV_TrasureToEscape, AI_MV_VillageToAttack, AI_MV_WeakEnemy, AI_MV_WeakEnemySide.

Parameters for each label still need to be documented.

# Modification
Due to how Intelligent Systems design the dispos files (with many labels and pointers), in-place modification for those files is pretty limited. To change items, skills, AI modes, add units (i.e. expand the dispos files via hex editing), read [here](https://github.com/RainThunder/fefates-tools/wiki/BIN-(File-Format)). 