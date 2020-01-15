# -*- coding: utf-8 -*-
from __future__ import print_function

import pyWinMCERemote


devices = pyWinMCERemote.get_ir_devices()

if not devices:
    raise RuntimeError('No devices found')


ir_device = devices[0]

attr_names = (
    'name',
    'device_path',
    'description',
    'hardware_id',
    'manufacturer',
    'model',
    'vid',
    'pid',
    'num_connected_tx_ports',
    'num_tx_ports',
    'tx_ports',
    'num_rx_ports',
    'rx_ports',
    'can_flash_led',
    'supports_wake',
    'supports_multiple_wake',
    'supports_programmable_wake',
    'has_volitile_wake',
    'is_learn_only',
    'has_narrow_bpf',
    'has_software_decode_input',
    'has_hardware_decode_input',
    'has_attached_tuner',
    'tuner_id',
    'emulator_version',
    'packet_timeout',
    'use_alternate_receive'
)

for attr_name in attr_names:
    value = getattr(ir_device, attr_name)
    label = attr_name.replace('_', ' ').title()
    print(label + ':', value)

print()


def receive_callback(code):
    print()
    print('--RECEIVED IR CODE')
    print('Decoded:', code)
    print('RLC Code:', code.rlc_code)
    print('Pronto Code:', code.pronto)
    print('IR Frequency:', code.frequency)


ir_device.bind(receive_callback)
ir_device.start_receive()


try:
    raw_input('Press and key to exit')
except NameError:
    input('Press and key to exit')

ir_device.stop_receive()

