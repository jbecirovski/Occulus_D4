# script pour le fonctionnement de la station de base

import os
import socket
import subprocess
import sys
import threading
import time
import functions
import pathlib
import thread_camera

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from multiprocessing import Process, Queue


class Window(QtWidgets.QMainWindow):

    # contructeur de la classe
    def __init__(self):
        # on va chercher le path dans où le script s'exécute
        self.path = pathlib.Path(__file__).parent.absolute()

        super(Window, self).__init__()
        self.setFixedHeight(800)
        self.setFixedWidth(1400)
        self.setWindowTitle("Application Camera")
        self.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))

        # paramètre de la classe
        self.active_camera = 0

        # créer la deuxième fenêtre pour la faire apparaître lorsque nécessaire
        self.fileWindow = ""

        # détermine l'adresse IP de la station de base
        functions.get_wifi_ip_address()

        # initialisation des variables constantes
        self.hosts = []
        self.CAMERA_PORT = 60000
        self.COMM_PORT = 61000
        self.BROADCAST_IP = "255.255.255.255"
        self.BROADCAST_PORT = 12345

        # initialisation de la variable pour l'envoi de preview
        self.active_preview = False

        # création du socket de communication pour la gestion de la caméra
        self.camera_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.camera_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # création du socket de communication pour la gestion des autres commandes de la caméra
        self.comm_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.comm_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # création du socket UDP pour le broadcasting
        self.udp_skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.udp_skt.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # on envoie un message bidon avec le socket UDP pour l'initialiser
        self.udp_skt.sendto(b"enabling socket", ("192.168.0.0", self.BROADCAST_PORT))

        # déclaration des différents composants de l'interface graphique
        self.btn_quit = QtWidgets.QPushButton("Quit", self)
        self.camera_combo_box = QtWidgets.QComboBox(self)
        self.btn_detect_cameras = QtWidgets.QPushButton("Detect Cameras", self)
        self.btn_start_camera = QtWidgets.QPushButton("Start Camera", self)
        self.btn_stop_camera = QtWidgets.QPushButton("Stop Camera", self)
        self.btn_start_all_camera = QtWidgets.QPushButton("Start All Camera", self)
        self.btn_manage_files = QtWidgets.QPushButton("Manage Files", self)
        self.btn_stop_all_camera = QtWidgets.QPushButton("Stop All Camera", self)
        self.btn_remove = QtWidgets.QPushButton("remove", self)
        self.btn_up_arrow = QtWidgets.QToolButton(self)
        self.moveup_key = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Up), self)
        self.btn_left_arrow = QtWidgets.QToolButton(self)
        self.moveleft_key = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Left), self)
        self.btn_right_arrow = QtWidgets.QToolButton(self)
        self.moveright_key = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Right), self)
        self.btn_down_arrow = QtWidgets.QToolButton(self)
        self.movedown_key = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Down), self)
        self.info = QtWidgets.QLabel(self)
        self.preview = QtWidgets.QLabel(self)
        self.preview_button = QtWidgets.QToolButton(self)
        self.statusBar()
        self.main_menu = self.menuBar()
        self.palette = QtGui.QPalette()

        # déclaration des process pour aller chercher l'information des caméras
        self.info_process = Process()
        # self.preview_process = Process()

        # déclaration des threads pour faire du aller updater le UI
        self.info_thread = threading.Thread()
        self.preview_thread = None

        # création du thread pour aller chercher les réponses du broadcast UDP
        self.broadcast_thread = threading.Thread()

        # déclaration des queues pour la gestion des communications entre les process et threads
        self.info_queue = Queue()
        self.preview_queue = Queue()

        # déclaration de la queue pour le traitement des réponses de broadcast UDP
        self.broadcast_queue = Queue()

        # déclaration d'une variable pour garder si la caméra est déjà partie ou non
        self.camera_activated = False

        # on vient démarrer le process pour la gestion du serveur FTP
        cmd = "python {}/ftp_station.py".format(self.path)
        subprocess.Popen(cmd)

    # création de l'interface
    def create_ui(self):
        self.btn_quit.clicked.connect(self.close_application)
        self.btn_quit.resize(200, 100)
        self.btn_quit.move(1180, 680)

        self.camera_combo_box.move(20, 50)
        self.camera_combo_box.activated.connect(self.choose_camera)

        self.btn_remove.move(125, 50)
        self.btn_remove.resize(50, 30)
        self.btn_remove.clicked.connect(self.remove)

        self.btn_detect_cameras.clicked.connect(self.detect_cameras)
        self.btn_detect_cameras.resize(100, 40)
        self.btn_detect_cameras.move(20, 100)

        self.btn_start_camera.clicked.connect(self.start_camera)
        self.btn_start_camera.resize(100, 40)
        self.btn_start_camera.move(20, 150)

        self.btn_stop_camera.clicked.connect(self.stop_camera)
        self.btn_stop_camera.resize(100, 40)
        self.btn_stop_camera.move(20, 200)

        self.btn_start_all_camera.clicked.connect(self.start_cameras)
        self.btn_start_all_camera.resize(120, 60)
        self.btn_start_all_camera.move(20, 645)

        self.btn_manage_files.clicked.connect(self.manage_files)
        self.btn_manage_files.resize(120, 60)
        self.btn_manage_files.move(20, 570)

        self.btn_stop_all_camera.clicked.connect(self.stop_cameras)
        self.btn_stop_all_camera.resize(120, 60)
        self.btn_stop_all_camera.move(20, 720)

        self.btn_up_arrow.setArrowType(QtCore.Qt.UpArrow)
        self.btn_up_arrow.setGeometry(1260, 500, 30, 30)
        self.btn_up_arrow.clicked.connect(self.up_arrow)
        self.moveup_key.activated.connect(self.up_arrow)

        self.btn_left_arrow.setArrowType(QtCore.Qt.LeftArrow)
        self.btn_left_arrow.setGeometry(1205, 550, 30, 30)
        self.btn_left_arrow.clicked.connect(self.left_arrow)
        self.moveleft_key.activated.connect(self.left_arrow)

        self.btn_right_arrow.setArrowType(QtCore.Qt.RightArrow)
        self.btn_right_arrow.setGeometry(1315, 550, 30, 30)
        self.btn_right_arrow.clicked.connect(self.right_arrow)
        self.moveright_key.activated.connect(self.right_arrow)

        self.btn_down_arrow.setArrowType(QtCore.Qt.DownArrow)
        self.btn_down_arrow.setGeometry(1260, 600, 30, 30)
        self.btn_down_arrow.clicked.connect(self.down_arrow)
        self.movedown_key.activated.connect(self.down_arrow)

        self.info.setStyleSheet("border: 2px solid grey;")
        self.info.resize(200, 100)
        self.info.move(1180, 50)

        self.preview.move(180, 100)
        self.preview.resize(960, 540)
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setPixmap(QtGui.QPixmap("{}/ressource/protolabLogo.png".format(self.path)))
        self.preview.setStyleSheet("border: 2px solid grey;")

        self.preview_button.setText("Get preview")
        self.preview_button.move(600, 720)
        self.preview_button.resize(120, 60)
        self.preview_button.clicked.connect(self.start_stop_preview)

        self.preview.setPixmap(QtGui.QPixmap("{}/ressource/protolabLogo.png".format(self.path)))

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

        # Édition du style de la fenêtre
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        self.palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.darkGray)
        self.palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        self.palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        self.palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.darkGray)
        self.palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        self.palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        self.palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        self.palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        self.palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.darkRed)
        QtWidgets.qApp.setPalette(self.palette)

        # starter le thread pour traiter les réponses UDP du broadcast
        self.broadcast_thread = threading.Thread(target=functions.get_response,
                                                 args=(self.broadcast_queue, self.udp_skt,),
                                                 daemon=True).start()

        # détecte les caméras qui sont sur le network au start
        while len(self.hosts) == 0:
            self.detect_cameras()
            time.sleep(0.5)

        ip = self.hosts[self.active_camera][0]
        self.camera_skt.connect((ip, self.CAMERA_PORT))
        self.comm_skt.connect((ip, self.COMM_PORT))

        # va chercher les infos de la caméra par défaut
        self.get_infos()

        # créer le process pour aller chercher les infos de la caméra
        self.info_process = Process(target=functions.get_info_process,
                                    args=(self.comm_skt, self.hosts[self.active_camera], self.COMM_PORT, self.info_queue,))
        self.info_process.start()

        # starter le thread pour aller updater l'info de la caméra
        self.info_thread = threading.Thread(target=functions.update_infos_thread,
                                            args=(self.info_queue, self.info,), daemon=True).start()

    # méthodes de classe
    def start_stop_preview(self):
        if self.active_preview:
            self.active_preview = False
            self.preview_button.setText("Start preview")
            self.preview_thread.stop()
            time.sleep(1)
            self.preview.setPixmap(QtGui.QPixmap("{}/ressource/protolabLogo.png".format(self.path)))
            self.preview_thread = None
            os.remove("{}/preview.jpg".format(self.path))

        else:
            self.preview_thread = thread_camera.CameraTask(args=(self.preview, self.camera_skt, self.path,))
            self.active_preview = True
            self.preview_button.setText("Stop preview")
            self.preview_thread.start()

    def choose_camera(self):
        if not self.active_preview:
            new_active_camera = self.camera_combo_box.currentIndex()
            if new_active_camera != self.active_camera:
                self.active_camera = new_active_camera

                # on vient fermer les connexions en cours et on les redémarrent avec la bonne caméra
                self.camera_skt.send(b"")
                self.camera_skt.shutdown(socket.SHUT_RDWR)
                self.camera_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.camera_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.camera_skt.connect((str(self.hosts[self.active_camera][0]), self.CAMERA_PORT))
                self.comm_skt.send(b"")
                self.comm_skt.shutdown(socket.SHUT_RDWR)
                self.comm_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.comm_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.comm_skt.connect((str(self.hosts[self.active_camera][0]), self.COMM_PORT))
                self.get_infos()

                # stopper le process pour aller chercher l'info de la caméra et restarter avec la nouvelle caméra
                self.info_process.terminate()
                self.info_process = Process(target=functions.get_info_process,
                                            args=(self.comm_skt, self.hosts[new_active_camera], self.COMM_PORT, self.info_queue,))
                self.info_process.start()
            else:
                pass
        else:
            msg = QtWidgets.QMessageBox()
            msg.setText("Please stop preview before switching to another camera.")
            msg.setWindowTitle("Choose error")
            msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def detect_cameras(self):
        # déclaration de la variable pour stocker les résultats
        text_results = []

        # on envoie le broadcast
        self.udp_skt.sendto(b"requesting_broadcast", (self.BROADCAST_IP, self.BROADCAST_PORT))

        # on va chercher les adresses dans la queue
        for i in range(self.broadcast_queue.qsize()):
            item = self.broadcast_queue.get()
            text_results.append(item)

        # classer les ips en ordre croissant
        text_results.sort()

        # ajouter un numéro de caméra à chaque ip en ordre croissant
        count = 0
        for i in range(len(text_results)):
            text_results[i] = (text_results[i], count)
            count += 1

        # on regarde si les nouvelles caméras détectées sont les mêmes que celles d'avant
        if text_results != self.hosts:
            self.hosts = text_results
            self.camera_combo_box.clear()
            for i in range(len(text_results)):
                self.camera_combo_box.addItem("Camera " + str(i + 1))

    def start_camera(self):
        if self.camera_activated:
            msg = QtWidgets.QMessageBox()
            msg.setText("Please stop camera before starting another recording.")
            msg.setWindowTitle("Record error")
            msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            if self.active_preview:
                msg = QtWidgets.QMessageBox()
                msg.setText("Please stop preview before starting another recording.")
                msg.setWindowTitle("Record error")
                msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                self.camera_skt.send(b"start_camera")
                self.camera_activated = True

    def stop_camera(self):
        if not self.camera_activated:
            msg = QtWidgets.QMessageBox()
            msg.setText("Please start camera before stopping it.")
            msg.setWindowTitle("Record error")
            msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            if self.active_preview:
                msg = QtWidgets.QMessageBox()
                msg.setText("Please stop preview before stopping a recording.")
                msg.setWindowTitle("Record error")
                msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                self.camera_skt.send(b"stop_camera")
                self.camera_activated = False

    # TODO À vérifier si le contrôle du GPIO se fait avec deux caméras
    def start_cameras(self):
        if self.camera_activated:
            msg = QtWidgets.QMessageBox()
            msg.setText("Please stop camera before starting another recording.")
            msg.setWindowTitle("Record error")
            msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            if self.active_preview:
                msg = QtWidgets.QMessageBox()
                msg.setText("Please stop preview before starting another recording.")
                msg.setWindowTitle("Record error")
                msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                if len(self.hosts) == 1:
                    self.camera_skt.send(b"start_camera")
                else:
                    for i in range(len(self.hosts)):
                        if i == 0:
                            self.camera_skt.send(b"start_camera")
                        else:
                            ip = self.hosts[i][0]
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            s.connect((ip, self.CAMERA_PORT))
                            s.send(b"start_camera")
                            s.send(b"")
                            s.shutdown(socket.SHUT_RDWR)
                self.camera_activated = True

    def stop_cameras(self):
        if not self.camera_activated:
            msg = QtWidgets.QMessageBox()
            msg.setText("Please start camera before stopping it.")
            msg.setWindowTitle("Record error")
            msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            if self.active_preview:
                msg = QtWidgets.QMessageBox()
                msg.setText("Please stop preview before stopping a recording.")
                msg.setWindowTitle("Record error")
                msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                if len(self.hosts) == 1:
                    self.camera_skt.send(b"stop_camera")
                else:
                    for i in range(len(self.hosts)):
                        if i == 0:
                            self.camera_skt.send(b"stop_camera")
                        else:
                            ip = self.hosts[i][0]
                            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                            s.connect((ip, self.CAMERA_PORT))
                            s.send(b"stop_camera")
                            s.send(b"")
                            s.shutdown(socket.SHUT_RDWR)
                self.camera_activated = False

    # TODO à regarder pourquoi ça plante en utilisant le moteur après un retour du menu avec deux caméras
    def manage_files(self):
        self.fileWindow = FileWindow(self.active_camera, self.comm_skt, self.hosts[self.active_camera], self.COMM_PORT,
                                     self.hosts, self.path)
        if self.fileWindow.isVisible():
            self.fileWindow.hide()
        else:
            self.fileWindow.show()

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, "Extract!", "Are you sure you want to quit",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            self.comm_skt.send(b"")
            self.camera_skt.send(b"")
            functions.close_port(self.comm_skt)
            functions.close_port(self.camera_skt)
            self.info_process.terminate()
            self.info_process.join()

            # il est possible de quitter l'application sans avoir starter le process pour les previews
            try:
                self.preview_process.stop()
            except AttributeError:
                pass
            sys.exit()
        else:
            pass

    def close_event(self, event):
        event.ignore()
        self.close_application()

    def up_arrow(self):
        self.comm_skt.send(b"move_up")

    def right_arrow(self):
        self.comm_skt.send(b"move_right")

    def left_arrow(self):
        self.comm_skt.send(b"move_left")

    def down_arrow(self):
        self.comm_skt.send(b"move_down")

    def get_infos(self):
        self.comm_skt.send(b"get_infos")
        data = self.comm_skt.recv(1024)
        data = data.decode('utf-8')
        data = data.split(',')
        battery = data[1]
        # update le label d'infos
        cam = self.hosts[self.active_camera]
        self.info.setText(" Informations\n Nom de la camera: Camera " + str(cam[1] + 1) +
                          "\n Adresse IP: " + str(cam[0]) +
                          "\n Batterie restante: " + battery)

    def remove(self):
        if not self.active_preview:
            if len(self.hosts) > 1:
                camera = self.hosts[self.active_camera]
                num = camera[1]
                ip = camera[0]
                self.hosts.remove((ip, num))
                self.camera_combo_box.clear()
                for i in range(len(self.hosts)):
                    self.camera_combo_box.addItem("Camera " + str(i + 1))
                    ip = self.hosts[i][0]
                    num = i
                    self.hosts[i] = (ip, num)
                self.active_camera = self.hosts[0][1]

                # on vient fermer les connexions en cours et on les redémarrent avec la bonne caméra
                self.camera_skt.send(b"")
                self.camera_skt.shutdown(socket.SHUT_RDWR)
                self.camera_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.camera_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.camera_skt.connect((str(self.hosts[self.active_camera][0]), self.CAMERA_PORT_PORT))
                self.comm_skt.send(b"")
                self.comm_skt.shutdown(socket.SHUT_RDWR)
                self.comm_skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.comm_skt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.comm_skt.connect((str(self.hosts[self.active_camera][0]), self.COMM_PORT))
                self.get_infos()

                # stopper le process pour aller chercher l'info de la caméra et restarter avec la nouvelle caméra
                self.info_process.terminate()
                self.info_process = Process(target=functions.get_info_process,
                                            args=(self.comm_skt, self.hosts[self.active_camera], self.COMM_PORT, self.info_queue,))
                self.info_process.start()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setText("Please stop preview before removing a camera from the network.")
            msg.setWindowTitle("Remove error")
            msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.path)))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


