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

import ctypes
import comtypes
from ctypes.wintypes import (
    ULONG,
    LONG,
    WCHAR,
    LPVOID,
    BOOL,
    DWORD,
    INT,
    HANDLE,
)

from comtypes import GUID
import threading
from collections import deque
from struct import unpack_from, pack
from os import environ
import time
from . import pronto


if environ.get("PROCESSOR_ARCHITECTURE") == "AMD64" or environ.get("PROCESSOR_ARCHITEW6432") == "AMD64":
    PACK_FORMAT = "q"  # pack/unpack format for 64 bit int
    IR_ULONG_PTR = ctypes.c_ulonglong
else:
    PACK_FORMAT = "i"  # pack/unpack format for 32 bit int
    IR_ULONG_PTR = ctypes.c_ulong

IR_PTR_SIZE = ctypes.sizeof(IR_ULONG_PTR)

if ctypes.sizeof(ctypes.c_void_p) == 8:
    ULONG_PTR = ctypes.c_ulonglong
else:
    ULONG_PTR = ctypes.c_ulong

POINTER = ctypes.POINTER
HDEVINFO = LPVOID
NULL = None

PUCHAR = POINTER(ctypes.c_ubyte)

INFINITE = 0xFFFFFFFF
STATUS_WAIT_0 = 0x00000000
WAIT_OBJECT_0 = STATUS_WAIT_0 + 0
WAIT_OBJECT_1 = STATUS_WAIT_0 + 1
WAIT_FAILED = 0xFFFFFFFF
ERROR_NO_MORE_ITEMS = 0x00000103
ERROR_IO_PENDING = 0x000003E5
INVALID_HANDLE_VALUE = -1

FILE_FLAG_OVERLAPPED = 0x40000000
FILE_DEVICE_IRCLASS = 0x0F60
MAXIMUM_FILENAME_LENGTH = 256
OPEN_EXISTING = 3

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000

DEV_CAPS_PROTOCOL_VERSION = 0x100
DEV_CAPS_PROTOCOL_VERSION_V1 = 0x100
DEV_CAPS_PROTOCOL_VERSION_V2 = 0x200

# Valid capabilities bits for protocol V1
DEV_CAPS_SUPPORTS_LEGACY_SIGNING = 0x1
DEV_CAPS_HAS_UNIQUE_SERIAL = 0x2
DEV_CAPS_CAN_FLASH_RECEIVER_LED = 0x4
DEV_CAPS_IS_LEGACY = 0x8
V1_DEV_CAPS_VALID_BITS = 0xF

# Valid capabilities bits for protocol V2

V2_DEV_CAPS_SUPPORTS_WAKE = 0x10
V2_DEV_CAPS_MULTIPLE_WAKE = 0x20
V2_DEV_CAPS_PROGRAMMABLE_WAKE = 0x40
V2_DEV_CAPS_VOLATILE_WAKE_PATTERN = 0x80

V2_DEV_CAPS_LEARNING_ONLY = 0x100
V2_DEV_CAPS_NARROW_BPF = 0x200
V2_DEV_CAPS_NO_SWDECODE_INPUT = 0x400
V2_DEV_CAPS_HWDECODE_INPUT = 0x800

V2_DEV_CAPS_EMULATOR_V1 = 0x1000
V2_DEV_CAPS_EMULATOR_V2 = 0x2000
V2_DEV_CAPS_ATTACHED_TO_TUNER = 0x4000

V2_DEV_CAPS_VALID_BITS = 0x7fff

# Wake protocols

V2_WAKE_PROTOCOL_RC6 = 0x1
V2_WAKE_PROTOCOL_QP = 0x2
V2_WAKE_PROTOCOL_SAMSUNG = 0x4
V2_WAKE_PROTOCOL_DONTCARE = 0x8

V2_VALID_WAKE_PROTOCOLS = 0xF

# Valid wake keys. A good implementation will be able to wake on all
# key codes but this is not required.
WAKE_KEY_POWER_TOGGLE = 0x0C
WAKE_KEY_DISCRETE_ON = 0x29
WAKE_KEY_ALL_KEYS = 0xFFFF

TRANSMIT_FLAGS_PULSE_MODE = 0x0001
TRANSMIT_FLAGS_DC_MODE = 0x0002

# Define the method codes for how buffers are passed for I/O and FS controls
METHOD_BUFFERED = 0
METHOD_IN_DIRECT = 1
METHOD_OUT_DIRECT = 2
METHOD_NEITHER = 3

# Define the access check value for any access
# The FILE_READ_ACCESS and FILE_WRITE_ACCESS constants are also defined in
# ntioapi.h as FILE_READ_DATA and FILE_WRITE_DATA. The values for these
# constants *MUST* always be in sync.
# FILE_SPECIAL_ACCESS is checked by the NT I/O system the same as
# FILE_ANY_ACCESS.
# The file systems, however, may add additional access checks for I/O and
# FS controls that use this value.
FILE_ANY_ACCESS = 0
FILE_SPECIAL_ACCESS = FILE_ANY_ACCESS
FILE_READ_ACCESS = 0x0001
FILE_WRITE_ACCESS = 0x0002

# Flags controlling what is included in the device information set built by SetupDiGetClassDevs
DIGCF_DEFAULT = 0x00000001
DIGCF_PRESENT = 0x00000002
DIGCF_ALLCLASSES = 0x00000004
DIGCF_PROFILE = 0x00000008
DIGCF_DEVICEINTERFACE = 0x00000010

#
#
# # Start receiving IR.
# IoCtrl_StartReceive  = IOCTL_IR_ENTER_PRIORITY_RECEIVE
# # Stop receiving IR.
# IoCtrl_StopReceive   = IOCTL_IR_EXIT_PRIORITY_RECEIVE
# # Get IR device details.
# IoCtrl_GetDetails    = IOCTL_IR_GET_DEV_CAPS
# # Get IR blasters
# IoCtrl_GetBlasters   = IOCTL_IR_GET_EMITTERS
# # Receive IR.
# IoCtrl_Receive       = IOCTL_IR_PRIORITY_RECEIVE
# # Transmit IR.
# IoCtrl_Transmit      = IOCTL_IR_TRANSMIT
# # Reset IR.
# IoCtrl_Reset         = IOCTL_IR_RESET_DEVICE

setupapi = ctypes.windll.SetupApi

# WINSETUPAPI
# HDEVINFO
# WINAPI
# SetupDiGetClassDevsW(
# _In_opt_ CONST GUID *ClassGuid,
# _In_opt_ PCWSTR Enumerator,
# _In_opt_ HWND hwndParent,
# _In_ DWORD Flags
# );
SetupDiGetClassDevsW = setupapi.SetupDiGetClassDevsW
SetupDiGetClassDevsW.restype = HDEVINFO

