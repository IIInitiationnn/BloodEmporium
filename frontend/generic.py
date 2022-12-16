from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QLabel, QLineEdit, QCheckBox, QComboBox, QListView, QPushButton, QWidget, QVBoxLayout, \
    QToolButton, QProxyStyle, QStyle

from frontend.stylesheets import StyleSheets


class Font(QFont):
    def __init__(self, font_size):
        super().__init__()
        self.setFamily("Segoe UI")
        self.setPointSize(font_size)

class TextLabel(QLabel):
    def __init__(self, parent, object_name, text, font=Font(10), style_sheet=StyleSheets.white_text):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setText(text)
        self.setFont(font)
        self.setStyleSheet(style_sheet)
        self.setAlignment(Qt.AlignVCenter)

class HyperlinkTextLabel(QLabel):
    def __init__(self, parent, object_name, text, link, font):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setFont(font)
        self.setText(f"<a style=\"color: white; text-decoration:none;\" href=\"{link}\">{text}</a>")
        self.setAlignment(Qt.AlignVCenter)
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.setOpenExternalLinks(True)

class TextInputBox(QLineEdit):
    on_focus_in_callback = lambda: None
    on_focus_out_callback = lambda: None

    def __init__(self, parent, object_name, size, placeholder_text, text=None, font=Font(10),
                 style_sheet=StyleSheets.text_box):
        QLineEdit.__init__(self, parent)
        self.setObjectName(object_name)
        self.setFixedSize(size)
        self.setPlaceholderText(placeholder_text)
        if text is not None:
            self.setText(text)
        self.setFont(font)
        self.setStyleSheet(style_sheet)

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        super().focusInEvent(event)
        TextInputBox.on_focus_in_callback()
        if not self.isReadOnly():
            QTimer.singleShot(0, self.selectAll)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        super().focusOutEvent(event)
        TextInputBox.on_focus_out_callback()

class CheckBox(QCheckBox):
    def __init__(self, parent, object_name, style_sheet=StyleSheets.check_box):
        super().__init__(parent)
        if object_name is not None:
            self.setObjectName(object_name)
        self.setAutoFillBackground(False)
        self.setStyleSheet(style_sheet)

class Selector(QComboBox):
    def __init__(self, parent, object_name, size, items, active_item=None):
        super().__init__(parent)
        self.view = QListView()
        self.view.setFont(Font(8))

        self.setObjectName(object_name)
        self.setFont(Font(10))
        self.setFixedSize(size)
        self.addItems(items)
        if active_item is not None:
            self.setCurrentIndex(self.findText(active_item))
        self.setView(self.view)
        self.setStyleSheet(StyleSheets.selector)

class Button(QPushButton):
    def __init__(self, parent, object_name, text, size: QSize):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setFixedSize(size)
        self.setFont(Font(10))
        self.setText(text)
        self.setStyleSheet(StyleSheets.button)

class CheckBoxWithFunction(CheckBox):
    def __init__(self, parent, object_name, on_click, style_sheet=StyleSheets.check_box):
        super().__init__(parent, object_name, style_sheet)
        self.clicked.connect(on_click)

class CollapsibleBox(QWidget):
    def __init__(self, parent, object_name, text):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        self.toggleButton = QToolButton(self)
        self.toggleButton.setObjectName(object_name)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)
        self.toggleButton.setFont(Font(12))
        self.toggleButton.setStyleSheet(StyleSheets.collapsible_box_inactive)
        self.toggleButton.setText(text)
        self.toggleButton.setIcon(QIcon(Icons.right_arrow))
        self.toggleButton.setIconSize(QSize(20, 20))
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.pressed.connect(self.on_pressed)
        self.toggleButton.setStyle(NoShiftStyle())

        self.layout.addWidget(self.toggleButton, alignment=Qt.AlignTop)

    def on_pressed(self):
        pass

# https://forum.qt.io/topic/15068/prevent-flat-qtoolbutton-from-moving-when-clicked/8
class NoShiftStyle(QProxyStyle):
    def pixelMetric(self, metric, option, widget):
        if metric == QStyle.PM_ButtonShiftHorizontal or metric == QStyle.PM_ButtonShiftVertical:
            ret = 0
        else:
            ret = QProxyStyle.pixelMetric(self, metric, option, widget)
        return ret

class Icons:
    __base = "assets/images/icons"
    icon = "assets/images/inspo1.png"
    splash = "assets/images/splash.png"
    minimize = __base + "/icon_minimize.png"
    restore = __base + "/icon_restore.png"
    maximize = __base + "/icon_maximize.png"
    close = __base + "/icon_close.png"
    menu = __base + "/icon_menu.png"
    home = __base + "/icon_home.png"
    preferences = __base + "/icon_preferences.png"
    settings = __base + "/icon_settings.png"
    bloodweb = __base + "/icon_graph.png"
    help = __base + "/icon_help.png"
    down_arrow = __base + "/icon_down_arrow.png"
    right_arrow = __base + "/icon_right_arrow.png"
    up_arrow = __base + "/icon_up_arrow.png"
    discord = __base + "/icon_discord.png"
    twitter = __base + "/icon_twitter.png"
