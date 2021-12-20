import os
import sys

from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QFont, QMouseEvent, QColor, QKeySequence
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QFrame, QPushButton, QGridLayout, QVBoxLayout, \
    QHBoxLayout, QGraphicsDropShadowEffect, QShortcut, QStackedWidget, QSizePolicy, QSpacerItem, QComboBox, QListView, \
    QScrollArea, QScrollBar, QCheckBox

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.config import Config
from backend.data import Data, Unlockable

debug_style_sheet = '''
    background-color: rgb(40, 44, 52);
    border: 5px solid black;
'''

'''
pink: rgb(255, 121, 198)
purple: rgb(189, 147, 249)


'''

class Font(QFont):
    def __init__(self, font_size):
        QFont.__init__(self)
        self.setFamily("Segoe UI")
        self.setPointSize(font_size)

class TopBar(QFrame):
    style_sheet = '''
        QFrame#topBar {
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
            background-color: transparent;
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

    def __init__(self, icon, parent, function, style_sheet=style_sheet):
        QPushButton.__init__(self, parent)
        self.setFixedSize(QSize(35, 35))

        self.setStyleSheet(style_sheet)

        # icon
        self.setIconSize(QSize(20, 20))
        self.setIcon(icon)

        self.clicked.connect(function)

class TitleBar(QWidget):
    def __init__(self, parent, on_double_click, on_drag):
        QWidget.__init__(self, parent)
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

    inactive_style_sheet = f'''
        QPushButton {{
            background-color: transparent;
            padding: 0 {padding} 0 -{padding};
            border: none;
        }}
        QPushButton:hover {{
            background-color: rgb(40, 44, 52);
            border: none;
        }}
        QPushButton:pressed {{
            background-color: rgb(189, 147, 249);
            border: none;
        }}'''

    active_style_sheet = f'''
        QPushButton {{
            background-color: rgb(40, 44, 52);
            padding: 0 {padding} 0 -{padding};
            border: none;
        }}
        QPushButton:hover {{
            border: none;
        }}
        QPushButton:pressed {{
            border: none;
        }}'''

    def __init__(self, icon, parent, main_window, is_active=False):
        QPushButton.__init__(self, parent)
        self.setMinimumSize(QSize(LeftMenuButton.max_width, 60))
        self.setMaximumSize(QSize(LeftMenuButton.max_width, 60))
        self.setIconSize(QSize(30, 30))
        self.setIcon(icon)

        self.main = main_window

        self.is_active = is_active
        self.setStyleSheet(LeftMenuButton.active_style_sheet if is_active else LeftMenuButton.inactive_style_sheet)

        self.clicked.connect(self.on_click)

    def setBar(self, bar):
        self.bar = bar

    def setPage(self, page):
        self.page = page

    def activate(self):
        self.is_active = True
        self.setStyleSheet(LeftMenuButton.active_style_sheet)
        self.bar.activate()
        self.main.stack.setCurrentWidget(self.page)

    def deactivate(self):
        self.is_active = False
        self.setStyleSheet(LeftMenuButton.inactive_style_sheet)
        self.bar.deactivate()

    def on_click(self):
        if not self.is_active:
            for button in self.main.buttons:
                button.deactivate()
        self.activate()

class LeftMenuBar(QFrame):
    def __init__(self, parent, visible=False):
        QFrame.__init__(self, parent)
        self.setFixedSize(3, 60)
        self.setStyleSheet("background-color: rgb(189, 147, 249);")
        self.setVisible(visible)

    def activate(self):
        self.setVisible(True)

    def deactivate(self):
        self.setVisible(False)

class LeftMenuLabel(QLabel):
    style_sheet = "color: rgb(255, 255, 255);"

    def __init__(self, parent, text, style_sheet=style_sheet):
        QLabel.__init__(self, parent)
        self.setFont(Font(8))
        self.setFixedHeight(60)
        self.setText(text)
        self.setStyleSheet(style_sheet)
        self.move(self.geometry().topLeft() - parent.geometry().topLeft() + QPoint(80, 0))

class ToggleButton(LeftMenuButton):
    def __init__(self, icon, parent, main_window, on_click):
        LeftMenuButton.__init__(self, icon, parent, main_window)
        self.clicked.connect(on_click)

    def on_click(self):
        pass

class HomePageLabel(QLabel):
    def __init__(self, parent, text):
        QLabel.__init__(self, parent)
        self.setFont(Font(10))
        self.setText(text)
        self.setStyleSheet("color: rgb(255, 255, 255);")

class PageButton(QPushButton):
    style_sheet = '''
        QPushButton {
            background-color: transparent;
            border: none;
            border-radius: 5;
        }
        QPushButton:hover {
            background-color: rgb(33, 37, 43);
            border: none;
            border-radius: 5;
        }
        QPushButton:pressed {
            background-color: rgb(255, 121, 198);
            border: none;
            border-radius: 5;
        }'''

    def __init__(self, icon, parent, on_click):
        QPushButton.__init__(self, parent)
        self.setFixedSize(QSize(30, 30))
        self.setIconSize(QSize(30, 30))
        self.setIcon(icon)

        self.setStyleSheet(PageButton.style_sheet)

        self.clicked.connect(on_click)

class SaveButton(QPushButton):
    def __init__(self, parent, object_name, text, size: QSize):
        QPushButton.__init__(self, parent)
        self.setObjectName(object_name)
        self.setFixedSize(size)
        self.setFont(Font(10))
        self.setText(text)
        self.setStyleSheet(f'''
            QPushButton {{
                color: rgb(255, 255, 255);
                background-color: rgb(56, 62, 73);
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: rgb(94, 104, 122);
                border: none;
            }}
            QPushButton:pressed {{
                background-color: rgb(139, 158, 194);
                border: none;
            }}''')

class CheckBox(QCheckBox):
    def __init__(self, parent, object_name):
        QCheckBox.__init__(self, parent)
        self.setObjectName(object_name)
        self.setAutoFillBackground(False)
        self.setStyleSheet(f'''
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 3px solid rgb(94, 104, 122);
                border-radius: 5px;
            }}
            
            QCheckBox::indicator:unchecked:hover {{
                border: 3px solid rgb(139, 158, 194);
            }}
            
            QCheckBox::indicator:checked {{
                background: rgb(94, 104, 122);
            }}''')

class UnlockableWidget(QWidget):
    def __init__(self, parent, unlockable: Unlockable):
        # TODO also add check box to the left, name to the right, tier to the right of that then subtier
        name = "".join([i for i in unlockable.name if i.isalpha() or i == " "]).title().replace(" ", "")
        name = name[0].lower() + name[1:]

        QWidget.__init__(self, parent)
        self.setObjectName(f"{name}Widget")

        self.layout = QGridLayout(self)
        self.layout.setObjectName(f"{name}Layout")
        self.layout.setContentsMargins(25, 0, 0, 0)
        self.layout.setSpacing(15)

        self.checkBox = CheckBox(self, f"{name}CheckBox")
        self.checkBox.setFixedSize(25, 25)
        self.layout.addWidget(self.checkBox, 0, 0, 1, 1)

        self.image = QLabel(self)
        self.image.setObjectName(f"{name}Image")
        self.image.setFixedSize(QSize(75, 75))
        self.image.setPixmap(QPixmap(unlockable.image_path))
        self.image.setScaledContents(True)
        self.layout.addWidget(self.image, 0, 1, 1, 1)

        self.label = QLabel(self)
        self.label.setObjectName(f"{name}Label")
        self.label.setFont(Font(10))
        self.label.setStyleSheet("color: rgb(255, 255, 255);")
        self.label.setText(unlockable.name)
        self.layout.addWidget(self.label, 0, 2, 1, 1)

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

    def __init__(self):
        QMainWindow.__init__(self)
        config = Config()
        # TODO windows up + windows down; resize areas; cursor when hovering over buttons

        self.is_maximized = False

        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.resize(1000, 580)
        self.setMinimumSize(800, 500)
        self.setWindowTitle("Blood Emporium")
        self.setWindowIcon(QIcon(Icons.icon))

        self.shortcut = QShortcut(QKeySequence(Qt.Key_Meta), self)
        self.shortcut.activated.connect(self.maximize)

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

        self.minimizeButton = TopBarButton(QIcon(Icons.minimize), self.windowButtons, self.minimize)
        self.minimizeButton.setObjectName("minimizeButton")

        maximize_icon = QIcon(Icons.restore) if self.is_maximized else QIcon(Icons.maximize)
        self.maximizeButton = TopBarButton(maximize_icon, self.windowButtons, self.maximize_restore)
        self.maximizeButton.setObjectName("maximizeButton")
        self.closeButton = TopBarButton(QIcon(Icons.close), self.windowButtons, self.close)
        self.closeButton.setObjectName("closeButton")

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

        self.toggleButton = ToggleButton(QIcon(Icons.menu), self.leftMenu, self, self.animate)
        self.toggleButton.setObjectName("toggleButton")
        self.toggleLabel = LeftMenuLabel(self.toggleButton, "Hide", "color: rgb(150, 150, 150);")
        self.toggleLabel.setObjectName("toggleLabel")

        self.homeButton = LeftMenuButton(QIcon(Icons.home), self.leftMenu, self, True)
        self.homeButton.setObjectName("homeButton")
        self.homeLabel = LeftMenuLabel(self.homeButton, "Home")
        self.homeLabel.setObjectName("homeLabel")
        self.homeBar = LeftMenuBar(self.homeButton, True)
        self.homeBar.setObjectName("homeLeftBar")
        self.homeButton.setBar(self.homeBar)

        self.preferencesButton = LeftMenuButton(QIcon(Icons.preferences), self.leftMenu, self)
        self.preferencesButton.setObjectName("preferencesButton")
        self.preferencesLabel = LeftMenuLabel(self.preferencesButton, "Preference Profiles")
        self.preferencesLabel.setObjectName("preferencesLabel")
        self.preferencesBar = LeftMenuBar(self.preferencesButton)
        self.preferencesBar.setObjectName("preferencesBar")
        self.preferencesButton.setBar(self.preferencesBar)

        self.bloodwebButton = LeftMenuButton(QIcon(Icons.bloodweb), self.leftMenu, self)
        self.bloodwebButton.setObjectName("bloodwebButton")
        self.bloodwebLabel = LeftMenuLabel(self.bloodwebButton, "Run")
        self.bloodwebLabel.setObjectName("bloodwebLabel")
        self.bloodwebBar = LeftMenuBar(self.bloodwebButton)
        self.bloodwebBar.setObjectName("bloodwebBar")
        self.bloodwebButton.setBar(self.bloodwebBar)

        # settings button
        self.settingsButton = LeftMenuButton(QIcon(Icons.settings), self.menuColumn, self)
        self.settingsButton.setObjectName("settingsButton")
        self.settingsLabel = LeftMenuLabel(self.settingsButton, "Settings")
        self.settingsLabel.setObjectName("settingsLabel")
        self.settingsBar = LeftMenuBar(self.settingsButton)
        self.settingsBar.setObjectName("settingsBar")
        self.settingsButton.setBar(self.settingsBar)

        self.buttons = [self.homeButton, self.preferencesButton, self.bloodwebButton, self.settingsButton]

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
        self.homePageLayout.setSpacing(0)

        self.homePageIcon = QLabel(self.homePage)
        self.homePageIcon.setObjectName("homePageIcon") # TODO large icon with Blood Emporium text like in Github splash
        self.homePageIcon.setFixedSize(QSize(300, 300))
        self.homePageIcon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.icon))
        self.homePageIcon.setScaledContents(True)

        self.homePageRow1 = QWidget(self.homePage)
        self.homePageRow1.setObjectName("homePageRow1")
        self.homePageButton1 = PageButton(QIcon(Icons.settings), self.homePageRow1, self.settingsButton.on_click)
        self.homePageButton1.setObjectName("homePageButton1")
        self.homePageLabel1 = HomePageLabel(self.homePageRow1, "First time here? Recently change your game / display settings? Set up your config.")
        self.homePageLabel1.setObjectName("homePageLabel1")

        self.homePageRow2 = QWidget(self.homePage)
        self.homePageRow2.setObjectName("homePageRow2")
        self.homePageButton2 = PageButton(QIcon(Icons.preferences), self.homePageRow2, self.preferencesButton.on_click)
        self.homePageButton2.setObjectName("homePageButton2")
        self.homePageLabel2 = HomePageLabel(self.homePageRow2, "What would you like from the bloodweb? Set up your preferences.")
        self.homePageLabel2.setObjectName("homePageLabel2")

        self.homePageRow3 = QWidget(self.homePage)
        self.homePageRow3.setObjectName("homePageRow3")
        self.homePageButton3 = PageButton(QIcon(Icons.bloodweb), self.homePageRow3, self.bloodwebButton.on_click)
        self.homePageButton3.setObjectName("homePageButton3")
        self.homePageLabel3 = HomePageLabel(self.homePageRow3, "Ready? Start clearing your bloodweb!")
        self.homePageLabel3.setObjectName("homePageLabel3")

        # stack: preferencesPage
        self.preferencesPage = QWidget()
        self.preferencesPage.setObjectName("preferencesPage")
        self.preferencesButton.setPage(self.preferencesPage)

        self.preferencesPageLayout = QGridLayout(self.preferencesPage)
        self.preferencesPageLayout.setObjectName("preferencesPageLayout")
        self.preferencesPageLayout.setContentsMargins(25, 25, 25, 25)
        self.preferencesPageLayout.setSpacing(0)

        self.preferencesPageScrollBar = QScrollBar(self.preferencesPage)
        self.preferencesPageScrollBar.setObjectName("preferencesPageScrollBar")
        self.preferencesPageScrollBar.setOrientation(Qt.Vertical)
        self.preferencesPageScrollBar.setStyleSheet('''
            QScrollBar:vertical {
                background: rgb(52, 59, 72);
                width: 8px;
                border: 0px solid white;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {	
                background: rgb(189, 147, 249);
                min-height: 25px;
                border-radius: 4px;
            }
            
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
            }''')

        self.preferencesPageScrollArea = QScrollArea(self.preferencesPage)
        self.preferencesPageScrollArea.setObjectName("preferencesPageScrollArea")
        self.preferencesPageScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.preferencesPageScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preferencesPageScrollArea.setVerticalScrollBar(self.preferencesPageScrollBar)
        self.preferencesPageScrollArea.setWidgetResizable(True)
        self.preferencesPageScrollArea.setStyleSheet('''
            QScrollArea#preferencesPageScrollArea {
                background: transparent;
                border: 0px;
            }''')

        self.preferencesPageScrollAreaContent = QWidget(self.preferencesPageScrollArea)
        self.preferencesPageScrollAreaContent.setObjectName("preferencesPageScrollAreaContent")
        self.preferencesPageScrollAreaContent.setStyleSheet('''
            QWidget#preferencesPageScrollAreaContent {
                background: transparent;
            }''')
        self.preferencesPageScrollArea.setWidget(self.preferencesPageScrollAreaContent)

        self.preferencesPageScrollAreaContentLayout = QVBoxLayout(self.preferencesPageScrollAreaContent)
        self.preferencesPageScrollAreaContentLayout.setObjectName("preferencesPageScrollAreaContentLayout")
        self.preferencesPageScrollAreaContentLayout.setContentsMargins(0, 0, 0, 0)
        self.preferencesPageScrollAreaContentLayout.setSpacing(15)

        self.preferencesPageProfileLabel = QLabel(self.preferencesPageScrollAreaContent)
        self.preferencesPageProfileLabel.setObjectName("preferencesPageProfileLabel")
        self.preferencesPageProfileLabel.setMaximumWidth(80)
        self.preferencesPageProfileLabel.setFont(Font(11))
        self.preferencesPageProfileLabel.setText("Profile")
        self.preferencesPageProfileLabel.setStyleSheet("QLabel#preferencesPageProfileLabel {color: rgb(255, 255, 255);}")

        self.preferencesPageProfileRowWidget = QWidget(self.preferencesPageScrollAreaContent)
        self.preferencesPageProfileRowWidget.setObjectName("preferencesPageProfileRowWidget")
        self.preferencesPageProfileRowWidgetLayout = QHBoxLayout(self.preferencesPageProfileRowWidget)
        self.preferencesPageProfileRowWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.preferencesPageProfileRowWidgetLayout.setSpacing(15)

        self.preferencesPageProfileView = QListView()
        self.preferencesPageProfileView.setFont(Font(8))
        self.preferencesPageProfileSelector = QComboBox(self.preferencesPageProfileRowWidget)
        self.preferencesPageProfileSelector.setObjectName("preferencesPageProfileSelector")
        self.preferencesPageProfileSelector.setFont(Font(10))
        self.preferencesPageProfileSelector.setFixedSize(150, 40)
        self.preferencesPageProfileSelector.addItems(config.profile_names())
        self.preferencesPageProfileSelector.setView(self.preferencesPageProfileView)
        self.preferencesPageProfileSelector.setStyleSheet('''
            QComboBox {
                background-color: rgb(33, 37, 43);
                color: rgb(255, 255, 255);
                border-radius: 5px;
                border: 2px solid rgba(0, 0, 0, 0);
                padding-left: 10px;
            }
            
            QComboBox:hover {
                border: 2px solid rgb(47, 52, 61);
            }
            
            QComboBox::drop-down {
                width: 30px;
                border: transparent;
            }
            
            QComboBox::down-arrow {
                image: url("assets/images/icons/icon_down_arrow.png");
                width: 15;
                height: 15;
            }
            
            QComboBox QAbstractItemView {
                outline: 0px;
                color: rgb(189, 147, 249);
                background-color: rgb(33, 37, 43);
                padding: 10px 0px 10px 10px;
            }
            
            QComboBox QAbstractItemView::item {
                min-height: 25px;
            }
            
            QListView::item:selected {
                color: rgb(255, 255, 255);
                background-color: rgb(39, 44, 54);
            }''')

        self.preferencesPageSaveButton = SaveButton(self.preferencesPageProfileRowWidget, "preferencesPageSaveButton",
                                                    "Save", QSize(60, 35))
        # TODO create new profile, save as (with text box), clone

        # TODO search bar and sort / filter by properties, also save button all as floating bar at the bottom
        self.preferencesPageUnlockableWidgets = []
        for unlockable in Data.get_unlockables():
            if unlockable.category in ["unused", "retired"]:
                continue

            # each one should be a widget with all the items, then can make visible or not using that
            # retain check box status even when filtering by different things

            unlockable_widget = UnlockableWidget(self.preferencesPageScrollAreaContent, unlockable)
            self.preferencesPageUnlockableWidgets.append(unlockable_widget)

        # stack: bloodwebPage
        self.bloodwebPage = QWidget()
        self.bloodwebPage.setObjectName("bloodwebPage")
        self.bloodwebButton.setPage(self.bloodwebPage)

        # stack: settingsPage
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName("settingsPage")
        self.settingsButton.setPage(self.settingsPage)

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
        self.bottomBarLayout.setContentsMargins(10, 0, 10, 0)

        self.authorLabel = QLabel(self.bottomBar)
        self.authorLabel.setObjectName("authorLabel")
        self.authorLabel.setFont(Font(8))
        self.authorLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.authorLabel.setText("Made by IIInitiationnn")

        self.versionLabel = QLabel(self.bottomBar)
        self.versionLabel.setObjectName("versionLabel")
        self.versionLabel.setFont(Font(8))
        self.versionLabel.setStyleSheet("color: rgb(255, 255, 255);")
        self.versionLabel.setText("v0.1.1") # TODO get from backend


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
        # self.contentLayout.setColumnStretch(1, 1) # stretch contentPages and bottomBar on the leftMenu

        '''
        leftMenu
            -> menuColumn
            -> settingsButton
        '''
        self.leftMenuLayout.addWidget(self.menuColumn, 0, Qt.AlignTop)
        self.leftMenuLayout.addWidget(self.settingsButton)

        '''
        menuColumn
            -> 4 buttons
        '''
        self.menuColumnLayout.addWidget(self.toggleButton)
        self.menuColumnLayout.addWidget(self.homeButton)
        self.menuColumnLayout.addWidget(self.preferencesButton)
        self.menuColumnLayout.addWidget(self.bloodwebButton)

        '''
        bottomBar
            -> authorLabel
            -> versionLabel
        '''
        self.bottomBarLayout.addWidget(self.authorLabel)
        self.bottomBarLayout.addWidget(self.versionLabel)
        self.bottomBarLayout.setStretch(0, 1)

        '''
        contentPage
            -> stack
                
        '''
        self.contentPagesLayout.addWidget(self.stack, 0, 0, 1, 1)

        '''
        stack
            -> homePage
            -> preferencesPage
            -> bloodwebPage
            -> settingsPage
        '''
        self.stack.addWidget(self.homePage)
        self.stack.addWidget(self.preferencesPage)
        self.stack.addWidget(self.bloodwebPage)
        self.stack.addWidget(self.settingsPage)
        self.stack.setCurrentWidget(self.homePage)

        '''
        homePage
        '''
        self.homePageLayout.addStretch(1)

        self.homePageLayout.addWidget(self.homePageIcon, alignment=Qt.AlignHCenter)

        self.homePageRow1Layout = QHBoxLayout(self.homePageRow1)
        self.homePageRow1Layout.setContentsMargins(0, 0, 0, 0)
        self.homePageRow1Layout.addStretch(1)
        self.homePageRow1Layout.addWidget(self.homePageButton1)
        self.homePageRow1Layout.addWidget(self.homePageLabel1)
        self.homePageRow1Layout.addStretch(1)
        self.homePageLayout.addWidget(self.homePageRow1)

        self.homePageRow2Layout = QHBoxLayout(self.homePageRow2)
        self.homePageRow2Layout.setContentsMargins(0, 0, 0, 0)
        self.homePageRow2Layout.addStretch(1)
        self.homePageRow2Layout.addWidget(self.homePageButton2)
        self.homePageRow2Layout.addWidget(self.homePageLabel2)
        self.homePageRow2Layout.addStretch(1)
        self.homePageLayout.addWidget(self.homePageRow2)

        self.homePageRow3Layout = QHBoxLayout(self.homePageRow3)
        self.homePageRow3Layout.setContentsMargins(0, 0, 0, 0)
        self.homePageRow3Layout.addStretch(1)
        self.homePageRow3Layout.addWidget(self.homePageButton3)
        self.homePageRow3Layout.addWidget(self.homePageLabel3)
        self.homePageRow3Layout.addStretch(1)
        self.homePageLayout.addWidget(self.homePageRow3)

        self.homePageLayout.addStretch(1)

        '''
        preferencesPage
            -> scrollArea
                -> scrollAreaContent (widget)
                    -> labels, combobox, everything
            -> scrollBar
        '''
        self.preferencesPageLayout.addWidget(self.preferencesPageScrollArea, 0, 0, 1, 1)
        self.preferencesPageLayout.addWidget(self.preferencesPageScrollBar, 0, 1, 1, 1)
        self.preferencesPageLayout.setRowStretch(0, 1)
        self.preferencesPageLayout.setColumnStretch(0, 1)

        self.preferencesPageProfileRowWidgetLayout.addWidget(self.preferencesPageProfileSelector)
        self.preferencesPageProfileRowWidgetLayout.addWidget(self.preferencesPageSaveButton)
        self.preferencesPageProfileRowWidgetLayout.addStretch(1)

        self.preferencesPageScrollAreaContentLayout.addWidget(self.preferencesPageProfileLabel)
        self.preferencesPageScrollAreaContentLayout.addWidget(self.preferencesPageProfileRowWidget)
        for unlockableWidget in self.preferencesPageUnlockableWidgets:
            self.preferencesPageScrollAreaContentLayout.addWidget(unlockableWidget)
        self.preferencesPageScrollAreaContentLayout.addStretch(1)

        # self.preferencesPageProfileSelector.setStyleSheet(debug_style_sheet)
        # self.preferencesPageSaveButton.setStyleSheet(debug_style_sheet)
        # self.preferencesPageProfileLabel.setStyleSheet(debug_style_sheet)

        self.show()

class Icons:
    __base = "assets/images/icons"
    icon = "assets/images/inspo1.png"
    minimize = __base + "/icon_minimize.png"
    restore = __base + "/icon_restore.png"
    maximize = __base + "/icon_maximize.png"
    close = __base + "/icon_close.png"
    menu = __base + "/icon_menu.png"
    home = __base + "/icon_home.png"
    preferences = __base + "/icon_preferences.png"
    settings = __base + "/icon_settings.png"
    bloodweb = __base + "/icon_graph.png"

if __name__ == "__main__":
    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"

    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())