SetupDiGetClassDevs = SetupDiGetClassDevsW

# WINSETUPAPI
# BOOL
# WINAPI
# SetupDiEnumDeviceInfo(
# _In_ HDEVINFO DeviceInfoSet,
# _In_ DWORD MemberIndex,
# _Out_ PSP_DEVINFO_DATA DeviceInfoData
# );
SetupDiEnumDeviceInfo = setupapi.SetupDiEnumDeviceInfo
SetupDiEnumDeviceInfo.restype = BOOL

# WINSETUPAPI
# BOOL
# WINAPI
# SetupDiEnumDeviceInterfaces(
# _In_ HDEVINFO DeviceInfoSet,
# _In_opt_ PSP_DEVINFO_DATA DeviceInfoData,
# _In_ CONST GUID *InterfaceClassGuid,
# _In_ DWORD MemberIndex,
# _Out_ PSP_DEVICE_INTERFACE_DATA DeviceInterfaceData
# );
SetupDiEnumDeviceInterfaces = setupapi.SetupDiEnumDeviceInterfaces
SetupDiEnumDeviceInterfaces.restype = BOOL

# WINSETUPAPI
# BOOL
# WINAPI
# SetupDiGetDeviceInterfaceDetailW(
# _In_ HDEVINFO DeviceInfoSet,
# _In_ PSP_DEVICE_INTERFACE_DATA DeviceInterfaceData,
# _Out_writes_bytes_to_opt_(DeviceInterfaceDetailDataSize, *RequiredSize) PSP_DEVICE_INTERFACE_DETAIL_DATA_W DeviceInterfaceDetailData,
# _In_ DWORD DeviceInterfaceDetailDataSize,
# _Out_opt_ _Out_range_(>=, sizeof(SP_DEVICE_INTERFACE_DETAIL_DATA_W)) PDWORD RequiredSize,
# _Out_opt_ PSP_DEVINFO_DATA DeviceInfoData
# );
SetupDiGetDeviceInterfaceDetailW = setupapi.SetupDiGetDeviceInterfaceDetailW
SetupDiGetDeviceInterfaceDetailW.restype = BOOL

SetupDiGetDeviceInterfaceDetail = SetupDiGetDeviceInterfaceDetailW

# WINSETUPAPI
# BOOL
# WINAPI
# SetupDiDestroyDeviceInfoList(
# _In_ HDEVINFO DeviceInfoSet
# );
SetupDiDestroyDeviceInfoList = setupapi.SetupDiDestroyDeviceInfoList
SetupDiDestroyDeviceInfoList.restype = BOOL

kernel32 = ctypes.windll.Kernel32

# WINBASEAPI
# BOOL
# WINAPI
# DeviceIoControl(
# _In_ HANDLE hDevice,
# _In_ DWORD dwIoControlCode,
# _In_reads_bytes_opt_(nInBufferSize) LPVOID lpInBuffer,
# _In_ DWORD nInBufferSize,
# _Out_writes_bytes_to_opt_(nOutBufferSize,*lpBytesReturned) LPVOID lpOutBuffer,
# _In_ DWORD nOutBufferSize,
# _Out_opt_ LPDWORD lpBytesReturned,
# _Inout_opt_ LPOVERLAPPED lpOverlapped
# );
DeviceIoControl = kernel32.DeviceIoControl
DeviceIoControl.restype = BOOL

# WINBASEAPI
# _Ret_maybenull_
# HANDLE
# WINAPI
# CreateEventW(
# _In_opt_ LPSECURITY_ATTRIBUTES lpEventAttributes,
# _In_ BOOL bManualReset,
# _In_ BOOL bInitialState,
# _In_opt_ LPCWSTR lpName
# );
CreateEventW = kernel32.CreateEventW
CreateEventW.restype = HANDLE

CreateEvent = CreateEventW

# WINBASEAPI
# HANDLE
# WINAPI

# CreateFileW(
# _In_ LPCWSTR lpFileName,
# _In_ DWORD dwDesiredAccess,
# _In_ DWORD dwShareMode,
# _In_opt_ LPSECURITY_ATTRIBUTES lpSecurityAttributes,
# _In_ DWORD dwCreationDisposition,
# _In_ DWORD dwFlagsAndAttributes,
# _In_opt_ HANDLE hTemplateFile
# );
CreateFileW = kernel32.CreateFileW
CreateFileW.restype = HANDLE

CreateFile = CreateFileW

# WINBASEAPI
# BOOL
# WINAPI
# CloseHandle(
# _In_ _Post_ptr_invalid_ HANDLE hObject
# );
CloseHandle = kernel32.CloseHandle
CloseHandle.restype = BOOL

# WINBASEAPI
# BOOL
# WINAPI
# CancelIo(
# _In_ HANDLE hFile
# );
CancelIo = kernel32.CancelIo
CancelIo.restype = BOOL

# WINBASEAPI
# DWORD
# WINAPI
# WaitForMultipleObjects(
# _In_ DWORD nCount,
# _In_reads_(nCount) CONST HANDLE* lpHandles,
# _In_ BOOL bWaitAll,
# _In_ DWORD dwMilliseconds
# );
WaitForMultipleObjects = kernel32.WaitForMultipleObjects
WaitForMultipleObjects.restype = DWORD

# WINBASEAPI
# BOOL
# WINAPI
# GetOverlappedResult(
# _In_ HANDLE hFile,
# _In_ LPOVERLAPPED lpOverlapped,
# _Out_ LPDWORD lpNumberOfBytesTransferred,
# _In_ BOOL bWait
# );
GetOverlappedResult = kernel32.GetOverlappedResult
GetOverlappedResult.restype = BOOL


def CTL_CODE(DeviceType, Function, Method, Access):
    return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method


def DEFINE_GUID(l, w1, w2, b1, b2, b3, b4, b5, b6, b7, b8):
    w0 = hex(l)[2:].upper().rstrip('L')
    w1 = hex(w1)[2:].upper().rstrip('L')
    w2 = hex(w2)[2:].upper().rstrip('L')
    w3 = hex((b1 << 8) | b2)[2:].upper().rstrip('L')
    w4 = hex(
        (((b3 << 8) | b4) << 32) |
        (((b5 << 8) | b6) << 16) |
        ((b7 << 8) | b8)
    )[2:].upper().rstrip('L')

    return GUID('{' + '-'.join([w0, w1, w2, w3, w4]) + '}')


