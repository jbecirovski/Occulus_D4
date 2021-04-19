# script de définition des fonctions

import socket
import time
import queue

import numpy as np
import skimage as sk
import skimage.io as skio

from PyQt5 import QtGui
from skimage.transform import resize


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
        # time.sleep(120)
        time.sleep(5)
        skt.send(b"get_infos")
        data = skt.recv(1024)
        data = data.decode('utf-8')
        info_queue.put((str(ip[1] + 1), str(ip[0]), str(data)))


def get_preview_process(skt):
    while True:
        print("Getting preview")
        skt.send(b"get_preview")
        time.sleep(1)


def update_infos_thread(info_queue, info):
    while True:
        try:
            infos = info_queue.get()
            try:
                battery = infos[2].split(',')
                battery = battery[1]
                info.setText(" Informations\n Nom de la camera: Camera " + str(infos[0]) +
                             "\n Adresse IP: " + str(infos[1]) +
                             "\n Batterie restante: " + str(battery))
            except IndexError:
                pass
        except queue.Empty:
            # time.sleep(30)
            time.sleep(5)


def update_preview_thread(preview):
    while True:
        try:
            file = open(r"../station_base/preview.jpg", "r")
            """data = file.read()
            file.close()
            file.write(image)
            file.close()
            data = np.asarray(data)
            data = resize(data, (360, 640))
            data = sk.img_as_ubyte(data)
            skio.imsave("../station_base/good_preview.jpg", data)"""
            preview.setPixmap(QtGui.QPixmap(r"../station_base/preview.jpg"))
        except OSError:
            time.sleep(1)

