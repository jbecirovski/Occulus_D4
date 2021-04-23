# script secondaire pour le contrôle de la caméra (reste des fonctions)

import socket
import subprocess

from ftplib import FTP
from smbus2 import SMBus


class BMSCom:

    def __int__(self):
        # self._bus = SMBus(1)  # indicates /dev/ic2-1
        self.bus = SMBus(1)
        self.address = 0x0B  # bus address of the battery status manager
        self.polynomial = '100000111'  # PEC checksum polynomial binary 0x107 (CRC-8)
        # pec = 1  # Enable PEC verification
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
        return self.bus.read_word_data(i2c_addr=self.address, register=self.reg_cell_voltage)

    # gets battery charge in % with a 1% precision
    # return int
    def get_charge100(self):
        return self.bus.read_word_data(i2c_addr=self.address, register=self.reg_rsoc100)

    # gets battery charge in % with a 0.1% precision
    # return int
    def get_charge1000(self):
        return self.bus.read_word_data(i2c_addr=self.address, register=self.reg_rsoc1000) / 10

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
        for j in range(1, len(second)):
            if first[j] == second[j]:
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
        for j in range(0, len(str_checksum)):
            n = n - 1
            if str_checksum[j] == '1':
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
        self.bus.write_i2c_block_data(i2c_addr=self.address, register=self.reg_low_voltage,
                                      data=[data_byte_low, data_byte_high, checksum])

    # set low rsoc for the alarm in %
    # input int <= 0x0064 = 100
    def set_low_rsoc_alarm(self, min_rsoc):
        if min_rsoc > 100:
            min_rsoc = 100
        [data_byte_low, data_byte_high] = self._separate_bytes(min_rsoc)
        checksum = self._calculation_checksum(self.reg_low_rsoc, data_byte_low, data_byte_high)
        self.bus.write_i2c_block_data(i2c_addr=self.address, register=self.reg_low_rsoc,
                                      data=[data_byte_low, data_byte_high, checksum])


# on définit les paramètres pour la communication socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
LOCAL_IP = s.getsockname()[0]
s.close()
LOCAL_PORT = 61000

# déclaration des infos du socket de la station de base
STATION_IP = ""
STATION_PORT = 0

# déclaration des variables pour tenir compte des déplacements de la caméra
horizontal = 45
vertical = 45

# déclaration de l'objet pour aller lire la charge de la batterie
battery_manager = BMSCom()
battery_manager.__int__()

# création du sockets pour la communication
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# binder le socket
tcp_sock.bind((LOCAL_IP, LOCAL_PORT))

# écoute pour les connexions entrantes
tcp_sock.listen(100)

while True:
    # s'il y a connexion TCP, on l'accepte et on la traite
    connection, address = tcp_sock.accept()
    STATION_IP = address[0]
    STATION_PORT = address[1]
    with connection:
        while True:
            data = connection.recv(1024).decode('utf-8')
            if not data:
                break
            data = data.split("_")
            command = data[0] + "_" + data[1]

            if data[0] == "get":
                battery = str(battery_manager.get_charge1000()) + "%"
                rep = LOCAL_IP + "," + battery

                # on envoie la réponse à la station de base
                connection.send(rep.encode('utf-8'))

            # référence de 45 degrés
            elif data[0] == "move":
                if command == "move_up":
                    vertical = vertical + 5
                    if vertical <= 90:
                        cmd = "python3 servomotor_master.py 33 {}".format(str(vertical))
                        subprocess.Popen(cmd, shell=True)
                    else:
                        vertical = vertical - 5

                elif command == "move_right":
                    horizontal = horizontal + 5
                    if horizontal <= 90:
                        cmd = "python3 servomotor_master.py 32 {}".format(str(horizontal))
                        subprocess.Popen(cmd, shell=True)
                    else:
                        horizontal = horizontal - 5

                elif command == "move_left":
                    horizontal = horizontal - 5
                    if horizontal >= 0:
                        cmd = "python3 servomotor_master.py 32 {}".format(str(horizontal))
                        subprocess.Popen(cmd, shell=True)
                    else:
                        horizontal = horizontal + 5

                elif command == "move_down":
                    vertical = vertical - 5
                    if vertical >= 0:
                        cmd = "python3 servomotor_master.py 33 {}".format(str(vertical))
                        subprocess.Popen(cmd, shell=True)
                    else:
                        vertical = vertical + 5

                else:
                    break

            elif data[0] == "delete":
                if command == "delete_file":
                    # on va chercher les différents fichiers à supprimer
                    fichiers = data[2]
                    fichiers = fichiers.split(',')
                    for i in range(len(fichiers) - 1):
                        cmd = "rm /home/pi/recordings/" + str(fichiers[i])
                        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                        output = process.stdout.read()

                elif command == "delete_all":
                    cmd = "rm /home/pi/recordings/*"
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    output = process.stdout.read()

                else:
                    break

            elif data[0] == "download":
                # on vient établir la connection
                ftp = FTP('')
                ftp.connect(STATION_IP, 2121)
                ftp.login("user", "12345")
                ftp.cwd("/")
                if command == "download_file":
                    files = data[2]
                    files = files.split(',')

                    # on crée un thread pour chaque fichier à télécharger
                    for i in range(len(files) - 1):
                        ftp.storbinary('STOR ' + files[i], open('/home/pi/recordings/' + files[i], 'rb'))
                    ftp.quit()

                elif command == "download_all":

                    # on va chercher le nombre de fichiers totaux à downloader
                    cmd = "ls /home/pi/recordings/"
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    output = process.stdout.read().decode('utf-8')
                    files = output.split("\n")

                    # on crée un thread pour chaque fichier à télécharger
                    for i in range(len(files) - 1):
                        ftp.storbinary('STOR ' + files[i], open('/home/pi/recordings/' + files[i], 'rb'))
                    ftp.quit()

            else:
                if command == "refresh_files":
                    cmd = "ls /home/pi/recordings/"
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    output = process.stdout.read().decode()
                    files = output.split(" ")
                    names = ""
                    for i in range(len(files)):
                        if i == 0:
                            names = names + files[0]
                        else:
                            names = names + "," + files[i]
                    rep = names
                    if rep == "":
                        rep = "none,"

                    # on envoie la réponse à la station de base
                    connection.send(rep.encode('utf-8'))

                else:
                    break

    connection.close()
