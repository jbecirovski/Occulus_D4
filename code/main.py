import sys
import socket
from code.other.functions import get_wifi_ip_address
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox


class Window(QtWidgets.QMainWindow):

    # paramètre de la classe
    activeCamera = ""

    # contructeur de la classe
    def __init__(self):
        super(Window, self).__init__()
        self.setFixedHeight(800)
        self.setFixedWidth(1200)
        self.setWindowTitle("Application Camera")
        self.setWindowIcon(QtGui.QIcon(r"ressource/protolabLogo.png"))

        # initialisation du port de communication
        localIP = get_wifi_ip_address()

        # initialisation des variables constantes
        # TODO à changer pour faire un scan de toutes les caméras existantes au lancement
        HOSTS = ['192.168.50.160', '192.168.50.161']
        PORT = 60000

        # création du socket de communication (BLOCKING for now)
        # TODO voir si on doit le garder en blocking si plusieurs cameras ou envoi des images
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # TODO À voir si ça affecte les performances lors de l'envoi de gros fichiers (images)
        # bind un port pour que l'hôte utilise toujours le même port(éviter création trop ports différents)
        skt.bind((localIP, 61515))

        # mise de la caméra active à la valeur par défaut de l'application
        Window.activeCamera = "Camera 1"

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
        self.btn_left_arrow = QtWidgets.QToolButton(self)
        self.btn_right_arrow = QtWidgets.QToolButton(self)
        self.btn_down_arrow = QtWidgets.QToolButton(self)
        self.info = QtWidgets.QLabel(self)
        self.preview = QtWidgets.QLabel(self)
        self.statusBar()
        self.main_menu = self.menuBar()
        self.palette = QtGui.QPalette()

    # création de l'interface
    def create_ui(self):
        self.btn_quit.clicked.connect(self.close_application)
        self.btn_quit.resize(200, 100)
        self.btn_quit.move(980, 680)

        self.camera_combo_box.addItem("Camera 1")
        self.camera_combo_box.addItem("Camera 2")
        self.camera_combo_box.addItem("Camera 3")
        self.camera_combo_box.setCurrentText("Camera 1")
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

        self.btn_left_arrow.setArrowType(QtCore.Qt.LeftArrow)
        self.btn_left_arrow.setGeometry(1005, 550, 30, 30)
        self.btn_left_arrow.clicked.connect(self.left_arrow)

        self.btn_right_arrow.setArrowType(QtCore.Qt.RightArrow)
        self.btn_right_arrow.setGeometry(1115, 550, 30, 30)
        self.btn_right_arrow.clicked.connect(self.right_arrow)

        self.btn_down_arrow.setArrowType(QtCore.Qt.DownArrow)
        self.btn_down_arrow.setGeometry(1060, 600, 30, 30)
        self.btn_down_arrow.clicked.connect(self.down_arrow)

        self.info.setText(" Informations:\n Nom de la camera:\n Batterie restante:")
        self.info.setStyleSheet("border: 2px solid grey;")
        self.info.resize(200, 100)
        self.info.move(950, 50)

        self.preview.move(200, 100)
        self.preview.resize(700, 600)
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setPixmap(QtGui.QPixmap(r"ressource/protolabLogo.png"))
        self.preview.setStyleSheet("border: 2px solid grey;")

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))

        extract_action = QtWidgets.QAction("Setting", self)
        extract_action.setShortcut("Ctrl+X")
        extract_action.triggered.connect(self.close_application)
        extract_action1 = QtWidgets.QAction("Style", self)
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

    # méthodes de classe
    def choose_camera(self):
        print(Window.activeCamera)
        Window.activeCamera = self.camera_combo_box.currentText()
        print(Window.activeCamera)
        pass

    def start_camera(self):
        print("Record debuter d'une camera")
        pass

    def detect_cameras(self):
        print("Detection des cameras")
        pass

    def stop_camera(self):
        print("Arret de l'enregistrement")
        pass

    def start_cameras(self):
        print("Record debuter de toute les cameras")
        pass

    def manage_files(self):
        print("Managing files")
        pass

    def stop_cameras(self):
        print("Arret du record de toute les cameras")
        pass

    def close_application(self):
        choice = QtWidgets.QMessageBox.question(self,
                                                "Extract!",
                                                "Are you sure you want to quit",
                                                QtWidgets.QMessageBox.Yes |
                                                QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def close_event(self, event):
        event.ignore()
        self.close_application()

    def up_arrow(self):
        print("Up")
        pass

    def right_arrow(self):
        print("Right")
        pass

    def left_arrow(self):
        print("Left")
        pass

    def down_arrow(self):
        print("Down")
        pass

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
