# -*- coding: utf-8 -*-
#
# This file is part of EventGhost.
# Copyright © 2005-2016 EventGhost Project <http://www.eventghost.org/>
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

import math
import time
from . import pronto
from . import utils


XBOX360_COMMANDS = {
    0x7428: 'Button.OpenCloseTray',
    0xF464: 'Button.Xbox',
    0x740C: 'Power.Toggle',
    0xF419: 'Media.Toggle',
    0x7418: 'Media.Pause',
    0xF415: 'Media.Rewind',
    0x7414: 'Media.FastForward',
    0xF41B: 'Media.Previous',
    0x741A: 'Media.Next',
    0xF416: 'Media.Play',
    0x744F: 'Button.Display',
    0xF451: 'Button.Title',
    0x7424: 'Menu.DVD',
    0xF423: 'Navigation.Back',
    0x740F: 'Button.Info',
    0xF41E: 'Navigation.Up',
    0x7420: 'Navigation.Left',
    0xF421: 'Navigation.Right',
    0x741F: 'Navigation.Down',
    0xF422: 'Navigation.Ok',
    0x7426: 'Button.Y',
    0xF468: 'Button.X',
    0x7466: 'Button.A',
    0xF425: 'Button.B',
    0x7412: 'Channel.Up',
    0xF413: 'Channel.Down',
    0xF411: 'Volume.Up',
    0xF410: 'Voluem.Down',
    0xF40E: 'Volume.Mute',
    0xF40D: 'Button.Start',
    0x7416: 'Media.Play',
    0xF40B: 'Navigation.Enter',
    0x7417: 'Media.Record',
    0xF40A: 'Button.Clear',
    0x7400: 'Number.0',
    0x7401: 'Number.1',
    0xF402: 'Number.2',
    0x7403: 'Number.3',
    0xF404: 'Number.4',
    0x7405: 'Number.5',
    0xF406: 'Number.6',
    0x7407: 'Number.7',
    0xF408: 'Number.8',
    0x7409: 'Number.9',
    0xF41D: 'Button.100',
    0x741C: 'Button.Reload'
}

MCE_COMMANDS = {
    0x0400: "Number.0",
    0x0401: "Number.1",
    0x0402: "Number.2",
    0x0403: "Number.3",
    0x0404: "Number.4",
    0x0405: "Number.5",
    0x0406: "Number.6",
    0x0407: "Number.7",
    0x0408: "Number.8",
    0x0409: "Number.9",
    0x040A: "Navigation.Escape",
    0x040B: "Navigation.Enter",
    0x040C: "Power.Toggle",
    0x040D: "Button.Start",
    0x040E: "Volume.Mute",
    0x040F: "Menu.Info",
    0x0410: "Volume.Up",
    0x0411: "Volume.Down",
    0x0412: "Channel.Up",
    0x0413: "Channel.Down",
    0x0414: "Media.FastForward",
    0x0415: "Media.Rewind",
    0x0416: "Media.Play",
    0x0417: "Media.Record",
    0x0418: "Media.Pause",
    0x0419: "Media.Stop",
    0x041A: "Media.Skip",
    0x041B: "Media.Replay",
    0x041C: "Number.Pound",
    0x041D: "Number.Star",
    0x041E: "Navigation.Up",
    0x041F: "Navigation.Down",
    0x0420: "Navigation.Left",
    0x0421: "Navigation.Right",
    0x0422: "Navigation.Ok",
    0x0423: "Navigation.Back",
    0x0424: "Menu.DVD",
    0x0425: "Source.LiveTV",
    0x0426: "Menu.Guide",
    0x0427: "Video.Aspect",
    0x0446: "Source.TV",
    0x0447: "Source.Music",
    0x0448: "Source.RecordedTV",
    0x0449: "Source.Pictures",
    0x044A: "Source.Videos",
    0x044C: "Source.Audio",
    0x044D: "Button.Subtitle",
    0x0450: "Source.Radio",
    0x045A: "Button.Teletext",
    0x045B: "Button.Red",
    0x045C: "Button.Green",
    0x045D: "Button.Yellow",
    0x045E: "Button.Blue",
}

