import atexit
import os
import subprocess
import sys
from io import BytesIO
from multiprocessing import freeze_support, Pipe
from threading import Thread
from zipfile import ZipFile

import requests
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QRect, QObject, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QFrame, QPushButton, QGridLayout, QVBoxLayout, \
    QGraphicsDropShadowEffect, QStackedWidget, QSizeGrip, QMessageBox, QSplashScreen
from parse import parse

from backend.util.timer import Timer
from dialogs import UpdateDialog
from frontend.generic import Font, TextLabel, HyperlinkTextLabel, TextInputBox, Icons
from frontend.layouts import RowLayout
from frontend.pages.bloodweb import BloodwebPage
from frontend.pages.help import HelpPage
from frontend.pages.preferences import PreferencesPage
from frontend.pages.settings import SettingsPage
from frontend.stylesheets import StyleSheets

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.state import State

# auto-update code courtesy of DAzVise#1666
def get_latest_update():
    resp = requests.get("https://api.github.com/repos/IIInitiationnn/BloodEmporium/releases/latest")

    if resp.status_code == 200:
        data = resp.json()
        old_version = State.version
        new_version = data["tag_name"]

        # compare version numbers MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-alpha.PRERELEASE
        # TODO could maybe put into a new class
        if "alpha" in old_version:
            old_maj, old_min, old_patch, old_prerelease = parse("v{:n}.{:n}.{:n}-alpha.{:n}", old_version)
        else:
            old_maj, old_min, old_patch = parse("v{:n}.{:n}.{:n}", old_version)
            old_prerelease = None
        new_maj, new_min, new_patch = parse("v{:n}.{:n}.{:n}", new_version)
        if old_maj < new_maj or \
                (old_maj == new_maj and old_min < new_min) or \
                (old_maj == new_maj and old_min == new_min and old_patch < new_patch) or \
                (old_maj == new_maj and old_min == new_min and old_patch == new_patch and old_prerelease is not None):
            return data

def install_update(update):
    download = requests.get(update["assets"][0]["browser_download_url"])
    zipped = ZipFile(BytesIO(download.content))

    os.rename(sys.argv[0], f"Blood Emporium Old ({State.version}).exe")
    # TODO maybe also get rid of old assets e.g. dusty noose went universal -> retired
    zipped.extractall(path=".")

def handle_updates():
    if os.path.isfile(f"Blood Emporium Old ({State.version}).exe"):
        os.remove(f"Blood Emporium Old ({State.version}).exe")

    if getattr(sys, "frozen", False):
        update = get_latest_update()

        if update is not None:
            install_update(update)
            subprocess.Popen("Blood Emporium.exe")
            sys.exit()

