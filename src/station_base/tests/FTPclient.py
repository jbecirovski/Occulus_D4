# exemple de base pour un client FTP
import os

from ftplib import FTP


def upload_file():
    filename = 'networkSweep.py'  # replace with your file in your home folder
    ftp.storbinary('STOR '+filename, open(filename, 'rb'))
    ftp.quit()


def download_file():
    filename = 'networkSweep.py'  # replace with your file in the directory ('directory_name')
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    ftp.quit()
    localfile.close()


ftp = FTP('')
ftp.connect('127.0.0.1', 2121)
ftp.login("user", "12345")
ftp.cwd("/")

upload_file()
