# -*- coding: utf-8 -*-
#
# This file is part of EventGhost.
# Copyright © 2005-2019 EventGhost Project <http://www.eventghost.org/>
#
# EventGhost is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# EventGhost is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with EventGhost. If not, see <http://www.gnu.org/licenses/>.

"""
This file is part of the **pyWinMCERemote**
project https://github.com/kdschlosser/pyWinMCERemote

:platform: Windows
:license: GPL version 2 or newer
:synopsis: pronto encoder/decoder

.. moduleauthor:: Kevin Schlosser @kdschlosser <kevin.g.schlosser@gmail.com>
"""


from struct import pack

pronto_clock = 0.241246
SignalFree = 10000
SignalFreeRC6 = 2700
RC6Start = [2700, -900, 450, -900, 450, -450, 450, -450, 450, -450]
RC6AStart = [3150, -900, 450, -450, 450, -450, 450, -900, 450]

#
# def pronto_raw_to_ir(code):
#     code = code.split(' ')
#
#     preamble = code[:4]
#     pronto_carrier = int('0x' + preamble[1], 16)
#     carrier = pronto_carrier * pronto_clock
#     raw = []
#
#     if int('0x' + code[-1], 16) == SignalFree:
#         code = code[:-1]
#
#     for step in code[4:]:
#         step = int('0x' + step, 16)
#         duration = step * carrier
#         raw += [step]
#
#
def ir_to_pronto_raw(freq, data):
    if freq <= 0:
        freq = 36000

    pronto_carrier = int(1000000 / (freq * pronto_clock))
    carrier = pronto_carrier * pronto_clock

    pronto_data = [0x0000, pronto_carrier, 0x0000, 0x0000]

    for val in data:
        duration = abs(val)
        pronto_data.append(round(duration / carrier))

    if len(pronto_data) % 2 != 0:
        pronto_data.append(SignalFree)

    pronto_data[3] = (len(pronto_data) - 4) / 2

    out = '%04X' % int(pronto_data[0])

    for v in pronto_data[1:]:
        out += ' %04X' % int(v)

    return out


def pronto_raw_to_ir(pronto_data, repeat_count):  # repeat_count is ignored for Raw
    if len(pronto_data) < 6 or pronto_data[0] not in (0x0000, 0x0100):
        raise Exception("Invalid Raw data %s" % str(pronto_data))

    pronto_carrier = pronto_data[1]
    if pronto_carrier == 0:
        pronto_carrier = int(1000000 / (36000 * pronto_clock))

    pw = pronto_carrier * pronto_clock
    firstSeq = 2 * pronto_data[2]
    repeatSeq = 2 * pronto_data[3]
    pulse = True
    repeatCount = 0
    start = 4
    done = False
    index = start
    sequence = firstSeq

    if firstSeq == 0:
        if repeatSeq == 0:
            return None

        sequence = repeatSeq
        repeatCount = 1

    timingData = []
    while not done:
        time = int(pronto_data[index] * pw)

        if pulse:
            timingData.append(time)
        else:
            timingData.append(-time)
        index += 1
        pulse = not pulse

        if index == start + sequence:
            if repeatCount == 0:
                if repeatSeq != 0:
                    start += firstSeq
                    sequence = repeatSeq
                    index = start
                    pulse = True
                    repeatCount += 1
                else:
                    done = True
            elif repeatCount == 1:
                done = True
            else:
                index = start
                pulse = True
                repeatCount += 1

    freq = int(1000000 / (pronto_carrier * pronto_clock))
    return freq, timingData


def encode_bits(data, start, stop, s_false, s_true):
    out = ""

    for i in range(start, stop - 1, -1):
        if data & (1 << i) > 0:
            out = out + s_true
        else:
            out = out + s_false

    return out


def zero_one_sequences(String, Delay):
    final_data = []
    ind = 0
    n = len(String)

    while True:
        countUp = 0
        countDown = 0
        while ind < n and String[ind] == "0":
            ind += 1

        while ind < n and String[ind] == "1":
            countUp += 1
            ind += 1

        while ind < n and String[ind] == "0":
            countDown += 1
            ind += 1

        final_data.extend([Delay * countUp, -Delay * countDown])

        if ind >= n:
            break

    if final_data[-1] == 0:
        final_data[-1] = -10000
    else:
        final_data[-1] -= 10000

    return final_data