GUID_CLASS_IRBUS = DEFINE_GUID(0x7951772d, 0xcd50, 0x49b7, 0xb1, 0x03, 0x2b, 0xaa, 0xc4, 0x94, 0xfc, 0x57)

# + + IOCTL_IR_GET_DEVCAPS Returns device capabilities. For legacy
# devices, the Capabilities registry entry can be used to populate
# this structure. For new devices, the implementation is left as an
# exercise for the reader. The capabilities structure gets rev'ed when
# new capabilities are added to the class driver. The class driver
# sends the largest possible structure size to the port driver. The
# port driver populates the capabilties structure, including the
# ProtocolVersion member. The class driver then uses the
# ProtocolVersion member to decide which version of IR_DEV_CAPS the
# port driver has filled in. Used in IR DDI Versions: V1, V2 V1: port
# driver must set ProtocolVersion to 0x100 and fill in required
# members of IR_DEV_CAPS_V1 structure. V2: port driver must set
# ProtocolVersion to 0x200 and fill in required members of
# IR_DEV_CAPS_V2 structure Parameters: lpOutBuffer - pointer to caller
# - allocated IR_DEV_CAPS_V2 structure nOutBufferSize - ctypes.sizeof
# (IR_DEV_CAPS_V2) - -
IOCTL_IR_GET_DEV_CAPS = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    1,
    METHOD_BUFFERED,
    FILE_READ_ACCESS
)

# + + IOCTL_IR_GET_EMITTERS Gets attached emitters and returns the
# information in a bitmask. Information returned in lpOutBuffer. Used
# in IR DDI Versions: V1, V2 Parameters: lpOutBuffer - pointer to
# caller - allocated buffer ctypes.sizeof(ULONG) nOutBufferSize -
# ctypes.sizeof(ULONG) - -
IOCTL_IR_GET_EMITTERS = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    2,
    METHOD_BUFFERED,
    FILE_READ_ACCESS,
)

# + + IOCTL_IR_FLASH_RECEIVER Flash an LED on the given receiver. Used
# to tell the user where to point their remote, so a given
# "receiver box" with multiple receiver parts only needs one LED to
# flash. Used in IR DDI Versions: V1, V2 Parameters: lpInBuffer -
# pointer to caller - allocated buffer ctypes.sizeof(ULONG) with
# bitmask of receivers to flash nInBufferSize - ctypes.sizeof(ULONG) -
# -
IOCTL_IR_FLASH_RECEIVER = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    3,
    METHOD_BUFFERED,
    FILE_WRITE_ACCESS,
)

# + + IOCTL_IR_RESET_DEVICE Resets the given device. When a device is
# reset, all pending transmit and receive IOCTLs are cancelled by the
# class driver Used in IR DDI Versions: V1, V2 Parameters: - -
IOCTL_IR_RESET_DEVICE = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    4,
    METHOD_BUFFERED,
    FILE_WRITE_ACCESS,
)

# + + IOCTL_IR_TRANSMIT Transmits the given IR stream on the given
# port(s) at the given carrier frequency. On legacy devices, this
# maintains the pre - existing carrier frequency, port masks, and
# sample period values.
# (ie. it gets the old values, changes them, transmits, and then changes them back.)
# This IOCTL is synchronous. It does not return until the IR has
# actually been transmitted. Used in IR DDI Versions: V1, V2
# Parameters:
# lpInBuffer - pointer to caller - allocated IR_TRANSMIT_PARAMS structure
# nInBufferSize - ctypes.sizeof(IR_TRANSMIT_PARAMS)
# lpOutBuffer - pointer to caller - allocated IR_TRANSMIT_CHUNCK that contains the data to be transmitted
# nOutBufferSize - size of caller - allocated buffer. - -
IOCTL_IR_TRANSMIT = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    5,
    METHOD_IN_DIRECT,
    FILE_WRITE_ACCESS,
)

# + + IOCTL_IR_RECEIVE Receives IR. Does not return until IR is
# available. If there is no more IR data available than space in the
# buffer, IrReceiveParms - >DataEnd is set to TRUE. The provided
# timeout is used to define the end of a keypress. So, once the driver
# starts receiving IR from the hardware, it will continue to add it to
# the buffer until the specified time passes with no IR. Used in IR
# DDI Versions: V1, V2 Parameters: lpOutBuffer - pointer to caller -
# allocated IR_RECEIVE_PARAMS structure nOutBufferSize -
# ctypes.sizeof(IR_RECEIVE_PARAMS) - -
IOCTL_IR_RECEIVE = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    6,
    METHOD_OUT_DIRECT,
    FILE_READ_ACCESS,
)

# + + IOCTL_IR_PRIORITY_RECEIVE This request is sent from CIRClass and
# receives Run Length Coded (RLC) IR data when the device is running
# in Priority Receive mode. If the device is not already in Priority
# Receive mode, initiated by having previously received an
# IOCTL_ENTER_PRIORITY_RECEIVE, the CIR Port driver fails this request
# immediately. If in Priority Receive mode, the request will remain
# pending until one of two events occurs:
# 1) The data buffer provided in the request has been completely filled with data.
# 2) An IR timeout occurs. The length of time required for the IR
# timeout was specified when entering Priority Receive mode. While in
# Priority Receive mode and processing IOCTL_IR_PRIORITY_RECEIVE
# requests, IOCTL_IR_RECEIVE requests remain pending and are not
# filled with IR data.
# Used in IR DDI Versions: V1, V2
# Parameters:
# lpOutBuffer - pointer to caller - allocated IR_PRIORITY_RECEIVE_PARAMS structure
# nOutBufferSize - ctypes.sizeof(IR_PRIORITY_RECEIVE_PARAMS) - -
#
IOCTL_IR_PRIORITY_RECEIVE = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    8,
    METHOD_OUT_DIRECT,
    FILE_READ_ACCESS,
)

# + + IOCTL_IR_HANDSHAKE This IOCTL is sent from CIRClass before
# creating the HID child device to represent the port. This IOCTL is
# to be completed synchronously by the port as an indication that it
# is prepared to return RLC IR data to the class driver. Used in IR
# DDI Versions: V1, V2 Parameters: - -
IOCTL_IR_HANDSHAKE = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    9,
    METHOD_BUFFERED,
    FILE_ANY_ACCESS,
)

# + + IOCTL_IR_ENTER_PRIORITY_RECEIVE This request is sent to prepare
# the port to enter Priority Receive mode. While the device is in
# Priority Receive mode, all IOCTL_IR_RECEIVE requests should be
# starved and IOCTL_IR_PRIORITY_RECEIVE requests should be completed.
# Used in IR DDI Versions: V1, V2 Parameters: lpOutBuffer - pointer to
# caller - allocated IOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS structure
# nOutBufferSize -
# ctypes.sizeof(IOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS) - -
IOCTL_IR_ENTER_PRIORITY_RECEIVE = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    10,
    METHOD_BUFFERED,
    FILE_WRITE_ACCESS,
)

