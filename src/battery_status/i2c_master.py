#  Raspberry Pi Master for battery status manager Slave
#  i2c_master.py
#  Connects to battery status manager via I2C
#  useful for battery fuel gauge LC709203F

#  ProtolabQuebec 2021
#  By: Alberto Perez

from smbus2 import SMBus


class BMSCom:

    def __init__(self):
        self._bus = SMBus(1)  # indicates /dev/ic2-1
        self.address = 0x0B  # bus address of the battery status manager
        self.polynomial = '100000111'  # PEC checksum polynomial binary 0x107 (CRC-8)
        self._bus.pec = 1  # Enable PEC verification
        # commands read
        self.reg_cell_voltage = 0x09  # command code to read the voltage of a cell (1mV)
        self.reg_rsoc100 = 0x0D  # command code to read the RSOC value based on a 0−100 scale (1%)
        self.reg_rsoc1000 = 0x0F  # command code to read the RSOC value based on a 0−1000 scale (0.1%)
        # commands write
        self.reg_low_rsoc = 0x13  # command code to sets or read the RSOC threshold to generate Alarm signal (1%)
        self.reg_low_voltage = 0x14  # command code to sets or read the voltage threshold to generate Alarm signal (1mV)

    # gets voltage for a cell in mV
    # return int
    def get_voltage(self):
        return self._bus.read_word_data(i2c_addr=self.address, register=self.reg_cell_voltage)

    # gets battery charge in % with a 1% precision
    # return int
    def get_charge100(self):
        charge = self._bus.read_word_data(i2c_addr=self.address, register=self.reg_rsoc100)
        if charge > 80:
            charge = 80
        charge = 1.25*charge  # charge will be at its maximum at 80%
        return charge

    # gets battery charge in % with a 0.1% precision
    # return int
    def get_charge1000(self):
        charge = self._bus.read_word_data(i2c_addr=self.address, register=self.reg_rsoc1000) / 10
        if charge > 80:
            charge = 80
        charge = 1.25*charge  # charge will be at its maximum at 80%
        return charge

    # separate a number in two Bytes (data Byte low and data_byte_high)
    # input int <= 0xFFFF = 65535
    # return a list [data_byte_low, data_byte_high]
    @staticmethod
    def _separate_bytes(number):
        list_bytes = [255, 255]
        if number <= 0xFFFF & number >= 0:
            data_byte_high1 = number // (16 ** 3)  # most significant 4 bits of the most significant Byte
            data_byte_high2 = (number - data_byte_high1 * 16 ** 3) // (16 ** 2)  # less significant 4 bits of the most
            # significant Byte
            data_byte_high = data_byte_high1 * 16 + data_byte_high2  # most significant Byte
            data_byte_low1 = (number - data_byte_high1 * 16 ** 3 - data_byte_high2 * 16 ** 2) // (16 ** 1)  # most
            # significant 4 bits of the less significant Byte
            data_byte_low2 = (
                        number - data_byte_high1 * 16 ** 3 - data_byte_high2 * 16 ** 2 - data_byte_low1 * 16)  # less
            # significant 4 bits of the less significant Byte
            data_byte_low = data_byte_low1 * 16 + data_byte_low2  # less significant Byte
            list_bytes = [data_byte_low, data_byte_high]
        elif number < 0:
            list_bytes = [0, 0]
        return list_bytes

    # xor operation with str
    @staticmethod
    def _xor(first, second):

        # initialize result
        result = []

        # Traverse all bits, if bits are
        # same, then XOR is 0, else 1
        for i in range(1, len(second)):
            if first[i] == second[i]:
                result.append('0')
            else:
                result.append('1')

        return ''.join(result)

    # Performs Modulo-2 division
    def _mod2div(self, divident, divisor):

        # Number of bits to be XORed at a time.
        pick = len(divisor)

        # Slicing the divident to appropriate
        # length for particular step
        tmp = divident[0: pick]

        while pick < len(divident):

            if tmp[0] == '1':

                # replace the divident by the result
                # of XOR and pull 1 bit down
                tmp = self._xor(divisor, tmp) + divident[pick]

            else:  # If leftmost bit is '0'

                # If the leftmost bit of the dividend (or the
                # part used in each step) is 0, the step cannot
                # use the regular divisor; we need to use an
                # all-0s divisor.
                tmp = self._xor('0' * pick, tmp) + divident[pick]

                # increment pick to move further
            pick += 1

        # For the last n bits, we have to carry it out
        # normally as increased value of pick will cause
        # Index Out of Bounds.
        if tmp[0] == '1':
            tmp = self._xor(divisor, tmp)
        else:
            tmp = self._xor('0' * pick, tmp)

        checkword = tmp
        return checkword

        # Function used at the sender side to encode

    # calcul checksum CRC-8 for self.polynomial
    # inputs int
    # output int
    def _calculation_checksum(self, register, data_byte_low, data_byte_high):
        write_adress = self.address * 2  # address for writing
        data_send = bin(write_adress * 2 ** 24 + register * 2 ** 16 + data_byte_low * 2 ** 8 + data_byte_high)  #
        # transform data in srt binary
        data_send = data_send[2:len(data_send)]  # get rid of the beginning ('0b')
        l_polynomial = len(self.polynomial)

        # Appends n-1 zeroes at end of data
        appended_data = data_send + '0' * (l_polynomial - 1)
        str_checksum = self._mod2div(appended_data, self.polynomial)
        n = len(str_checksum)
        checksum = 0
        for i in range(0, len(str_checksum)):
            n = n - 1
            if str_checksum[i] == '1':
                bit = 1
            else:
                bit = 0
            checksum = checksum + bit * 2 ** n
        return checksum

    # set low voltage for the alarm in mV
    # input int <= 0xFFFF = 65535
    def set_low_voltage_alarm(self, min_voltage):
        [data_byte_low, data_byte_high] = self._separate_bytes(min_voltage)
        checksum = self._calculation_checksum(self.reg_low_voltage, data_byte_low, data_byte_high)
        self._bus.write_i2c_block_data(i2c_addr=self.address, register=self.reg_low_voltage,
                                       data=[data_byte_low, data_byte_high, checksum])

    # set low rsoc for the alarm in %
    # input int <= 0x0064 = 100
    def set_low_rsoc_alarm(self, min_rsoc):
        if min_rsoc > 100:
            min_rsoc = 100
        [data_byte_low, data_byte_high] = self._separate_bytes(min_rsoc)
        checksum = self._calculation_checksum(self.reg_low_rsoc, data_byte_low, data_byte_high)
        self._bus.write_i2c_block_data(i2c_addr=self.address, register=self.reg_low_rsoc,
                                       data=[data_byte_low, data_byte_high, checksum])
