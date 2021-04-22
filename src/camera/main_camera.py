# script principal pour le fonctionnement des caméras (enregistrement et preview)

import socket
import subprocess
import time
import i2c_master

import RPi.GPIO as GPIO

from picamera import PiCamera
from ftplib import FTP


# on vient débuté le script secondaire et le script de broadcast
cmd = "python3 secondary_camera.py &"
subprocess.Popen(cmd, shell=True)

# on lui laisse un peu de temps pour s'assurer que tout soit correct
time.sleep(1)

cmd = "python3 broadcast_camera.py &"
subprocess.Popen(cmd, shell=True)
time.sleep(1)

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

# on met la camera en preview pour la préparer et on la garde afin de s'assurer qu'elle soit prête à prendre une photo
# à n'importe quel moment
camera.start_preview()

# création du sockets pour la communication
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

# on vient garder en mémoire si on est connecter au serveur FTP on non pour les previews
is_connected = False

# on vient ouvrir la LED verte pour dire que la caméra est prête à enregistrer
GPIO.setmode(GPIO.BOARD)
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

                    camera.capture("/home/pi/preview/preview.jpg")

                    try:
                        image = open("/home/pi/preview/preview.jpg", 'rb')
                        ftp.storbinary("STOR preview.jpg", image)
                        ftp.close()
                    except Exception as e:
                        print(e)
                        """if not is_connected:
                        # on vient se connecter au serveur FTP
                        ftp = FTP('')
                        ftp.connect(STATION_IP, 2121)
                        ftp.login("user", "12345")
                        ftp.cwd("/")
                        is_connected = True

                    if not preview:
                        # on prend l'image
                        camera.capture("/home/pi/preview/preview.jpg")

                        try:
                            image = open("/home/pi/preview/preview.jpg", 'rb')
                            ftp.storbinary("STOR preview.jpg", image)
                            preview = True

                        except Exception as e:
                            print("Erreur: {}".format(e))
                            try:
                                # si erreur, on se déconnecte et on réessaie de se connecter
                                ftp.close()
                                ftp = FTP('')
                                ftp.connect(STATION_IP, 2121)
                                ftp.login("user", "12345")
                                ftp.cwd("/")
                            except Exception as f:
                                print("Erreurs: {} et {}".format(e, f))

                    else:
                        # on prend l'image
                        camera.capture("/home/pi/preview/preview1.jpg")

                        try:
                            image = open("/home/pi/preview/preview.jpg", 'rb')
                            ftp.storbinary("STOR preview1.jpg", image)
                            preview = False

                        except Exception as e:
                            print("Erreur: {}".format(e))
                            try:
                                # si erreur, on se déconnecte et on réessaie de se connecter
                                ftp.close()
                                ftp = FTP('')
                                ftp.connect(STATION_IP, 2121)
                                ftp.login("user", "12345")
                                ftp.cwd("/")
                            except Exception as f:
                                print("Erreurs: {} et {}".format(e, f))

                else:
                    ftp.close()
                    is_connected = False"""

                    """if not preview:
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
                        ftp.storbinary('STOR preview1.jpg', open('/home/pi/preview/preview1.jpg', 'rb'))
                        ftp.quit()

                        preview = False"""

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

            else:
                break

    connection.close()