# + + IOCTL_IR_EXIT_PRIORITY_RECEIVE This request is sent to end
# Priority Receive mode. Upon receipt of the request, the port should
# abort any outstanding IOCTL_IR_PRIORITY_RECEIVE requests and fail
# any future IOCTL_IR_PRIORITY_RECEIVE requests
# (before receiving a new IOCTL_IR_ENTER_PRIORITY_RECEIVE request). As
# a result of receiving this IOCTL, the CIR Port driver is responsible
# for restoring the device to the state that it was in before receipt
# of the IOCTL_IR_ENTER_PRIORITY_RECEIVE. Used in IR DDI Versions: V1,
# V2 Parameters: - -
IOCTL_IR_EXIT_PRIORITY_RECEIVE = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    11,
    METHOD_BUFFERED,
    FILE_WRITE_ACCESS,
)

# + + IOCTL_IR_USER_OPEN This IOCTL is sent from the class driver when
# a user has indirectly opened the port driver through IRCLASS. This
# IOCTL is informational only, allowing the port to do any
# initialization or bookkeeping required to handle requests not
# directly originating from IRCLASS. Used in IR DDI Versions: V1, V2
# Parameters: - -
IOCTL_IR_USER_OPEN = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    12,
    METHOD_BUFFERED,
    FILE_WRITE_ACCESS,
)

# + + IOCTL_IR_USER_CLOSE This IOCTL is sent from IRCLASS when a user
# has indirectly closed the port driver. This IOCTL is informational
# only, allowing the port to do any cleanup required when closed by a
# user. Used in IR DDI Versions: V1, V2 Parameters: - -
IOCTL_IR_USER_CLOSE = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    13,
    METHOD_BUFFERED,
    FILE_WRITE_ACCESS,
)

# + + IOCTL_IR_SET_WAKE_PATTERN This IOCTL is sent from IRCLASS to
# configure the wake pattern. This is done dynamically in response to
# user input, so it could be done at any time. Used in IR DDI
# Versions: V2 only Parameters: lpInBuffer - pointer to caller -
# allocated IR_SET_WAKE_PATTERN_PARAMS structure nInBufferSize -
# ctypes.sizeof(IR_SET_WAKE_PATTERN_PARAMS) - -
IOCTL_IR_SET_WAKE_PATTERN = CTL_CODE(
    FILE_DEVICE_IRCLASS,
    14,
    METHOD_BUFFERED,
    FILE_WRITE_ACCESS,
)


class _IR_DEV_CAPS(ctypes.Structure):
    _fields_ = [
        ('ProtocolVersion', IR_ULONG_PTR),  # out
        ('NumTransmitPorts', IR_ULONG_PTR),  # out
        ('NumReceivePorts', IR_ULONG_PTR),  # out
        ('LearningReceiverMask', IR_ULONG_PTR),  # out
        ('DevCapsFlags', IR_ULONG_PTR),  # out
    ]


IR_DEV_CAPS = _IR_DEV_CAPS
PIR_DEV_CAPS = POINTER(_IR_DEV_CAPS)


class _IR_DEV_CAPS_V2(IR_DEV_CAPS):
    _fields_ = [
        ('WakeProtocols', IR_ULONG_PTR),
        ('TunerPnpId', WCHAR * MAXIMUM_FILENAME_LENGTH)
    ]


IR_DEV_CAPS_V2 = _IR_DEV_CAPS_V2
PIR_DEV_CAPS_V2 = POINTER(_IR_DEV_CAPS_V2)


class _IR_TRANSMIT_PARAMS(ctypes.Structure):
    _fields_ = [
        ('TransmitPortMask', IR_ULONG_PTR),  # in
        ('CarrierPeriod', IR_ULONG_PTR),  # in
        ('Flags', IR_ULONG_PTR),  # in
        ('PulseSize', IR_ULONG_PTR),  # in
    ]


IR_TRANSMIT_PARAMS = _IR_TRANSMIT_PARAMS
PIR_TRANSMIT_PARAMS = POINTER(_IR_TRANSMIT_PARAMS)


class _IR_TRANSMIT_CHUNK(ctypes.Structure):
    _fields_ = [
        ('OffsetToNextChunk', IR_ULONG_PTR),  # IR_TRANSMIT_CHUNK (or zero if no more chunks in buffer)
        ('RepeatCount', IR_ULONG_PTR),  # number of times to serially repeat "ByteCount" bytes of data
        ('ByteCount', IR_ULONG_PTR),  # count of data bytes to be sent
        ('Data', IR_ULONG_PTR * 1),  # Note: Each chunk is filled to integral ULONG_PTR boundary
    ]


IR_TRANSMIT_CHUNK = _IR_TRANSMIT_CHUNK
PIR_TRANSMIT_CHUNK = POINTER(_IR_TRANSMIT_CHUNK)


class _IR_RECEIVE_PARAMS(ctypes.Structure):
    _fields_ = [
        ('DataEnd', IR_ULONG_PTR),  # out
        ('ByteCount', IR_ULONG_PTR),  # in
        # ('Data', IR_ULONG_PTR * 100), # out
    ]


IR_RECEIVE_PARAMS = _IR_RECEIVE_PARAMS
PIR_RECEIVE_PARAMS = POINTER(_IR_RECEIVE_PARAMS)


class _IR_PRIORITY_RECEIVE_PARAMS(ctypes.Structure):
    _fields_ = [
        ('DataEnd', IR_ULONG_PTR),  # out
        ('ByteCount', IR_ULONG_PTR),  # in
        ('CarrierFrequency', IR_ULONG_PTR),  # out
        # ('Data', IR_ULONG_PTR * 100), # in
    ]


IR_PRIORITY_RECEIVE_PARAMS = _IR_PRIORITY_RECEIVE_PARAMS
PIR_PRIORITY_RECEIVE_PARAMS = POINTER(_IR_PRIORITY_RECEIVE_PARAMS)


class _IOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS(ctypes.Structure):
    _fields_ = [
        ('Receiver', IR_ULONG_PTR),  # in
        ('TimeOut', IR_ULONG_PTR),  # in
    ]


IOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS = _IOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS
PIOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS = POINTER(_IOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS)


class _IOCTL_IR_SET_WAKE_PATTERN_PARAMS(ctypes.Structure):
    _fields_ = [
        ('Protocol', IR_ULONG_PTR),  # in
        ('Payload', IR_ULONG_PTR),  # in
        ('Address', IR_ULONG_PTR),  # in
    ]


