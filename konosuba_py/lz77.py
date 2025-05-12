import io
'''
Implement the LZ77 variant used in the game.
This variant of LZ77 precedes a block of data with an 8-bit bitmap specifying whether decompressor should read a literal byte or a reference.

The references are encoded as 16-bit big-endian (sic!) integers. It encodes offset and length of the reference,
but the amount of bits spent on each part is dependent on the format (const generics are used to specify this, in this fuction def as *offset_bits*).

Offset is specified as amount to seek back from the current position.
The minimum offset is 1, so the actual offset is offset + 1.
The minimum length is 3, so the actual length is length + 3.
'''

dbg_instructions = []
dbg_compress_instructions = []
dbg_input_data = None
dbg_output_data = None

def decompress(input_data: bytes, offset_bits: int) -> bytes:
    input_stream = io.BytesIO(input_data)
    output = io.BytesIO()

    while input_stream.tell() < len(input_data):
        map_byte = input_stream.read(1)
        for i in range(8):
            if input_stream.tell() >= len(input_data): break
            if ((map_byte[0] >> i) & 1) == 0: # direct byte output
                # if input_stream.tell() >= len(input_data): break  # sometimes no other bytes in the end
                # literal value
                output.write(input_stream.read(1))
            else:
                # back seek
                backseek_spec = int.from_bytes(input_stream.read(2), 'big', signed=False)  # big endian Oo
                '''
                MSB  XXXXXXXX          YYYYYYYY    LSB
                val  len               backOffset
                size (16-OFFSET_BITS)  OFFSET_BITS
                '''
                back_offset_mask = (1 << offset_bits) - 1  # magic to get the last OFFSET_BITS bits
                back_length = (backseek_spec >> offset_bits) + 3
                back_offset = (backseek_spec & back_offset_mask) + 1

                for _ in range(back_length):  # push char to output one by one
                    last = output.tell() - back_offset
                    assert last >= 0
                    # TODO: make this fallible?
                    # TODO: this might be optimized by stopping the bounds checking after we have enough data to guarantee that it's in bounds
                    output.write(bytes([output.getbuffer()[last]]))
    return output.getvalue()

def decompress_debug(input_data: bytes, offset_bits: int) -> bytes:
    input_stream = io.BytesIO(input_data)
    output = io.BytesIO()
    global dbg_instructions,dbg_input_data,dbg_output_data
    dbg_input_data = input_data
    while input_stream.tell() < len(input_data):
        map_byte = input_stream.read(1)
        for i in range(8):
            if input_stream.tell() >= len(input_data): break
            if ((map_byte[0] >> i) & 1) == 0: # direct byte output
                # if input_stream.tell() >= len(input_data): break  # sometimes no other bytes in the end
                # literal value
                output.write(input_stream.read(1))
                dbg_instructions.append(output.getvalue()[-1])
            else:
                # back seek
                backseek_spec = int.from_bytes(input_stream.read(2), 'big', signed=False)  # big endian Oo
                '''
                MSB  XXXXXXXX          YYYYYYYY    LSB
                val  len               backOffset
                size (16-OFFSET_BITS)  OFFSET_BITS
                '''
                back_offset_mask = (1 << offset_bits) - 1  # magic to get the last OFFSET_BITS bits
                back_length = (backseek_spec >> offset_bits) + 3
                back_offset = (backseek_spec & back_offset_mask) + 1
                dbg_instructions.append([back_length, back_offset])
                for _ in range(back_length):  # push char to output one by one
                    last = output.tell() - back_offset
                    # TODO: make this fallible?
                    # TODO: this might be optimized by stopping the bounds checking after we have enough data to guarantee that it's in bounds
                    output.write(bytes([output.getbuffer()[last]]))
    # debug part
    dbg_output_data = output.getvalue()
    compress_output = compress(dbg_output_data,offset_bits)
    if compress_output!=dbg_input_data:
        raise Exception('check for debug')
    dbg_instructions,dbg_input_data,dbg_output_data = [],None,None
    return output.getvalue()


