# CSA-GUI-
For RF &amp; General CSA Catapult engineering testbed work. Connection instruments using pyvisa & pysimple with Keysight VISA instrument communication protocol.
An instrument GUI designed for automatic RF amplifier testing, by safe turn on of device at 5v then finding quiescent voltage then stepping through RF supply input 
frequency and power then of pae and export to csv. General instrument check and assignment functions means furthur device test procedures can be easily developed on 
differant tabs. Currently only tested for SMW200A Signal Generator, but can be easily used for alternative generators by changing the serial visa commands to compatible 
ones. These can be found in the respective instrument manual.