IOCTL_IR_SET_WAKE_PATTERN_PARAMS = _IOCTL_IR_SET_WAKE_PATTERN_PARAMS
PIOCTL_IR_SET_WAKE_PATTERN_PARAMS = POINTER(_IOCTL_IR_SET_WAKE_PATTERN_PARAMS)


class _SP_DEVINFO_DATA(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('cbSize', DWORD),
        ('ClassGuid', GUID),
        ('DevInst', DWORD),  # DEVINST handle
        ('Reserved', ULONG_PTR),
    ]


SP_DEVINFO_DATA = _SP_DEVINFO_DATA
PSP_DEVINFO_DATA = POINTER(_SP_DEVINFO_DATA)


class _SP_DEVICE_INTERFACE_DATA(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('cbSize', DWORD),
        ('InterfaceClassGuid', GUID),
        ('Flags', DWORD),
        ('Reserved', ULONG_PTR),
    ]


SP_DEVICE_INTERFACE_DATA = _SP_DEVICE_INTERFACE_DATA
PSP_DEVICE_INTERFACE_DATA = POINTER(_SP_DEVICE_INTERFACE_DATA)


class _SP_DEVICE_INTERFACE_DETAIL_DATA_W(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ('cbSize', DWORD),
        ('DevicePath', WCHAR * 1)
    ]


SP_DEVICE_INTERFACE_DETAIL_DATA_W = _SP_DEVICE_INTERFACE_DETAIL_DATA_W
PSP_DEVICE_INTERFACE_DETAIL_DATA_W = POINTER(_SP_DEVICE_INTERFACE_DETAIL_DATA_W)

SP_DEVICE_INTERFACE_DETAIL_DATA = SP_DEVICE_INTERFACE_DETAIL_DATA_W
PSP_DEVICE_INTERFACE_DETAIL_DATA = PSP_DEVICE_INTERFACE_DETAIL_DATA_W


class _OVERLAPPED(ctypes.Structure):
    class _DUMMYUNIONNAME(ctypes.Union):
        class _DUMMYSTRUCTNAME(ctypes.Structure):
            _fields_ = [
                ('Offset', DWORD),
                ('OffsetHigh', DWORD),
            ]

        _fields_ = [
            ('DUMMYSTRUCTNAME', _DUMMYSTRUCTNAME),
            ('Pointer', LPVOID),
        ]

    _fields_ = [
        ('Internal', ULONG_PTR),
        ('InternalHigh', ULONG_PTR),
        ('DUMMYUNIONNAME', _DUMMYUNIONNAME),
        ('hEvent', HANDLE),
    ]


OVERLAPPED = _OVERLAPPED
LPOVERLAPPED = POINTER(_OVERLAPPED)


def _get_ir_receiver_paths():
    DeviceInfoSet = SetupDiGetClassDevs(
        ctypes.byref(GUID_CLASS_IRBUS),
        NULL,
        NULL,
        DIGCF_PRESENT | DIGCF_DEVICEINTERFACE
    )
    if DeviceInfoSet == INVALID_HANDLE_VALUE:
        raise ctypes.WinError()

    DeviceInterfaceData = SP_DEVICE_INTERFACE_DATA()
    DeviceInterfaceData.cbSize = ctypes.sizeof(SP_DEVICE_INTERFACE_DATA)
    DeviceInfoData = SP_DEVINFO_DATA()
    DeviceInfoData.cbSize = ctypes.sizeof(SP_DEVINFO_DATA)
    MemberIndex = 0
    device_paths = []

    while True:
        if not SetupDiEnumDeviceInterfaces(
                DeviceInfoSet,
                None,
                ctypes.byref(GUID_CLASS_IRBUS),
                MemberIndex,
                ctypes.byref(DeviceInterfaceData)
        ):
            err = ctypes.GetLastError()
            if err == ERROR_NO_MORE_ITEMS:
                break
            else:
                raise ctypes.WinError(err)

        RequiredSize = DWORD()
        SetupDiGetDeviceInterfaceDetail(
            DeviceInfoSet,
            ctypes.byref(DeviceInterfaceData),
            None,
            0,
            ctypes.byref(RequiredSize),
            ctypes.byref(DeviceInfoData)
        )
        DevicePath = ctypes.create_string_buffer(RequiredSize.value)
        pDeviceInterfaceDetailData = ctypes.cast(DevicePath, PSP_DEVICE_INTERFACE_DETAIL_DATA)
        pDeviceInterfaceDetailData.contents.cbSize = ctypes.sizeof(
            SP_DEVICE_INTERFACE_DETAIL_DATA
        )
        SetupDiGetDeviceInterfaceDetail(
            DeviceInfoSet,
            ctypes.byref(DeviceInterfaceData),
            pDeviceInterfaceDetailData,
            RequiredSize.value,
            ctypes.byref(RequiredSize),
            None
        )

        device_path = ctypes.wstring_at(ctypes.addressof(pDeviceInterfaceDetailData.contents) + 4)
        device_paths += [device_path]
        MemberIndex += 1

    SetupDiDestroyDeviceInfoList(DeviceInfoSet)

    return device_paths


def _open_ir_receiver(device_path):
    lpFileName = ctypes.create_unicode_buffer(device_path)
    dwDesiredAccess = DWORD(GENERIC_READ | GENERIC_WRITE)
    dwShareMode = DWORD(0)
    lpSecurityAttributes = NULL
    dwCreationDisposition = DWORD(OPEN_EXISTING)
    dwFlagsAndAttributes = DWORD(FILE_FLAG_OVERLAPPED)
    hTemplateFile = NULL

    handle = CreateFile(
        lpFileName,
        dwDesiredAccess,
        dwShareMode,
        lpSecurityAttributes,
        dwCreationDisposition,
        dwFlagsAndAttributes,
        hTemplateFile
    )

    return handle


def _get_ir_capabilities(hDevice):
    outBuffer = IR_DEV_CAPS()

    if _io_control(IOCTL_IR_GET_DEV_CAPS, hDevice, NULL, outBuffer):
        if outBuffer.ProtocolVersion == DEV_CAPS_PROTOCOL_VERSION_V2:
            _io_control(IOCTL_IR_GET_DEV_CAPS, hDevice, NULL, outBuffer)
            outBuffer_2 = IR_DEV_CAPS_V2()

            if _io_control(IOCTL_IR_GET_DEV_CAPS, hDevice, NULL, outBuffer_2):
                return outBuffer_2

        return outBuffer