def compress(input_bytes: bytes, offset_bits:int=10) -> bytes:
    count_bits = (16-offset_bits)
    max_count = (1 << count_bits) - 1 + 3  # max_count as look_ahead_buf_len
    max_offset = (1 << offset_bits) - 1 + 1  # max_offset as search_buf_len

    def find_offset(search_bytes: bytes, map_bytes: bytes):
        for i in range(len(search_bytes)):
            if search_bytes[-(i+1)]==map_bytes[0] and\
                  search_bytes[-(i+1):].startswith(map_bytes):
                return i+1
        else:
            raise Exception('err')

    def all_the_same(input_list, compare):
            for item in input_list:
                if compare != item:
                    return False
            return True
    
    # first, map all input bytes to instruction format
    instructions = [input_bytes[0]]
    log_len = 1  # a length to logging how many input_bytes already encode
    map_bytes = []  # a look ahead window to logging already mapping bytes
    search_buf, len_offset = None, None  # encode to instruction: [len,offset]
    i = 1
    while i < len(input_bytes):
        log_bytes = input_bytes[:log_len]
        # map byte in look ahead buf
        if map_bytes:
            if all_the_same(map_bytes, input_bytes[i]) and len_offset[1]==1:
                map_bytes.append(input_bytes[i])
                len_offset[0] = len(map_bytes)
                if len(map_bytes)==max_count:  # full look window size
                    instructions.append(len_offset)
                    log_len += len(map_bytes)
                    map_bytes = []
                    search_buf = None    
                    len_offset = None
                elif (i+1)==len(input_bytes):  # already look all input
                    if len_offset[0]<3:
                        instructions.extend(map_bytes)
                    else:
                        instructions.append(len_offset)
                    log_len += len(map_bytes)
                i+=1
            else:
                if len_offset[0]==len_offset[1] and\
                        input_bytes[i]==map_bytes[0]:
                    # add sub-map routine, when (new byte*N) == map_bytes[:N]
                    # TODO: maybe this routine can merge with the [N,1]->all_the_same routine above
                    main_map_len = len(map_bytes)
                    sub_map_len = main_map_len
                    sub_pos = i
                    while (max_count-len(map_bytes))>0:
                        if (max_count-len(map_bytes))<main_map_len:
                            sub_map_len = (max_count-len(map_bytes))
                        if input_bytes[sub_pos:(sub_pos+sub_map_len)] != bytes(map_bytes[:sub_map_len]):
                            break
                        map_bytes.extend(map_bytes[:sub_map_len])
                        sub_pos += sub_map_len
                    # if still has some bytes can't map the map_bytes[:main_map_len]
                    if len(map_bytes)<max_count:
                        for j in range(len(map_bytes),0,-1):
                            if input_bytes[sub_pos:sub_pos+j] == bytes(map_bytes[:j]):
                                # ? if bytes(map_bytes+map_bytes[:j]) in search_buf
                                # finded part of main_map
                                map_bytes.extend(map_bytes[:j])
                                sub_pos += j
                                break
                    i = sub_pos
                    len_offset[0] = len(map_bytes)
                    # at this time, only full of max_count will save
                    if len_offset[0]==max_count or i==len(input_bytes): #>len_offset[1]:
                        if len_offset[0]==2:
                            print('',end='')
                        instructions.append(len_offset)
                        log_len += len(map_bytes)  # bp
                        map_bytes = []
                        search_buf, len_offset = None, None
                        continue
                if bytes(map_bytes+[input_bytes[i]]) not in search_buf:
                    if 0<len(map_bytes)<3:
                        if len(map_bytes)==2 and \
                            (not all_the_same(map_bytes,map_bytes[0]) or\
                                bytes([map_bytes[1],input_bytes[i]]) in search_buf):
                            # dont known why but:
                            # 1. look ahead (m n h), if (m n) find in search_buf but (m n h) not find, 
                            # 2. look ahead (m m h), if (m m) find in search_buf but (m m h) not find but (m h) find,
                            # those look ahead pos should -1
                            map_bytes = map_bytes[:1]
                            i -= 1
                        instructions.extend(map_bytes)
                    else:
                        len_offset[0] = len(map_bytes)
                        if len_offset[0]==2:
                            print('',end='')
                        instructions.append(len_offset)
                    log_len += len(map_bytes)  # bp
                    map_bytes = []
                    search_buf = None    
                    len_offset = None
                else:
                    if len(map_bytes)==max_count:
                        len_offset = [len(map_bytes),find_offset(search_buf,bytes(map_bytes))]  # bp
                        instructions.append(len_offset)
                        log_len += len(map_bytes)
                        map_bytes = []
                        search_buf = None
                    else:
                        map_bytes.append(input_bytes[i])
                        len_offset = [len(map_bytes),find_offset(search_buf,bytes(map_bytes))]
                        # already look all input
                        if (i+1)==len(input_bytes):
                            if len_offset[0]<3:
                                instructions.extend(map_bytes)
                            else:
                                instructions.append(len_offset)
                            log_len += len(map_bytes)
                        i += 1
        else:
            # if no map, first find next search_buf
            if not search_buf:
                search_buf = log_bytes[-(max_offset):] if len(log_bytes)>1023 else log_bytes
            if bytes([input_bytes[i]]) in search_buf and (i+1)!=len(input_bytes):
                map_bytes.append(input_bytes[i])
                len_offset = [1,find_offset(search_buf,bytes(map_bytes))]
            else:
                instructions.append(input_bytes[i])
                log_len += 1  # bp
                search_buf = None
            i += 1
    # # need to debug if whole input_bytes is encode?
    # global dbg_instructions,dbg_compress_instructions
    # dbg_compress_instructions = None
    # if len(instructions)!=len(dbg_instructions):
    #     dbg_compress_instructions = instructions
    #     print("input_bytes maybe not whole encode")
    # elif instructions!=dbg_instructions:
    #     dbg_compress_instructions = instructions
    #     print("not the same instructions")
    
    # padding to make sure all sub_instruction are 8
    # if len(instructions)%8!=0:
    #     instructions.extend([0]*(len(instructions)%8))
    
    # next encode all instructions to compress bytes
    slices = []
    for i in range(0, len(instructions), 8):
        compress_part = instructions[i:i + 8]
        bitmap_marker = sum((1 << i) if isinstance(e, list) else (0<<i) for i, e in enumerate(compress_part))
        bytes_ = []
        for e in compress_part:
            if isinstance(e, list):
                count, offset = e
                # some raise for debug
                if count > max_count:
                    raise ValueError(f"count too high ({count} > {max_count})")
                if count < 3:
                    raise ValueError(f"count too low ({count} < 3)")
                if offset > max_offset:
                    raise ValueError(f"offset too high ({offset} > {max_offset})")
                if offset <= 0:
                    raise ValueError(f"offset too low ({offset} <= 0)")
                len_b = ((count - 3) << (8-count_bits)) | ((offset-1) >> 8)
                offset_b = (offset-1) & 0xff  # bitwise-AND with 8-bits offset_mask
                bytes_.extend([len_b, offset_b])
            else:
                if e > 255 or e < 0:  # raise for debug
                    raise ValueError(f"Byte out of range ({e})")
                bytes_.append(e)
        slices.extend([bitmap_marker, *bytes_])
    
    return bytes(slices)

# result = decompress(b'\xc0HELLO 0\x05\x80\x0b',12)
