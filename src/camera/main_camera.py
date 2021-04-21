# script principal pour le fonctionnement des caméras
import socket
import subprocess
import time
import i2c_master

import RPi.GPIO as GPIO

from picamera import PiCamera
from ftplib import FTP

# on définit les paramètres pour la communication socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
LOCAL_IP = s.getsockname()[0]
s.close()
LOCAL_PORT = 60000

# déclaration des infos du socket de la station de base
STATION_IP = ""
STATION_PORT = 0

# déclaration de l'objet caméra pour effectuer les opérations
camera = PiCamera()

# on met la résolution comme ça pour les previews pour ne pas avoir à la changer à chaque call
camera.resolution = (960, 540)
camera.framerate = 30

# déclaration des variables pour tenir compte des déplacements de la caméra
horizontal = 45
vertical = 45

battery_manager = i2c_master.BMSCom()

# on met la camera en preview pour la préparer et on la garde afin de s'assurer qu'elle soit prête à prendre une photo
# à n'importe quel moment
camera.start_preview()

# création des sockets pour la communication
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# binder le socket
tcp_sock.bind((LOCAL_IP, LOCAL_PORT))

# écoute pour les connexions entrantes
tcp_sock.listen(100)

# déclaration de la variable pour voir dans quel fichier on doit sauvegarder les images (pour éviter écrasement)
preview = False

# on vient centrer la caméra pour être sûr qu'elle soit centrée au commencement
cmd = "python3 servomotor_master.py 33 45"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

cmd = "python3 servomotor_master.py 32 45"
subprocess.Popen(cmd, shell=True)

time.sleep(1)

# on vient ouvrir la LED verte pour dire que la caméra est prête à enregistrer
GPIO.setmode(GPIO.board)
GPIO.setup(36, GPIO.OUT)
GPIO.output(36, GPIO.HIGH)

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
                if command == "get_preview":
                    ftp = FTP('')
                    ftp.connect(STATION_IP, 2121)
                    ftp.login("user", "12345")
                    ftp.cwd("/")

                    if not preview:
                        # on prend l'image
                        camera.capture("/home/pi/preview/preview.jpg")

                        # on va sauvegarder l'image sur le serveur
                        ftp.storbinary('STOR preview.jpg', open('/home/pi/preview/preview.jpg', 'rb'))
                        ftp.quit()
                        preview = True

                    else:
                        # on prend l'image
                        camera.capture("/home/pi/preview/preview1.jpg")

                        # on va sauvegarder l'image sur le serveur
                        ftp.storbinary('STOR preview.jpg', open('/home/pi/preview/preview.jpg', 'rb'))
                        ftp.quit()
                        preview = False

                elif command == "get_infos":
                    # battery = battery_manager.get_charge1000()
                    battery = "50%"
                    rep = LOCAL_IP + "," + battery

                    # on envoie la réponse à la station de base
                    connection.send(rep.encode('utf-8'))
                else:
                    break

            elif data[0] == "start":
                # on va chercher le nombre de fichier dans le dossier recordings
                cmd = "ls /home/pi/recordings/"
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                output = process.stdout.read()
                output = output.decode()
                files = output.split("\n")
                number = len(files)
                camera.resolution = (1920, 1080)
                camera.start_recording("/home/pi/recordings/" + LOCAL_IP + "recording" + str(number) + ".h264")

            elif data[0] == "stop":
                camera.stop_recording()
                camera.resolution = (960, 540)

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