def get_ir_devices():
    devices = []

    for device_path in _get_ir_receiver_paths():
        hDevice = _open_ir_receiver(device_path)

        if hDevice == INVALID_HANDLE_VALUE:
            continue

        caps = _get_ir_capabilities(hDevice)

        if caps is None:
            CloseHandle(hDevice)
            continue

        devices += [IRDevice(hDevice, device_path, caps)]

    return devices


def _io_control(ioControlCode, hDevice, inBuffer, outBuffer, outBufferSize=None):
    dwIoControlCode = DWORD(ioControlCode)

    if inBuffer is NULL:
        lpInBuffer = NULL
        nInBufferSize = INT(0)
    elif 'PyCPointerType' in str(type(inBuffer)):
        lpInBuffer = inBuffer
        nInBufferSize = INT(ctypes.sizeof(inBuffer.contents.__class__))
    else:
        lpInBuffer = ctypes.byref(inBuffer)
        nInBufferSize = INT(ctypes.sizeof(inBuffer.__class__))

    if outBuffer is NULL:
        lpOutBuffer = NULL
        nOutBufferSize = INT(0)

    elif 'PyCPointerType' in str(type(outBuffer)):
        lpOutBuffer = outBuffer
        if outBufferSize is None:
            nOutBufferSize = INT(ctypes.sizeof(outBuffer.contents.__class__))
        else:
            nOutBufferSize = INT(outBufferSize)
    else:
        lpOutBuffer = ctypes.byref(outBuffer)

        if outBufferSize is None:
            nOutBufferSize = INT(ctypes.sizeof(outBuffer.__class__))
        else:
            nOutBufferSize = INT(outBufferSize)

    lpNumberOfBytesTransferred = DWORD()
    lpOverlapped = OVERLAPPED()

    lpEventAttributes = NULL
    bManualReset = BOOL(False)
    bInitialState = BOOL(False)
    lpName = NULL

    lpHandles = (HANDLE * 1)()

    lpHandles[0] = lpOverlapped.hEvent = CreateEvent(
        lpEventAttributes,
        bManualReset,
        bInitialState,
        lpName
    )

    if not DeviceIoControl(
            hDevice,
            dwIoControlCode,
            lpInBuffer,
            nInBufferSize,
            lpOutBuffer,
            nOutBufferSize,
            ctypes.byref(lpNumberOfBytesTransferred),
            ctypes.byref(lpOverlapped)
    ):
        err = ctypes.GetLastError()

        if err != ERROR_IO_PENDING:
            CancelIo(hDevice)
            CloseHandle(lpOverlapped.hEvent)
            return 0

        nCount = DWORD(1)
        bWaitAll = BOOL(False)
        dwMilliseconds = DWORD(INFINITE)

        response = WaitForMultipleObjects(
            nCount,
            lpHandles,
            bWaitAll,
            dwMilliseconds
        )

        if response == WAIT_OBJECT_0:
            bWait = BOOL(True)
            if not GetOverlappedResult(
                    hDevice,
                    ctypes.byref(lpOverlapped),
                    ctypes.byref(lpNumberOfBytesTransferred),
                    bWait
            ):
                CancelIo(hDevice)
                CloseHandle(lpOverlapped.hEvent)
                raise ctypes.WinError()

            CloseHandle(lpOverlapped.hEvent)
            return lpNumberOfBytesTransferred

        CancelIo(hDevice)
        CloseHandle(lpOverlapped.hEvent)
        raise ctypes.WinError()

    CloseHandle(lpOverlapped.hEvent)
    return lpNumberOfBytesTransferred


