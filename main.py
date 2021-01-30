import sys
import socket
import other.functions
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        self.setFixedHeight(800)
        self.setFixedWidth(1200)
        self.setWindowTitle("Application Camera")
        self.setWindowIcon(QtGui.QIcon("ressource/protolabLogo.png"))

        # initialisation du port de communication
        localIP = other.functions.get_wifi_ip_address()

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

        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
        extract_action = QtWidgets.QAction("Setting", self)
        extract_action.setShortcut("Ctrl+X")
        extract_action.triggered.connect(self.fermetureApplication)
        extract_action1 = QtWidgets.QAction("Style", self)
        extract_action1.triggered.connect(self.style_pop_up)

        self.statusBar()
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('&File')
        file_menu.addAction(extract_action)
        file_menu = main_menu.addMenu('&Edit')
        file_menu.addAction(extract_action1)

        # Édition du style de la fenêtre
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.darkGray)
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.darkGray)
        palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.darkRed)
        QtWidgets.qApp.setPalette(palette)

        self.home()

    def home(self):
        btn_quit = QtWidgets.QPushButton("Quit", self)
        btn_quit.clicked.connect(self.fermetureApplication)
        btn_quit.resize(200, 100)
        btn_quit.move(980, 680)

        camera_combo_box = QtWidgets.QComboBox(self)
        camera_combo_box.addItem("Camera 1")
        camera_combo_box.addItem("Camera 2")
        camera_combo_box.addItem("Camera 3")
        camera_combo_box.move(20, 50)
        camera_combo_box.activated.connect(self.choose_camera_combo_box)

        btn_detect_cameras = QtWidgets.QPushButton("Detect Cameras", self)
        btn_detect_cameras.clicked.connect(self.btn_detect_cameras)
        btn_detect_cameras.resize(100, 40)
        btn_detect_cameras.move(20, 100)

        btn_start_camera = QtWidgets.QPushButton("Start Camera", self)
        btn_start_camera.clicked.connect(self.btn_start_camera)
        btn_start_camera.resize(100, 40)
        btn_start_camera.move(20, 150)

        btn_stop_camera = QtWidgets.QPushButton("Stop Camera", self)
        btn_stop_camera.clicked.connect(self.btn_stop_camera)
        btn_stop_camera.resize(100, 40)
        btn_stop_camera.move(20, 200)

        btn_start_all_camera = QtWidgets.QPushButton("Start All Camera", self)
        btn_start_all_camera.clicked.connect(self.startAllCamera)
        btn_start_all_camera.resize(120, 60)
        btn_start_all_camera.move(20, 645)

        btn_manage_files = QtWidgets.QPushButton("Manage Files", self)
        btn_manage_files.clicked.connect(self.manage_files)
        btn_manage_files.resize(120, 60)
        btn_manage_files.move(20, 570)

        btn_stop_all_camera = QtWidgets.QPushButton("Stop All Camera", self)
        btn_stop_all_camera.clicked.connect(self.stopAllCamera)
        btn_stop_all_camera.resize(120, 60)
        btn_stop_all_camera.move(20, 720)

        btn_up_arrow = QtWidgets.QToolButton(self)
        btn_up_arrow.setArrowType(QtCore.Qt.UpArrow)
        btn_up_arrow.setGeometry(1060, 500, 30, 30)
        btn_up_arrow.clicked.connect(self.btn_up_arrow)

        btn_left_arrow = QtWidgets.QToolButton(self)
        btn_left_arrow.setArrowType(QtCore.Qt.LeftArrow)
        btn_left_arrow.setGeometry(1005, 550, 30, 30)
        btn_left_arrow.clicked.connect(self.btn_left_arrow)

        btn_right_arrow = QtWidgets.QToolButton(self)
        btn_right_arrow.setArrowType(QtCore.Qt.RightArrow)
        btn_right_arrow.setGeometry(1115, 550, 30, 30)
        btn_right_arrow.clicked.connect(self.btn_right_arrow)

        btn_down_arrow = QtWidgets.QToolButton(self)
        btn_down_arrow.setArrowType(QtCore.Qt.DownArrow)
        btn_down_arrow.setGeometry(1060, 600, 30, 30)
        btn_down_arrow.clicked.connect(self.btn_down_arrow)

        info = QtWidgets.QLabel(self)
        info.setText(" Info\n Nom de la camera:\n Batterie restante:")
        info.setStyleSheet("border: 2px solid grey;")
        info.resize(200, 100)
        info.move(950, 50)

        preview = QtWidgets.QLabel(self)
        preview.move(200, 100)
        preview.resize(700, 600)
        preview.setAlignment(QtCore.Qt.AlignCenter)
        preview.setPixmap(QtGui.QPixmap("ressource/protolabLogo.png"))
        preview.setStyleSheet("border: 2px solid grey;")

        self.show()

    def choose_camera_combo_box(self):
        print("hey")
        pass

    def btn_start_camera(self):
        print("Record debuter d'une camera")
        pass

    def btn_detect_cameras(self):
        print("Detection des cameras")
        pass

    def btn_stop_camera(self):
        print("Arret de l'enregistrement")
        pass

    def startAllCamera(self):
        print("Record debuter de toute les cameras")
        pass

    def manage_files(self):
        print("Managing files")
        pass

    def stopAllCamera(self):
        print("Arret du record de toute les cameras")
        pass

    def fermetureApplication(self):
        choice = QtWidgets.QMessageBox.question(self,
                                                "Extract!",
                                                "Are you sure you want to quit",
                                                QtWidgets.QMessageBox.Yes |
                                                QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def closeEvent(self, event):
        event.ignore()
        self.fermetureApplication()

    def btn_up_arrow(self):
        print("Up")
        pass

    def btn_right_arrow(self):
        print("Right")
        pass

    def btn_left_arrow(self):
        print("Left")
        pass

    def btn_down_arrow(self):
        print("down")
        pass

    def style_pop_up(self):
        msg = QMessageBox()
        msg.setWindowTitle("Style choice")
        msg.setWindowIcon(QtGui.QIcon("ressource/protolabLogo.png"))
        msg.setText("Choose the window style")
        msg.setStandardButtons(QMessageBox.Apply | QMessageBox.Cancel)
        x = msg.exec()


def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = Window()
    sys.exit(app.exec_())


main()
