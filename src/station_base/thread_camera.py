# script de définition du thread stoppable pour la gestion des previews

import threading
import time
import socket

from PyQt5 import QtGui


# on lui passe en argument premièrement l'objet de preview, le socket, ensuite et le path du fichier
class CameraThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        for x in range(len(kwargs['args'])):
            if x == 0:
                self.preview = kwargs['args'][0]
            elif x == 1:
                self.skt = kwargs['args'][1]
            else:
                self.path = kwargs['args'][2]

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.isSet()


class CameraTask(CameraThread):
    def run(self):
        while not self.stopped():
            self.skt.send(b"get_preview")
            data = self.skt.recv(1024)
            if data.decode('utf-8') == "preview_sent":
                self.preview.setPixmap(QtGui.QPixmap("{}/preview.jpg".format(self.path)))
            time.sleep(1)
