# pyWinMCERemote
An impossibly simple Python binding to the Windows Ehome CIR Remote API

Still being developed. at the present time most of the code has been completed. just need to 
iron out any possible bugs.



#### ***Updates***

---------------------------------

* Instance Singleton: only one instance of an IRDevice class can exist per device. This 
  will stop any possibility of having more then a single handle to a device created.

* Removes close() method: There is no longer a need to close a device. The closing of the
  handle gets done by reference count. This may add a smidge of additional overhead
  but the benifits of making sure that handle gets closed outweigh the tiny expense 
  of the new mechanism.
  You will however need to call `stop_receive()` if you called `start_receive()`
  
* Adds Setup.py: Adds the setup program.
    
   
#### ***Requirements***

---------------------------------

* comtypes
* six


There are only a few classes/methods/functions that need to be known about.


#### ***pyWinMCERemote.get_ir_devices()***

-------------------------------------

This is a simple function that enumerates all of the IR receivers/blasters attached to a PC.
This library/package supports multiple devices beaing attached. There is an attribute `IRDevice.device_path`
that can be used to identify a device. This attribute is persistant beten restarts. the only thing that can
cause this to not maintain being the same is if the device gets plugged into a different USB port.

This is the main entry point that you need to use to inerface with a receiver/blaster. it is going to return
a list of `pyWinMCERemote.ioctl.IRDevice` instances.


#### ***pyWinMCERemote.IRDevice***

--------------------------------------

* *Properties*

  Some of the propertis listed below I do not have a clue what whey are for. There 
  are added for the sake of completeness. There are 2 versions of the IR API the 
  items below `can_flash_led` are the ones that only version 2 support. if the 
  device is a version 1 device a defaulted value will be returned from those properties. 

  * packet_timeout: adjust the length of time to wait for a packet (ir code).
    This gets passed to the actual device. it is ho long the device will wait for 
    an incoming IR transmission. You can adjust this if you like. The default value 
    is set at 100 ms and this is done by the Windows API. I am sure this is probably 
    going to be the ideal ait time. There could be use case scenarios here a remote has
    an ir code that takes longer then 100ms for the whole transmission. In that cause you 
    may need to "tweak" this setting.
     
  * num_connected_tx_ports: the TX ports are the emitters/blasters. a single device can support
    up to 32. I have not seen such a device but the mechanics are in place to handle this.
    I personally have a device that has 2 blaster ports on it. If I only have one "eye" plugged
    in this will return a 1. because only 1 of the 2 are connected. 
    
  * tx_ports: list of blaster port numbers. This list is only going to contain the port numbers
    of the the connected ports. 
    
  * num_rx_ports: the number of available receive/learn ports.
  * rx_ports: list of port numbers for the availble receive.learn ports
  
  * can_flash_led: informational purposes. If a device has more then a single rx/learn port it
    might be setup in the same manner as the tx ports here there are jacks available to plug in
    a receiver eye. If that is the case then there may also be an LED on the device for each of 
    these jacks. The API allows me to flash the led of a specific tx port if the device supports
    it. and this does get done to notify the user that the learning process is running on that 
    port.
        
  * supports_wake: if the device supports waking the system
  * supports_multiple_wake: ???
  * supports_programmable_wake: ???
  * has_volitile_wake: ???
  * is_learn_only: if the device is learn only
  * has_narrow_bpf: ???
  * has_software_decode_input: ???
  * has_hardware_decode_input: ???
  * has_attached_tuner: if the device is apart of a tuner/capture card
  * emulator_version: ???
        
