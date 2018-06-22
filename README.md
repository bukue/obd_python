# obd_python
A simple Python wrapper for OBD serial communications.

To use it you would need a OBD II connector with the ELM327 chipset. I have tested it on a USB one, but after pairing it, it should work fine with bluetooh and wifi.

In order to use it just follow the next instructions

Instantiate the adapter:

`adapter = elm327.Elm327()`

Connect to the ECU:

```
# change parameters accordingly
adapter.initialize(port=self.adapter_port, bps=38400, debug=True, data_rate = 1 ) 
adapter.connect()
```

Query away!

```
# will query Monitors status since DTCs cleared.
adapter.query("0101") 
``` 

You can even write to the ECUS:

`adapter.write("please don't break your ECUs")`

For the PIDS codes please reference: https://en.wikipedia.org/wiki/OBD-II_PIDs

If you want to keep things clear, disconnect:

`adapter.disconnect()`

I am not liable if you write weird things to your ECU or suddenly your car starts acting weird. Please be mindful and responsible with what you do.
