# script pour le fonctionnement des caméras

import socket
import subprocess

# from picamera import PiCamera
from datetime import datetime
from multiprocessing import Process


# définition de la fonction pour aller lire l'image dans un process externe (non-bloquant)
def read_file(input_file, send_to):
    # on va lire le fichier tant qu'on n'a pas atteint la fin et on envoie l'info
    image = input_file.read(4096)
    while image:
        send_to.send(read)
        image = file.read(4096)


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

# on met la camera en preview pour la préparer et on la garde afin de s'assurer qu'elle soit prête à prendre une photo
# à n'importe quel moment
# TODO à voir si ça affecte les performances
camera.start_preview()

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
            date = datetime.now()
            date = date.strftime("%d/%m/%Y %H:%M:%S")
            camera.start_recording("/home/ProtolabQuebec/recordings/" + date + ".h264")
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
            # TODO faire le download selon comment va marcher le serveur FTP
            if command == "download_file":
                print("Downloading file!")

            elif command == "download_all":
                print("Downloading all files!")

        else:
            if command == "check_files":
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