class TopBar(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("topBar")
        self.setMinimumSize(QSize(300, 60))
        self.setStyleSheet(f"QFrame#topBar {{background-color: {StyleSheets.background};}}")

class TopBarButton(QPushButton):
    def __init__(self, parent, object_name, icon, on_click, style_sheet=StyleSheets.top_bar_button):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setFixedSize(QSize(35, 35))
        self.setStyleSheet(style_sheet)

        # icon
        self.setIconSize(QSize(20, 20))
        self.setIcon(icon)

        self.clicked.connect(on_click)

class TitleBar(QWidget):
    def __init__(self, parent, on_double_click, on_drag):
        super().__init__(parent)
        self.setObjectName("titleBar")
        self.setMinimumHeight(60)
        self.onDoubleClick = on_double_click
        self.onDrag = on_drag

    def mouseDoubleClickEvent(self, event):
        self.onDoubleClick()

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        self.onDrag(event.globalPos() - self.dragPos)
        self.dragPos = event.globalPos()

class LeftMenuButton(QPushButton):
    min_width = 70
    max_width = 230

    padding = (max_width - min_width) / 2

    def __init__(self, parent, object_name, icon, main_window, is_active=False):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setMinimumSize(QSize(LeftMenuButton.max_width, 60))
        self.setMaximumSize(QSize(LeftMenuButton.max_width, 60))
        self.setIconSize(QSize(30, 30))
        self.setIcon(icon)

        self.main = main_window
        self.bar = None
        self.page = None

        self.is_active = is_active
        self.setStyleSheet(StyleSheets.left_menu_button(LeftMenuButton.padding, is_active))

        self.clicked.connect(self.on_click)

    def setBar(self, bar):
        self.bar = bar

    def setPage(self, page):
        self.page = page

    def activate(self):
        self.is_active = True
        self.setStyleSheet(StyleSheets.left_menu_button_active(LeftMenuButton.padding))
        self.bar.activate()
        self.main.stack.setCurrentWidget(self.page)

    def deactivate(self):
        self.is_active = False
        self.setStyleSheet(StyleSheets.left_menu_button_inactive(LeftMenuButton.padding))
        self.bar.deactivate()

    def on_click(self):
        if not self.is_active:
            for button in self.main.buttons:
                button.deactivate()
        self.activate()

class LeftMenuBar(QFrame):
    def __init__(self, parent, object_name, visible=False):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setFixedSize(3, 60)
        self.setStyleSheet(f"QFrame#{object_name} {{background-color: {StyleSheets.purple};}}")
        self.setVisible(visible)

    def activate(self):
        self.setVisible(True)

    def deactivate(self):
        self.setVisible(False)

class LeftMenuLabel(QLabel):
    def __init__(self, parent, object_name, text, style_sheet=StyleSheets.white_text):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setFont(Font(8))
        self.setFixedHeight(60)
        self.setText(text)
        self.setStyleSheet(style_sheet)
        self.move(self.geometry().topLeft() - parent.geometry().topLeft() + QPoint(80, 0))

class HomeRow(QWidget):
    def __init__(self, parent, object_number, icon, on_click, text):
        super().__init__(parent)
        self.setObjectName(f"homePageRow{object_number}")
        self.button = PageButton(self, f"homePageButton{object_number}", icon, on_click)
        self.label = TextLabel(self, f"homePageLabel{object_number}", text)

        self.layout = RowLayout(self, "homePageLayout", spacing=0)
        self.layout.addStretch(1)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)
        self.layout.addStretch(1)

class HelpRow(QWidget):
    def __init__(self, parent, object_name, icon_path, text):
        super().__init__(parent)
        self.setObjectName(object_name)

        self.icon = QLabel(self)
        self.icon.setObjectName(f"{object_name}Icon")
        self.icon.setFixedSize(QSize(60, 60))
        self.icon.setPixmap(QPixmap(icon_path))
        self.icon.setScaledContents(True)

        self.label = TextLabel(self, f"{object_name}Label", text)

        self.layout = RowLayout(self, f"{object_name}Layout", spacing=0)
        self.layout.addWidget(self.icon)
        self.layout.addWidget(self.label)
        self.layout.addStretch(1)

class ToggleButton(LeftMenuButton):
    def __init__(self, parent, object_name, icon, main_window, on_click):
        super().__init__(parent, object_name, icon, main_window)
        self.clicked.connect(on_click)

    def on_click(self):
        pass # override base method

class PageButton(QPushButton):
    def __init__(self, parent, object_name, icon, on_click):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setFixedSize(QSize(30, 30))
        self.setIconSize(QSize(30, 30))
        self.setIcon(icon)

        self.setStyleSheet(StyleSheets.page_button)

        self.clicked.connect(on_click)