def pronto_rc5_to_ir(pronto_data, repeat_count=0):
    if len(pronto_data) != 6 or pronto_data[0] != 0x5000:  # CodeType RC5
        raise Exception("Invalid RC5 data %s" % str(pronto_data))

    pronto_carrier = pronto_data[1]
    if pronto_carrier == 0x0000:
        pronto_carrier = int(1000000 / (36000 * pronto_clock))

    rc5_string = ''

    for j in range(repeat_count + 1):
        toggle = repeat_count % 2 == 0
        if pronto_data[5] > 63:
            rc5_string += encode_bits(2, 1, 0, '10', '01')
        else:
            rc5_string += encode_bits(3, 1, 0, '10', '01')
        if toggle:
            rc5_string += encode_bits(1, 0, 0, '10', '01')
        else:
            rc5_string += encode_bits(0, 0, 0, '10', '01')

        rc5_string += encode_bits(pronto_data[4], 4, 0, '10', '01')
        rc5_string += encode_bits(pronto_data[5], 5, 0, '10', '01')

    final_data = zero_one_sequences(rc5_string, 900)

    freq = int(1000000 / (pronto_carrier * pronto_clock))
    return freq, final_data


def pronto_rc5x_to_ir(pronto_data, repeat_count):
    if not (
            len(pronto_data) == 7 or
            (len(pronto_data) == 8 and pronto_data[7] == 0x0000)
    ) or pronto_data[0] != 0x5001:  # CodeType RC5X

        raise Exception("Invalid RC5X data %s" % str(pronto_data))

    pronto_carrier = pronto_data[1]
    if pronto_carrier == 0x0000:
        pronto_carrier = int(1000000 / (36000 * pronto_clock))

    if pronto_data[2] + pronto_data[3] != 2:
        raise Exception("Invalid RC5X data %s" % str(pronto_data))

    rc5x_string = ''

    for j in range(repeat_count + 1):
        toggle = repeat_count % 2 == 0
        if pronto_data[5] > 63:
            rc5x_string += encode_bits(2, 1, 0, '10', '01')
        else:
            rc5x_string += encode_bits(3, 1, 0, '10', '01')
        if toggle:
            rc5x_string += encode_bits(1, 0, 0, '10', '01')
        else:
            rc5x_string += encode_bits(0, 0, 0, '10', '01')
            
        rc5x_string += encode_bits(pronto_data[4], 4, 0, '10', '01')
        rc5x_string += '0000'
        rc5x_string += encode_bits(pronto_data[5], 5, 0, '10', '01')
        rc5x_string += encode_bits(pronto_data[6], 5, 0, '10', '01')

    final_data = zero_one_sequences(rc5x_string, 900)

    freq = int(1000000 / (pronto_carrier * pronto_clock))
    return freq, final_data


def pronto_rc6_to_ir(pronto_data, repeat_count):
    if len(pronto_data) != 6 or pronto_data[0] != 0x6000:  # CodeType RC6
        raise Exception("Invalid RC6 data %s" % str(pronto_data))

    pronto_carrier = pronto_data[1]
    if pronto_carrier == 0x0000:
        pronto_carrier = int(1000000 / (36000 * pronto_clock))

    if pronto_data[2] + pronto_data[3] != 1:
        raise Exception("Invalid RC6 data %s" % str(pronto_data))

    rc6_string = ""
    for j in range(repeat_count + 1):
        toggle = repeat_count % 2 == 0
        rc6_string += '1111110010010101'
        if toggle:
            rc6_string += '1100'
        else:
            rc6_string += '0011'
            
        rc6_string += encode_bits(pronto_data[4], 7, 0, '01', '10')
        rc6_string += encode_bits(pronto_data[5], 7, 0, '01', '10')

    final_data = zero_one_sequences(rc6_string, 450)

    freq = int(1000000 / (pronto_carrier * pronto_clock))
    return freq, final_data