class IRDevice(object):
    def __init__(self, handle, device_path, caps):

        self.handle = handle
        self.device_path = device_path

        self.num_tx_ports = caps.NumTransmitPorts
        self._learn_mask = caps.LearningReceiverMask
        self._capabilities = caps.DevCapsFlags

        if caps.ProtocolVersion == DEV_CAPS_PROTOCOL_VERSION_V2:
            self.version = 2
            self._wake_protocols = caps.WakeProtocols
            self.tuner_id = ctypes.wstring_at(ctypes.addressof(caps) + 24)

        else:
            self.version = 1
            self._wake_protocols = None
            self.tuner_id = None

        self._packet_timeout = 100

        self._end_event = threading.Event()
        self._process_event = threading.Event()
        self._learn_lock = threading.Lock()
        self._receive_thread = None
        self._process_thread = None
        self._callbacks = []
        self._process_queue = deque()
        self.use_alternate_receive = True

    def bind(self, callback):
        if callback not in self._callbacks:
            self._callbacks += [callback]
            return True
        return False

    def unbind(self, callback):
        if callback in self._callbacks:
            self._callbacks.remove(callback)
            return True

        return False

    def stop_receive(self):
        if self._receive_thread is not None:
            self._end_event.set()
            if (
                    threading.current_thread() != self._receive_thread and
                    self._receive_thread.is_alive()
            ):
                self._receive_thread.join(1.0)

            self._receive_thread = None
            self._process_thread = None

    def start_receive(self):
        if self._receive_thread is None:
            self._receive_thread = threading.Thread(target=self.__receive_loop)
            self._receive_thread.daemon = True
            self._end_event.clear()
            self._receive_thread.start()

    def __decode(self, data, result, freqs):
        nGot = len(data)

        try:
            while nGot > 0:
                header = unpack_from(3 * PACK_FORMAT, data)
                if header[0] == 1 and header[2] > 0:
                    freqs.append(header[2])
                dataEnd = nGot
                if nGot > 100 + 3 * IR_PTR_SIZE:
                    dataEnd = 100 + 3 * IR_PTR_SIZE
                nGot -= dataEnd

                val_data = data[3 * IR_PTR_SIZE:dataEnd]
                dataEnd -= 3 * IR_PTR_SIZE
                vals = unpack_from((dataEnd / 4) * "i", val_data)
                data = data[100 + 3 * IR_PTR_SIZE:]

                for i, v in enumerate(vals):
                    a = abs(v)
                    result.append(a)
                    if a > 6500:
                        if len(result) >= 5:
                            return True
                        else:
                            del result[:]
                            del freqs[:]
                            freqs.append(0)

                            return False
        except:
            del result[:]
            del freqs[:]
            freqs.append(0)

            return None

        return False

    def __process_loop(self):
        freqs = [0]
        result = []

        while not self._end_event.is_set():
            while len(self._process_queue):
                data = self._process_queue.popleft()

                if not data:
                    continue

                ret = self.__decode(data, result, freqs)

                if ret is True:
                    for callback in self._callbacks[:]:
                        callback(IRCode(result[:], freqs[-1]))

                    del result[:]
                    del freqs[:]
                    freqs.append(0)

            self._process_event.wait()
            self._process_event.clear()

    def __receive_loop(self):

        if self.use_alternate_receive:
            port = self.__get_first_rx_port()
            if port is None:
                return

            with self._learn_lock:
                inBuffer = IOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS()
                inBuffer.Receiver = port
                inBuffer.TimeOut = self._packet_timeout

                _io_control(
                    IOCTL_IR_ENTER_PRIORITY_RECEIVE,
                    self.handle,
                    inBuffer,
                    NULL
                )

        self._process_thread = threading.Thread(target=self.__process_loop)
        self._process_thread.daemon = True
        self._process_thread.start()

        if self.use_alternate_receive:
            outBuffer = IR_PRIORITY_RECEIVE_PARAMS()
            max_chunk_size = ctypes.sizeof(IR_PRIORITY_RECEIVE_PARAMS) + 100
            outBufferSize = max_chunk_size + ctypes.sizeof(IR_ULONG_PTR)
            outBuffer.ByteCount = 100
        else:
            outBuffer = IR_RECEIVE_PARAMS()
            max_chunk_size = ctypes.sizeof(IR_RECEIVE_PARAMS) + 100
            outBufferSize = max_chunk_size + ctypes.sizeof(IR_ULONG_PTR)
            outBuffer.ByteCount = 100

        while not self._end_event.is_set():
            with self._learn_lock:
                if self.use_alternate_receive:
                    byte_count = _io_control(
                        IOCTL_IR_PRIORITY_RECEIVE,
                        self.handle,
                        NULL,
                        outBuffer,
                        outBufferSize
                    )
                else:
                    byte_count = _io_control(
                        IOCTL_IR_RECEIVE,
                        self.handle,
                        NULL,
                        outBuffer,
                        outBufferSize
                    )

                data = ctypes.cast(ctypes.byref(outBuffer), PUCHAR)

                byte_count = byte_count.value
                start = 0

                try:
                    while byte_count > max_chunk_size:
                        chunk = bytearray()

                        for i in range(start, max_chunk_size):
                            chunk.append(bytearray([data[i]])[0])

                        start += max_chunk_size
                        byte_count -= max_chunk_size
                        self._process_queue.append(chunk[:])

                    chunk = bytearray()
                    for i in range(start, start + byte_count):
                        chunk.append(bytearray([data[i]])[0])

                    self._process_queue.append(chunk[:])
                    self._process_event.set()
                except:
                    pass

        if self.use_alternate_receive:
            _io_control(IOCTL_IR_EXIT_PRIORITY_RECEIVE, self.handle, NULL, NULL)

        self._process_queue.clear()
        self._process_event.set()
        self._process_thread.join(1.0)

    def learn(self, port=-1, timeout=10.0):

        def exit_learn():
            _io_control(IOCTL_IR_EXIT_PRIORITY_RECEIVE, self.handle, NULL, NULL)

            if self.use_alternate_receive and self._receive_thread is not None:
                p = self.__get_first_rx_port()
                if p is not None:
                    inBuffer = IOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS()
                    inBuffer.Receiver = p
                    inBuffer.TimeOut = self._packet_timeout

                    _io_control(
                        IOCTL_IR_ENTER_PRIORITY_RECEIVE,
                        self.handle,
                        inBuffer,
                        NULL
                    )

        if port == -1:
            port = self.__get_first_learn_port()

            if port is None:
                return

        if port in self.rx_ports:
            with self._learn_lock:
                if self.use_alternate_receive and self._receive_thread is not None:
                    _io_control(IOCTL_IR_EXIT_PRIORITY_RECEIVE, self.handle, NULL, NULL)

                inBuffer = IOCTL_IR_ENTER_PRIORITY_RECEIVE_PARAMS()
                inBuffer.Receiver = port
                inBuffer.TimeOut = self._packet_timeout

                _io_control(IOCTL_IR_ENTER_PRIORITY_RECEIVE, self.handle, inBuffer, NULL)

                if self.can_flash_led:
                    inBuffer = ULONG(0 | (1 << port))
                    _io_control(IOCTL_IR_FLASH_RECEIVER, self.handle, inBuffer, NULL)

                outBuffer = IR_PRIORITY_RECEIVE_PARAMS()
                max_chunk_size = ctypes.sizeof(IR_PRIORITY_RECEIVE_PARAMS) + 100
                outBufferSize = max_chunk_size + ctypes.sizeof(IR_ULONG_PTR)
                outBuffer.ByteCount = 100

                result = []
                freqs = [0]

                start_time = time.time()

                while time.time() - start_time < timeout:
                    byte_count = _io_control(
                        IOCTL_IR_PRIORITY_RECEIVE,
                        self.handle,
                        NULL,
                        outBuffer,
                        outBufferSize
                    )
                    data = ctypes.cast(ctypes.byref(outBuffer), PUCHAR)

                    byte_count = byte_count.value
                    start = 0

                    try:
                        while byte_count > max_chunk_size:
                            chunk = bytearray()

                            for i in range(start, max_chunk_size):
                                chunk.append(bytearray([data[i]])[0])

                            start += max_chunk_size
                            byte_count -= max_chunk_size

                            if self.__decode(chunk[:], result, freqs):
                                exit_learn()
                                return IRCode(result[:], freqs[-1])

                        chunk = bytearray()
                        for i in range(start, start + byte_count):
                            chunk.append(bytearray([data[i]])[0])

                        if self.__decode(chunk[:], result, freqs):
                            exit_learn()
                            return IRCode(result[:], freqs[-1])
                    except:
                        pass

        exit_learn()

    def __get_first_rx_port(self):
        for i in range(32):
            if self._learn_mask & (1 << i) == 0:
                return i

    def __get_first_learn_port(self):
        for i in range(32):
            if self._learn_mask & (1 << i) != 0:
                return i

    @property
    def packet_timeout(self):
        return self._packet_timeout

    @packet_timeout.setter
    def packet_timeout(self, value):
        self._packet_timeout = value

    def test_tx_ports(self):
        command = [
            0, 1, 272, 2650, -900, 400, -500, 400, -500, 400, -950, 400, -950, 1300, -950, 400, -500, 400,
            -500, 400, -500, 400, -500, 400, -500, 400, -500, 400, -500, 400, -500, 400, -500, 400, -500, 850,
            -500, 400, -500, 400, -500, 400, -950, 400, -500, 400, -500, 400, -500, 400, -500, 850, -950, 400,
            -500, 400, -500, 400, -500, 400, -500, 400, -500, 400, -500, 400, -500, 400, -500, 850, -69700
        ]
        params = [0, 27, 0, 0]

        outBuffer = (DWORD * len(command))(*command)
        inBuffer = ctypes.cast((DWORD * len(params))(*params), PIR_TRANSMIT_PARAMS)

        ports = {}
        for port in self.tx_ports:
            inBuffer.contents.TransmitPortMask = ULONG_PTR(0 | (1 << port))

            ports[port] = _io_control(IOCTL_IR_TRANSMIT, self.handle, inBuffer, outBuffer)

        return ports


    def transmit(self, ir_code, port=-1):

        if not isinstance(ir_code, IRCode):
            raise ValueError('ir code is not an instance is the IRCode class')

        data = ir_code.mce

        in_data = data[:ctypes.sizeof(IR_TRANSMIT_PARAMS)]
        out_data = data[ctypes.sizeof(IR_TRANSMIT_PARAMS):]
        in_data = (ctypes.c_char * len(in_data))(*list(in_data))
        out_data = (ctypes.c_char * len(out_data))(*list(out_data))

        inBuffer = ctypes.cast(in_data, PIR_TRANSMIT_PARAMS)
        if port == -1:
            ports = 0

            for p in self.tx_ports:
                ports |= (1 << p)

            inBuffer.contents.TransmitPortMask = ULONG_PTR(ports)

        elif port in self.tx_ports:
            inBuffer.contents.TransmitPortMask = ULONG_PTR(0 | (1 << port))

        else:
            return False

        outBuffer = ctypes.cast(out_data, PIR_TRANSMIT_CHUNK)
        _io_control(IOCTL_IR_TRANSMIT, self.handle, inBuffer, outBuffer)

        return True

    @property
    def num_connected_tx_ports(self):
        return len(self.tx_ports)

    @property
    def tx_ports(self):
        outBuffer = ULONG(0)
        ports = []

        if _io_control(IOCTL_IR_GET_EMITTERS, self.handle, NULL, outBuffer):
            for i in range(32):
                if outBuffer.value & (1 << i):
                    ports += [i]

        return ports

    @property
    def num_rx_ports(self):
        return len(self.rx_ports)

    @property
    def rx_ports(self):
        ports = []

        for i in range(32):
            if self._learn_mask & (1 << i):
                ports += [i]

        return ports

    @property
    def can_flash_led(self):
        return bool(self._capabilities & DEV_CAPS_CAN_FLASH_RECEIVER_LED)

    @property
    def supports_wake(self):
        if self.version == 1:
            return False

        return bool(self._capabilities & V2_DEV_CAPS_SUPPORTS_WAKE)

    @property
    def supports_multiple_wake(self):
        if self.version == 1:
            return False

        return bool(self._capabilities & V2_DEV_CAPS_MULTIPLE_WAKE)

    @property
    def supports_programmable_wake(self):
        if self.version == 1:
            return False

        return bool(self._capabilities & V2_DEV_CAPS_PROGRAMMABLE_WAKE)

    @property
    def has_volitile_wake(self):
        if self.version == 1:
            return False

        return bool(self._capabilities & V2_DEV_CAPS_VOLATILE_WAKE_PATTERN)

    @property
    def is_learn_only(self):
        if self.version == 1:
            return False

        return bool(self._capabilities & V2_DEV_CAPS_LEARNING_ONLY)

    @property
    def has_narrow_bpf(self):
        if self.version == 1:
            return False

        return bool(self._capabilities & V2_DEV_CAPS_NARROW_BPF)

    @property
    def has_software_decode_input(self):
        if self.version == 1:
            return False

        return not bool(self._capabilities & V2_DEV_CAPS_NO_SWDECODE_INPUT)

    @property
    def has_hardware_decode_input(self):
        if self.version == 1:
            return False

        return bool(self._capabilities & V2_DEV_CAPS_HWDECODE_INPUT)

    @property
    def has_attached_tuner(self):
        if self.version == 1:
            return False

        return bool(self._capabilities & V2_DEV_CAPS_ATTACHED_TO_TUNER)

    @property
    def emulator_version(self):
        if self.version == 2:

            if bool(self._capabilities & V2_DEV_CAPS_EMULATOR_V1):
                return 1

            if bool(self._capabilities & V2_DEV_CAPS_EMULATOR_V2):
                return 2

    def reset(self):
        return _io_control(IOCTL_IR_RESET_DEVICE, self.handle, NULL, NULL)

    def close(self):
        if self._receive_thread is not None:
            self.stop_receive()

        CloseHandle(self.handle)

    def __del__(self):
        self.close()


