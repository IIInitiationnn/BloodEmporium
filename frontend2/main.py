import os
import sys

from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QPixmap, QFont, QMouseEvent
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QFrame, QPushButton, QGridLayout, QVBoxLayout, \
    QHBoxLayout

from base import Ui_main

class Font(QFont):
    def __init__(self, font_size):
        QFont.__init__(self)
        self.setFamily("Segoe UI")
        self.setPointSize(font_size)

class TopBar(QFrame):
    style_sheet = '''
        QFrame {
            background-color: rgb(33, 37, 43);
        }'''

    def __init__(self, parent):
        QFrame.__init__(self, parent)
        self.setObjectName("topBar")
        self.setMinimumSize(QSize(300, 60))
        self.setStyleSheet(TopBar.style_sheet)

class TopBarButton(QPushButton):
    style_sheet = '''
        QPushButton {
            background-color: rgba(0, 0, 0, 0);
            border-radius: 5;
        }
        QPushButton:hover {
            background-color: rgb(40, 44, 52);
            border: none;
            border-radius: 5;
        }
        QPushButton:pressed {
            background-color: rgb(255, 121, 198);
            border: none;
            border-radius: 5;
        }'''

    def __init__(self, icon, parent, function, main, style_sheet=style_sheet):
        QPushButton.__init__(self, parent)
        self.setFixedSize(QSize(35, 35))

        self.setStyleSheet(style_sheet)

        # icon
        self.setIconSize(QSize(20, 20))
        self.setIcon(icon)

        self.setCheckable(True)
        self.clicked.connect(function)

class TitleBar(QWidget):
    def __init__(self, parent, on_double_click, on_drag):
        QWidget.__init__(self, parent)
        self.setObjectName("titleBar")
        self.onDoubleClick = on_double_click
        self.onDrag = on_drag
        # self.setStyleSheet('''
        #     background-color: rgb(40, 44, 52);
        #     border-width: 10;
        #     border-style: solid;
        #     border-color: rgb(0, 0, 0);
        # ''') # for debugging to see the region it occupies

    def mouseDoubleClickEvent(self, event):
        self.onDoubleClick()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        self.onDrag(event.globalPos() - self.dragPos)
        self.dragPos = event.globalPos()

class LeftMenuButton(QPushButton):
    style_sheet = '''
        QPushButton {
            background-color: rgba(0, 0, 0, 0);
        }
        QPushButton:hover {
            background-color: rgb(40, 44, 52);
            border: none;
        }
        QPushButton:pressed {
            background-color: rgb(189, 147, 249);
            border: none;
        }'''

    def __init__(self, icon, parent, style_sheet=style_sheet):
        QPushButton.__init__(self, parent)
        self.setMinimumSize(QSize(70, 60))
        self.setBaseSize(QSize(70, 60))
        self.setMaximumSize(QSize(250, 60))
        self.setStyleSheet(style_sheet)
        self.setIconSize(QSize(30, 30))
        self.setIcon(icon)

class ToggleButton(LeftMenuButton):
    def __init__(self, icon, parent, on_click):
        LeftMenuButton.__init__(self, icon, parent)
        self.clicked.connect(on_click)

