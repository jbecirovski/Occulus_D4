# exemple de base pour un client FTP
from ftplib import FTP


def upload_file():  # pas nécessaire si on va directement dans le bon path (disons recordings)
    file_path = r"../ressource/512MB.zip"  # replace with path of file
    file_name = "file.zip"  # replace with the name you want the file to have on server
    ftp.storbinary('STOR ' + file_name, open(file_path, 'rb'))
    ftp.quit()


def download_file():
    file_path = r"../../../../../Desktop/file.zip"  # replace with path of file
    file_name = "file.zip"  # replace with the name you want the file to have on server
    localfile = open(file_path, 'wb')
    ftp.retrbinary('RETR ' + file_name, localfile.write)
    ftp.quit()
    localfile.close()


ftp = FTP('')
ftp.connect('127.0.0.1', 2121)
ftp.login("user", "12345")
ftp.cwd("/")

# upload_file()
download_file()
