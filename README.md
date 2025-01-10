# Control a Newport Picomotor 8742 Controller over USB

Python program to control one (or more, connected in an RS-485 daisy-chain) Newport Picomotor 8742 Controllers.

## Requirements

#### Install [pyUSB](https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst)
```bash
$ pip install pyusb
```

#### Install USB backend [libusb](https://libusb.info/)
It is not enough to install libusb as a Python package. Instead you must:
1. Download and unzip ```libusb-1.0.27.7z``` (or more recent version) from the [libusb Github](https://github.com/libusb/libusb/releases).
2. Go to ```libusb-1.0.27 -> MinGW64 -> dll``` and copy the ```libusb-1.0.dll``` file into your System32 folder.

## Docs
In the ```docs``` folder you will find:
- The Picomotor 8742 Controller User Manual, with extensive documentation on the commands being sent to the controller.
- [```api.html```](docs/api.html) - API documentation for the methods in ```picomotor.py```