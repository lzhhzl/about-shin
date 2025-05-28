fontdb, the database for tile font format

# PC
|  Game Name | Game ID | File | Plugin | Format | Note | Preview |
|  ----      | ----    | ---- | ----   | ---    | ---  | ---     |
| 祝姫 | vndb-v17863 | [font48.xtx](https://github.com/user-attachments/assets/7ae71bd7-3581-4bb1-a295-5c8e6a2cec0e) | [iwaihime_xtx.lua](https://github.com/YuriSizuku/TileViewer/blob/master/asset/plugin/iwaihime_xtx.lua)| - | swizzle in each block | [font48.xtx.png](https://github.com/user-attachments/assets/9241a178-2453-4bb1-afc5-b4910434ddb0)|
| 百花百狼 戦国忍法帖 | vndb-v17287| [font0.img](https://github.com/user-attachments/assets/ed4b9755-e224-43e6-86a0-953b8ed6f7d0) | - | --width 34 --height 34 --bpp 4 | - | [font0.img.png](https://github.com/user-attachments/assets/09a4b1df-86ff-4df9-9f87-693c121515f6)|

# PSP
|  Game Name | Game ID | File | Plugin | Format | Note | Preview |
|  ----      | ----    | ---- | ----   | ---    | ---  | ---     |
| らき☆すた〜陵桜学園 桜藤祭 | ULJM05752 | [it.bin](https://github.com/YuriSizuku/TileViewer/blob/master/asset/sample/it.bin) | - |  --width 20 --height 18 --bpp 2 --nbytes 92 | - | [it.bin.png](https://github.com/YuriSizuku/TileViewer/raw/master/asset/picture/tile_test1.png) |
| 薔薇ノ木ニ薔薇ノ花咲ク | ULJM05802 | [MINTYOU16.FNT](https://github.com/user-attachments/assets/9aae85bb-98d7-4c8a-9d08-ee9d442dda11) | [baranoki_fnt_psp.lua](https://github.com/YuriSizuku/TileViewer/blob/master/asset/plugin/baranoki_fnt_psp.lua) | - | non monospace | [MINTYOU16.FNT.png](https://github.com/user-attachments/assets/063089b0-e375-4478-a8de-70e698e7e64f)
| 金色のコルダ | ULJM05054 | [Out16.bin](https://github.com/user-attachments/assets/416f6e32-9211-4dc0-ac30-9b14fb907948) | - | --width 16 --height 16 --bpp 4 | - | [Out16.bin.png](https://github.com/user-attachments/assets/2064393d-680e-476b-a03f-f65bb833af74) |
| JewelicNightmare | ULJM06326 | [380](https://github.com/user-attachments/assets/09fb9c80-58df-48da-a4fc-2b918d67c1da) | - | --width 18 --height 18 --bpp 4 --start 66263 --pluginparam "{'endian': 1}" | - | [380.png](https://github.com/user-attachments/assets/92c55420-01a4-4236-8d95-589c810b8524) |
| 神々の悪戯 | NPJH50809 | [FontA000.txp](https://github.com/user-attachments/assets/9064df52-11c2-4bd5-8393-53e889c1d795) | - | --width 32 --height 8 --bpp 4 --nrow 9 --start 80 | as a puzzle, nrow and tilew, tileh are important | [FontA000.txp.png](https://github.com/user-attachments/assets/9a873238-1b89-4c40-9343-f777a8e777d2) |

# PSV
|  Game Name | Game ID | File | Plugin | Format | Note | Preview |
|  ----      | ----    | ---- | ----   | ---    | ---  | ---     |
| Air | PCSG00940 | [mdnp32.fnt](https://github.com/user-attachments/assets/e3f0b6f1-2e83-4988-8d07-2f6d12630ea4) | - |  --width 32 --height 32 --bpp 4 --start 14256 --pluginparam "{'endian': 1}" | - | [mdnp32 fnt.png](https://github.com/user-attachments/assets/1a304d55-1b69-4c80-b36d-37c8d1165a69) |
| Cross Channel | PCSG00365 | [font32 vtx](https://github.com/user-attachments/assets/63b7721b-c9b1-4148-a8dd-ca3bb1f63b54) | - | --width 32 --height 32 --bpp 4 --start 128 | - | [font32.vtx.png](https://github.com/user-attachments/assets/b361bd13-01a1-4d9a-9bae-43b49b103ac1) |
| この素晴らしい世界に祝福を | PCSG01265 | [font_a_42.gof](https://github.com/user-attachments/assets/207393db-9595-4eb7-8020-ca996ae2ae26) | [konosuba_gof_psv.lua](https://github.com/YuriSizuku/TileViewer/blob/master/asset/plugin/konosuba_gof_psv.lua) | - | non monospace | [font_a_42.gof.png](https://github.com/user-attachments/assets/05ab1c67-5236-459e-85f2-53ef4ea83315)|
| はつゆきさくら | PCSG00997 | [font_00.fnt.7z]() | [hatsuyuki_fnt_psv.lua](https://github.com/YuriSizuku/TileViewer/blob/master/asset/plugin/hatsuyuki_fnt_psv.lua) | - | lz77 on each glphy, FNT4 old version | [font_00.fnt.png]()|.

# SWITCH
|  Game Name | Game ID | File | Plugin | Format | Note | Preview |
|  ----      | ----    | ---- | ----   | ---  | ---  | ---     |
| アサツグトリ | 010060301588A000 | [font_type1.nltx.dec.7z](https://github.com/user-attachments/assets/f0af7d6d-a805-412a-b0a0-bce970e61e45) | [yomawari3_nltx_switch.lua](https://github.com/YuriSizuku/TileViewer/blob/master/asset/plugin/yomawari3_nltx_switch.lua) | --width 4096 --height 4096 --pluginparam "{'block_height': 16}" | tegra swizzle format, need to decompress ykcmp in advance |  [font_type1.nltx.dec.png](https://github.com/user-attachments/assets/18f1561d-9baf-42ef-b36a-609a2c9a1ebe) |
| 9nine | 01005CE015CA2000 | [font_00.fnt.7z](https://github.com/user-attachments/assets/fb0203b7-1f8f-46ee-9873-2405b415d889) | [9nine_fnt_switch.lua](https://github.com/YuriSizuku/TileViewer/blob/master/asset/plugin/9nine_fnt_switch.lua) | - | lz77 on each glphy | [font_00.fnt.png](https://github.com/user-attachments/assets/3a3287a2-e7d6-4d90-bb6a-d651ef36a473) |

# SEGA SATURN
|  Game Name | Game ID | File | Plugin | Format | Note | Preview |
|  ----      | ----    | ---- | ----   | ---    | ---  | ---     |
|機動戦艦ナデシコ The blank of 3 years| GS9195 | END26.FNT | -| --width 26 --height 26 --bpp 3 --nbytes 255 --start 32 --pluginparam "{'endian': 1}" | - | [END26.FNT.png](https://github.com/user-attachments/assets/ada58e1a-6bb9-4ddb-afbb-58ae3da6c6a5)|
|機動戦艦ナデシコ The blank of 3 years| GS9195 | ZI24.FNT | -| --width 24 --height 24 --bpp 2 --pluginparam "{'endian': 1}" | - | [ZI24.FNT.png](https://github.com/user-attachments/assets/624c27aa-d26a-4653-bceb-ab1ee2a8c9f1)|