def pronto_rc6a_to_ir(pronto_data, repeat_count):
    if len(pronto_data) != 8 or pronto_data[0] != 0x6001:  # CodeType RC6A
        raise Exception("Invalid RC6A data %s" % str(pronto_data))

    pronto_carrier = pronto_data[1]
    if pronto_carrier == 0x0000:
        pronto_carrier = int(1000000 / (36000 * pronto_clock))

    if pronto_data[2] + pronto_data[3] != 2:
        raise Exception("Invalid RC6A data %s" % str(pronto_data))

    rc6a_string = ""
    for j in range(repeat_count + 1):
        toggle = repeat_count % 2 == 0
        rc6a_string += '11111110010101001'
        if toggle:
            rc6a_string += '1100'
        else:
            rc6a_string += '0011'
            
        if pronto_data[4] > 127:
            rc6a_string += encode_bits(1, 0, 0, '01', '10')
            rc6a_string += encode_bits(pronto_data[4], 14, 0, '01', '10')
        else:
            rc6a_string += encode_bits(0, 0, 0, '01', '10')
            rc6a_string += encode_bits(pronto_data[4], 6, 0, '01', '10')
        rc6a_string += encode_bits(pronto_data[5], 7, 0, '01', '10')
        rc6a_string += encode_bits(pronto_data[6], 7, 0, '01', '10')

    final_data = zero_one_sequences(rc6a_string, 450)

    freq = int(1000000 / (pronto_carrier * pronto_clock))
    return freq, final_data


handlers = {
    0x0: pronto_raw_to_ir,
    0x0100: pronto_raw_to_ir,
    0x5000: pronto_rc5_to_ir,
    0x5001: pronto_rc5x_to_ir,
    0x6000: pronto_rc6_to_ir,
    0x6001: pronto_rc6a_to_ir,
}


def pronto_to_mce(pronto, repeat_count=0):
    pronto_data = list(int(v, 16) for v in pronto.split(" "))
    try:
        handler = handlers[pronto_data[0]]
    except:
        raise Exception(
            "Don't have a decoder for pronto format %s" % hex(pronto_data[0])[2:].upper()
        )

    freq, timings = handler(pronto_data, repeat_count)

    return freq, timings


def round_and_pack_timings(timing_data):
    out = ""
    for v in timing_data:
        newVal = 50 * int(round(v / 50))
        out += pack("i", newVal)

    return out


if __name__ == '__main__':

    freq, transmit_values = pronto_to_mce('0000 0067 0000 000d 0060 0018 0030 0018 0018 0018 0030 0018 0018 0018 0030 0018 0018 0018 0018 0018 0018 0018 0018 0018 0018 0018 0018 0018 0030 0409')
    transmit_code = round_and_pack_timings(transmit_values)
    header = pack(7 * "q", 2, int(1000000. / freq), 0, 0, 0, 1, len(transmit_code))

    print repr(header)
    print repr(transmit_code)
    print transmit_values

    import ctypes


    ptr = ctypes.cast((ctypes.c_char * len(transmit_code))(*list(transmit_code)), ctypes.POINTER(ctypes.c_long))

    result = []
    for i in range(len(transmit_code)):
        result += [ptr[i]]

    print result


    print
    print
    ptr = ctypes.cast((ctypes.c_char * 8)('\x02', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00'), ctypes.POINTER(ctypes.c_ulonglong))
    print ptr.contents.value
    ptr = ctypes.cast((ctypes.c_char * 8)('\x18', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00'), ctypes.POINTER(ctypes.c_ulonglong))
    print ptr.contents.value
    ptr = ctypes.cast((ctypes.c_char * 8)('\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00'), ctypes.POINTER(ctypes.c_ulonglong))
    print ptr.contents.value
    ptr = ctypes.cast((ctypes.c_char * 8)('\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00'), ctypes.POINTER(ctypes.c_ulonglong))
    print ptr.contents.value

    print
    ptr = ctypes.cast((ctypes.c_char * 8)('\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00'), ctypes.POINTER(ctypes.c_ulonglong))
    print ptr.contents.value
    ptr = ctypes.cast((ctypes.c_char * 8)('\x01', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00'), ctypes.POINTER(ctypes.c_ulonglong))
    print ptr.contents.value
    ptr = ctypes.cast((ctypes.c_char * 8)('h', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00'), ctypes.POINTER(ctypes.c_ulonglong))
    print ptr.contents.value
    print

    print int(1000000. / freq)
    print len(transmit_code)