# about-shin

collect some tools and projects for shin engine——a game engine used by some visual novels released by [Entergram](http://www.entergram.co.jp/) on Nintendo Switch, PS4 and PS Vita.

For now, this repo is mainly aim to help making localization mod for games.

## File Format

Usually, you can find those file-formats similar to the following in the rom of the game which use shin engine:

- `.bup` - Character sprites
- `.pic` - Backgrounds & CGs
- `.nxa` - Game audio
- `.snr` - game scenario
- `.fnt` - Font data
- `.txa` - Texture archives (used mostly for UI)

You might also find other format files but relevant: `sysse.bin` `.msk` and so on...

## about FNT4 Font

The main Font(magic `FNT4`) file use in shin-engine, name e.g.`default.fnt` `font_00.fnt`, is basically composed of LZ77(variant, more like LZSS) compressed glyphs based on Unicode/Shift-Jis encoding. For now, we find that it has two version:

- FNT4 v1
- FNT4 v0 (older format)

I also made my own tool about fnt for Konosuba(PCSG01258 psvita) localization mod. You can made your own tool for analysing shin engine game based on this. Also welcome to raise issue if you have any questions.

There are some other games with different engine released by Entergram that also use the FNT4 struct font file:

| title id | name |
|---|---|
|PCSG00997|はつゆきさくら|
|01003A6013486000|金色ラブリッチェ-Golden Time-|
|0100FE001327C000|金色ラブリッチェ|
|0100D1A014A4A000|かけぬけ★青春スパーキング！|
|01005CE015CA2000|9-nine-|

## Thanks

Although I only cloned a few of the main related projects for this repo, there are still other useful ones also list below. Without these great projects and analyses, the localization work in shin-engine would not be possible:

- [shin](https://github.com/DCNick3/shin), [ShinDataUtil](https://github.com/DCNick3/ShinDataUtil), [shin-translation-tools](https://github.com/DCNick3/shin-translation-tools) by [DCNick3](https://github.com/DCNick3), He did a lot of work in this engine, Really awesome and Appreciated!!!
- [kaleido](https://gitlab.com/Neurochitin/kaleido) by Neurochitin, has support for scenario translation of vita's umineko and vita/switch's Kaleido. There's also a generate-FNT code prototype in it.
- [9nine_switch_fnt analysis in GalgameReverse](https://github.com/YuriSizuku/GalgameReverse/blob/master/project/entergram/src/9nine_switch_fnt.py) by my friend(and teacher) [YuriSizuku](https://github.com/YuriSizuku), he used to help imKota to [analyze](https://github.com/YuriSizuku/GalgameReverse/issues/7) the 9nine(switch) font file.
- [enter_extractor](https://github.com/07th-mod/enter_extractor) by [07th-mod](https://github.com/07th-mod), old repo but has support for extraction and patching of most formats across several versions of the engine

## Disclaimer

This repo just collect fan projects to enable unofficial translations of shin-based games or relevant games. It is by no means affiliated with Entergram or any other rightsholder.