# https://stackoverflow.com/questions/62807295/how-to-resize-a-window-from-the-edges-after-adding-the-property-qtcore-qt-framel
class SideGrip(QWidget):
    def __init__(self, parent, edge):
        super().__init__(parent)
        if edge == Qt.LeftEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeLeft
        elif edge == Qt.TopEdge:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeTop
        elif edge == Qt.RightEdge:
            self.setCursor(Qt.SizeHorCursor)
            self.resizeFunc = self.resizeRight
        else:
            self.setCursor(Qt.SizeVerCursor)
            self.resizeFunc = self.resizeBottom
        self.mousePos = None

    def resizeLeft(self, delta):
        w = self.window()
        width = max(w.minimumWidth(), w.width() - delta.x())
        geo = w.geometry()
        geo.setLeft(geo.right() - width)
        w.setGeometry(geo)

    def resizeTop(self, delta):
        w = self.window()
        height = max(w.minimumHeight(), w.height() - delta.y())
        geo = w.geometry()
        geo.setTop(geo.bottom() - height)
        w.setGeometry(geo)

    def resizeRight(self, delta):
        w = self.window()
        width = max(w.minimumWidth(), w.width() + delta.x())
        w.resize(width, w.height())

    def resizeBottom(self, delta):
        w = self.window()
        height = max(w.minimumHeight(), w.height() + delta.y())
        w.resize(w.width(), height)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.mousePos is not None:
            delta = event.pos() - self.mousePos
            self.resizeFunc(delta)

    def mouseReleaseEvent(self, event):
        self.mousePos = None

