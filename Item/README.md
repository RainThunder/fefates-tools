# How to use
Run Nightmare, then open GameData.bin file with Item.nmm file.

# Flag guide
## Main flags (1 - 64)
| Flag Index | Flag ID | Meaning |
| --- | --- | --- |
| 1 | ISID_使用可能 | Can be used via "Use" menu |
| 2 | ISID_魔法武器 | Magic weapon |
| 3 | ISID_遠距離 | Long distance weapon |
| 4 | ISID_効果+魔力/3 | Effect + Magic / 3 |
| 5 | ISID_特効無効 | Special effect is disabled |
| 6 | ISID_宝箱鍵 | Chest Key |
| 7 | ISID_扉鍵 | Door Key |
| 8 | ISID_貴重品 | Valuables |
| 9 | ISID_外せない | Cannot be unequipped |
| 10 | ISID_章限定 | Chapter limited |
| 11 | ISID_神武器 | Regalia |
| 12 | ISID_無限回数 | Infinite uses |
| 13 | ISID_装備自動回復 | HP regen |
| 14 | ISID_吸収半分 | Absorb HP |
| 15 | ISID_基本杖 | Basic staff |
| 16 | ISID_回復杖 | Recovery staff |
| 17 | ISID_妨害杖 | Interference staff |
| 18 | ISID_特殊杖 | Special staff |
| 19 | ISID_プレイヤー専用 | Avatar only |
| 20 | ISID_ダークマージ系専用 | Dark Mage only |
| 21 | ISID_男性専用 | Men only |
| 22 | ISID_女性専用 | Women only |
| 23 | ISID_錬成不可 | Cannot be forged |
| 24 | ISID_敵専用 | Enemy only |
| 25 | ISID_強制オンバト |  |
| 26 | ISID_通信譲渡禁止 | Cannot be used in communication |
| 27 | ISID_即換金 | Gold |
| 28 | ISID_必殺奥義禁止 | Cannot crit |
| 29 | ISID_追撃禁止 | Cannot double |
| 30 | ISID_非特効時威力－ | Lower Mt if ineffectively used |
| 31 | ISID_非特効時命中－ | Lower Hit if ineffectively used |
| 32 | ISID_必殺倍率＋ | Damage x4 for crit |
| 33 | ISID_戦闘後能力減少 | Lower stats after battle |
| 34 | ISID_戦闘後能力半減 | Halves stats after battle |
| 35 | ISID_3すくみ反転 | Reverse weapon triangle |
| 36 | ISID_攻撃時2回攻撃 | Strike twice when attacking |
| 37 | ISID_攻撃時武器威力2倍 | Mt x2 when attacking |
| 38 | ISID_反撃時武器威力2倍 | Mt x2 during counterattacking |
| 39 | ISID_技勝利時武器威力2倍 | Mt x2 if Skill is higher than enemy's Skill |
| 40 | ISID_剣特効 | Sword slayer |
| 41 | ISID_槍特効 | Lance slayer |
| 42 | ISID_斧特効 | Axe slayer |
| 43 | ISID_魔法特効 | Magic slayer |
| 44 | ISID_常備薬 | Medicines |
| 45 | ISID_所持強化 | Possession effect |
| 46 | ISID_風神弓 | Fujin Yumi |
| 47 | ISID_ブリュンヒルデ | Brynhildr |
| 48 | ISID_タクミ専用 | Takumi only |
| 49 | ISID_リョウマ専用 | Ryoma only |
| 50 | ISID_レオン専用 | Leo only |
| 51 | ISID_マークス専用 | Xander only |
| 52 | ISID_追い剥ぎ | Strips clothes |
| 53 | ISID_戦闘後叫び | Rally after battle |
| 54 | ISID_戦闘後HP変化 | Changes user's HP after combat |
| 55 | ISID_戦闘後対象HP変化 | Changes target's HP after combat |
| 56 | ISID_暗器 | Hidden weapon |
| 57 | ISID_祈り | Miracle |
| 58 | ISID_手加減 | Enemy survive with 1 HP |
| 59 | ISID_地形効果無効 | Ignores terrain effects on combat |
| 60 | ISID_薬効果自分 | Affect user |
| 61 | ISID_薬効果対象 | Affect ally |
| 62 | ISID_回復効果自分 | Self recovery staff |
| 63 | ISID_竜鱗有効 | Dragon scale effect (for Yato) |
| 64 | ISID_オフェリア専用 | Ophelia only |

## Special flags (1 - 12)
Determine weapon advantages and special weapons. They are the same as special flags in class data.

| Flag Index | Flag ID | Meaning |
| --- | --- | --- |
| 1 | JCID_飛行 | Flier |
| 2 | JCID_竜 | Dragon |
| 3 | JCID_獣 | Beast |
| 4 | JCID_アーマー | Armor |
| 5 | JCID_魔物 | Claw (Monster classes only) |
| 6 | JCID_人形 | Saw (Automaton classes only) |
| 7 | JCID_マムクート | Dragonstones (Manakete classes only) |
| 8 | JCID_ラグズ | Beaststones (Wolves / Foxes only) |
| 9 | JCID_騎乗 | Mounted |
| 10 | JCID_ダークマージ | Dark tomes (Dark Mage, Sorcerer, Witch) |
| 11 | JCID_変身 | Breath (Dragon classes only) |
| 12 | JCID_シューター | Ballistician |

# Extra bytes
They are called "Extra" in this module. The following list may not cover everything, but you will get the idea.
* For most items, 8 extra bytes is stat bytes, following the normal order (HP / Str / Mag / Skl / Spd / Lck / Def / Res).
  * For Daggers, Shurikens, Saws, Enfeeble and all weapons that can be used to debuff the enemy (i.e. have flag 56), the extra bytes are debuff stats.
  * For all weapons that change HP after combat (i.e. have flag 54 and 55, like Spirit Katana, Moonlight, Berserker's Axe, etc.), the first byte is HP percent. They are different than the weapons that can be used via "Use" command to heal HP (like Sheep Spirit, etc.).
  * For all weapons that give user some bonuses while in possession, the extra bytes are stat bonuses.
  * For all items that have the same effect as **Rally** command (e.g. Violin Bow, Allegro Harp, etc.), the first byte determined which Rally is used. 0x1 is Rally Strength, 0x2 is Rally Magic, etc. If the sign of the first byte is reversed, Rally effect will be applied to the enemy team, e.g. 0xFC (-4) is Rally Speed for the enemy.
  * For all items that change user's stats when choosing **Use** command (e.g. Sheep Spirit, Vulnerary, Tonics, Statboosters etc.), the extra bytes are stats, obviously.
* For class-changing Seals, the first byte determines Seal type. If the first byte is 0x5, the second and third byte will determine class. For example, 8 extra bytes for Dread Scroll are `05 76 00 00 00 00 00 00` (76 is class ID of Dread Fighter class).

| Value | Meaning |
| --- | --- |
| 0x0 | Master Seal |
| 0x1 | Heart Seal |
| 0x2 | Partner Seal |
| 0x3 | Friendship Seal |
| 0x4 | Eternal Seal |
| 0x5 | Custom Seal |
* For skill items, the first byte is skill ID, and the second byte is level limit. E.g. Aether: `1A 19 00 00 00 00 00 00`
* Special staff: Candy Cane, Mushroom Staff, Bouquet Staff.