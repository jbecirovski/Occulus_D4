import locale
import socket
import sys
import queue
import threading
import time
import ctypes

import src.other.functions

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox


class Window(QtWidgets.QMainWindow):

    # contructeur de la classe
    def __init__(self):
        super(Window, self).__init__()
        self.setFixedHeight(800)
        self.setFixedWidth(1200)
        self.setWindowTitle("Application Camera")
        self.setWindowIcon(QtGui.QIcon(r"ressource/protolabLogo.png"))

        # paramètre de la classe
        self.active_camera = 0

        # détermine la langue de l'OS (change quelque chose pour les commandes bash)
        windll = ctypes.windll.kernel32
        lang = locale.windows_locale[windll.GetUserDefaultUILanguage()].split('_')[0]
        if lang == 'fr':
            self.osLanguage = 'fr'
        else:
            self.osLanguage = 'en'

        # initialisation du port de communication
        self.localIP = src.other.functions.get_wifi_ip_address()

        # initialisation des variables constantes
        self.HOSTS = []
        self.PORT = 60000

        # initialisation de la variable pour l'envoi de preview
        self.active_preview = False

        # création du socket de communication (BLOCKING for now)
        # TODO voir si on doit le garder en blocking si plusieurs cameras ou envoi des images
        self.skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # TODO À voir si ça affecte les performances lors de l'envoi de gros fichiers (images)
        # bind un port pour que l'hôte utilise toujours le même port(éviter création trop ports différents)
        self.skt.bind((self.localIP, 61515))

        # déclaration des différents composants de l'interface graphique
        self.btn_quit = QtWidgets.QPushButton("Quit", self)
        self.camera_combo_box = QtWidgets.QComboBox(self)
        self.btn_detect_cameras = QtWidgets.QPushButton("Detect Cameras", self)
        self.btn_start_camera = QtWidgets.QPushButton("Start Camera", self)
        self.btn_stop_camera = QtWidgets.QPushButton("Stop Camera", self)
        self.btn_start_all_camera = QtWidgets.QPushButton("Start All Camera", self)
        self.btn_manage_files = QtWidgets.QPushButton("Manage Files", self)
        self.btn_stop_all_camera = QtWidgets.QPushButton("Stop All Camera", self)
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

        # déclaration des threads pour faire du pooling
        self.infoThread = threading.Thread()
        self.previewThread = threading.Thread()

        # détecte les caméras qui sont sur le network au start
        while len(self.HOSTS) == 0:
            self.detect_cameras()
            if len(self.HOSTS) == 0:
                print("No camera was detected. Trying again!")

        # va chercher les infos de la caméra par défaut
        self.get_infos()

    # création de l'interface
    def create_ui(self):
        self.btn_quit.clicked.connect(self.close_application)
        self.btn_quit.resize(200, 100)
        self.btn_quit.move(980, 680)

        self.camera_combo_box.move(20, 50)
        self.camera_combo_box.activated.connect(self.choose_camera)

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
        self.btn_up_arrow.setGeometry(1060, 500, 30, 30)
        self.btn_up_arrow.clicked.connect(self.up_arrow)
        self.moveup_key.activated.connect(self.up_arrow)

        self.btn_left_arrow.setArrowType(QtCore.Qt.LeftArrow)
        self.btn_left_arrow.setGeometry(1005, 550, 30, 30)
        self.btn_left_arrow.clicked.connect(self.left_arrow)
        self.moveleft_key.activated.connect(self.left_arrow)

        self.btn_right_arrow.setArrowType(QtCore.Qt.RightArrow)
        self.btn_right_arrow.setGeometry(1115, 550, 30, 30)
        self.btn_right_arrow.clicked.connect(self.right_arrow)
        self.moveright_key.activated.connect(self.right_arrow)

        self.btn_down_arrow.setArrowType(QtCore.Qt.DownArrow)
        self.btn_down_arrow.setGeometry(1060, 600, 30, 30)
        self.btn_down_arrow.clicked.connect(self.down_arrow)
        self.movedown_key.activated.connect(self.down_arrow)

        self.info.setStyleSheet("border: 2px solid grey;")
        self.info.resize(200, 100)
        self.info.move(950, 50)

        self.preview.move(200, 100)
        self.preview.resize(700, 600)
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setPixmap(QtGui.QPixmap(r"ressource/protolabLogo.png"))
        self.preview.setStyleSheet("border: 2px solid grey;")

        self.preview_button.setText("Start preview")
        self.preview_button.move(490, 720)
        self.preview_button.resize(120, 60)
        self.preview_button.clicked.connect(self.start_stop_preview)

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

        extract_action = QtWidgets.QAction("Setting", self)
        extract_action.setShortcut("Ctrl+X")
        extract_action.triggered.connect(self.close_application)
        extract_action1 = QtWidgets.QAction("Style", self)
        extract_action1.setShortcut("Ctrl+M")
        extract_action1.triggered.connect(self.style_pop_up)

        file_menu = self.main_menu.addMenu('&File')
        file_menu.addAction(extract_action)
        file_menu = self.main_menu.addMenu('&Edit')
        file_menu.addAction(extract_action1)

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

        # créer le thread pour aller chercher les infos de la camera active
        self.infoThread = threading.Thread(target=src.other.functions.get_infos_thread,
                        args=(self.skt, self.HOSTS[self.active_camera], self.PORT, self.info),
                        daemon=True).start()

    # méthodes de classe
    def start_stop_preview(self):
        if self.active_preview:
            self.active_preview = False
            self.preview_button.setText("Start preview")
            print("Stop preview")
            # stop le thread pour aller pooler les images de preview
            self.previewThread.join()
        else:
            self.active_preview = True
            self.preview_button.setText("Stop preview")
            print("Start preview")
            # start le thread pour aller pooler les images de preview
            self.previewThread = threading.Thread(target=src.other.functions.get_preview,
                                args=(self.skt, self.HOSTS[self.active_camera], self.PORT, self.preview,),
                                daemon=True).start()

    def choose_camera(self):
        new_active_camera = self.camera_combo_box.currentIndex()
        if new_active_camera != self.active_camera:
            self.active_camera = new_active_camera
            print("Camera " + str(self.active_camera + 1) + " active")
            self.get_infos()
            # restarter le thread pour pooler l'info de la caméra et restarter avec la nouvelle caméra
            self.infoThread.join()
            self.infoThread = threading.Thread(target=src.other.functions.get_infos_thread,
                                               args=(self.skt, self.HOSTS[new_active_camera], self.PORT, self.info,),
                                               daemon=True).start()
        else:
            pass

    def start_camera(self):
        """ip = self.HOSTS[self.active_camera][0]
        self.skt.connect((ip, self.PORT))
        self.skt.send(b"start_camera")
        data = self.skt.recv(1024)
        data = data.decode('utf-8')
        print(data)"""
        print("Starting camera: " + str(self.active_camera + 1))

    # TODO À changer avec range d'adresse des caméras
    def detect_cameras(self):
        print("Detect cameras!")
        localIP = self.localIP.split('.')
        network = localIP[0] + '.' + localIP[1] + '.' + localIP[2] + '.'
        size = 20
        num_of_threads = 20
        jobs = queue.Queue()
        results = queue.Queue()
        text_results = []

        for i in range(0, size + 1):
            jobs.put(network + str(i))

        if self.osLanguage == 'fr':
            for i in range(num_of_threads):
                thread = threading.Thread(target=src.other.functions.sweep_network_fr,
                                          args=(jobs, results), daemon=True)
                thread.start()
        else:
            for i in range(num_of_threads):
                thread = threading.Thread(target=src.other.functions.sweep_network, args=(jobs, results), daemon=True)
                thread.start()

        t1 = time.time()
        jobs.join()
        t2 = time.time()
        print(t2 - t1)

        count = 0
        while not results.empty():
            result = results.get()
            text_results.append((result, count))
            count += 1

        # classer en ordre croissant
        text_results.sort()

        # on regarde si le nombre de caméra créé est le même
        if len(text_results) != len(self.HOSTS):
            self.HOSTS = text_results
            self.camera_combo_box.clear()
            for i in range(len(text_results)):
                self.camera_combo_box.addItem("Camera " + str(i + 1))
        return text_results

    def stop_camera(self):
        """ip = self.HOSTS[self.active_camera][0]
        self.skt.connect((ip, self.PORT))
        self.skt.send(b"stop_camera")
        data = self.skt.recv(1024)
        data = data.decode('utf-8')
        print(data)"""
        print("Stopping camera: " + str(self.active_camera + 1))

    def start_cameras(self):
        """for i in range(len(self.HOSTS)):
            ip = self.HOSTS[i][0]
            self.skt.connect((ip, self.PORT))
            self.skt.send(b"start_camera")
            data = self.skt.recv(1024)
            data = data.decode('utf-8')
            print(data)"""
        print("Start cameras!")

    def stop_cameras(self):
        """for i in range(len(self.HOSTS)):
            ip = self.HOSTS[i][0]
            self.skt.connect((ip, self.PORT))
            self.skt.send(b"stop_camera")
            data = self.skt.recv(1024)
            data = data.decode('utf-8')
            print(data)"""
        print("Stop cameras!")

    def manage_files(self):
        print("Managing files")

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self, "Extract!", "Are you sure you want to quit",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            src.other.functions.close_port(self.skt)
            sys.exit()
        else:
            pass

    def close_event(self, event):
        event.ignore()
        self.close_application()

    def up_arrow(self):
        """ip = self.HOSTS[self.active_camera][0]
        self.skt.connect((ip, self.PORT))
        self.skt.send(b"move_up")
        data = self.skt.recv(1024)
        data = data.decode('utf-8')
        print(data)"""
        print("up")

    def right_arrow(self):
        """ip = self.HOSTS[self.active_camera][0]
        self.skt.connect((ip, self.PORT))
        self.skt.send(b"move_right")
        data = self.skt.recv(1024)
        data = data.decode('utf-8')
        print(data)"""
        print("right")

    def left_arrow(self):
        """ip = self.HOSTS[self.active_camera][0]
        self.skt.connect((ip, self.PORT))
        self.skt.send(b"move_left")
        data = self.skt.recv(1024)
        data = data.decode('utf-8')
        print(data)"""
        print("left")

    def down_arrow(self):
        """ip = self.HOSTS[self.active_camera][0]
        self.skt.connect((ip, self.PORT))
        self.skt.send(b"move_down")
        data = self.skt.recv(1024)
        data = data.decode('utf-8')
        print(data)"""
        print("down")

    def get_infos(self):
        """ip = self.HOSTS[self.active_camera][0]
        self.skt.connect((ip, self.PORT))
        self.skt.send(b"get_infos")
        data = self.skt.recv(1024)
        data = data.decode('utf-8')
        print(data)"""
        data = "100%"
        print("getting infos from camera: " + str(self.active_camera + 1) + "!")
        # update le label d'infos
        cam = self.HOSTS[self.active_camera]
        self.info.setText(" Informations\n Nom de la camera: " + str(cam[1] + 1) +
                          "\n Adresse IP: " + str(cam[0]) +
                          "\n Batterie restante: " + str(data))

    def style_pop_up(self):
        msg = QMessageBox()
        msg.setWindowTitle("Style choice")
        msg.setWindowIcon(QtGui.QIcon("ressource/protolabLogo.png"))
        msg.setText("Choose the window style")
        msg.setStandardButtons(QMessageBox.Apply | QMessageBox.Cancel)
        x = msg.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    gui = Window()
    gui.create_ui()
    gui.show()
    sys.exit(app.exec_())