class MainWindow(QMainWindow):
    def minimize(self):
        self.showMinimized()

    def restore(self):
        self.showNormal()
        self.is_maximized = False
        self.maximizeButton.setIcon(QIcon(Icons.maximize))
        self.centralLayout.setContentsMargins(10, 10, 10, 10)
        self.set_grip_size(10)

    def maximize(self):
        self.showMaximized()
        self.is_maximized = True
        self.maximizeButton.setIcon(QIcon(Icons.restore))
        self.centralLayout.setContentsMargins(0, 0, 0, 0)
        self.set_grip_size(0)

    def maximize_restore(self):
        if self.is_maximized:
            self.restore()
        else:
            self.maximize()

    def drag(self, dpos):
        if self.is_maximized:
            pass # TODO if dragging from maximized, after restoring, move window to cursor
        self.restore()

        self.move(self.pos() + dpos)

    def animate(self):
        self.animation = QPropertyAnimation(self.leftMenu, b"minimumWidth")
        self.animation.setDuration(500)
        self.animation.setStartValue(self.leftMenu.width())
        self.animation.setEndValue(LeftMenuButton.min_width if self.leftMenu.width() == LeftMenuButton.max_width
                                   else LeftMenuButton.max_width)
        self.animation.setEasingCurve(QEasingCurve.InOutQuint)
        self.animation.start()

    # bloodweb
    def get_runtime_profile(self):
        return self.bloodwebPage.profileSelector.currentText()

    def get_runtime_character(self):
        return self.bloodwebPage.characterSelector.currentText()

    def get_runtime_naive_mode(self):
        return self.bloodwebPage.naiveModeCheckBox.isChecked()

    def get_runtime_prestige_limit(self) -> str or None:
        return self.bloodwebPage.prestigeInput.text() if self.bloodwebPage.prestigeCheckBox.isChecked() else None

    def get_runtime_bloodpoint_limit(self) -> str or None:
        return self.bloodwebPage.bloodpointInput.text() if self.bloodwebPage.bloodpointCheckBox.isChecked() else None

    def run_terminate(self):
        debug, write_to_output = self.bloodwebPage.get_run_mode()
        if not self.state.is_active(): # run
            # check prestige limit
            prestige_limit = self.get_runtime_prestige_limit()
            if prestige_limit is not None:
                try:
                    prestige_limit = int(prestige_limit)
                except:
                    return self.bloodwebPage.show_run_error("Prestige level must be an integer from 1 to 100.", True)
                if not (1 <= prestige_limit <= 100):
                    return self.bloodwebPage.show_run_error("Prestige level must be an integer from 1 to 100.", True)

            bp_limit = self.get_runtime_bloodpoint_limit()
            if bp_limit is not None:
                try:
                    bp_limit = int(bp_limit)
                except:
                    return self.bloodwebPage.show_run_error("Bloodpoint limit must be a positive integer.", True)
                if not (1 <= bp_limit):
                    return self.bloodwebPage.show_run_error("Bloodpoint limit must be a positive integer.", True)

            self.state.run((debug, write_to_output, self.get_runtime_profile(), self.get_runtime_character(),
                            self.get_runtime_naive_mode(), prestige_limit, bp_limit))
            self.toggle_run_terminate_text("Running...", False, True)
        else: # terminate
            self.state.terminate()
            self.toggle_run_terminate_text("Manually terminated.", False, True)

    def toggle_run_terminate_text(self, text, is_error, hide):
        self.bloodwebPage.hide_run_text()
        if not self.state.is_active():
            self.bloodwebPage.runButton.setText("Run")
            self.bloodwebPage.runButton.setFixedSize(QSize(60, 35))
        else:
            self.bloodwebPage.runButton.setText("Terminate")
            self.bloodwebPage.runButton.setFixedSize(QSize(92, 35))

        if is_error:
            self.bloodwebPage.show_run_error(text, hide)
        else:
            self.bloodwebPage.show_run_success(text, hide)

    @property
    def grip_size(self):
        return self.__grip_size

    def set_grip_size(self, grip_size):
        self.__grip_size = grip_size
        self.update_grips()

    def update_grips(self):
        self.setContentsMargins(*[self.grip_size] * 4)

        out_rect = self.rect()
        out_rect = out_rect.adjusted(10, 10, -10, -10)
        in_rect = out_rect.adjusted(self.grip_size, self.grip_size, -self.grip_size, -self.grip_size)

        # top left
        self.corner_grips[0].setGeometry(QRect(out_rect.topLeft(), in_rect.topLeft()))
        # top right
        self.corner_grips[1].setGeometry(QRect(out_rect.topRight(), in_rect.topRight()).normalized())
        # bottom right
        self.corner_grips[2].setGeometry(QRect(in_rect.bottomRight(), out_rect.bottomRight()))
        # bottom left
        self.corner_grips[3].setGeometry(QRect(out_rect.bottomLeft(), in_rect.bottomLeft()).normalized())

        # left edge
        self.side_grips[0].setGeometry(out_rect.left(), in_rect.top(), self.grip_size, in_rect.height())
        # top edge
        self.side_grips[1].setGeometry(in_rect.left(), out_rect.top(), in_rect.width(), self.grip_size)
        # right edge
        self.side_grips[2].setGeometry(in_rect.left() + in_rect.width(), in_rect.top(), self.grip_size,
                                       in_rect.height())
        # bottom edge
        self.side_grips[3].setGeometry(self.grip_size, in_rect.top() + in_rect.height(), in_rect.width(),
                                       self.grip_size)

        [grip.raise_() for grip in self.side_grips]
        [grip.raise_() for grip in self.corner_grips]

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)
        self.update_grips()

    def __init__(self, state_pipe_, emitter, dev_mode):
        super().__init__()
        # TODO windows up + windows down; cursor when hovering over buttons
        self.is_maximized = False
        self.state = State(state_pipe_)

        self.emitter = emitter
        self.emitter.start() # start the thread, calling Emitter.run()

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setMinimumSize(1100, 600)
        self.resize(1230, 670)
        self.setWindowTitle("Blood Emporium")
        self.setWindowIcon(QIcon(Icons.icon))

        self.__grip_size = 10
        self.side_grips = [
            SideGrip(self, Qt.LeftEdge),
            SideGrip(self, Qt.TopEdge),
            SideGrip(self, Qt.RightEdge),
            SideGrip(self, Qt.BottomEdge),
        ]
        self.corner_grips = [QSizeGrip(self) for _ in range(4)]
        for corner_grip in self.corner_grips:
            corner_grip.setStyleSheet("background-color: transparent;")

        # self.shortcut = QShortcut(QKeySequence(Qt.Key_Meta + Qt.Key_Up), self) # TODO
        # self.shortcut.activated.connect(self.maximize)

        # central widget
        self.centralWidget = QWidget(self)
        self.centralWidget.setObjectName("centralWidget")
        self.centralWidget.setAutoFillBackground(False)
        self.setCentralWidget(self.centralWidget)

        self.centralLayout = QGridLayout(self.centralWidget)
        self.centralLayout.setObjectName("centralLayout")
        self.centralLayout.setContentsMargins(10, 10, 10, 10)
        self.centralLayout.setSpacing(0)

        # background
        self.background = QFrame(self.centralWidget)
        self.background.setObjectName("background")
        self.background.setStyleSheet(f"""
            QFrame#background {{
                background-color: {StyleSheets.passive};
            }}""")
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 200))
        self.background.setGraphicsEffect(self.shadow)

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
        self.icon.setObjectName("icon")
        self.icon.setFixedSize(QSize(60, 60))
        self.icon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.icon))
        self.icon.setScaledContents(True)

        # title bar
        self.titleBar = TitleBar(self.topBar, self.maximize_restore, self.drag)

        self.titleBarLayout = QGridLayout(self.titleBar)
        self.titleBarLayout.setObjectName("titleBarLayout")
        self.titleBarLayout.setContentsMargins(0, 0, 0, 0)
        self.titleBarLayout.setSpacing(0)

        # title label
        self.titleLabel = TextLabel(self.titleBar, "titleLabel", "Blood Emporium")

        # window buttons
        self.windowButtons = QWidget(self.topBar)
        self.windowButtons.setObjectName("windowButtons")
        self.windowButtons.setFixedSize(QSize(105, 60))

        self.windowButtonsLayout = QGridLayout(self.windowButtons)
        self.windowButtonsLayout.setObjectName("windowButtonsLayout")
        self.windowButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.windowButtonsLayout.setSpacing(0)

        self.minimizeButton = TopBarButton(self.windowButtons, "minimizeButton", QIcon(Icons.minimize), self.minimize)
        self.maximizeButton = TopBarButton(self.windowButtons, "maximizeButton",
                                           QIcon(Icons.restore) if self.is_maximized else QIcon(Icons.maximize),
                                           self.maximize_restore)
        self.closeButton = TopBarButton(self.windowButtons, "closeButton", QIcon(Icons.close), self.close)

        # content
        self.content = QFrame(self.background)
        self.content.setObjectName("content")

        self.contentLayout = QGridLayout(self.content)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.contentLayout.setSpacing(0)

        # left menu
        self.leftMenu = QFrame(self.content)
        self.leftMenu.setObjectName("leftMenu")
        self.leftMenu.setMinimumWidth(LeftMenuButton.min_width)
        self.leftMenu.setMaximumWidth(LeftMenuButton.min_width)
        self.leftMenu.setStyleSheet(f"""
            QFrame#leftMenu {{
                background-color: {StyleSheets.background};
            }}""")

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

        self.toggleButton = ToggleButton(self.leftMenu, "toggleButton", QIcon(Icons.menu), self, self.animate)
        self.toggleLabel = LeftMenuLabel(self.toggleButton, "toggleLabel", "Hide", f"color: {StyleSheets.purple};")

        self.homeButton = LeftMenuButton(self.leftMenu, "homeButton", QIcon(Icons.home), self, True)
        self.homeLabel = LeftMenuLabel(self.homeButton, "homeLabel", "Home")
        self.homeBar = LeftMenuBar(self.homeButton, "homeBar", True)
        self.homeButton.setBar(self.homeBar)

        self.preferencesButton = LeftMenuButton(self.leftMenu, "preferencesButton", QIcon(Icons.preferences), self)
        self.preferencesLabel = LeftMenuLabel(self.preferencesButton, "preferencesLabel", "Preference Profiles")
        self.preferencesBar = LeftMenuBar(self.preferencesButton, "preferencesBar")
        self.preferencesButton.setBar(self.preferencesBar)

        self.bloodwebButton = LeftMenuButton(self.leftMenu, "bloodwebButton", QIcon(Icons.bloodweb), self)
        self.bloodwebLabel = LeftMenuLabel(self.bloodwebButton, "bloodwebLabel", "Run")
        self.bloodwebBar = LeftMenuBar(self.bloodwebButton, "bloodwebBar")
        self.bloodwebButton.setBar(self.bloodwebBar)

        # help button
        self.helpButton = LeftMenuButton(self.menuColumn, "helpButton", QIcon(Icons.help), self)
        self.helpLabel = LeftMenuLabel(self.helpButton, "helpLabel", "Help & Contact")
        self.helpBar = LeftMenuBar(self.helpButton, "helpBar")
        self.helpButton.setBar(self.helpBar)

        # settings button
        self.settingsButton = LeftMenuButton(self.menuColumn, "settingsButton", QIcon(Icons.settings), self)
        self.settingsLabel = LeftMenuLabel(self.settingsButton, "settingsLabel", "Settings")
        self.settingsBar = LeftMenuBar(self.settingsButton, "settingsBar")
        self.settingsButton.setBar(self.settingsBar)

        self.buttons = [self.homeButton, self.preferencesButton, self.bloodwebButton, self.helpButton,
                        self.settingsButton]

        # content pages
        self.contentPages = QFrame(self.content)
        self.contentPages.setObjectName("contentPages")

        self.contentPagesLayout = QGridLayout(self.contentPages)
        self.contentPagesLayout.setObjectName("contentPagesLayout")
        self.contentPagesLayout.setContentsMargins(0, 0, 0, 0)
        self.contentPagesLayout.setSpacing(0)

        # stack
        self.stack = QStackedWidget(self.contentPages)
        self.stack.setObjectName("stack")
        self.stack.setStyleSheet("QStackedWidget#stack {background: transparent;}")

        # stack: homePage
        self.homePage = QWidget()
        self.homePage.setObjectName("homePage")
        self.homeButton.setPage(self.homePage)

        self.homePageLayout = QVBoxLayout(self.homePage)
        self.homePageLayout.setObjectName("homePageLayout")
        self.homePageLayout.setContentsMargins(0, 0, 0, 0)
        self.homePageLayout.setSpacing(5)

        self.homePageIcon = QLabel(self.homePage)
        self.homePageIcon.setObjectName("homePageIcon")
        self.homePageIcon.setFixedSize(QSize(200, 200))
        self.homePageIcon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.icon))
        self.homePageIcon.setScaledContents(True)

        self.homePageRow1 = HomeRow(self.homePage, 1, QIcon(Icons.settings), self.settingsButton.on_click,
                                    "Using a custom icon pack? Set up your settings.")
        self.homePageRow2 = HomeRow(self.homePage, 2, QIcon(Icons.preferences), self.preferencesButton.on_click,
                                    "What would you like from the bloodweb? Set up your preferences.")
        self.homePageRow3 = HomeRow(self.homePage, 3, QIcon(Icons.bloodweb), self.bloodwebButton.on_click,
                                    "Ready? Start clearing your bloodweb (with optional spending limits)!")
        self.homePageRow4 = HomeRow(self.homePage, 4, QIcon(Icons.help), self.helpButton.on_click,
                                    "Instructions & contact details here.")

        # stack: bloodwebPage
        self.bloodwebPage = BloodwebPage(dev_mode)
        self.bloodwebButton.setPage(self.bloodwebPage)
        self.bloodwebPage.runButton.clicked.connect(self.run_terminate)

        # stack: preferencesPage
        self.preferencesPage = PreferencesPage(self.bloodwebPage)
        self.preferencesButton.setPage(self.preferencesPage)

        # stack: helpPage
        self.helpPage = HelpPage()
        self.helpButton.setPage(self.helpPage)

        # stack: settingsPage
        self.settingsPage = SettingsPage(self.run_terminate, self.bloodwebPage)
        self.settingsButton.setPage(self.settingsPage)
        TextInputBox.on_focus_in_callback = self.settingsPage.stop_keyboard_listener
        TextInputBox.on_focus_out_callback = self.settingsPage.start_keyboard_listener
        self.settingsPage.start_keyboard_listener()

        # bottom bar
        self.bottomBar = QFrame(self.content)
        self.bottomBar.setObjectName("bottomBar")
        self.bottomBar.setMinimumSize(QSize(0, 25))
        self.bottomBar.setStyleSheet(f"""
            QFrame#bottomBar {{
                background-color: {StyleSheets.selection};
            }}""")

        self.bottomBarLayout = RowLayout(self.bottomBar, "bottomBarLayout")
        self.bottomBarLayout.setContentsMargins(10, 0, 10, 0)

        self.authorLabel = HyperlinkTextLabel(self.bottomBar, "authorLabel", "Made by IIInitiationnn",
                                              "https://github.com/IIInitiationnn/BloodEmporium", Font(8))
        self.versionLabel = TextLabel(self.bottomBar, "versionLabel", State.version, Font(8))

        """
        central
            -> background
        """

        self.centralLayout.addWidget(self.background, 1, 1)

        """
        background
            -> topBar
            -> content
        """
        self.backgroundLayout.addWidget(self.topBar, 0, 0, 1, 1)
        self.backgroundLayout.addWidget(self.content, 1, 0, 1, 1)
        self.backgroundLayout.setRowStretch(1, 1) # content fill out as much of background as possible

        """
        topBar
           -> icon
           -> titleBar
           -> windowButtons
        """
        self.topBarLayout.addWidget(self.icon, 0, 0, 1, 1, Qt.AlignVCenter)
        self.topBarLayout.addWidget(self.titleBar, 0, 1, 1, 1, Qt.AlignVCenter)
        self.topBarLayout.addWidget(self.windowButtons, 0, 2, 1, 1, Qt.AlignVCenter)

        """
        titleBar
            -> titleLabel
        """
        self.titleBarLayout.addWidget(self.titleLabel, 0, 0, 1, 1, Qt.AlignVCenter)

        """
        windowButtons
            -> 3 buttons
        """
        self.windowButtonsLayout.addWidget(self.minimizeButton, 0, 0, 1, 1, Qt.AlignVCenter)
        self.windowButtonsLayout.addWidget(self.maximizeButton, 0, 1, 1, 1, Qt.AlignVCenter)
        self.windowButtonsLayout.addWidget(self.closeButton, 0, 2, 1, 1, Qt.AlignVCenter)

        """
        content
            -> leftMenu
            -> contentPage
            -> bottomBar
        """
        self.contentLayout.addWidget(self.leftMenu, 0, 0, 2, 1)
        self.contentLayout.addWidget(self.contentPages, 0, 1, 1, 1)
        self.contentLayout.addWidget(self.bottomBar, 1, 1, 1, 1)
        self.contentLayout.setRowStretch(0, 1) # maximally stretch contentPages down (pushing down on bottomBar)
        # self.contentLayout.setColumnStretch(1, 1) # stretch contentPages and bottomBar on the leftMenu

        """
        leftMenu
            -> menuColumn
            -> helpButton
            -> settingsButton
        """
        self.leftMenuLayout.addWidget(self.menuColumn, 0, Qt.AlignTop)
        self.leftMenuLayout.addWidget(self.helpButton)
        self.leftMenuLayout.addWidget(self.settingsButton)

        """
        menuColumn
            -> 4 buttons
        """
        self.menuColumnLayout.addWidget(self.toggleButton)
        self.menuColumnLayout.addWidget(self.homeButton)
        self.menuColumnLayout.addWidget(self.preferencesButton)
        self.menuColumnLayout.addWidget(self.bloodwebButton)

        """
        bottomBar
            -> authorLabel
            -> versionLabel
        """
        self.bottomBarLayout.addWidget(self.authorLabel)
        self.bottomBarLayout.addWidget(self.versionLabel)
        self.bottomBarLayout.setStretch(0, 1)

        """
        contentPage
            -> stack
                
        """
        self.contentPagesLayout.addWidget(self.stack, 0, 0, 1, 1)

        """
        stack
            -> homePage
            -> preferencesPage
            -> bloodwebPage
            -> helpPage
            -> settingsPage
        """
        self.stack.addWidget(self.homePage)
        self.stack.addWidget(self.preferencesPage)
        self.stack.addWidget(self.bloodwebPage)
        self.stack.addWidget(self.helpPage)
        self.stack.addWidget(self.settingsPage)
        self.stack.setCurrentWidget(self.homePage)

        """
        homePage
        """
        self.homePageLayout.addStretch(1)
        self.homePageLayout.addWidget(self.homePageIcon, alignment=Qt.AlignHCenter)
        self.homePageLayout.addWidget(self.homePageRow1)
        self.homePageLayout.addWidget(self.homePageRow2)
        self.homePageLayout.addWidget(self.homePageRow3)
        self.homePageLayout.addWidget(self.homePageRow4)
        self.homePageLayout.addStretch(1)

        self.emitter.prestige.connect(self.bloodwebPage.on_prestige_signal)
        self.emitter.bloodpoint.connect(self.bloodwebPage.on_bloodpoint_signal)
        self.emitter.terminate.connect(self.state.terminate)
        self.emitter.toggle_text.connect(self.toggle_run_terminate_text)

