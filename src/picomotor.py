import usb.core
import usb.util
from commands import COMMANDS

MOTOR_TYPE = {
        "0":"No motor connected",
        "1":"Motor Unknown",
        "2":"'Tiny' Motor",
        "3":"'Standard' Motor"
        }


class Controller(object):
    """Picomotor Controller"""

    def __init__(self, idProduct, idVendor):
        """
        Initialize the Picomotor class with the specs of the attached device

        Call self._connect to set up communication with usb device and endpoints

        Args:
            idProduct (hex): Product ID of Picomotor controller
            idVendor (hex): Vendor ID of Picomotor controller
        """
        self.idProduct = idProduct
        self.idVendor = idVendor
        self._connect()

    def _connect(self):
        """
        Connect class to USB device

        Find device from Vendor ID and Product ID
        Setup taken from [1]

        Raises:
            ValueError: if the device cannot be found by the Vendor ID and Product ID
            Assert False: if the input and outgoing endpoints can't be established
        """

        # find the device
        self.dev = usb.core.find(
                        idProduct=self.idProduct,
                        idVendor=self.idVendor
                        )

        if self.dev is None:
            raise ValueError('Device not found')

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        self.dev.set_configuration()

        # get an endpoint instance
        cfg = self.dev.get_active_configuration()
        intf = cfg[(0,0)]

        self.ep_out = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)

        self.ep_in = usb.util.find_descriptor(
            intf,
            # match the first IN endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN)

        assert (self.ep_out and self.ep_in) is not None

        # Confirm connection to user
        resp = self.get_firmware_version()
        print("Connected to Motor Controller Model {}. Firmware {} {} {}\n".format(
                                                    *resp.split(' ')
                                                    ))

    def send_command(self, usb_command, get_reply=False):
        """
        Send command to USB device endpoint

        Args:
            usb_command (str):  Correctly formated command for USB driver
            get_reply (bool):   query the IN endpoint after sending command, to
                                get controller's reply

        Returns:
            Character representation of returned hex values if a reply is requested
        """
        self.ep_out.write(usb_command)
        if get_reply:
            return self.ep_in.read(100)


    def parse_reply(self, reply):
        """
        Take controller's reply and make human readable

        Args:
            reply (list): list of bytes returns from controller in hex format

        Returns:
            reply (str): Cleaned string of controller reply
        """

        # convert hex to characters
        reply = ''.join([chr(x) for x in reply])

        # return string without the "1>" or "2>" in front - the user already knows the address given the command sent
        return reply.rstrip()[2:]


    def verify_command(self, cmd):
        if not cmd in COMMANDS.values():
            raise ValueError('Invalid command')


    def verify_address_value(self, addr):
        if not (addr == 1 or addr == 2):
            raise ValueError('Invalid address value')


    def verify_axis_value(self, axis):
        if not (type(axis) == int and 1 <= axis <= 4):
            raise ValueError('Invalid axis value')


    def format_command(self, ascii_cmd, addr = 1, axis = None, val = None):
        self.verify_command(ascii_cmd)
        self.verify_address_value(addr)

        if axis:
            self.verify_axis_value(axis)
            cmd = f'{addr}>{axis}{ascii_cmd}'
        else:
            cmd = f'{addr}>{ascii_cmd}'

        if val is not None:
            cmd += f'{val}\r'
        else:
            cmd += '\r'

        return cmd


    def get_id(self, addr):
        """Get instrument ID of the form 'New_Focus XXXX vYYY mm/dd/yy, SNZZZZ'"""

        cmd = self.format_command(COMMANDS['id_string'], addr)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return reply


    def get_firmware_version(self):
        """Get firmware version of the form 'XXXX Version Y.Y mm/dd/yy'"""

        cmd = self.format_command(COMMANDS['query_firmware'])
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return reply


    def set_velocity(self, addr, axis, val):
        """
        Set velocity for a specified axis. A command will not
        impact a move that is already in motion.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
            val (int):  Velocity (steps/sec). 1 to 2000.
        """

        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        if not(type(val) == int and 1 <= val <= 2000):
            raise ValueError('Velocity must be between 1 and 2000')

        cmd = self.format_command(COMMANDS['set_velocity'], addr, axis, val)
        self.send_command(cmd)


    def get_velocity(self, addr, axis):
        """
        Get velocity for a specified axis.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
        Returns:
            reply (int): Velocity (steps/sec)
        """

        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        cmd = self.format_command(COMMANDS['query_velocity'], addr, axis)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return int(reply)


    def set_acceleration(self, addr, axis, val):
        """
        Set acceleration for a specified axis. A command will not
        impact a move that is already in motion.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
            val (int):  Acceleration (steps/sec^2). 1 to 200000.
        """

        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        if not (type(val) == int and 0 < val <= 200000):
            raise ValueError('Invalid acceleration value')

        cmd = self.format_command(COMMANDS['set_accel'], addr, axis, val)
        self.send_command(cmd)


    def get_acceleration(self, addr, axis):
        """
        Get acceleration for a specified axis.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
        Returns:
            reply (int): Acceleration (steps/sec^2)
        """

        cmd = self.format_command(COMMANDS['query_accel'], addr, axis)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return int(reply)


    def get_position(self, addr, axis):
        """
        Get the number of steps made by the controller relative to its
        position when it was powered ON, a system reset occurred, or
        set_home() was called

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
        Returns:
            reply (int): Number of steps
        """

        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        cmd = self.format_command(COMMANDS['query_pos'], addr, axis)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return int(reply)


    def set_home(self, addr, axis, val = None):
        """
        Define the 'home' position for an axis.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
            val (int):  Number of steps that the current position is away from 'home'
                        If 'val' is not passed, then home is set to 0.
        """
        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        if not type(val) == int:
            raise ValueError('Invalid acceleration value')

        cmd = self.format_command(COMMANDS['define_home'], addr, axis, val)
        self.send_command(cmd)


    def get_home(self, addr, axis):
        cmd = self.format_command(COMMANDS['query_home'], addr, axis)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return reply


    def finished_moving(self, addr, axis):
        """
        Query the motion status of an axis.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
        Returns:
            reply (bool): True if done moving, False otherwise
        """

        cmd = self.format_command(COMMANDS['query_motion_done'], addr, axis)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return reply[-1] == '1'


    def move_indefinitely(self, addr, axis, direction):
        """
        Move the specified axis in the given direction, indefinitely.
        Issue a stop_motion() command to stop the motor.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
            direction (str): '+' or '-'
        """

        if not (direction == '+' or direction == '-'):
            raise ValueError('Direction must be + or -')

        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        cmd = self.format_command(COMMANDS['move_indefinitely'], addr, axis, direction)
        self.send_command(cmd)


    def move_to_target(self, addr, axis, target):
        """
        Move an axis to a desired target (absolute) position w.r.t. the defined 'home'.
        Method finishes (i.e. allows a new method call) once motion is done.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
            target (int): Target position in steps from 'home' position. Can be negative or positive.
        """

        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        if not type(target) == int:
            raise ValueError('Invalid target position')

        cmd = self.format_command(COMMANDS['move_to_target_pos'], addr, axis, target)
        self.send_command(cmd)

        while not self.finished_moving(addr, axis):
            pass


    def get_target(self, addr, axis):
        cmd = self.format_command(COMMANDS['query_target_pos'], addr, axis)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return int(reply)


    def move_relative(self, addr, axis, steps):
        """
        Move an axis by a specified number of steps from current position.
        Method finishes (i.e. allows a new method call) once motion is done.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
            steps (int): Number of steps to move. Can be negative or positive.
        """

        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        if not type(steps) == int:
            raise ValueError('Invalid target position')

        cmd = self.format_command(COMMANDS['move_relative'], addr, axis, steps)
        self.send_command(cmd)

        while not self.finished_moving(addr, axis):
            pass


    def get_relative_target(self, addr, axis):
        cmd = self.format_command(COMMANDS['query_target_rel'], addr, axis)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return reply


    def detect_motors(self, addr):
        """
        Automatically detect what motor is connected to which axis.

        Args:
            addr (int): 1 or 2
        """

        self.verify_address_value(addr)

        cmd = self.format_command(COMMANDS['motor_check'], addr)
        self.send_command(cmd)


    def set_motor_type(self, addr, axis, val):
        """
        Manually set the motor type for a specified axis.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
            val (int):  0 for "No motor connected"
                        1 for "Motor type unknown"
                        2 for "'Tiny' motor"
                        3 for "'Standard' motor"
        """

        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        if not (type(val) == int and 0 <= val <= 3):
            raise ValueError('Invalid motor type')

        cmd = self.format_command(COMMANDS['set_motor_type'], addr, axis, val)
        self.send_command(cmd)


    def get_motor_type(self, addr, axis):
        """
        Get the motor type for a specified axis. This method reports the present motor type
        setting in memory - it does NOT perform a check to determine whether the setting is
        still valid.

        If motors have been removed or reconnected to a different axis, it is recommended to
        first run the detect_motors() method.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
        Returns:
            reply (str): A description of the motor type (if any)
        """

        cmd = self.format_command(COMMANDS['query_motor_type'], addr, axis)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return MOTOR_TYPE[f'{reply[-1]}']


    def set_address(self, addr, val = 1):
        """
        Manually set the address of a controller.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
            val (int):  New address. Default = 1. Valid values between 1 and 31.
        """

        self.verify_address_value(addr)
        if not (type(val) == int and 1 <= val <= 31):
            raise ValueError('New address must be between 1 and 31')

        cmd = self.format_command(COMMANDS['set_address'], addr, val)
        self.send_command(cmd)


    def get_address(self, addr):
        """
        Get the address of a controller.

        Args:
            addr (int): 1 or 2
        Returns:
            reply (int): Controller address
        """

        self.verify_address_value(addr)

        cmd = self.format_command(COMMANDS['query_address'], addr)
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return int(reply)


    def scan(self, conflict_resolution = 0):
        """
        Initiate a scan of controllers on RS-485 network.
        Method finishes (i.e. allows a new method call) once scan is done.

        Args:
            conflict_resolution (int):  0 - Does not resolve address conflicts
                                        1 - Address conflicts are resolved by reassigning
                                            conflicting addresses to the lowest available value
                                        2 - Address conflicts are resolved by reassigning ALL
                                            addresses in ascending order, starting with the
                                            master controller at address 1
        """

        if not (type(conflict_resolution) == int and 0 <= conflict_resolution <= 2):
            raise ValueError('Conflict resolution scheme must be 0, 1, or 2.')

        cmd = self.format_command(COMMANDS['scan_RS485'], val = conflict_resolution)
        self.send_command(cmd)

        while not self.is_scan_done():
            pass


    def is_scan_done(self):
        cmd = self.format_command(COMMANDS['query_scan_status'])
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return reply[-1] == '1'


    def get_controller_address_map(self):
        """
        Get a list of all addresses occupied in the RS-485 network.

        Returns:
            reply (list):   Binary list where each index corresponds to an address.
                            Index 0 is reserved for showing if there are conflicts.
        """

        cmd = self.format_command(COMMANDS['query_RS485_addr'])
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        address_map = [int(s) for s in format(int(reply), 'b')]
        return address_map[::-1]


    def save_settings(self):
        """
        Save the controller settings to its non-volatile memory. These settings are reloaded to working
        registers automatically after system reboot. Parameters for all motors are saved.

        The following settings are saved:
            1. Motor type
            2. Desired velocity
            3. Desired acceleration
        """

        cmd = self.format_command(COMMANDS['save'])
        self.send_command(cmd)


    def stop_motion(self, addr, axis):
        """
        Stop the motion of an axis. Motion slows down according to the desired acceleration.

        Args:
            addr (int): 1 or 2
            axis (int): 1 to 4
        """

        self.verify_address_value(addr)
        self.verify_axis_value(axis)

        cmd = self.format_command(COMMANDS['stop'], addr, axis)
        self.send_command(cmd)


    def get_latest_error_msg(self):
        """
        Pop the latest error (with code and message) from the error stack.
        (see docs\"8742 Controller User Manual.pdf" Appendix for complete listing of error codes).

        Returns:
            reply (str): Error message of the form "[Error code], [Error message]"
        """

        cmd = self.format_command(COMMANDS['query_error_msg'])
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return reply


    def get_latest_error_code(self):
        """
        Pop the latest error code (without its message) from the error stack.
        (see docs\"8742 Controller User Manual.pdf" Appendix for complete listing of error codes).

        Returns:
            reply (str): Error code
        """

        cmd = self.format_command(COMMANDS['query_error_nr'])
        reply = self.parse_reply(
            self.send_command(cmd, True)
        )
        return reply


    def purge_all_settings(self):
        """
        Purge all settings in the controller non-volatile memory.
        These settings include:
            1. Motor type
            2. Desired velocity
            3. Desired acceleration
        """

        cmd = self.format_command(COMMANDS['purge_memory'])
        self.send_command(cmd)

