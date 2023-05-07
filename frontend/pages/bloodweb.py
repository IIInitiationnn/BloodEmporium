import os
import sys

from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout

from backend.util.text_util import TextUtil
from frontend.generic import TextLabel, Font, TextInputBox, Selector, CheckBoxWithFunction, Button, CheckBox, ScrollBar, \
    ScrollArea, ScrollAreaContent
from frontend.layouts import RowLayout
from frontend.stylesheets import StyleSheets

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.config import Config
from backend.data import Data

class BloodwebPage(QWidget):
    def on_select_run_mode(self, mode):
        self.naiveCheckBox.setChecked(mode == "naive")
        self.awareCheckBox.setChecked(mode == "aware")
        self.profileSelector.setEnabled(mode != "naive")

    def on_toggle_prestige_limit(self):
        if self.prestigeCheckBox.isChecked():
            self.prestigeInput.setReadOnly(False)
            text = self.prestigeInput.text()
            self.prestigeInput.setStyleSheet(StyleSheets.prestige_input(text))
        else:
            self.prestigeInput.setReadOnly(True)
            self.prestigeInput.setStyleSheet(StyleSheets.text_box_read_only)

    def on_edit_prestige_limit_input(self):
        text = self.prestigeInput.text()
        self.prestigeInput.setStyleSheet(StyleSheets.prestige_input(text))

    def on_prestige_signal(self, prestige_total, prestige_limit):
        self.runPrestigeProgress.setText(f"Prestige levels completed: {prestige_total} / {prestige_limit}"
                                         if prestige_limit is not None else
                                         f"Prestige levels completed: {prestige_total}")

    def on_toggle_bloodpoint_limit(self):
        if self.bloodpointCheckBox.isChecked():
            self.bloodpointInput.setReadOnly(False)
            text = self.bloodpointInput.text()
            self.bloodpointInput.setStyleSheet(StyleSheets.bloodpoint_input(text))
        else:
            self.bloodpointInput.setReadOnly(True)
            self.bloodpointInput.setStyleSheet(StyleSheets.text_box_read_only)

    def on_edit_bloodpoint_limit_input(self):
        text = self.bloodpointInput.text()
        self.bloodpointInput.setStyleSheet(StyleSheets.bloodpoint_input(text))

    def on_bloodpoint_signal(self, bp_total, bp_limit):
        self.runBloodpointProgress.setText(f"Bloodpoints spent: {bp_total:,} / {bp_limit:,}"
                                           if bp_limit is not None else f"Bloodpoints spent: {bp_total:,}")

    def show_run_success(self, text, hide):
        self.runErrorText.setText(text)
        self.runErrorText.setStyleSheet(StyleSheets.pink_text)
        self.runErrorText.setVisible(True)
        if hide:
            QTimer.singleShot(10000, self.hide_run_text)

    def show_run_error(self, text, hide):
        self.runErrorText.setText(text)
        self.runErrorText.setStyleSheet(StyleSheets.purple_text)
        self.runErrorText.setVisible(True)
        if hide:
            QTimer.singleShot(10000, self.hide_run_text)

    def hide_run_text(self):
        self.runErrorText.setVisible(False)

    def refresh_run_description(self):
        self.pressed_keys = Config().hotkey()
        self.runDescription.setText("Make sure your game is open on your primary monitor; shaders, visual "
                                    "effects, colourblind modes, or any other colour modifications should be disabled."
                                    "\nIf the app is not selecting unlockables in the bloodweb, try "
                                    "running the app as an administrator.\n\nShortcut to run or terminate: " +
                                    " + ".join([TextUtil.title_case(k) for k in self.pressed_keys]) +
                                    " (can be changed in settings).")

    def get_run_mode(self):
        return (self.devDebugCheckBox.isChecked(), self.devOutputCheckBox.isChecked()) \
            if self.dev_mode else (False, False)

    def __init__(self, dev_mode):
        super().__init__()
        self.dev_mode = dev_mode
        self.setObjectName("bloodwebPage")

        self.layout = QGridLayout(self)
        self.layout.setObjectName("bloodwebPageLayout")
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.setSpacing(0)

        self.scrollBar = ScrollBar(self, "bloodwebPage")
        self.scrollArea = ScrollArea(self, "bloodwebPage", self.scrollBar)
        self.scrollAreaContent = ScrollAreaContent(self.scrollArea, "bloodwebPage")
        self.scrollArea.setWidget(self.scrollAreaContent)
        self.scrollAreaContentLayout = QVBoxLayout(self.scrollAreaContent)
        self.scrollAreaContentLayout.setObjectName("bloodwebPageScrollAreaContentLayout")
        self.scrollAreaContentLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaContentLayout.setSpacing(15)

        self.profileLabel = TextLabel(self, "bloodwebPageProfileLabel", "Profile", Font(12))
        self.profileSelector = Selector(self, "bloodwebPageProfileSelector", QSize(250, 40), Config().profile_names())

        self.characterLabel = TextLabel(self, "bloodwebPageCharacterLabel", "Character", Font(12))
        self.characterDescription = TextLabel(self, "bloodwebPageCharacterDescription",
                                              "Select the character whose bloodweb you are levelling.")
        self.characterSelector = Selector(self, "bloodwebPageCharacterSelector", QSize(150, 40),
                                          Data.get_characters(True))

        self.runModeLabel = TextLabel(self, "bloodwebPageRunModeLabel", "Run Mode", Font(12))

        self.naiveRow = QWidget(self)
        self.naiveRow.setObjectName("bloodwebPageNaiveRow")
        self.naiveRowLayout = RowLayout(self.naiveRow, "bloodwebPageNaiveRowLayout")
        self.naiveCheckBox = CheckBox(self.naiveRow, "bloodwebPageNaiveCheckBox")
        self.naiveCheckBox.clicked.connect(lambda: self.on_select_run_mode("naive"))
        self.naiveDescription = TextLabel(self.naiveRow, "bloodwebPageNaiveDescription",
                                          "Naive mode: selected profile will be ignored and auto-buy will be used "
                                          "where possible (use if you do not care about which items are selected).")

        self.awareRow = QWidget(self)
        self.awareRow.setObjectName("bloodwebPageAwareRow")
        self.awareRowLayout = RowLayout(self.awareRow, "bloodwebPageAwareRowLayout")
        self.awareCheckBox = CheckBox(self.awareRow, "bloodwebPageAwareCheckBox")
        self.awareCheckBox.setChecked(True)
        self.awareCheckBox.clicked.connect(lambda: self.on_select_run_mode("aware"))
        self.awareDescription = TextLabel(self.awareRow, "bloodwebPageAwareDescription",
                                          "Aware mode: items will be selected according to your preference profile.")

        self.limitsLabel = TextLabel(self, "bloodwebPageLimitsLabel", "Limits", Font(12))
        self.limitsDescription = TextLabel(self, "bloodwebPageLimitsDescription",
                                           "If multiple of the following limits are selected, the program "
                                           "will terminate when any limit is reached.")

        self.prestigeRow = QWidget(self)
        self.prestigeRow.setObjectName("bloodwebPagePrestigeRow")
        self.prestigeRowLayout = RowLayout(self.prestigeRow, "bloodwebPagePrestigeRowLayout")

        self.prestigeCheckBox = CheckBoxWithFunction(self.prestigeRow, "bloodwebPagePrestigeCheckBox",
                                                     self.on_toggle_prestige_limit)
        self.prestigeLabel = TextLabel(self.prestigeRow, "bloodwebPagePrestigeLabel", "Prestige Limit")
        self.prestigeInput = TextInputBox(self.prestigeRow, "bloodwebPagePrestigeInput", QSize(94, 40), "Enter levels",
                                          "1", style_sheet=StyleSheets.text_box_read_only)
        self.prestigeInput.textEdited.connect(self.on_edit_prestige_limit_input)
        self.prestigeInput.setReadOnly(True)
        self.prestigeDescription = TextLabel(self.prestigeRow, "bloodwebPagePrestigeDescription",
                                             "The number of prestige levels to complete before terminating "
                                             "(any integer from 1 to 100).", Font(10))

        self.bloodpointRow = QWidget(self)
        self.bloodpointRow.setObjectName("bloodwebPageBloodpointRow")
        self.bloodpointRowLayout = RowLayout(self.bloodpointRow, "bloodwebPageBloodpointRowLayout")

        self.bloodpointCheckBox = CheckBoxWithFunction(self.prestigeRow, "bloodwebPageBloodpointCheckBox",
                                                       self.on_toggle_bloodpoint_limit)
        self.bloodpointLabel = TextLabel(self.prestigeRow, "bloodwebPageBloodpointLabel", "Bloodpoint Limit")
        self.bloodpointInput = TextInputBox(self.prestigeRow, "bloodwebPageBloodpointInput", QSize(142, 40),
                                            "Enter bloodpoints", "69420", style_sheet=StyleSheets.text_box_read_only)
        self.bloodpointInput.textEdited.connect(self.on_edit_bloodpoint_limit_input)
        self.bloodpointInput.setReadOnly(True)
        self.bloodpointDescription = TextLabel(self.prestigeRow, "bloodwebPageBloodpointDescription",
                                               "The number of bloodpoints to spend before terminating.", Font(10))
        if dev_mode:
            self.devLabel = TextLabel(self, "settingsPageDevLabel", "Dev Options", Font(12))

            self.devDebugRow = QWidget(self)
            self.devDebugRow.setObjectName("bloodwebPageDevDebugRow")
            self.devDebugRowLayout = RowLayout(self.devDebugRow, "bloodwebPageDevDebugRowLayout")
            self.devDebugCheckBox = CheckBox(self, "bloodwebPageDevDebugCheckBox")
            self.devDebugLabel = TextLabel(self, "bloodwebPageDevDebugLabel", "Debug Mode", Font(10))

            self.devOutputRow = QWidget(self)
            self.devOutputRow.setObjectName("bloodwebPageDevOutputRow")
            self.devOutputRowLayout = RowLayout(self.devOutputRow, "bloodwebPageDevOutputRowLayout")
            self.devOutputCheckBox = CheckBox(self, "bloodwebPageDevOutputCheckBox")
            self.devOutputLabel = TextLabel(self, "bloodwebPageDevOutputLabel", "Write Output to Folder", Font(10))

            self.devDebugRowLayout.addWidget(self.devDebugCheckBox)
            self.devDebugRowLayout.addWidget(self.devDebugLabel)
            self.devDebugRowLayout.addStretch(1)
            self.devOutputRowLayout.addWidget(self.devOutputCheckBox)
            self.devOutputRowLayout.addWidget(self.devOutputLabel)
            self.devOutputRowLayout.addStretch(1)

        self.runLabel = TextLabel(self, "bloodwebPageRunLabel", "Run", Font(12))
        self.runDescription = TextLabel(self, "bloodwebPageRunLabel", "", Font(10))
        self.refresh_run_description()

        self.runRow = QWidget(self)
        self.runRow.setObjectName("bloodwebPageRunRow")
        self.runRowLayout = RowLayout(self.runRow, "bloodwebPageRunRowLayout")

        self.runButton = Button(self.runRow, "bloodwebPageRunButton", "Run", QSize(60, 35))
        self.runErrorText = TextLabel(self.runRow, "bloodwebPageRunErrorText", "", Font(10))
        self.runErrorText.setVisible(False)

        self.runPrestigeProgress = TextLabel(self, "bloodwebPageRunPrestigeProgress", "", Font(10))
        self.runBloodpointProgress = TextLabel(self, "bloodwebPageRunBloodpointProgress", "", Font(10))

        self.naiveRowLayout.addWidget(self.naiveCheckBox)
        self.naiveRowLayout.addWidget(self.naiveDescription)
        self.naiveRowLayout.addStretch(1)
        self.awareRowLayout.addWidget(self.awareCheckBox)
        self.awareRowLayout.addWidget(self.awareDescription)
        self.awareRowLayout.addStretch(1)

        self.prestigeRowLayout.addWidget(self.prestigeCheckBox)
        self.prestigeRowLayout.addWidget(self.prestigeLabel)
        self.prestigeRowLayout.addWidget(self.prestigeInput)
        self.prestigeRowLayout.addWidget(self.prestigeDescription)
        self.prestigeRowLayout.addStretch(1)

        self.bloodpointRowLayout.addWidget(self.bloodpointCheckBox)
        self.bloodpointRowLayout.addWidget(self.bloodpointLabel)
        self.bloodpointRowLayout.addWidget(self.bloodpointInput)
        self.bloodpointRowLayout.addWidget(self.bloodpointDescription)
        self.bloodpointRowLayout.addStretch(1)

        self.runRowLayout.addWidget(self.runButton)
        self.runRowLayout.addWidget(self.runErrorText)
        self.runRowLayout.addStretch(1)

        self.scrollAreaContentLayout.addWidget(self.profileLabel)
        self.scrollAreaContentLayout.addWidget(self.profileSelector)
        self.scrollAreaContentLayout.addWidget(self.characterLabel)
        self.scrollAreaContentLayout.addWidget(self.characterDescription)
        self.scrollAreaContentLayout.addWidget(self.characterSelector)
        self.scrollAreaContentLayout.addWidget(self.runModeLabel)
        self.scrollAreaContentLayout.addWidget(self.naiveRow)
        self.scrollAreaContentLayout.addWidget(self.awareRow)
        self.scrollAreaContentLayout.addWidget(self.limitsLabel)
        self.scrollAreaContentLayout.addWidget(self.limitsDescription)
        self.scrollAreaContentLayout.addWidget(self.prestigeRow)
        self.scrollAreaContentLayout.addWidget(self.bloodpointRow)
        if dev_mode:
            self.scrollAreaContentLayout.addWidget(self.devLabel)
            self.scrollAreaContentLayout.addWidget(self.devDebugRow)
            self.scrollAreaContentLayout.addWidget(self.devOutputRow)
        self.scrollAreaContentLayout.addWidget(self.runLabel)
        self.scrollAreaContentLayout.addWidget(self.runDescription)
        self.scrollAreaContentLayout.addWidget(self.runRow)
        self.scrollAreaContentLayout.addWidget(self.runPrestigeProgress)
        self.scrollAreaContentLayout.addWidget(self.runBloodpointProgress)
        self.scrollAreaContentLayout.addStretch(1)

        self.layout.addWidget(self.scrollArea)
        self.layout.setRowStretch(0, 1)
        self.layout.setColumnStretch(0, 1)