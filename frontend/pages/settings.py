import os
import sys

from PyQt5.QtCore import QSize, QTimer, Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QGridLayout
from pynput import keyboard

from frontend.generic import Font, TextLabel, TextInputBox, Button, HotkeyInput, ScrollAreaContent, ScrollBar, \
    ScrollArea, Selector
from frontend.layouts import RowLayout
from frontend.stylesheets import StyleSheets

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.config import Config
from backend.util.text_util import TextUtil

class SettingsPage(QWidget):
    def set_path(self):
        icon_dir = QFileDialog.getExistingDirectory(self, "Select Icon Folder", self.pathText.text())
        if icon_dir != "":
            self.pathText.setText(icon_dir)

    def on_path_update(self):
        text = self.pathText.text()
        self.pathText.setStyleSheet(StyleSheets.settings_input(text))

    def show_settings_page_save_success_text(self, text):
        self.saveSuccessText.setText(text)
        self.saveSuccessText.setStyleSheet(StyleSheets.pink_text)
        self.saveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_settings_page_save_success_text)

    def show_settings_page_save_fail_text(self, text):
        self.saveSuccessText.setText(text)
        self.saveSuccessText.setStyleSheet(StyleSheets.purple_text)
        self.saveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_settings_page_save_success_text)

    def hide_settings_page_save_success_text(self):
        self.saveSuccessText.setVisible(False)

    def save_settings(self):
        path = self.pathText.text()
        if not Config.verify_path(path):
            self.show_settings_page_save_fail_text("Ensure path is an actual folder (can be empty if you are not using "
                                                   "custom icons). Changes not saved.")
            return

        hotkey = self.hotkeyInput.pressed_keys

        config = Config()
        config.set_path(path)
        config.set_hotkey(hotkey)
        config.set_interaction(self.interactionSelector.currentText())
        config.set_primary_mouse(self.primaryMouseSelector.currentText())
        self.config_cache = Config()
        self.bloodweb_page.refresh_run_description()
        self.show_settings_page_save_success_text("Settings saved.")

    def revert_settings(self):
        self.pathText.setText(self.config_cache.path())
        self.hotkeyInput.set_keys(self.config_cache.hotkey())
        self.interactionSelector.setCurrentIndex(self.interactionSelector.findText(self.config_cache.interaction()))
        self.primaryMouseSelector.setCurrentIndex(self.primaryMouseSelector.findText(self.config_cache.primary_mouse()))
        self.show_settings_page_save_success_text("Settings reverted to last saved state.")

    def start_hotkey_listener(self):
        self.hotkey_listener = keyboard.Listener(on_press=self.on_key_down, on_release=self.on_key_up)
        self.hotkey_listener.start()

    def stop_hotkey_listener(self):
        self.hotkey_listener.stop()
        self.hotkey_listener = None

    def on_key_down(self, key):
        if self.hotkey_listener is not None:
            key = TextUtil.pynput_to_key_string(self.hotkey_listener, key)
            if key is None:
                return
            self.pressed_keys = list(dict.fromkeys(self.pressed_keys + [key]))
            if sorted(self.pressed_keys) == sorted(Config().hotkey()):
                self.run_terminate()

    def on_key_up(self, key):
        if self.hotkey_listener is not None:
            key = TextUtil.pynput_to_key_string(self.hotkey_listener, key)
            if key is None:
                return
            try:
                self.pressed_keys.remove(key)
            except ValueError:
                pass

    def __init__(self, run_terminate, bloodweb_page):
        super().__init__()
        self.hotkey_listener = None
        self.pressed_keys = []
        self.config_cache = Config()
        self.setObjectName("settingsPage")
        self.run_terminate = run_terminate
        self.bloodweb_page = bloodweb_page

        self.layout = QGridLayout(self)
        self.layout.setObjectName("settingsPageLayout")
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.setSpacing(0)

        self.scrollBar = ScrollBar(self, "settingsPage")
        self.scrollArea = ScrollArea(self, "settingsPage", self.scrollBar)
        self.scrollAreaContent = ScrollAreaContent(self.scrollArea, "settingsPage")
        self.scrollArea.setWidget(self.scrollAreaContent)
        self.scrollAreaContentLayout = QVBoxLayout(self.scrollAreaContent)
        self.scrollAreaContentLayout.setObjectName("settingsPageScrollAreaContentLayout")
        self.scrollAreaContentLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaContentLayout.setSpacing(15)

        self.pathLabel = TextLabel(self, "settingsPagePathLabel", "Installation Path", Font(12))
        self.pathLabelDefaultLabel = TextLabel(self, "settingsPagePathLabelDefaultLabel",
                                               "<p style=line-height:125%>"
                                               "You only need to modify this if you are using custom icons.<br>"
                                               "Default path on Steam is C:/Program Files (x86)/Steam/steamapps/common/"
                                               "Dead by Daylight/DeadByDaylight/Content/UI/Icons<br>"
                                               "Default path on Epic Games is C:/Program Files/Epic Games/"
                                               "DeadByDaylight/Content/UI/Icons</p>", Font(10))
        self.pathLabelDefaultLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.pathLabelDefaultLabel.setCursor(Qt.IBeamCursor)

        self.pathRow = QWidget(self)
        self.pathRow.setObjectName("settingsPagePathRow")
        self.pathRowLayout = RowLayout(self.pathRow, "settingsPagePathRowLayout")

        self.pathText = TextInputBox(self, "settingsPagePathText", QSize(550, 40),
                                     "Path to Dead by Daylight game icon files", str(self.config_cache.path()))
        self.on_path_update()
        self.pathText.textChanged.connect(self.on_path_update)
        self.pathButton = Button(self, "settingsPagePathButton", "Browse for icons folder", QSize(180, 35))
        self.pathButton.clicked.connect(self.set_path)

        self.hotkeyLabel = TextLabel(self, "settingsPageHotkeyLabel", "Hotkey", Font(12))
        self.hotkeyDescription = TextLabel(self, "settingsPageHotkeyDescription",
                                           "Shortcut to run or terminate the automatic bloodweb process.", Font(10))

        self.hotkeyInput = HotkeyInput(self, "settingsPageHotkeyInput", QSize(300, 40),
                                       self.stop_hotkey_listener, self.start_hotkey_listener)

        self.accessibilityLabel = TextLabel(self, "settingsPageAccessibilityLabel", "Accessibility Options", Font(12))

        self.interactionRow = QWidget(self)
        self.interactionRow.setObjectName("settingsPageInteractionRow")
        self.interactionRowLayout = RowLayout(self.interactionRow, "settingsPageInteractionRowLayout")

        self.interactionDescription = TextLabel(self, "settingsPageInteractionDescription", "Bloodweb Interaction Mode",
                                                Font(10))
        self.interactionSelector = Selector(self, "settingsPageInteractionSelector", QSize(85, 35),
                                            ["press", "hold"], self.config_cache.interaction())

        self.primaryMouseRow = QWidget(self)
        self.primaryMouseRow.setObjectName("settingsPagePrimaryMouseRow")
        self.primaryMouseRowLayout = RowLayout(self.primaryMouseRow, "settingsPagePrimaryMouseRowLayout")

        self.primaryMouseDescription = TextLabel(self, "settingsPagePrimaryMouseDescription", "Primary Mouse Button",
                                                 Font(10))
        self.primaryMouseSelector = Selector(self, "settingsPagePrimaryMouseSelector", QSize(80, 35),
                                             ["left", "right"], self.config_cache.primary_mouse())

        self.saveRow = QWidget(self)
        self.saveRow.setObjectName("settingsPageSaveRow")
        self.saveRowLayout = RowLayout(self.saveRow, "settingsPageSaveRowLayout")

        self.saveButton = Button(self.saveRow, "settingsPageSaveButton", "Save", QSize(60, 35))
        self.saveButton.clicked.connect(self.save_settings)
        self.revertButton = Button(self.saveRow, "settingsPageRevertButton", "Revert", QSize(70, 35))
        self.revertButton.clicked.connect(self.revert_settings)

        self.saveSuccessText = TextLabel(self.saveRow, "settingsPageSaveSuccessText", "", Font(10))
        self.saveSuccessText.setVisible(False)

        self.pathRowLayout.addWidget(self.pathText)
        self.pathRowLayout.addWidget(self.pathButton)
        self.pathRowLayout.addStretch(1)

        self.interactionRowLayout.addWidget(self.interactionDescription)
        self.interactionRowLayout.addWidget(self.interactionSelector)
        self.interactionRowLayout.addStretch(1)

        self.primaryMouseRowLayout.addWidget(self.primaryMouseDescription)
        self.primaryMouseRowLayout.addWidget(self.primaryMouseSelector)
        self.primaryMouseRowLayout.addStretch(1)

        self.saveRowLayout.addWidget(self.saveButton)
        self.saveRowLayout.addWidget(self.revertButton)
        self.saveRowLayout.addWidget(self.saveSuccessText)
        self.saveRowLayout.addStretch(1)

        self.scrollAreaContentLayout.addWidget(self.pathLabel)
        self.scrollAreaContentLayout.addWidget(self.pathLabelDefaultLabel)
        self.scrollAreaContentLayout.addWidget(self.pathRow)
        self.scrollAreaContentLayout.addWidget(self.hotkeyLabel)
        self.scrollAreaContentLayout.addWidget(self.hotkeyDescription)
        self.scrollAreaContentLayout.addWidget(self.hotkeyInput)
        self.scrollAreaContentLayout.addWidget(self.accessibilityLabel)
        self.scrollAreaContentLayout.addWidget(self.interactionRow)
        self.scrollAreaContentLayout.addWidget(self.primaryMouseRow)
        self.scrollAreaContentLayout.addWidget(self.saveRow)
        self.scrollAreaContentLayout.addStretch(1)

        self.layout.addWidget(self.scrollArea)
        self.layout.setRowStretch(0, 1)
        self.layout.setColumnStretch(0, 1)