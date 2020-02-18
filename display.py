# Included with thanks to the original source:
# http://www.extremeelectronics.co.uk/blog/i2c-control-of-lcd-display-using-ywrobot-lcm1602-v2-raspberry-pi/


import socketserver
import textwrap

import smbus
from time import sleep


# General i2c device class so that other devices can be added easily
class i2c_device:
    def __init__(self, addr, port):
        self.addr = addr
        self.bus = smbus.SMBus(port)

    def write(self, byte):
        self.bus.write_byte(self.addr, byte)

    def read(self):
        return self.bus.read_byte(self.addr)

    def read_nbytes_data(self, data, n): # For sequential reads > 1 byte
        return self.bus.read_i2c_block_data(self.addr, data, n)


# Encapsulates LCD component
class LCD:
    def __init__(self, addr, port):
        self.lcd_device = i2c_device(addr, port)
        self.backlight = 1

        # Work around initialization glitch by performing init twice
        for _ in range(2):
            self.lcd_device_writebl(0x20)
            self.lcd_strobe()
            sleep(0.05)
            self.lcd_strobe()
            sleep(0.05)
            self.lcd_strobe()
            sleep(0.05)
            self.lcd_write(0x28)
            self.lcd_write(0x08)
            self.lcd_write(0x01)
            self.lcd_write(0x06)
            self.lcd_write(0x0C)
            self.lcd_write(0x0F)

    def lcd_device_writebl(self, value):
        if self.backlight:
            self.lcd_device.write(value | 0x08)
        else:
            self.lcd_device.write(value)

    def lcd_backlight(self, on):
        self.backlight = on
        self.lcd_strobe()

    def lcd_strobe(self):
        self.lcd_device_writebl((self.lcd_device.read() | 0x04))
        self.lcd_device_writebl((self.lcd_device.read() & 0xFB))

    def lcd_write(self, cmd):
        self.lcd_device_writebl((cmd >> 4)<<4)
        self.lcd_strobe()
        self.lcd_device_writebl((cmd & 0x0F)<<4)
        self.lcd_strobe()
        self.lcd_device_writebl(0x0)

    def lcd_write_char(self, charvalue):
        self.lcd_device_writebl((0x01 | (charvalue >> 4)<<4))
        self.lcd_strobe()
        self.lcd_device_writebl((0x01 | (charvalue & 0x0F)<<4))
        self.lcd_strobe()
        self.lcd_device_writebl(0x0)

    def lcd_putc(self, char):
        self.lcd_write_char(ord(char))

    def lcd_puts(self, string, line):
        if line == 1:
            self.lcd_write(0x80)
        if line == 2:
            self.lcd_write(0xC0)

        for char in string:
            self.lcd_putc(char)

    def lcd_clear(self):
        self.lcd_write(0x1)
        self.lcd_write(0x2)

    def lcd_load_custon_chars(self, fontdata):
        self.lcd_device.bus.write(0x40)
        for char in fontdata:
            for line in char:
                self.lcd_write_char(line)


class DisplayHandler(socketserver.StreamRequestHandler):
    def handle(self):
        display = self.server.display
        data = self.rfile.readline().strip()

        display.lcd_clear()

        if data:
            lines = data.decode('ascii').split('|')
            while len(lines) > 2:
                display.lcd_puts(lines.pop(0)[:16], 1)
                display.lcd_puts(lines[0][:16], 2)
                sleep(2)
            if lines:
                display.lcd_puts(lines.pop(0)[:16], 1)
            if lines:
                display.lcd_puts(lines.pop(0)[:16], 2)


class DisplayServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super(DisplayServer, self).__init__(server_address, RequestHandlerClass, bind_and_activate)

        self.display = LCD(0x27, 1)
        self.display.lcd_clear()


if __name__ == '__main__':
    with DisplayServer(('0.0.0.0', 7070), DisplayHandler) as s:
        s.serve_forever()