# classe pour la fenêtre de menu pour gérer les fichiers
class FileWindow(QtWidgets.QWidget):

    # constructeur de la classe
    def __init__(self, camera, skt, host, port, hosts, local_path):
        super(FileWindow, self).__init__()
        self.camera = camera
        self.skt = skt
        self.host = host
        self.port = port
        self.hosts = hosts
        self.local_path = local_path
        self.setFixedHeight(600)
        self.setFixedWidth(1000)
        self.setWindowTitle("Manage Files")
        self.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.local_path)))

        # déclaration de la variable pour garder la valeur du fichier sélectionné
        self.selected_files = []

        # déclaration de la variable pour garder les boutons
        self.button_list = []

        # déclaration des différents composants de l'interface graphique
        self.quit_button = QtWidgets.QPushButton("Quit", self)
        self.refresh_button = QtWidgets.QPushButton("Refresh", self)
        self.download_button = QtWidgets.QPushButton("Download", self)
        self.download_all_button = QtWidgets.QPushButton("Download All", self)
        self.delete_button = QtWidgets.QPushButton("Delete", self)
        self.delete_all_button = QtWidgets.QPushButton("Delete All", self)
        self.path = QtWidgets.QLabel(self)
        self.file_label = QtWidgets.QLabel(self)
        self.selected_file_label = QtWidgets.QLabel(self)

        # on va regarder les fichiers de la caméra
        # files = self.refresh()
        self.refresh()

        self.create_ui()

    # création de l'interface
    def create_ui(self):
        self.selected_file_label.move(10, 30)
        self.selected_file_label.resize(700, 20)
        self.selected_file_label.setText("Selected file(s): ")

        self.file_label.move(10, 60)
        self.file_label.resize(40, 20)
        self.file_label.setText("Files: ")

        self.refresh_button.resize(120, 60)
        self.refresh_button.move(40, 530)
        self.refresh_button.clicked.connect(self.refresh)

        self.download_button.resize(120, 60)
        self.download_button.move(200, 530)
        self.download_button.clicked.connect(self.download)

        self.download_all_button.resize(120, 60)
        self.download_all_button.move(360, 530)
        self.download_all_button.clicked.connect(self.download_all)

        self.delete_button.resize(120, 60)
        self.delete_button.move(520, 530)
        self.delete_button.clicked.connect(self.delete)

        self.delete_all_button.resize(120, 60)
        self.delete_all_button.move(680, 530)
        self.delete_all_button.clicked.connect(self.delete_all)

        self.quit_button.resize(120, 60)
        self.quit_button.move(840, 530)
        self.quit_button.clicked.connect(self.quit)

        self.path.resize(600, 20)
        self.path.move(10, 0)
        self.path.setText("Directory in camera " + str(self.camera + 1) + ": /home/pi/recordings/")

    def select_file(self):
        clicked_button = self.sender()
        name = clicked_button.objectName()

        # on regarde si le nom est déjà dans la liste
        if name not in self.selected_files:
            self.selected_files.append(name)
        else:
            self.selected_files.remove(name)

        # on met à jour la liste des nom de fichier
        files = ""
        for i in range(len(self.selected_files)):
            files = files + self.selected_files[i] + ", "
        self.selected_file_label.setText("Selected file(s): " + files)

    def quit(self):
        self.close()

    def refresh(self):
        for i in range(len(self.button_list)):
            self.button_list[i].deleteLater()
        self.button_list = []
        self.skt.send(b"refresh_files")
        data = self.skt.recv(1024)
        data = data.decode('utf-8')
        if data != "none,":
            data = data.split("\n")
            for i in range(len(data) - 1):  # -1 pour éviter le dernier string vide de split
                self.button_list.append(QtWidgets.QPushButton(data[i], self))
                self.button_list[i].setObjectName(data[i])
                self.button_list[i].move(30, 40 + 20 * (i + 2))
                self.button_list[i].resize(960, 20)
                self.button_list[i].released.connect(self.select_file)
                self.button_list[i].show()
        self.selected_files = []
        self.selected_file_label.setText("Selected file: ")

    def download(self):
        if not self.selected_files:
            msg = QtWidgets.QMessageBox()
            msg.setText("Please select a file before downloading.")
            msg.setWindowTitle("Download error")
            msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.local_path)))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            files = ""
            for i in range(len(self.selected_files)):
                files = files + self.selected_files[i] + ","
            self.skt.send(b"download_file_" + files.encode('utf-8'))

        msg = QtWidgets.QMessageBox()
        msg.setText("All selected file(s) have been downloaded!")
        msg.setWindowTitle("Download message")
        msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.local_path)))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def download_all(self):
        if len(self.hosts) == 1:
            self.skt.send(b"download_all")
        else:
            for i in range(len(self.hosts)):
                if i == 0:
                    self.skt.send(b"download_all")
                else:
                    ip = self.hosts[i][0]
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.connect((ip, self.port))
                    s.send(b"download_all")
                    s.send(b"")
                    s.shutdown(socket.SHUT_RDWR)

        msg = QtWidgets.QMessageBox()
        msg.setText("All files have been downloaded.")
        msg.setWindowTitle("Download message")
        msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.local_path)))
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def delete(self):
        if not self.selected_files:
            msg = QtWidgets.QMessageBox()
            msg.setText("Please select a file before deleting.")
            msg.setWindowTitle("Delete error")
            msg.setWindowIcon(QtGui.QIcon("{}/ressource/protolabLogo.png".format(self.local_path)))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            files = ""
            for i in range(len(self.selected_files)):
                files = files + self.selected_files[i] + ","
            self.skt.send(b"delete_file_" + files.encode('utf-8'))
            self.refresh()

    def delete_all(self):
        if len(self.hosts) == 1:
            self.skt.send(b"delete_all")
        else:
            for i in range(len(self.hosts)):
                if i != 0:
                    self.skt.send(b"delete_all")
                else:
                    ip = self.hosts[i][0]
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.connect((ip, self.port))
                    self.skt.send(b"delete_all")
                    s.send(b"")
                    s.shutdown(socket.SHUT_RDWR)

        self.refresh()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    gui = Window()
    gui.create_ui()
    gui.show()
    sys.exit(app.exec_())