import six
from .IrDecoder import IrDecoder


class IRCodeMetaClass(type):

    def __call__(cls, code, frequency=None):
        if isinstance(code, (list, tuple)):
            if frequency is None:
                frequency = 0

            code = pronto.ir_to_pronto_raw(frequency, code)
        return super(IRCodeMetaClass, cls).__call__(code)


@six.add_metaclass(IRCodeMetaClass)
class IRCode(str):

    def __init__(self, code, *args, **kargs):
        self._pronto_code = code
        self.repeat_count = 0

        try:
            str.__init__(self, code)
        except TypeError:
            str.__init__(self)

    @property
    def pronto(self):
        return self._pronto_code

    @property
    def decimal(self):
        _, code = pronto.pronto_to_mce(self._pronto_code, self.repeat_count)
        return code

    @property
    def frequency(self):
        m_freq, _ = pronto.pronto_to_mce(self._pronto_code, self.repeat_count)
        return m_freq

    def decode(self, *_, **__):
        decoder = IrDecoder(1.0)

        return decoder.Decode(self, len(self))

    @property
    def mce(self):
        freq, transmit_values = pronto.pronto_to_mce(self._pronto_code, self.repeat_count)
        transmit_code = pronto.round_and_pack_timings(transmit_values)

        header = pack(7 * PACK_FORMAT, 2, int(1000000. / freq), 0, 0, 0, 1, len(transmit_code))
        return header + transmit_code


if __name__ == '__main__':
    for dvc in get_ir_devices():
        print dvc.reset()
        print 'device path:', dvc.device_path
        print 'protocol version:', dvc.version
        print 'can flash led:', dvc.can_flash_led
        print '# of TX ports:', dvc.num_tx_ports
        print '# of connected TX ports:', dvc.num_connected_tx_ports
        print 'connected TX port id\'s:', ', '.join(hex(port) for port in dvc.tx_ports)
        print
        print '# of RX ports:', dvc.num_rx_ports
        print 'RX port id\'s:', ', '.join(hex(port) for port in dvc.rx_ports)
        print 'test tx ports:', dvc.test_tx_ports()


        def cb(data):
            print repr(data)


        dvc.bind(cb)

        dvc.start_receive()

        evt = threading.Event()
        evt.wait()
        dvc.close()