MCE_CODE = 0x800F

COMMANDS = {
    0x00: 'Number.0',
    0x01: 'Number.1',
    0x02: 'Number.2',
    0x03: 'Number.3',
    0x04: 'Number.4',
    0x05: 'Number.5',
    0x06: 'Number.6',
    0x07: 'Number.7',
    0x08: 'Number.8',
    0x09: 'Number.9',
    0x0D: 'Volume.Mute',
    0x10: 'Volume.Up',
    0x11: 'Volume.Down',
    0x1D: 'Media.Repeat',
    0x20: 'Media.Next',
    0x21: 'Media.Previous',
    0x28: 'Media.FastForward',
    0x29: 'Media.Rewind',
    0x2C: 'Media.Play',
    0x30: 'Media.Pause',
    0x31: 'Media.Stop',
    0x3B: 'Button.a>b',
    0x48: 'Menu.OSD',
    0x4B: 'Button.Subtitle',
    0x4E: 'Button.Language',
    0x50: 'Button.Audio',
    0x58: 'Navigation.Up',
    0x59: 'Navigation.Down',
    0x54: 'Button.Menu',
    0x5A: 'Navigation.Left',
    0x5B: 'Navigation.Right',
    0x5C: 'Navigation.Ok',
    0x82: 'Menu.Setup',
    0x83: 'Navigation.Return',
    0x85: 'Video.Angle',
    0x91: 'Media.Play1/2',
    0xD3: 'Media.PlayMode',
    0xF7: 'Video.Zoom'
}

HEADER_MARK = 2666
HEADER_SPACE = -889

LOGICAL_0_MARK = 444
LOGICAL_0_SPACE = -444
LOGICAL_1_MARK = 889
LOGICAL_1_SPACE = -889

TRAILER_LOGIC_0_MARK = 889
TRAILER_LOGIC_0_SPACE = -889
TRAILER_LOGIC_1_MARK = 889
TRAILER_LOGIC_1_SPACE = -889

TIMING_TOLERANCE = 12.0


def TIMING_MATCH(value, expected_timing_value):
    high = math.floor(expected_timing_value + ((expected_timing_value * TIMING_TOLERANCE) / 100.0))
    low = math.floor(expected_timing_value - ((expected_timing_value * TIMING_TOLERANCE) / 100.0))

    # do a flip flop of the high and low so the same expression can
    # be used when evaluating a raw timing
    if expected_timing_value < 0:
        low, high = high, low

    return low <= value <= high


class DecodeError(Exception):  # Raised if code doesn't match expectation.
    pass


class RepeatExpired(Exception):
    pass


class CodeWrapper(list):

    @property
    def header(self):
        return self[0], self[1]

    @header.setter
    def header(self, value):
        mark, space = value
        self[0] = mark
        self[1] = space

    @property
    def header_mark(self):
        return self[0]

    @header_mark.setter
    def header_mark(self, value):
        self[0] = value

    @property
    def header_space(self):
        return self[1]

    @header_space.setter
    def header_space(self, value):
        self[1] = value

    @property
    def footer(self):
        return self[-2:]

    @property
    def footer_space(self):
        return self[-1]

    @property
    def footer_mark(self):
        return self[-2]

    @footer_mark.setter
    def footer_mark(self, value):
        self[len(self) - 2] = value

    @property
    def bits(self):
        code = self[2:-2]
        pairs = [[code[i], code[i + 1]] for i in range(0, len(code), 2)]
        return len(pairs)

    def get_burst_pair(self, index):
        # trim off the header and the footer value
        code = self[2:-2]
        pairs = [[code[i], code[i + 1]] for i in range(0, len(code), 2)]

        try:
            mark, space = pairs[index]
        except IndexError:
            raise IndexError('Invalid burst pair')

        return mark, space

    def set_burst_pair(self, index, mark, space):
        index = (index * 2) + 2
        self[index] = mark
        self[index + 1] = space

    def __getitem__(self, item):
        if isinstance(item, slice):
            return CodeWrapper(self[item])

        return list.__getitem__(self, item)


