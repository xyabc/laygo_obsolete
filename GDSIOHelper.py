#!/usr/bin/python
########################################################################################################################
#
# Copyright (c) 2014, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################################################################

"""GDSII IO Helper functions. Implemented by Eric Jan"""

import struct
import math
from math import *

_DICT = {
    'HEADER': b'\x00\x02',
    'BGNLIB': b'\x01\x02',
    'LIBNAME': b'\x02\x06',
    'ENDLIB': b'\x04\x00',
    'UNITS': b'\x03\x05',
    'BGNSTR': b'\x05\x02',
    'STRNAME': b'\x06\x06',
    'ENDSTR': b'\x07\x00',

    'BOUNDARY': b'\x08\x00',
    'SREF': b'\x0a\x00',
    'AREF': b'\x0b\x00',

    'SNAME': b'\x12\x06',
    'LAYER': b'\r\x02',
    'DATATYPE': b'\x0e\x02',
    'COLROW': b'\x13\x02',
    'XY': b'\x10\x03',
    'ENDEL': b'\x11\x00'
}
# format: actual_index datatype

# packs all the data ...

# pack structure/format
# 	length of the packed data + 4(4 hex digits)		+	 the tag from _DICT(4 hex digits)	+	actual packed data

no_data = struct.pack('>{0}H'.format(1), 4)
bgn_id = struct.pack('>{0}H'.format(12), *[0 for x in range(12)])
bgn_len = struct.pack('>{0}H'.format(1), 28)


# used to pack the beginning of libraries and structures
# dates represented by an array of 12 zeros

def pack_data(tag, data):
    record_type = _DICT[tag]
    pack_func = _PACK[record_type[1]]
    return pack_func(record_type, data)


def pack_double(tag, data):
    s = struct.pack('>{0}Q'.format(len(data)), *[_real_to_int(d) for d in data])
    return struct.pack('>{0}H'.format(1), len(s) + 4) + tag + s


def pack_int(tag, data):
    s = struct.pack('>{0}h'.format(len(data)), *data)
    return struct.pack('>{0}H'.format(1), len(s) + 4) + tag + s


def pack_long(tag, data):
    s = struct.pack('>{0}l'.format(len(data)), *data)
    return struct.pack('>{0}H'.format(1), len(s) + 4) + tag + s


def pack_text(tag, data):
    if type(data) != bytes:
        data = str.encode(data)
    if len(data) % 2 == 1:
        data += b'\0'
    return struct.pack('>{0}H'.format(1), len(data) + 4) + tag + data

_PACK = {
    2: pack_int,
    b'\x02': pack_int,
    3: pack_long,
    b'\x03': pack_long,
    5: pack_double,
    b'\x05': pack_double,
    6: pack_text,
    b'\x06': pack_text

}


def _real_to_int(d):
    """
    FORMAT
        1 sign bit
        7 bit exponent (offset = -64)
        56 bit mantissa (formed as 0.XXXXX)

    VALUE = SIGN * MANTISSA * 16 ^ (EXP)

    """

    if d < 0:
        sign = 0x8000000000000000
    else:
        sign = 0

    exponent = log(d, 16)
    if (exponent < 0):
        exponent = ceil(exponent)
    else:  # exponent > 0
        exponent = floor(exponent) + 1
    d = d / (16 ** exponent)

    mantissa = getMantissa(d)

    return sign | (int(exponent) + 64) << 56 | mantissa #updated for Python2 compatibility
    #return sign | (exponent + 64) << 56 | mantissa


def getMantissa(d):
    mantissa = ""
    for _ in range(56):
        d = d * 2
        mantissa += str((int)(d))
        d = d - (int)(d)
    retVal = eval("0b" + mantissa)
    return retVal


def pack_bgn(tag):
    return bgn_len + _DICT[tag] + bgn_id


def pack_no_data(tag):
    return no_data + _DICT[tag]