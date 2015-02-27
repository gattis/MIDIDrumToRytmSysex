# MIDIDrumToRytmSysex

Converts MIDI drum file(s) to Sysex file(s) containing Pattern(s) for the Elektron Analog Rytm.  Uses libanalogrytm which did the hard work of reverse-engineering the Sysex spec for this device.

Usage:
  > python midi_to_raw.py example.mid
  > ./raw_to_syx example.mid.raw
  [produces example.mid.raw.syx which you can upload to the Analog Rytm using C6]  
