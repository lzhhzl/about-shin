import os
import struct
from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from PIL import Image
import io
import numpy as np

import lz77
import crc32

# debug result when 19968<=unicode<=40959
LOG_ADW, LOG_OFS = [], []
# LOG_ADW = [48]
# LOG_OFS = [(-8, 32), (-8, 48), (-8, 56), (-16, 48), (-16, 56), (-8, 40)]

# Support for FNT4 format, storing bitmap fonts with 4 mip-map levels.

# util functions
class struct_t(struct.Struct):
    """
    base class for pack or unpack struct, 
    _ for meta info, __ for internal info
    """
    def __init__(self, data=None, cur=0, *, fmt=None, names=None) -> None:
        """"
        _meta_fmt: struct format
        _meta_names: method names 
        """
        if not hasattr(self, "_meta_names"): self._meta_names = []
        if not hasattr(self, "_meta_fmt"): self._meta_fmt = ""
        if names: self._meta_names = names
        if fmt: self._meta_fmt = fmt
        super().__init__(self._meta_fmt)
        if data: self.frombytes(data, cur)

    def cppinherit(self, fmt, names):
        if not hasattr(self, "_meta_names"): self._meta_names = names
        else: self._meta_names =  names + self._meta_names
        if not hasattr(self, "_meta_fmt"): self._meta_fmt = fmt
        else: self._meta_fmt += fmt.lstrip('<').lstrip('>')
        
    def frombytes(self, data, cur=0, *, fmt=None) -> None:
        if fmt: vals = struct.unpack_from(fmt, data, cur)
        else: vals = self.unpack_from(data, cur)
        for i, val in enumerate(vals):
            if i >= len(self._meta_names): break
            setattr(self, self._meta_names[i], val)
        self._data = data
    
    def tobytes(self, *, fmt=None) -> bytes:
        vals = []
        names = self._meta_names
        for name in names:
            vals.append(getattr(self, name))
        if fmt: _data = struct.pack(fmt, *vals)
        else: _data = self.pack(*vals)
        return _data

# class Endian(Enum):
#     LITTLE = '<'
#     BIG = '>'

class GlyphMipLevel(IntEnum):
    Level0 = 0
    Level1 = 1
    Level2 = 2
    Level3 = 3

class FontHeader(struct_t):
    def __init__(self, data) -> None:
        """
        version: u32
        fsize: u32
        ascent: u16
        descent: u16
        """
        if data[0x4:0x8]==b"\x01\x00\x00\x00":  # version 1
            super().__init__(data, cur=0, fmt=f'<4s2I2H', 
                names=['magic', 'version', 'fsize', 'ascent', 'descent'])
        else: # seem like have other version
            raise Exception("unknown version in header part")
        # check magic and version
        assert self.magic == b"FNT4", f"Invalid magic number: {self.magic}"
        # assert self.version == 0x01


class GlyphHeader(struct_t):
    '''terms are roughly based on https://freetype.org/freetype2/docs/glyphs/glyphs-3.html
    bearing_x: i8, Distance between the current position of the pen and left of the glyph bitmap
    bearing_y: i8, Distance between the baseline and the top of the glyph bitmap
    actual_width: u8, Width, without padding (glyph bitmap are padded to be a power of 2)
    actual_height: u8, Height, without padding (glyph bitmap are padded to be a power of 2)
    advance_width: u8, Amount of horizontal pen movements after drawing the glyph
    unused: u8, might have been advance_height, but always 0, not like the engine can render text vertically
    texture_width: u8, Width of the texture (should be a power of 2)
    texture_height: u8, Height of the texture (should be a power of 2)
    compressed_size: u16
    '''
    def __init__(self, data: bytes, cur=0):
        super().__init__(data, cur, fmt='<2b6BH',names=[
            'bearing_x', 'bearing_y', 'actual_width', 'actual_height', 'advance_width', 'unused', 'texture_width', 'texture_height', 'compressed_size'
            ])
        assert self.unused == 0


