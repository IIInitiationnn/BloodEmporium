from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QPushButton, QInputDialog, QDialog, QProgressBar

from frontend.generic import Icons

class Dialog(QDialog):
    def __init__(self, title, object_name):
        super().__init__()
        self.setObjectName(object_name)
        self.setWindowIcon(QIcon(Icons.icon))

        # TODO stylise like main window
        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(300, 200)
        self.setWindowTitle(title)

class UpdateDialog(QMessageBox, Dialog):
    def __init__(self, old_version, new_version):
        super().__init__(f"Update {new_version} available", "updateDialog")
        self.setText(f"A new version of Blood Emporium ({new_version}) is available.\n"
                     f"You are currently using version {old_version}.\n\nInstall now?")

        self.addButton(QPushButton("Install"), QMessageBox.AcceptRole)
        self.addButton(QPushButton("Not Now"), QMessageBox.RejectRole)

# https://stackoverflow.com/questions/19917232/how-to-subclass-qmessagebox-and-add-a-progress-bar-in-pyside
class UpdatingDialog(QMessageBox, Dialog):
    def __init__(self, new_version):
        super().__init__(f"Downloading installer for {new_version}", "updatingDialog")
        self.progressBar = QProgressBar(self)
        self.progressBar.setFixedSize(300, 15)
        layout = self.layout()
        layout.addWidget(self.progressBar, 0, 0, 1, layout.columnCount(), Qt.AlignHCenter)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)

        self.addButton(QPushButton("Cancel"), QMessageBox.AcceptRole)

    def setProgress(self, progress):
        self.progressBar.setValue(progress)

class ConfirmDialog(QMessageBox, Dialog):
    def __init__(self, text, accept_text="Confirm", reject_text="Cancel"):
        super().__init__("Confirm", "confirmDialog")
        self.setText(text)
        self.addButton(QPushButton(accept_text), QMessageBox.AcceptRole)
        self.addButton(QPushButton(reject_text), QMessageBox.RejectRole)

class InputDialog(QInputDialog, Dialog):
    def __init__(self, title, label_text, input_mode, ok_button_text):
        super().__init__(title, "inputDialog")
        self.setLabelText(label_text)
        self.setInputMode(input_mode)
        self.setOkButtonText(ok_button_text)

'''class PromptWindow(QMainWindow):
    def __init__(self, parent, title, object_name):
        super().__init__(parent)

        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(300, 200)
        self.setWindowTitle(title)

        self.centralWidget = QWidget(self)
        self.centralWidget.setObjectName(f"{object_name}CentralWidget")
        self.centralWidget.setAutoFillBackground(False)
        self.setCentralWidget(self.centralWidget)

        # TODO fix background
        # TODO add top bar
        # TODO maybe swap to message popup
        self.background = QFrame(self.centralWidget)
        self.background.setObjectName(f"{object_name}Background")
        self.background.setStyleSheet(f"""
            QFrame#{object_name}Background {{
                background-color: {StyleSheets.passive};
                border-width: 1;
                border-style: solid;
                border-color: rgb(58, 64, 76);
            }}""")
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 200))
        self.background.setGraphicsEffect(self.shadow)

    def add_button(self, name, dimensions, on_click):
        pass # TODO'''