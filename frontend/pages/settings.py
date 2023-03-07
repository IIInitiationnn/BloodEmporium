import os
import sys

from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog
from pynput import keyboard

from frontend.generic import Font, TextLabel, TextInputBox, Button, HotkeyInput
from frontend.layouts import RowLayout
from frontend.stylesheets import StyleSheets

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.config import Config
from backend.data import Data
from backend.util.text_util import TextUtil

class SettingsPage(QWidget):
    def on_width_update(self):
        text = self.resolutionWidthInput.text()
        self.resolutionWidthInput.setStyleSheet(StyleSheets.settings_input(width=text))

    def on_height_update(self):
        text = self.resolutionHeightInput.text()
        self.resolutionHeightInput.setStyleSheet(StyleSheets.settings_input(height=text))

    def on_ui_scale_update(self):
        text = self.resolutionUIInput.text()
        self.resolutionUIInput.setStyleSheet(StyleSheets.settings_input(ui_scale=text))

    def set_path(self):
        icon_dir = QFileDialog.getExistingDirectory(self, "Select Icon Folder", self.pathText.text())
        if icon_dir != "":
            self.pathText.setText(icon_dir)

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
        width = self.resolutionWidthInput.text()
        height = self.resolutionHeightInput.text()
        ui_scale = self.resolutionUIInput.text()
        if not Data.verify_settings_res(width, height, ui_scale):
            self.show_settings_page_save_fail_text("Ensure width, height and UI scale are all numbers. "
                                                   "UI scale must be an integer between 70 and 100. Changes not saved.")
            return

        path = self.pathText.text()
        if not Data.verify_path(path):
            self.show_settings_page_save_fail_text("Ensure path is an actual folder. Changes not saved.")
            return

        hotkey = self.hotkeyInput.pressed_keys

        config = Config()
        config.set_resolution(int(width), int(height), int(ui_scale))
        config.set_path(path)
        config.set_hotkey(hotkey)
        self.config_cache = Config()
        self.show_settings_page_save_success_text("Settings changed.")

    def reset_settings(self):
        res = self.config_cache.resolution()
        self.resolutionWidthInput.setText(str(res.width))
        self.on_width_update()
        self.resolutionHeightInput.setText(str(res.height))
        self.on_height_update()
        self.resolutionUIInput.setText(str(res.ui_scale))
        self.on_ui_scale_update()
        self.pathText.setText(self.config_cache.path())
        self.hotkeyInput.set_keys(self.config_cache.hotkey())
        self.show_settings_page_save_success_text("Settings reset to last saved state.")

    def start_keyboard_listener(self):
        self.listener = keyboard.Listener(on_press=self.on_key_down, on_release=self.on_key_up)
        self.listener.start()

    def stop_keyboard_listener(self):
        self.listener.stop()
        self.listener = None

    def on_key_down(self, key):
        key = TextUtil.pynput_to_key_string(self.listener, key)
        self.pressed_keys = list(dict.fromkeys(self.pressed_keys + [key]))
        if self.pressed_keys == Config().hotkey():
            self.run_terminate()

    def on_key_up(self, key):
        key = TextUtil.pynput_to_key_string(self.listener, key)
        try:
            self.pressed_keys.remove(key)
        except ValueError:
            pass

    def __init__(self, run_terminate):
        super().__init__()
        self.listener = None
        self.pressed_keys = []
        self.config_cache = Config()
        self.setObjectName("settingsPage")
        self.run_terminate = run_terminate

        self.layout = QVBoxLayout(self)
        self.layout.setObjectName("settingsPageLayout")
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.setSpacing(15)

        res = self.config_cache.resolution()
        self.resolutionLabel = TextLabel(self, "settingsPageResolutionLabel", "Display Resolution", Font(12))
        self.resolutionUIDescription = TextLabel(self, "settingsPageResolutionUIDescription",
                                                 "You can find your UI scale in your Dead by Daylight settings under "
                                                 "Graphics -> UI / HUD -> UI Scale.", Font(10))
        self.resolutionWidthRow = QWidget(self)
        self.resolutionWidthRow.setObjectName("settingsPageResolutionWidthRow")

        self.resolutionWidthRowLayout = RowLayout(self.resolutionWidthRow, "settingsPageResolutionWidthRowLayout")

        self.resolutionWidthLabel = TextLabel(self.resolutionWidthRow, "settingsPageResolutionWidthLabel", "Width",
                                              Font(10))
        self.resolutionWidthInput = TextInputBox(self.resolutionWidthRow, "settingsPageResolutionWidthInput",
                                                 QSize(70, 40), "Width", str(res.width))
        self.resolutionWidthInput.textEdited.connect(self.on_width_update)

        self.resolutionHeightRow = QWidget(self)
        self.resolutionHeightRow.setObjectName("settingsPageResolutionHeightRow")
        self.resolutionHeightRowLayout = RowLayout(self.resolutionHeightRow, "settingsPageResolutionHeightRowLayout")

        self.resolutionHeightLabel = TextLabel(self.resolutionHeightRow, "settingsPageResolutionHeightLabel", "Height",
                                               Font(10))
        self.resolutionHeightInput = TextInputBox(self.resolutionHeightRow, "settingsPageResolutionHeightInput",
                                                  QSize(70, 40), "Height", str(res.height))
        self.resolutionHeightInput.textEdited.connect(self.on_height_update)

        self.resolutionUIRow = QWidget(self)
        self.resolutionUIRow.setObjectName("settingsPageResolutionUIRow")
        self.resolutionUIRowLayout = RowLayout(self.resolutionUIRow, "settingsPageResolutionUIRowLayout")

        self.resolutionUILabel = TextLabel(self.resolutionUIRow, "settingsPageResolutionUILabel", "UI Scale", Font(10))
        self.resolutionUIInput = TextInputBox(self.resolutionUIRow, "settingsPageResolutionUIInput", QSize(70, 40),
                                              "UI Scale", str(res.ui_scale))
        self.resolutionUIInput.textEdited.connect(self.on_ui_scale_update)

        self.pathLabel = TextLabel(self, "settingsPagePathLabel", "Installation Path", Font(12))
        self.pathLabelDefaultLabel = TextLabel(self, "settingsPagePathLabelDefaultLabel",
                                               "<p style=line-height:125%>"
                                               "You only need to modify this if you are using custom icons.<br>"
                                               "Default path on Steam is C:/Program Files (x86)/Steam/steamapps/common/"
                                               "Dead by Daylight/DeadByDaylight/Content/UI/Icons.<br>"
                                               "Default path on Epic Games is C:/Program Files/Epic Games/"
                                               "DeadByDaylight/Content/UI/Icons.</p>", Font(10))

        self.pathRow = QWidget(self)
        self.pathRow.setObjectName("settingsPagePathRow")
        self.pathRowLayout = RowLayout(self.pathRow, "settingsPagePathRowLayout")

        self.pathText = TextInputBox(self, "settingsPagePathText", QSize(550, 40),
                                     "Path to Dead by Daylight game icon files", str(self.config_cache.path()))
        self.pathButton = Button(self, "settingsPagePathButton", "Browse for icons folder", QSize(180, 35))
        self.pathButton.clicked.connect(self.set_path)

        self.hotkeyLabel = TextLabel(self, "settingsPageHotkeyLabel", "Hotkey", Font(12))
        self.hotkeyDescription = TextLabel(self, "settingsPageHotkeyDescription",
                                           "Shortcut to run or terminate the automatic bloodweb process.", Font(10))

        self.hotkeyInput = HotkeyInput(self, "settingsPageHotkeyInput", QSize(300, 40),
                                       self.stop_keyboard_listener, self.start_keyboard_listener)

        self.saveRow = QWidget(self)
        self.saveRow.setObjectName("settingsPageSaveRow")
        self.saveRowLayout = RowLayout(self.saveRow, "settingsPageSaveRowLayout")

        self.saveButton = Button(self.saveRow, "settingsPageSaveButton", "Save", QSize(60, 35))
        self.saveButton.clicked.connect(self.save_settings)
        self.resetButton = Button(self.saveRow, "settingsPageResetButton", "Reset", QSize(70, 35))
        self.resetButton.clicked.connect(self.reset_settings)

        self.saveSuccessText = TextLabel(self.saveRow, "settingsPageSaveSuccessText", "", Font(10))
        self.saveSuccessText.setVisible(False)

        self.resolutionWidthRowLayout.addWidget(self.resolutionWidthLabel)
        self.resolutionWidthRowLayout.addWidget(self.resolutionWidthInput)
        self.resolutionWidthRowLayout.addStretch(1)

        self.resolutionHeightRowLayout.addWidget(self.resolutionHeightLabel)
        self.resolutionHeightRowLayout.addWidget(self.resolutionHeightInput)
        self.resolutionHeightRowLayout.addStretch(1)

        self.resolutionUIRowLayout.addWidget(self.resolutionUILabel)
        self.resolutionUIRowLayout.addWidget(self.resolutionUIInput)
        self.resolutionUIRowLayout.addStretch(1)

        self.pathRowLayout.addWidget(self.pathText)
        self.pathRowLayout.addWidget(self.pathButton)
        self.pathRowLayout.addStretch(1)

        self.saveRowLayout.addWidget(self.saveButton)
        self.saveRowLayout.addWidget(self.resetButton)
        self.saveRowLayout.addWidget(self.saveSuccessText)
        self.saveRowLayout.addStretch(1)

        self.layout.addWidget(self.resolutionLabel)
        self.layout.addWidget(self.resolutionUIDescription)
        self.layout.addWidget(self.resolutionWidthRow)
        self.layout.addWidget(self.resolutionHeightRow)
        self.layout.addWidget(self.resolutionUIRow)
        self.layout.addWidget(self.pathLabel)
        self.layout.addWidget(self.pathLabelDefaultLabel)
        self.layout.addWidget(self.pathRow)
        self.layout.addWidget(self.hotkeyLabel)
        self.layout.addWidget(self.hotkeyDescription)
        self.layout.addWidget(self.hotkeyInput)
        self.layout.addWidget(self.saveRow)
        self.layout.addStretch(1)