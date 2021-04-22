# script de définition du thread stoppable pour la gestion des previews

import threading
import time
import socket


# on lui passe en argument premièrement l'objet de preview, le socket, ensuite l'adresse ip et finalement le port
class CameraThread(threading.Thread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        for x in args:
            if x == 0:
                self.preview = x[0]
            elif x == 1:
                self.skt = x[1]
            elif x == 2:
                self.ip = x[2]
            else:
                self.port = x[3]

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.isSet()


class CameraTask(CameraThread):
    def run(self):
        while not self.stopped():
            self.skt.send(b"get_preview")
            time.sleep(1)
