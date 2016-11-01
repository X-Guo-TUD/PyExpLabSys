""" Implementation of SCPI standard """
from __future__ import print_function
import time
import serial
import random
import logging
import telnetlib
from PyExpLabSys.common.supported_versions import python2_and_3
python2_and_3(__file__)

LOGGER = logging.getLogger(__name__)
# Make the logger follow the logging setup from the caller
LOGGER.addHandler(logging.NullHandler())


class SCPI(object):
    """ Driver for scpi communication """
    def __init__(self, interface, device='', tcp_port=5025, hostname='', baudrate=9600,
                 allow_debug=False):
        self.device = device
        self.interface = interface
        try:
            if self.interface == 'file':
                self.f = open(self.device, 'w')
                self.f.close()
            if self.interface == 'serial':
                self.f = serial.Serial(self.device, baudrate, timeout=1, xonxoff=True)
            if self.interface == 'lan':
                self.f = telnetlib.Telnet(hostname, tcp_port)
            self.debug=False
        except Exception as e:
            if allow_debug:
                self.debug = True
                print("Debug mode: " + str(e))
            else:
                raise

    def scpi_comm(self, command, expect_return=False):
        """ Implements actual communication with SCPI instrument """
        return_string = ""
        if self.debug:
            return str(random.random())
        if self.interface == 'file':
            self.f = open(self.device, 'w')
            self.f.write(command)
            time.sleep(0.02)
            self.f.close()
            time.sleep(0.05)
            if command.find('?') > -1:
                self.f = open(self.device, 'r')
                return_string = self.f.readline()
                self.f.close()
        command_text = command + '\n'
        if self.interface == 'serial':
            self.f.write(command_text.encode('ascii'))
            if command.endswith('?') or (expect_return is True):
                return_string = self.f.readline().decode()
        if self.interface == 'lan':
            lan_time = time.time()
            self.f.write(command_text.encode('ascii'))
            if (command.find('?') > -1) or (expect_return is True):
                return_string = self.f.read_until(chr(10).encode('ascii'), 2).decode()
            LOGGER.info('Return string length: ' + str(len(return_string)))
            #time.sleep(0.025)
            LOGGER.info('lan_time for coomand ' + command_text.strip() +
                        ': ' + str(time.time() - lan_time))
        return return_string

    def read_software_version(self):
        """ Read version string from device """
        version_string = self.scpi_comm("*IDN?")
        version_string = version_string.strip()
        return version_string

    def reset_device(self):
        """ Rest device """
        self.scpi_comm("*RST")
        return True

    def device_clear(self):
        """ Stop current operation """
        self.scpi_comm("*abort")
        return True

    def clear_error_queue(self):
        """ Clear error queue """
        error = self.scpi_comm("*ESR?")
        self.scpi_comm("*cls")
        return error
