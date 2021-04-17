# script de définition des fonctions

import socket
import time
import queue

from PyQt5 import QtGui


def get_wifi_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    return ip


# fonction pour fermer le socket lors de la fermeture de l'application
def close_port(skt: socket):
    # essaie et si le port n'est pas connecté, on fait juste le fermer. Autrement on coupe la connexion avant de fermer
    try:
        skt.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    skt.close()


# fonction pour traiter les réponses du broadcast UDP
def get_response(broadcast_queue, skt):
    while True:
        data, address = skt.recvfrom(1024)
        if data:
            data = data.decode('utf-8')
            broadcast_queue.put(data)


def get_info_process(skt, ip, port, info_queue):
    while True:
        # pour être complémentaire à la fonction du UI (ne pas le faire 2 fois de suite en startant/changeant de camera)
        time.sleep(5)
        # print("Getting infos")
        skt.send(b"get_infos")
        data = skt.recv(1024)
        data = data.decode('utf-8')
        # print(data)
        # data = "25%"
        # print(data)
        info_queue.put((str(ip[1] + 1), str(ip[0]), str(data)))


def get_preview_process(skt, ip, port, preview_queue):
    while True:
        print("Getting preview")
        skt.send(b"get_preview")
        """datas = None
        data = skt.recv(65536)
        while data:
            datas = datas + data
            data = skt.recv(65536)"""
        # on vient attendre que le premier fichier se rende sur le serveur FTP
        time.sleep(1)
        # read_file = open(r"../ressource/regie.png", "rb")
        # data = read_file.read()
        # read_file.close()
        # preview_queue.put(data)
        # time.sleep(1)


def update_infos_thread(info_queue, info):
    while True:
        try:
            infos = info_queue.get()
            # print("Updating info")
            info.setText(" Informations\n Nom de la camera: Camera " + str(infos[0]) +
                         "\n Adresse IP: " + str(infos[1]) +
                         "\n Batterie restante: " + str(infos[2]))
        except queue.Empty:
            time.sleep(5)


def update_preview_thread(preview_queue, preview):
    while True:
        try:
            """image = preview_queue.get()
            print("updating preview")
            file = open(r"../ressource/previews.jpg", "rb")
            file.write(image)
            file.close()"""
            preview.setPixmap(QtGui.QPixmap(r"../ressource/preview.png"))
        except queue.Empty:
            time.sleep(1)


def upload_file(file_path, file_name, ftp):
    ftp.storbinary('STOR ' + file_name, open(file_path, 'rb'))
    ftp.quit()

