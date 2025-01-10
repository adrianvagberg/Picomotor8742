"""
Example usage of picomotor.py
"""
from picomotor import Controller
import time

# Don't change these
idProduct = '0x4000'
idVendor = '0x104d'

# convert hex value in string to hex value
idProduct = int(idProduct, 16)
idVendor = int(idVendor, 16)

# Initialize controller and start console
controller = Controller(idProduct=idProduct, idVendor=idVendor)

print('Scanning...')
controller.scan(conflict_resolution=2)

# Find master and slave addresses
addr_map = controller.get_controller_address_map()
print(f'Address map: {addr_map}\n')
addr_master = 1
addr_slave = addr_map.index(1,2)

print(f'Master: {addr_master}\nSlave: {addr_slave}\n')

# Detect the motor types connected to each axis
controller.detect_motors(addr_master)
for m in range(1,5):
    motor = controller.get_motor_type(addr_master,m)
    print(f'Master axis {m}: {motor}')
print('\n')

controller.detect_motors(addr_slave)
for m in range(1,5):
    motor = controller.get_motor_type(addr_slave,m)
    print(f'Slave axis {m}: {motor}')


# Try moving all axes with motors
print('Moving X...')
controller.move_to_target(addr_master,1,500)
print(f'X position: {controller.get_position(addr_master,1)}\n')

print('Moving Y...')
controller.move_to_target(addr_master,2,500)
print(f'Y position: {controller.get_position(addr_master,2)}\n')

print('Moving Z...')
controller.move_to_target(addr_master,3,500)
print(f'Z position: {controller.get_position(addr_master,3)}\n')

print('Moving pitch...')
controller.move_to_target(addr_slave,1,500)
print(f'Pitch position: {controller.get_position(addr_master,1)}\n')

print('Moving yaw...')
controller.move_to_target(addr_slave,2,500)
print(f'Yaw position: {controller.get_position(addr_master,2)}\n')

time.sleep(5)
print('Homing...')
controller.move_to_target(addr_master,1,0)
controller.move_to_target(addr_master,2,0)
controller.move_to_target(addr_master,3,0)
controller.move_to_target(addr_slave,1,0)
controller.move_to_target(addr_slave,2,0)