# https://stackoverflow.com/questions/26746379/how-to-signal-slots-in-a-gui-from-a-different-process
# https://stackoverflow.com/questions/34525750/mainwindow-object-has-no-attribute-connect
# receives data from state process via pipe, then emits to main window in this process
class Emitter(QObject, Thread):
    prestige = pyqtSignal(int, object) # total, limit
    bloodpoint = pyqtSignal(int, object) # total, limit
    terminate = pyqtSignal()
    toggle_text = pyqtSignal(str, bool, bool) # message, is error, hide

    def __init__(self, pipe):
        QObject.__init__(self)
        Thread.__init__(self)
        self.daemon = True # shut down when main window is closed
        self.pipe = pipe

    def emit(self, signature, args):
        {
            "prestige": lambda: self.prestige.emit(*args),
            "bloodpoint": lambda: self.bloodpoint.emit(*args),
            "terminate": lambda: self.terminate.emit(*args),
            "toggle_text": lambda: self.toggle_text.emit(*args),
        }[signature]()

    def run(self):
        while True:
            try:
                data = self.pipe.recv()
            except EOFError:
                break
            else:
                self.emit(*data)

if __name__ == "__main__":
    freeze_support() # --onedir (for exe)

    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"

    main_pipe, state_pipe = Pipe() # emit from state pipe to main pipe. main can receive, state can send
    main_emitter = Emitter(main_pipe)

    app = QApplication([])
    splash = QSplashScreen(QPixmap(Icons.app_splash))
    splash.show()

    window = MainWindow(state_pipe, main_emitter, len(sys.argv) > 1 and "--dev" in sys.argv[1:])
    splash.finish(window)
    window.show()

    # auto update
    try:
        try_update = get_latest_update()
        if try_update is not None:
            dialog = UpdateDialog(State.version, try_update["tag_name"])
            selection = dialog.exec()
            if selection == QMessageBox.AcceptRole:
                handle_updates()
    except:
        pass

    @atexit.register
    def shutdown():
        window.state.terminate() # terminate running process if main app is closed

    sys.exit(app.exec_())