class GlyphInfo:  # inherits from GlyphHeader
    '''bearing_x: i8, Distance between the current position of the pen and left of the glyph bitmap
    bearing_y: i8, Distance between the baseline and the top of the glyph bitmap
    advance_width: u8, Amount of horizontal pen movements after drawing the glyph
    actual_width: u8, Width of the glyph bitmap (w/o padding)
    actual_height: u8, Height of the glyph bitmap (w/o padding)
    texture_width: u8, Width of the texture (should be a power of 2)
    texture_height: u8, Height of the texture (should be a power of 2)'''
    def __init__(self, data:bytes=None, header:GlyphHeader=None, unicode_index=None):
        if not header:
            if data:
                header = GlyphHeader(data)
            else:
                raise Exception("no Glyph data")
        self.bearing_x = header.bearing_x
        self.bearing_y = header.bearing_y
        self.advance_width = header.advance_width
        self.actual_width = header.actual_width
        self.actual_height = header.actual_height
        self.texture_width = header.texture_width
        self.texture_height = header.texture_height
        self.unicode = unicode_index  # true unicode: \u{unicode_index:04x}

    def actual_size(self) -> tuple[int, int]:
        return (self.actual_width, self.actual_height)

    def actual_size_f32(self) -> tuple[float, float]:
        return (float(self.actual_width), float(self.actual_height))

    def texture_size(self) -> tuple[int, int]:
        return (self.texture_width, self.texture_height)

    def actual_size_normalized(self) -> tuple[float, float]:
        return (float(self.actual_width / self.texture_width),
                float(self.actual_height / self.texture_height))

    def bearing_screenspace_f32(self) -> tuple[float, float]:
        # NB: we flip the Y axis, since the engine uses a top-left origin, while font metrics are bottom-left
        return (float(self.bearing_x), float(-self.bearing_y))


class GlyphData:
    def __init__(self, data: bytes, is_compressed: bool):
        self.data = data
        self.is_compressed = is_compressed

    def decompress(self) -> bytes:
        if self.is_compressed:
            return lz77.decompress(self.data,10)
        return self.data


