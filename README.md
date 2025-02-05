# Control a Newport Picomotor 8742 Controller over USB

Python program to control one (or more, connected in an RS-485 daisy-chain) Newport Picomotor 8742 Controllers.

Based on the [python_newport_controller](https://github.com/bdhammel/python_newport_controller) repo by **bdhammel**.

## Requirements
#### Install Newport USB Drivers
- Verify that the USB drivers are installed correctly by running the ```setup.exe``` file in the flash drive that came with the Picomotor Controller.

#### Install [pyUSB](https://github.com/pyusb/pyusb/blob/master/docs/tutorial.rst)
```bash
$ pip install pyusb
```

#### Install USB backend [libusb](https://libusb.info/)
It is not enough to install libusb as a Python package. Instead you must:

- On Windows:
  - Download and unzip ```libusb-1.0.27.7z``` (or more recent version) from the [libusb Github](https://github.com/libusb/libusb/releases).
  - Go to ```libusb-1.0.27 -> MinGW64 -> dll``` and copy the ```libusb-1.0.dll``` file into your System32 folder.


- On MacOS:
  - Consider following the steps [here](https://github.com/bdhammel/python_newport_controller?tab=readme-ov-file#install-homebrew-and-python) to install ```libusb-compat``` through homebrew. **Note** that this has not been tested on this code.

## Docs
In the ```docs``` folder you will find:
- The Picomotor 8742 Controller User Manual, with extensive documentation on the commands being sent to the controller.
- API documentation for the methods in ```picomotor.py```. **Note:** This is viewable from your IDE after cloning the repo, but will only show up as html code in Github.