class MainWindow(QMainWindow):
    def minimize(self):
        self.showMinimized()

    def restore(self):
        self.showNormal()
        self.is_maximized = False
        self.maximizeButton.setIcon(QIcon(Icons.maximize))
        self.centralLayout.setContentsMargins(10, 10, 10, 10)

    def maximize(self):
        self.showMaximized()
        self.is_maximized = True
        self.maximizeButton.setIcon(QIcon(Icons.restore))
        self.centralLayout.setContentsMargins(0, 0, 0, 0)

    def maximize_restore(self):
        if self.is_maximized:
            self.restore()
        else:
            self.maximize()

    def drag(self, dpos):
        self.restore()
        self.move(self.pos() + dpos) # TODO fix when dragging from maximized

    def animate(self):
        # TODO expand width
        animation = QPropertyAnimation(self.leftMenu, b"size")
        animation.setEasingCurve(QEasingCurve.InOutQuint)
        animation.setDuration(500)
        animation.setStartValue(QSize(70, 500) if self.leftMenu.width() == 250 else QSize(250, 500))
        animation.setEndValue(QSize(250, 500) if self.leftMenu.width() == 250 else QSize(70, 500))
        animation.start()

    def __init__(self):
        QMainWindow.__init__(self)

        self.is_maximized = False

        # self.ui = Ui_main()
        # self.ui.setupUi(self)
        # widgets = self.ui

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)


        self.resize(1000, 580)
        self.setMinimumSize(800, 500)

        # central widget
        self.centralWidget = QWidget(self)
        self.centralWidget.setObjectName("centralWidget")
        self.centralWidget.setAutoFillBackground(False)
        self.setCentralWidget(self.centralWidget)

        self.centralLayout = QGridLayout(self.centralWidget)
        self.centralLayout.setObjectName("centralLayout")
        self.centralLayout.setContentsMargins(10, 10, 10, 10)

        # background
        self.background = QFrame(self.centralWidget)
        self.background.setObjectName("background")
        self.background.setStyleSheet('''
            QFrame#background {
                background-color: rgb(40, 44, 52);
                border-width: 1;
                border-style: solid;
                border-color: rgb(58, 64, 76);
            }''')
        # TODO drop shadow

        self.backgroundLayout = QGridLayout(self.background)
        self.backgroundLayout.setObjectName("backgroundLayout")
        self.backgroundLayout.setContentsMargins(0, 0, 0, 0)
        self.backgroundLayout.setSpacing(0)

        # top bar
        self.topBar = TopBar(self.background)

        self.topBarLayout = QGridLayout(self.topBar)
        self.topBarLayout.setObjectName("topBarLayout")
        self.topBarLayout.setContentsMargins(5, 0, 10, 0)
        self.topBarLayout.setHorizontalSpacing(10)

        # icon
        self.icon = QLabel(self.topBar)
        self.icon.setFixedSize(QSize(60, 60))
        self.icon.setPixmap(QPixmap(os.getcwd() + "/images/inspo1.png"))
        self.icon.setScaledContents(True)
        self.icon.setObjectName("icon")

        # title bar
        self.titleBar = TitleBar(self.topBar, self.maximize_restore, self.drag)

        self.titleBarLayout = QGridLayout(self.titleBar)
        self.titleBarLayout.setObjectName("titleBarLayout")
        self.titleBarLayout.setContentsMargins(0, 0, 0, 0)
        self.titleBarLayout.setSpacing(0)

        # title label
        self.titleLabel = QLabel(self.titleBar)
        self.titleLabel.setObjectName("titleLabel")
        self.titleLabel.setText("Blood Emporium")
        self.titleLabel.setFont(Font(10))
        self.titleLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.titleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # window buttons
        self.windowButtons = QWidget(self.topBar)
        self.windowButtons.setObjectName("windowButtons")
        self.windowButtons.setFixedSize(QSize(105, 60))

        self.windowButtonsLayout = QGridLayout(self.windowButtons)
        self.windowButtonsLayout.setObjectName("windowButtonsLayout")
        self.windowButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.windowButtonsLayout.setSpacing(0)

        self.minimizeButton = TopBarButton(QIcon(Icons.minimize), self.windowButtons, self.minimize, self)
        self.minimizeButton.setObjectName("minimizeButton")

        maximize_icon = QIcon(Icons.restore) if self.is_maximized else QIcon(Icons.maximize)
        self.maximizeButton = TopBarButton(maximize_icon, self.windowButtons, self.maximize_restore, self)
        self.maximizeButton.setObjectName("maximizeButton")
        self.closeButton = TopBarButton(QIcon(Icons.close), self.windowButtons, self.close, self)
        self.closeButton.setObjectName("closeButton")

        # content
        self.content = QFrame(self.background)
        self.content.setObjectName("content")
        # self.content.setStyleSheet('''
        #     QFrame#content {
        #         background-color: rgb(40, 44, 52);
        #         border-width: 10;
        #         border-style: solid;
        #         border-color: rgb(0, 0, 0);
        #     }
        # ''') # for debugging to see the region it occupies

        self.contentLayout = QGridLayout(self.content)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)

        # left menu
        self.leftMenu = QFrame(self.content)
        self.leftMenu.setObjectName("leftMenu")
        self.leftMenu.setBaseSize(QSize(70, 60))
        self.leftMenu.setStyleSheet('''
            QFrame#leftMenu {
                background-color: rgb(33, 37, 43);
            }''')

        self.leftMenuLayout = QVBoxLayout(self.leftMenu)
        self.leftMenuLayout.setObjectName("leftMenuLayout")
        self.leftMenuLayout.setContentsMargins(0, 0, 0, 25)
        self.leftMenuLayout.setSpacing(0)

        # menu column
        self.menuColumn = QFrame(self.leftMenu)
        self.menuColumn.setObjectName("menuColumn")

        self.menuColumnLayout = QVBoxLayout(self.menuColumn)
        self.menuColumnLayout.setObjectName("menuColumnLayout")
        self.menuColumnLayout.setContentsMargins(0, 0, 0, 0)
        self.menuColumnLayout.setSpacing(0)

        self.toggleButton = ToggleButton(QIcon(Icons.menu), self.leftMenu, self.animate)
        self.toggleButton.setObjectName("toggleButton")
        self.homeButton = LeftMenuButton(QIcon(Icons.home), self.leftMenu)
        self.homeButton.setObjectName("homeButton")
        self.preferencesButton = LeftMenuButton(QIcon(Icons.preferences), self.leftMenu)
        self.preferencesButton.setObjectName("preferencesButton")

        # settings button
        self.settingsButton = LeftMenuButton(QIcon(Icons.settings), self.menuColumn)
        self.settingsButton.setObjectName("settingsButton")

        # content pages
        self.contentPages = QFrame(self.content)
        self.contentPages.setObjectName("contentPages")
        # self.contentPages.setStyleSheet('''
        #     QFrame#contentPages {
        #         background-color: rgb(40, 44, 52);
        #         border-width: 5;
        #         border-style: solid;
        #         border-color: rgb(50, 50, 50);
        #     }
        # ''') # for debugging to see the region it occupies

        # bottom bar
        self.bottomBar = QFrame(self.content)
        self.bottomBar.setObjectName("bottomBar")
        self.bottomBar.setMinimumSize(QSize(0, 25))
        self.bottomBar.setStyleSheet('''
            QFrame#bottomBar {
                background-color: rgb(47, 52, 61);
            }''')

        self.bottomBarLayout = QHBoxLayout(self.bottomBar)
        self.bottomBarLayout.setObjectName("bottomBarLayout")
        self.bottomBarLayout.setContentsMargins(5, 0, 5, 0)

        # LAYOUTS

        '''
        central
            -> background
        '''

        self.centralLayout.addWidget(self.background)

        '''
        background
            -> topBar
            -> content
        '''
        self.backgroundLayout.addWidget(self.topBar, 0, 0, 1, 1)
        self.backgroundLayout.addWidget(self.content, 1, 0, 1, 1)
        self.backgroundLayout.setRowStretch(1, 1) # content fill out as much of background as possible

        '''
        topBar
           -> icon
           -> titleBar
           -> windowButtons
        '''
        self.topBarLayout.addWidget(self.icon, 0, 0, 1, 1, Qt.AlignVCenter)
        self.topBarLayout.addWidget(self.titleBar, 0, 1, 1, 1, Qt.AlignVCenter)
        self.topBarLayout.addWidget(self.windowButtons, 0, 2, 1, 1, Qt.AlignVCenter)

        '''
        titleBar
            -> titleLabel
        '''
        self.titleBarLayout.addWidget(self.titleLabel, 0, 0, 1, 1, Qt.AlignVCenter)

        '''
        windowButtons
            -> 3 buttons
        '''
        self.windowButtonsLayout.addWidget(self.minimizeButton, 0, 0, 1, 1, Qt.AlignVCenter)
        self.windowButtonsLayout.addWidget(self.maximizeButton, 0, 1, 1, 1, Qt.AlignVCenter)
        self.windowButtonsLayout.addWidget(self.closeButton, 0, 2, 1, 1, Qt.AlignVCenter)

        '''
        content
            -> leftMenu
            -> contentPage
            -> bottomBar
        '''
        self.contentLayout.addWidget(self.leftMenu, 0, 0, 2, 1)
        self.contentLayout.addWidget(self.contentPages, 0, 1, 1, 1)
        self.contentLayout.addWidget(self.bottomBar, 1, 1, 1, 1)
        self.contentLayout.setRowStretch(0, 1) # stretch contentPages down as much as possible (pushing down on bottomBar)
        self.contentLayout.setColumnStretch(1, 1) # stretch contentPages and bottomBar on the leftMenu


        '''
        leftMenu
            -> menuColumn
            -> settingsButton
        '''
        self.leftMenuLayout.addWidget(self.menuColumn, 0, Qt.AlignTop)
        self.leftMenuLayout.addWidget(self.settingsButton)

        '''
        menuColumn
            -> 3 buttons
        '''
        self.menuColumnLayout.addWidget(self.toggleButton)
        self.menuColumnLayout.addWidget(self.homeButton)
        self.menuColumnLayout.addWidget(self.preferencesButton)




        '''

        self.authorLabel = QtWidgets.QLabel(self.bottomBar)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.authorLabel.setFont(font)
        self.authorLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.authorLabel.setObjectName("authorLabel")
        self.bottomBarLayout.addWidget(self.authorLabel)
        self.versionLabel = QtWidgets.QLabel(self.bottomBar)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.versionLabel.setFont(font)
        self.versionLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.versionLabel.setObjectName("versionLabel")
        self.bottomBarLayout.addWidget(self.versionLabel)
        self.contentLayout.addWidget(self.bottomBar, 1, 1, 1, 1, QtCore.Qt.AlignRight|QtCore.Qt.AlignBottom)
)
        self.topBar = QtWidgets.QFrame(self.background)
        self.topBar.setMaximumSize(QtCore.QSize(16777215, 60))
        self.topBar.setStyleSheet("QFrame#topBar {\n"
"    background-color: rgb(33, 37, 43);\n"
"}")
        self.topBar.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.topBar.setFrameShadow(QtWidgets.QFrame.Raised)
        self.topBar.setObjectName("topBar")

        
        
        
        self.topBarLayout.addWidget(self.titleBar, 1, 1, 1, 1, QtCore.Qt.AlignLeft)

        self.backgroundLayout.addWidget(self.topBar, 0, 0, 1, 1)
        self.centralLayout.addWidget(self.background)
        main.setCentralWidget(self.centralWidget)

        self.retranslateUi(main)
        QtCore.QMetaObject.connectSlotsByName(main)







        '''



        self.show()

class Icons:
    __base = "images/icons"
    minimize = __base + "/icon_minimize.png"
    restore = __base + "/icon_restore.png"
    maximize = __base + "/icon_maximize.png"
    close = __base + "/icon_close.png"
    menu = __base + "/icon_menu.png"
    home = __base + "/icon_home.png"
    preferences = __base + "/icon_preferences.png"
    settings = __base + "/icon_settings.png"

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())