# Glyph that has not been decompressed yet
# Useful for on-demand decompression, as most of the glyphs are not needed right away by the game
@dataclass
class LazyGlyph:
    info: GlyphInfo
    texture_size: tuple[int, int]
    glyph_data: GlyphData

    def get_info(self) -> GlyphInfo:
        return self.info

    def decompress(self) -> 'Glyph':
        decompress_bytes = self.glyph_data.decompress()
        data = io.BytesIO(decompress_bytes)

        def read_texture(width:int, height:int, data:io.BytesIO) -> Image.Image:
            image_data = np.frombuffer(data.read(width*height), dtype=np.uint8).reshape([height,width])
            # return Image.frombytes('L', (width, height), image_data)
            return Image.fromarray(image_data)

        mip_level_0 = read_texture(self.texture_size[0], self.texture_size[1], data)
        mip_level_1 = read_texture(self.texture_size[0] // 2, self.texture_size[1] // 2, data)
        mip_level_2 = read_texture(self.texture_size[0] // 4, self.texture_size[1] // 4, data)
        mip_level_3 = read_texture(self.texture_size[0] // 8, self.texture_size[1] // 8, data)
        assert data.tell()==len(decompress_bytes), 'caculate decompress len error'
        return Glyph(self.info, mip_level_0, mip_level_1, mip_level_2, mip_level_3)

    @classmethod
    def read(cls, data: bytes, offset, unicode):
        glyph_header = GlyphHeader(data, offset)
        texture_size = (glyph_header.texture_width, glyph_header.texture_height)
        compressed_size = glyph_header.compressed_size
        uncompressed_size = glyph_header.texture_width * glyph_header.texture_height
        info = GlyphInfo(header=glyph_header,unicode_index=unicode)
        # debug
        if 19968<=info.unicode<=40959:
            global LOG_ADW,LOG_OFS
            if info.advance_width not in LOG_ADW:
                LOG_ADW.append(info.advance_width)
            if (info.bearing_x, info.bearing_y) not in LOG_OFS:
                LOG_OFS.append((info.bearing_x, info.bearing_y))
        # debug end
        # 获取未压缩/解压后的数据 get uncompressed/decompressed data
        reader = io.BytesIO(data)
        reader.seek(offset+glyph_header.size)
        if compressed_size == 0:
            data = reader.read(uncompressed_size)
            is_compressed = False
        else:
            data = reader.read(compressed_size)
            is_compressed = True

        data = GlyphData(data, is_compressed)
        return cls(info, texture_size, data)

# Glyph that has been decompressed
@dataclass
class Glyph:
    info: GlyphInfo
    mip_level_0: Image.Image
    mip_level_1: Image.Image
    mip_level_2: Image.Image
    mip_level_3: Image.Image
    
    def get_image(self, mip_level: GlyphMipLevel) -> Image.Image:
        return {
            GlyphMipLevel.Level0: self.mip_level_0,
            GlyphMipLevel.Level1: self.mip_level_1,
            GlyphMipLevel.Level2: self.mip_level_2,
            GlyphMipLevel.Level3: self.mip_level_3,
        }[mip_level]

    @classmethod
    def read(cls, data:bytes, offset, unicode):
        lazy_glyph = LazyGlyph.read(data, offset, unicode)
        return lazy_glyph


@dataclass
class Font:
    version: int
    ascent: int  # Distance between the baseline and the top of the font
    descent: int  # Distance between the baseline and the bottom of the font
    fdata: bytes
    character_table_crc: int  # Used as a font identifier for glyph caching
    characters: List[int] = field(default_factory=lambda: [0]*0x10000)
    glyphs: Dict[int, LazyGlyph] = field(default_factory=dict)
    dbg_offsets: List[int] = field(default_factory=list)

    @classmethod
    def read(cls, data):
        # 读取头部 check header
        header = FontHeader(data)
        # 检查数据大小 check whole data length
        if header.fsize != len(data):
            raise ValueError(f"Font size in header does not match actual stream size")
        # 读取字符表 read the unicode characters table
        character_table:List[int] = 0x10000 * [0] # unicode: addr
        for i in range(0x10000):
            start = i*4 + header.size
            character_table[i] = int.from_bytes(data[start: start+4], "little", signed=False)
        
        # 计算字符表CRC32校验和  calculate character table CRC32
        character_table_bytes = struct.pack(f'<{len(character_table)}I', *character_table)
        character_table_crc = crc32.crc32(character_table_bytes, 0)
        
        # 读取字形数据 read the glyph data in characters table
        known_glyph_offsets = defaultdict(lambda: len(known_glyph_offsets))
        characters = [0]*0x10000  # [GlyphId]*0x10000
        glyphs = {}
        for character_index, glyph_offset in enumerate(character_table):
            glyph_id = known_glyph_offsets[glyph_offset]
            characters[character_index] = glyph_id
            if glyph_id in glyphs.keys(): continue
            glyphs[glyph_id] = Glyph.read(data, glyph_offset, character_index)
        return cls(header.version, header.ascent, header.descent, data, character_table_crc, characters, glyphs,character_table)

    # Get the sum of the ascent and descent, giving the total height of the font
    def get_line_height(self) -> int:
        return self.ascent + self.descent

    def get_glyph_for_character(self, character: int) -> Glyph:
        return self.glyphs[self.characters[character]]

    def try_get_glyph_for_character(self, character: int) -> Optional[Glyph]:
        return self.glyphs.get(self.characters[character])

    def get_glyph(self, glyph_id: int) -> Optional[Glyph]:
        return self.glyphs.get(glyph_id)

    def get_character_mapping(self) -> List[int]:
        return self.characters


# def read_font(reader: io.BytesIO) -> Font:
#     return Font.read(reader)

def read_lazy_font(read_data: bytes) -> Font:
    return Font.read(read_data)

# def read_font_metrics(reader: io.BytesIO) -> Font:
#     return Font.read(reader)


def main():
    os.chdir(os.path.dirname(__file__))
    font_path = r""  # set fnt(FNT4) file path here
    output_path = r""  # set glyph output path here
    os.makedirs(output_path, exist_ok=True)

    with open(font_path, 'rb') as fp:
        font_data = fp.read()
    font = read_lazy_font(font_data)

    ascent = font.ascent
    descent = font.descent

    # first, write the metadata & character mappings to a text file
    metadata = []
    metadata.append(f"ascent: {ascent}")
    metadata.append(f"descent: {descent}")
    metadata.append("characters:")
    for character_unicode, glyph_id in enumerate(font.get_character_mapping()):
        metadata.append(f"  {character_unicode:04x}: {glyph_id:04}")
    # finally, write the glyph metadata
    metadata.append("glyphs:")
    for glyph_id, glyph_data in sorted(font.glyphs.items(), key=lambda v: v[0]):
        info = glyph_data.info
        metadata.append(f"  {glyph_id:04}")
        metadata.append(f"    bearing_y: {info.bearing_y}")
        metadata.append(f"    bearing_x: {info.bearing_x}")
        metadata.append(f"    advance  : {info.advance_width}")
    with open(os.path.join(output_path, "metadata.txt"), 'w') as f:
        f.write("\n".join(metadata))
    
    # then, save each glyph to a separate file
    for glyph_id, glyph_data in font.glyphs.items():
        glyph_info = glyph_data.info
        size = glyph_info.actual_size()
        glyph_data = glyph_data.decompress()
        # continue
        for i in GlyphMipLevel:
            glyph_pic = glyph_data.get_image(i)  # (GlyphMipLevel.Level0)
            # new_glyph_pic = glyph_pic.convert('LA')
            new_glyph_pic = Image.new('RGBA', (size[0]//(2**i.value),size[1]//(2**i.value)))
            for x in range(size[0]//(2**i.value)):
                for y in range(size[1]//(2**i.value)):
                    pixel = glyph_pic.getpixel((x, y))  # pixel here same as the grayscale value
                    new_pixel = (0, 0, 0, pixel)
                    new_glyph_pic.putpixel((x, y), new_pixel)

            new_glyph_pic.save(os.path.join(output_path, f"{glyph_id:04}_{glyph_info.unicode:04x}_{i.value}.png"))
            break  # only save first mip level of the glyph
    print("Done")

if __name__ == '__main__':
    main()
