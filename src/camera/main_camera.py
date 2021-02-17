# script pour le fonctionnement des caméras

import socket
import threading
import subprocess

from picamera import PiCamera
from datetime import datetime

# on définit les paramètres pour la communication socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
s.close()
LOCAL_PORT = 60000

# déclaration des infos du socket HOST
HOST_IP = ""
HOST_PORT = 0

# déclaration de l'objet caméra pour effectuer les opérations
camera = PiCamera()
camera.resolution = (1920, 1080)
camera.framerate = 30

# TODO Voir si on doit le garder en blocking si plusieurs cameras ou envoie des images
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# binder le socket
skt.bind((local_ip, LOCAL_PORT))

# écoute pour les connections entrantes
skt.listen()

while True:
    # s'il y a connexion, on l'accepte et on la traite
    connection, address = skt.accept()
    print("Connexion établie par: ", address[0], "sur le socket ", address[1])
    HOST_IP = address[0]
    HOST_PORT = address[1]
    with connection:
        data = connection.recv(1024).decode('utf-8')
        data = data.split("_")
        command = data[0] + "_" + data[1]

        # tous les choix possibles d'actions pour la caméra
        if data[0] == "broadcast":
            rep = local_ip
            print("Sending IP!")

        elif data[0] == "get":
            if command == "get_preview":
                # TODO faire la fonction pour aller get le preview de la caméra
                print("Getting preview!")
            elif command == "get_infos":
                # TODO faire la fonction pour aller get la charge de la batterie
                battery = "50%"
                rep = local_ip + "," + battery
                print("Getting infos!")
            else:
                break

        elif data[0] == "start":
            date = datetime.now()
            date = date.strftime("%d/%m/%Y %H:%M:%S")
            camera.start_recording("/home/pi/recordings/" + date + ".h264")
            rep = "camera started"
            print("Starting camera!")

        elif data[0] == "stop":
            # TODO à voir si ça soulève des erreurs de faire comme ça
            camera.stop_recording()
            rep = "camera stopped"
            print("Stopping camera!")

        elif data[0] == "move":
            # TODO faire fonction pour aller bouger la camera
            if command == "move_up":
                print("Moving up!")
                rep = "camera moved up"
            elif command == "move_right":
                print("Moving right!")
                rep = "camera moved right"
            elif command == "move_left":
                print("Moving left!")
                rep = "camera moved left"
            elif command == "move_down":
                print("Moving down!")
                rep = "camera moved down"
            else:
                break

        elif data[0] == "delete":
            if command == "delete_file":
                # on va chercher les différents fichiers à supprimer
                print("Deleting file!")
            elif command == "delete_all":
                print("Deleting all files!")
            else:
                break

        elif data[0] == "download":
            if command == "download_file":
                print("Downloading file!")
            elif command == "download_all":
                print("Downloading all files!")

        else:
            if command == "check_files":
                print("Checking files!")
            elif command == "refresh_files":
                print("Refreshing files!")
            else:
                break

        # on envoie la réponse à la station de base
        connection.sendto(rep.encode('utf-8'), (HOST_IP, HOST_PORT))