def decode(frequency, code):
    code = utils.clean_code(code[:], TIMING_TOLERANCE)
    try:
        protocol = RC6IRCode(code)
    except DecodeError:
        protocol = IrCode(code, frequency)
    except RepeatExpired:
        protocol = None

    return protocol


class IrCode(object):
    """
    IR decoder for unknown protocols.
    """

    def __init__(self, code, frequency=0):
        if not isinstance(code, (list, tuple)):
            code = pronto.pronto_to_mce(code)
            code = utils.clean_code(code, TIMING_TOLERANCE)

        self.diffTime = 3.0
        self.rlc_code = code[:]
        self.code = CodeWrapper(code[:])
        self.frequency = frequency

    @property
    def pronto(self):
        return pronto.ir_to_pronto_raw(self.frequency, self.rlc_code)

    def __str__(self):
        # print data
        lastPause = 0
        lastPulse = 0
        code = 0
        mask = 1
        for i, x in enumerate(self.code):
            if i % 2:
                diff = max(self.diffTime, lastPause * 0.2)
                if -diff < x - lastPause < diff:
                    code |= mask
                lastPause = x
            else:
                diff = max(self.diffTime, lastPulse * 0.2)
                if -diff < x - lastPulse < diff:
                    code |= mask
                lastPulse = x
            mask <<= 1
        code |= mask

        return "Unknown.%X" % code


class RC6IRCode(object):
    """
    IR decoder for the Philips RC-6 protocol.
    """

    lastCode = None
    lastTime = 0

    def __init__(self, code):

        if not isinstance(code, (list, tuple)):
            code = pronto.pronto_to_mce(code)
            code = utils.clean_code(code, TIMING_TOLERANCE)

        self.timeout = 130
        self.halfBitTime = 444
        self.pos = 0
        self.data = None
        self.bitState = 0
        self.bufferLen = 0
        self.frequency = 36000
        self.rlc_code = code[:]
        self.code = CodeWrapper(code[:])
        self._decoded = self._decode()

        # try:
        #     self.code = normalize_raw_code(code)
        # except ValueError:
        #     raise DecodeError('Invalid Code')

    @property
    def pronto(self):
        return pronto.ir_to_pronto_raw(self.frequency, self.rlc_code)

    @property
    def is_button_held(self):
        if RC6IRCode.lastCode is None:
            return False

        return (time.clock() - RC6IRCode.lastTime) * 1000 < self.timeout

    def __str__(self):
        return self._decoded

    def _decode(self):
        code = self.code

        # we have to subtract off the start, mode and trailer bits
        if code.bits not in (31, 32):
            raise DecodeError('Incorrect number of bits')

        data = list(abs(item) for item in code)

        self.SetData(data, 2)

        # Get the start bit
        if self.GetBit() != 1:
            raise DecodeError("missing start bit")

        mode = self.GetBitsLsbLast(3)
        trailerBit = self.GetTrailerBit()

        # Check for MCE remote
        if mode == 6:
            device = self.GetBitsLsbLast(16)
            command = self.GetBitsLsbLast(16)

            if device == MCE_CODE:
                if command & 0x7FFF != command:
                    trailerBit = 1
                    command &= 0x7FFF
                else:
                    trailerBit = 0

                if command in MCE_COMMANDS:
                    device = 'MCE.'
                    decoded = MCE_COMMANDS[command]
                elif command in XBOX360_COMMANDS:
                    device = 'XBox360.'
                    decoded = XBOX360_COMMANDS[command]
                else:
                    device = 'MCE.'
                    decoded = '%04X' % (command,)
            else:
                decoded = '%04X.%04X' % (device, command)
                device = 'RC6.06.'

            decoded = device + decoded

        else:
            device = self.GetBitsLsbLast(8)
            command = self.GetBitsLsbLast(8)

            decoded = '%02X.' % (device,)
            if command in COMMANDS:
                decoded += COMMANDS[command]
            else:
                decoded += '%02X.' % (command,)

            if mode != 0:
                decoded = '%02X.'.format(mode) + decoded

        if trailerBit == 1:
            if RC6IRCode.lastCode is None:
                RC6IRCode.lastTime = time.clock()
                RC6IRCode.lastCode = decoded
            elif RC6IRCode.lastCode == decoded:
                if (time.clock() - RC6IRCode.lastTime) * 1000 < self.timeout:
                    RC6IRCode.lastTime = time.clock()
                    decoded += '.Held'
                else:
                    RC6IRCode.lastTime = 0
                    RC6IRCode.lastCode = None
                    raise RepeatExpired()
            else:
                RC6IRCode.lastTime = time.clock()
                RC6IRCode.lastCode = decoded

        else:
            RC6IRCode.lastCode = None
            RC6IRCode.lastTime = 0

        return decoded

    def GetTrailerBit(self):
        sample = (
                self.GetSample() * 8 +
                self.GetSample() * 4 +
                self.GetSample() * 2 +
                self.GetSample()
        )
        if sample == 3:  # binary 0011
            return 0
        elif sample == 12:  # binary 1100
            return 1
        else:
            raise DecodeError("wrong trailer bit transition")

    def GetBit(self):
        sample = self.GetSample() * 2 + self.GetSample()
        if sample == 1:  # binary 01
            return 0
        elif sample == 2:  # binary 10
            return 1
        else:
            raise DecodeError("wrong bit transition")

    def GetBitsLsbFirst(self, numBits=8):
        """
        Returns numBits count manchester bits with LSB last order.
        """
        data = 0
        mask = 1
        for dummyCounter in range(numBits):
            data |= mask * self.GetBit()
            mask <<= 1
        return data

    def GetBitsLsbLast(self, numBits=8):
        """
        Returns numBits count manchester bits with LSB last order.
        """
        data = 0
        for dummyCounter in range(numBits):
            data <<= 1
            data |= self.GetBit()
        return data

    def GetSample(self):
        if self.bufferLen == 0:
            if self.pos >= len(self.data):
                raise DecodeError("not enough timings")
            self.bufferLen = (
                    (self.data[self.pos] + 2 * self.halfBitTime / 3) / self.halfBitTime
            )
            if self.bufferLen == 0:
                raise DecodeError("duration too short")
            self.pos += 1
            self.bitState = self.pos % 2
        self.bufferLen -= 1
        return self.bitState

    def SetData(self, data, pos=0):
        self.data = data
        self.pos = pos
        self.bufferLen = 0
        self.bitState = 0


