# -*- coding: utf-8 -*-
""" This module contains drivers for equipment from Omega. Specifically it
contains a driver for the ??? thermol couple read out unit.
"""


import time
import logging
import serial


LOGGER = logging.getLogger(__name__)
# Make the logger follow the logging setup from the caller
#LOGGER.addHandler(logging.NullHandler())
LOGGER.addHandler(logging.StreamHandler())


class ISeries(object):
    """Driver for the iSeries omega temperature controllers"""

    pre_string = chr(42)
    end_string = chr(13)

    def __init__(self, port, baudrate=19200, comm_stnd='rs232'):
        """Initialize internal parameters

        :param port: A serial port designation as understood by `pySerial
            <http://pyserial.sourceforge.net/pyserial_api.html#native-ports>`_
        """
        LOGGER.debug('Initialize driver')
        self.serial = serial.Serial(port, baudrate, bytesize=serial.SEVENBITS,
                                    parity=serial.PARITY_ODD,
                                    stopbits=serial.STOPBITS_ONE,
                                    timeout=2)
        self.comm_stnd = comm_stnd
        time.sleep(0.1)
        LOGGER.info('Driver initialized')

    def command(self, command, response_length=None, address=None):
        """Run a command and return the result

        :param command: The command to execute
        :type command: str
        :param response_length: The expected legth of the response. Will force
            the driver to wait untill this many characters is ready as a
            response from the device.
        :type response_length: int
        """

        LOGGER.debug('command called with {}, {}'.format(command,
                                                         response_length))
        if self.comm_stnd == 'rs485':
            command = '0' + str(address) + command
        comm_string = (self.pre_string + command + self.end_string)
        self.serial.write(comm_string)

        if response_length is not None:
            while self.serial.inWaiting() < response_length + 1:
                # If faster replies are needed this can be lowered to e.g. 0.05
                time.sleep(0.17)
        else:
            # If a response length is not given, assume that the command can be
            # executed in 0.5 seconds
            time.sleep(0.5)
        response = self.serial.read(self.serial.inWaiting())
        # Strip \r from responseRemove the echo response from the device
        LOGGER.debug('comand return {}'.format(response[:-1]))
        if response[0:len(command)] == command:
            response = response[len(command):]
        return response[:-1]

    def reset_device(self, address=None):
        """Reset the device"""
        command = 'Z02'
        return self.command(command, address=address)

    def identify_device(self, address=None):
        """Return the identity of the device"""
        command = 'R26'
        return self.command(command, address=address)

    def read_temperature(self, address=None):
        """Return the temperature"""
        LOGGER.debug('read_temperature called')
        command = 'X01'
        error = 1
        while (error > 0) and (error < 10):
            try:
                response = float(self.command(command,
                                              address=address))
                error = 0
            except ValueError:
                error = error + 1
                print 'AAA'
                response = None
                LOGGER.debug('read_temperature return {}'.format(response))
        return response

    def close(self):
        """Close the connection to the device"""
        LOGGER.debug('Driver asked to close')
        self.serial.close()
        LOGGER.info('Driver closed')


class CNi3244_C24(ISeries):
    """Driver for the CNi3244_C24 device"""

    def __init__(self, port):
        """Initialize internal parameters

        :param port: A serial port designation as understood by `pySerial
            <http://pyserial.sourceforge.net/pyserial_api.html#native-ports>`_
        """        
        super(CNi3244_C24, self).__init__(port)

if __name__ == '__main__':
    # This port name should be chages to a local port to do a local test
    port = 'usb-FTDI_USB-RS485_Cable_FTWGGPAS-if00-port0'
    omega = ISeries('/dev/serial/by-id/' + port, 9600, comm_stnd='rs485')
    print omega.identify_device(1)
    print omega.identify_device(2)

    print omega.read_temperature(1)
    print omega.read_temperature(2)

