# script pour le fonctionnement des caméras

import socket
import subprocess
import threading
import src.other.functions

from picamera import PiCamera
from datetime import datetime
from multiprocessing import Process
from ftplib import FTP


# définition de la fonction pour aller lire l'image dans un process externe (non-bloquant)
def read_file(input_file, send_to):
    # on va lire le fichier tant qu'on n'a pas atteint la fin et on envoie l'info
    image = input_file.read(4096)
    while image:
        send_to.send(image)
        image = file.read(4096)


# on définit les paramètres pour la communication socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_ip = s.getsockname()[0]
s.close()
LOCAL_PORT = 60000

# déclaration du port pour le broadcasting
BROADCAST_PORT = 12345

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
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# binder le socket
tcp_sock.bind((local_ip, LOCAL_PORT))
udp_sock.bind(("255.255.255.255", BROADCAST_PORT))

# écoute pour les connections entrantes
tcp_sock.listen()

while True:
    # on regarde si on ne reçoit pas un paquet UDP de broadcast
    data, address = udp_sock.recvfrom(1024)
    if data:
        print("Message: ", data.decode('utf-8'))
        print(address)
        print("---------------")
        if data.decode('utf_8') == "requesting_broadcast":
            udp_sock.sendto(local_ip.encode('utf-8'), (address[0], address[1]))

    # s'il y a connexion TCP, on l'accepte et on la traite
    connection, address = tcp_sock.accept()
    print("Connexion établie par: ", address[0], "sur le socket ", address[1])
    STATION_IP = address[0]
    STATION_PORT = address[1]
    with connection:
        data = connection.recv(1024).decode('utf-8')
        data = data.split("_")
        command = data[0] + "_" + data[1]

        if data[0] == "get":
            if command == "get_preview":
                # on capture une image avec la caméra
                # TODO à voir si c'est trop gros pour la lecture de l'autre côté
                camera.capture("/home/ProtolabQuebec/preview/preview.jpg")

                # on va ouvrir le fichier de l'image
                file = open("/home/ProtolabQuebec/preview/preview.jpg", "wb")

                # on crée le process pour aller faire la lecture de l'image et l'envoyer (child process)
                read_process = Process(target=read_file, args=(file, connection))
                read_process.start()

                # TODO à voir si c'est limitant
                # on attend que le process ait fini avant de fermer le fichier
                read_process.join()

                """# on va lire le fichier tant qu'on n'a pas atteint la fin et on envoie l'info
                read = file.read(4096)
                while read:
                    connection.send(read)
                    read = file.read(4096)"""

                # on vient fermer le fichier pour éviter des problèmes
                file.close()

                # on vient le supprimer pour pouvoir réécrire un fichier avec le même nom (call système)
                cmd = "rm /home/ProtolabQuebec/preview/preview.jpg"
                process = subprocess.Popen(cmd.split())
                process.communicate()
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

            # on va chercher le nombre de fichier dans le dossier recordings pour identifier le nouvel enregistrement
            # TODO à voir si ça marche
            cmd = "ls /home/ProtolabQuebec/recordings/"
            process = subprocess.Popen(cmd.split())
            output, error = process.communicate()
            output = output.decode()
            print(output)
            files = output.split(" ")
            number = len(output) + 1
            camera.start_recording("/home/ProtolabQuebec/recordings/" + str(number) + ".h264")
            print("Starting camera!")

        elif data[0] == "stop":
            # TODO à voir si ça soulève des erreurs de faire comme ça
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
                    process = subprocess.Popen(cmd.split())
                    output, error = process.communicate()
                print("Deleting file(s)!")

            elif command == "delete_all":
                cmd = "rm /home/ProtolabQuebec/recordings/*"
                process = subprocess.Popen(cmd.split())
                output, error = process.communicate()
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
                    threading.Thread(target=src.other.functions.upload_file, args=('/recordings/' + fichiers[i],
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
                    threading.Thread(target=src.other.functions.upload_file, args=('/recordings/' + fichiers[i],
                                                                                   fichiers[i], ftp)).start()
                print("Downloading all files!")

        else:
            if command == "check_files":
                # TODO à voir si ça marche
                cmd = "ls /home/ProtolabQuebec/recordings/"
                process = subprocess.Popen(cmd.split())
                output, error = process.communicate()
                output = output.decode()
                print(output)
                files = output.split(" ")
                names = ""
                for i in range(len(files)):
                    names = names + "," + files[0]
                print("Checking files!")
                rep = names

                # on envoie la réponse à la station de base
                connection.send(rep.encode('utf-8'))

            elif command == "refresh_files":
                cmd = "ls /home/ProtolabQuebec/recordings/"
                process = subprocess.Popen(cmd.split())
                output, error = process.communicate()
                output = output.decode()
                print(output)
                files = output.split(" ")
                names = ""
                for i in range(len(files)):
                    names = names + "," + files[0]
                print("Refreshing files!")
                rep = names

                # on envoie la réponse à la station de base
                connection.send(rep.encode('utf-8'))

            else:
                break

        # on ferme la connection
        connection.close()