* *methods*
  * start_receive(): starts the receiving thread. There are actually 2 threads for the receiving.
    one handles the API calls to Windows and the other decodes the data that is gotten from Windows.
    The "processing" thread is also responsible for passing the decoded information to an application
    via a callback. It is OK to stall this thread any IR codes received will be queued to get 
    processed. so no missed ir transmissions will happen.
    
  * stop_receive(): stops the receiving/processing threads.
  
  * transmit(ir_code, port=-1): this is how you will blast a code. the `ir_code` parameter ***MUST***
    be an instance of `pyWinMCERemote.IRCode`. the `port` parameter is defaulted to `-1` which tells the 
    program to emit the ir code on all available blasters. If you want to specify a port number
    use one of the numbers from the `tx_ports` property.
      
  * learn(port=-1, timeout=10.0): sets the device into a learn mode. The learn mode alters the 
    sensitivity of the receiver. It will produce a more acurate code but the range gets limited to 
    within a few feet because of stray IR emissions getting into the transmission. I have always
    suggested to place the remote about 6" from the receiver and place a towel over the receiver and 
    the remote to obtain the best possible results. things like LED light bulbs and flourscent light 
    bulbs produce a large amount of ir. There is also a phenomonom called ir bounce. this is when ir
    from a remote can bounce off of semi reflective surfaces, this will give you an inacurate code. 
    So best to not learn ir on a glass shelf of an entertainment center. 
    
    The `timeout` parameter is how long to keep on trying to get a sucessfull code for. the default 
    value is 10 seconds.   
  
  * reset(): "reboots" the physical device

  * bind(callback): attaches a function to be used to notify an application of a received ir code.
  * unbind(callback): detaches an attached function so it will no longer get callbacks for received 
    ir codes.
    
  * test_tx_ports(): experimental
    
* *attributes*

  * use_alternate_receive: exerimental. set to false to use a different receive mechanism.



#### ***pyWinMCERemote.IRCode***

--------------------------------------

This class gets used any time the library deals with an ir code. so transmitting, learning and receiving.
is a wrapper class around the string class that has several properties and methods. If printed it is going 
to look like a string of a pronto code.

it accepts either a string pronto code or a raw ir code code as a list with an option frequency to construct 
the instance.

* *properties*
    pronto: returnes a non wrapped string version of the pronto code
    decimal: returns the decimal version of the code as a list 
    frequency: the transmission frequency (how fast the led blinks)
    mce: the code used in the Windows API
    
* *methods*
    decode(): this will return a more user friendly name for the code. If the remote is an MCE remote it 
    will return a button name 

* *attributes*
    repeat_count: defaulted to 0 this you would set if you are passing this code to be transmitted.
    

The real beauty of how I designed this library is that you can take the instance of the IRCode class
passed to the callback as a received code and pass it right to the transmit. this also works the same
if it is a learned code as well. It also supports being pickled and saving it is as simple as writing it
directly to a file. restoring it from a file is as simply as reading and passing the read value to the 
constructor.



#### ***Examples***

--------------------------------

    from __future__ import print_function
    
    import pyWinMCERemote
    
    
    devices = pyWinMCERemote.get_ir_devices()
    if devices:
        device = devices[0]
      
        print('device_path:', device.device_path) 
        print('num_connected_tx_ports:', device.num_connected_tx_ports))
        print('tx_ports:', device.tx_ports)
        print('num_rx_ports:', device.num_rx_ports)
        print('rx_ports:', device.rx_ports)
        print('can_flash_led:', device.can_flash_led)
        print('supports_wake:', device.supports_wake)
        print('supports_multiple_wake:', device.supports_multiple_wake)
        print('supports_programmable_wake:', device.supports_programmable_wake)
        print('has_volitile_wake:', device.has_volitile_wake)
        print('is_learn_only:', device.is_learn_only)
        print('has_narrow_bpf:', device.has_narrow_bpf)
        print('has_software_decode_input:', device.has_software_decode_input)
        print('has_hardware_decode_input:', device.has_hardware_decode_input)
        print('has_attached_tuner:', device.has_attached_tuner)
        print('emulator_version:', device.emulator_version)
        
        test_codes = []
        
        def callback(ir_code):
            test_codes.append(ir_code)
            
            print()
            print()
            print('---- RECEIVED IR CODE')
            print(ir_code.decode())
            print('frequency:', ir_code.frequency)
            print('pronto:', ir_code)
            print('decimal:', ir_code.decimal)
            print('mce:', ir_code.mce)
        
        device.bind(callback)
        device.start_receive()
        
        input('press some button on the remote. then press any key to continue')
            
        device.stop_receive()
        device.unbind(callback)
        
        print('now we are going to learn a code. you have 10 seconds.')
        ir_code = device.learn()
        
        count = 2
        
        while ir_code is None and count:
            print('failed to learn code.. {0} attempts remaining.. try again'.format(count))
            count -= 1
            ir_code = device.learn()
        
        
        if ir_code is None:
            print('learn failed')
            
        else:
            print('blasting learned code to all emitters') 
            device.transmit(ir_code)
            
            
    for device in devices:
        device.close()

    else:
        print('No Devices Found!')
        