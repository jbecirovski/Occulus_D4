# script pour le fonctionnement des caméras

import socket
import threading

from src.other.functions import get_wifi_ip_address

# on définit les paramètres pour la communication socket
local_ip = get_wifi_ip_address()
LOCAL_PORT = 60000

# TODO Voir si on doit le garder en blocking si plusieurs cameras ou envoi des images
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# binder le socket
skt.bind((local_ip, LOCAL_PORT))

# écoute pour les connections entrantes
skt.listen()

while True:
    # s'il y a connexion, on l'accepte et on la traite
    connection, address = skt.accept()
    print("Connexion établie par: ", address[0], "sur le socket ", address[1])
    with connection:
        data = connection.recv(1024).decode('utf-8')
        data = data.split("_")
        command = data[0] + "_" + data[1]

        # tous les choix possibles d'actions pour la caméra
        if data[0] == "broadcast":
            print("Sending IP!")

        elif data[0] == "get":
            if command == "get_preview":
                print("Getting preview!")
            elif command == "get_infos":
                print("Getting infos!")
            else:
                break

        elif data[0] == "start":
            print("Starting camera!")

        elif data[0] == "stop":
            print("Stopping camera!")

        elif data[0] == "move":
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