def normalize_raw_code(code):
    code = CodeWrapper(code[:])

    if TIMING_MATCH(code.header_mark, HEADER_MARK):
        code.header_mark = HEADER_MARK
    else:
        raise ValueError('Invalid header mark')

    if TIMING_MATCH(code.header_space, HEADER_SPACE):
        code.header_space = HEADER_SPACE
    else:
        raise ValueError('Invalid header space')

    if code.footer_space >= -HEADER_MARK:
        raise ValueError('Invalid footer space')

    for i in range(code.bits):
        mark, space = code.get_burst_pair(i)

        if (
                TIMING_MATCH(mark, LOGICAL_0_MARK) and
                TIMING_MATCH(space, LOGICAL_0_SPACE)
        ):
            code.set_burst_pair(i, LOGICAL_0_MARK, LOGICAL_0_SPACE)

        elif (
                TIMING_MATCH(mark, LOGICAL_1_MARK) and
                TIMING_MATCH(space, LOGICAL_1_SPACE)
        ):
            code.set_burst_pair(i, LOGICAL_1_MARK, LOGICAL_1_SPACE)

        elif (
                TIMING_MATCH(mark, TRAILER_LOGIC_0_MARK) and
                TIMING_MATCH(space, TRAILER_LOGIC_0_SPACE)
        ):
            code.set_burst_pair(i, TRAILER_LOGIC_0_MARK, TRAILER_LOGIC_0_SPACE)

        elif (
                TIMING_MATCH(mark, TRAILER_LOGIC_1_MARK) and
                TIMING_MATCH(space, TRAILER_LOGIC_1_SPACE)
        ):
            code.set_burst_pair(i, TRAILER_LOGIC_1_MARK, TRAILER_LOGIC_1_SPACE)

        else:
            raise ValueError('Invalid code')

    return code


