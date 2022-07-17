# CSA-GUI-
For RF &amp; General CSA Catapult engineering testbed work. Connecting instruments using pyvisa with Keysight VISA instrument communication protocol.
An instrument GUI designed for automatic RF amplifier testing, by safe turn on of device at 5v then stepping down voltage to find quiescent current then stepping
through RF power/freq. 
Power Added Efficiency of amplifier is calculated using dc & rf measurements. All readings and inputs are exported to into a csv. A general instrument check and 
assignment functions means furthur device test procedures could be developed using this framework on differant tabs. 
Currently only tested for SMW200A Signal Generator, but can be easily used for alternative generators by changing the serial visa commands to compatible 
ones. These can be found in the respective instrument manual.
