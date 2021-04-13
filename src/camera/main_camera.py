# script principal pour le fonctionnement des caméras

import socket
import subprocess
import threading
import time

import functions

from picamera import PiCamera
from datetime import datetime
from multiprocessing import Process
from ftplib import FTP


# définition de la fonction pour aller lire l'image dans un process externe (non-bloquant)
def get_preview(cam, send_to):
    while True:
        # on prend l'image
        cam.capture("/home/ProtolabQuebec/preview/preview.jpg")

        # on va ouvrir l'image à envoyer
        input_file = open("/home/ProtolabQuebec/preview/preview.jpg", "wb")

        # on va lire le fichier tant qu'on n'a pas atteint la fin et on envoie l'info
        image = input_file.read(65536)
        while image:
            send_to.send(image)
            image = input_file.read(65536)
        input_file.close()
        time.sleep(0.5)


# on définit les paramètres pour la communication socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
s.close()
LOCAL_PORT = 60000

# déclaration des infos du socket de la station de base
STATION_IP = ""
STATION_PORT = 0

# déclaration de l'objet caméra pour effectuer les opérations
camera = PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 30

# on met la camera en preview pour la préparer et on la garde afin de s'assurer qu'elle soit prête à prendre une photo
# à n'importe quel moment
# TODO à voir si ça affecte les performances
camera.start_preview()

# création des sockets pour la communication
# TODO Voir si on doit le garder en blocking si plusieurs cameras ou envoie des images
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# binder le socket
tcp_sock.bind((local_ip, LOCAL_PORT))

# écoute pour les connexions entrantes
tcp_sock.listen()

# déclaration de la variable pour voir si on doit envoyer ou arrêter d'envoyer les previews
active_preview = False

while True:
    # s'il y a connexion TCP, on l'accepte et on la traite
    connection, address = tcp_sock.accept()
    print("Connexion établie par: ", address[0], "sur le socket ", address[1])
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
                    if not active_preview:
                        active_preview = True
                        # on crée le process pour aller faire la lecture de l'image et l'envoyer (child process)
                        read_process = Process(target=get_preview, args=(camera, connection))
                        read_process.start()

                    else:
                        # TODO à voir si c'est limitant
                        # on attend que le process ait fini
                        read_process.join()
                        # si ça ne marche pas ou si c'est trop long, faire un read_process.terminate

                    print("Getting preview!")

                elif command == "get_infos":
                    # TODO faire la fonction pour aller get la charge de la batterie
                    battery = "50%"
                    rep = local_ip + "," + battery
                    print("Getting infos!")

                    # on envoie la réponse à la station de base
                    connection.send(rep.encode('utf-8'))
                else:
                    break

            elif data[0] == "start":
                # on va chercher le nombre de fichier dans le dossier recordings
                # cmd = "ls /home/ProtolabQuebec/recordings/"
                cmd = "ls /home/pi/recordings/"
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                output = process.stdout.read()
                print(output)
                output = output.decode()
                files = output.split("\n")
                number = len(files)
                # camera.start_recording("/home/ProtolabQuebec/recordings/" + str(number) + ".h264")
                camera.start_recording("/home/pi/recordings/recording" + str(number) + ".h264")
                print("Starting camera!")

            elif data[0] == "stop":
                camera.stop_recording()
                print("Stopping camera!")

            elif data[0] == "move":
                # TODO faire fonction pour aller bouger la camera
                if command == "move_up":
                    print("Moving up!")

                elif command == "move_right":
                    print("Moving right!")

                elif command == "move_left":
                    print("Moving left!")

                elif command == "move_down":
                    print("Moving down!")

                else:
                    break

            elif data[0] == "delete":
                if command == "delete_file":
                    # on va chercher les différents fichiers à supprimer
                    fichiers = data[2]
                    fichiers = fichiers.split(',')
                    for i in range(len(fichiers)):
                        cmd = "rm /home/ProtolabQuebec/recordings/" + str(fichiers[i])
                        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                        output = process.stdout.read()
                        print(output)
                    print("Deleting file(s)!")

                elif command == "delete_all":
                    cmd = "rm /home/ProtolabQuebec/recordings/*"
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    output = process.stdout.read()
                    print(output)
                    print("Deleting all files!")

                else:
                    break

            elif data[0] == "download":
                # on vient établir la connection
                ftp = FTP('')
                ftp.connect(STATION_IP, 2121)
                ftp.login("user", "12345")
                ftp.cwd("/")
                if command == "download_file":
                    fichiers = data[2]
                    fichiers = fichiers.split(',')

                    # on crée un thread pour chaque fichier à télécharger
                    for i in range(len(fichiers)):
                        threading.Thread(target=functions.upload_file, args=('/recordings/' + fichiers[i],
                                                                             fichiers[i], ftp)).start()
                    print("Downloading file(s)!")

                elif command == "download_all":

                    # on va chercher le nombre de fichiers totaux à downloader
                    cmd = "ls /home/ProtolabQuebec/recordings/"
                    process = subprocess.Popen(cmd.split())
                    output, error = process.communicate()
                    output = output.decode()
                    print(output)
                    files = output.split(" ")
                    number = len(output)

                    # on crée un thread pour chaque fichier à télécharger
                    for i in range(len(files)):
                        threading.Thread(target=functions.upload_file, args=('/recordings/' + fichiers[i],
                                                                             fichiers[i], ftp)).start()
                    print("Downloading all files!")

            else:
                if command == "check_files":
                    cmd = "ls /home/ProtolabQuebec/recordings/"
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    output = process.stdout.read()
                    output = output.decode()
                    print(output)
                    files = output.split(" ")
                    names = ""
                    for i in range(len(files)):
                        if i == 0:
                            names = names + files[0]
                        else:
                            names = names + "," + files[i]
                    print("Checking files!")
                    rep = names

                    # on envoie la réponse à la station de base
                    connection.send(rep.encode('utf-8'))

                elif command == "refresh_files":
                    cmd = "ls /home/ProtolabQuebec/recordings/"
                    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                    output = process.stdout.read()
                    output = output.decode()
                    print(output)
                    files = output.split(" ")
                    names = ""
                    for i in range(len(files)):
                        if i == 0:
                            names = names + files[0]
                        else:
                            names = names + "," + files[i]
                    print("Refreshing files!")
                    rep = names

                    # on envoie la réponse à la station de base
                    connection.send(rep.encode('utf-8'))

                else:
                    break
