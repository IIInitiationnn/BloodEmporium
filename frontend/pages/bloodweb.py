import os
import sys

from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from frontend.generic import TextLabel, Font, TextInputBox, Selector, CheckBoxWithFunction, Button, CheckBox, ScrollBar, \
    ScrollArea, ScrollAreaContent
from frontend.layouts import RowLayout
from frontend.stylesheets import StyleSheets

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.config import Config
from backend.data import Data
from backend.runtime import Runtime
from backend.util.text_util import TextUtil

class BloodwebPage(QWidget):
    def on_select_run_mode(self, mode):
        self.naiveCheckBox.setChecked(mode == "naive")
        self.awareSingleCheckBox.setChecked(mode == "aware_single")
        self.awareMultiCheckBox.setChecked(mode == "aware_multi")
        self.profileSelector.setEnabled(mode != "naive")
        Runtime().set_mode(mode)

    def on_select_speed(self, speed):
        self.speedSlowCheckBox.setChecked(speed == "slow")
        self.speedFastCheckBox.setChecked(speed == "fast")
        Runtime().set_speed(speed)

    def on_toggle_prestige_limit(self):
        if self.prestigeCheckBox.isChecked():
            self.prestigeInput.setReadOnly(False)
            text = self.prestigeInput.text()
            self.prestigeInput.setStyleSheet(StyleSheets.prestige_input(text))
            Runtime().change_limit("prestige", enabled=True)
        else:
            self.prestigeInput.setReadOnly(True)
            self.prestigeInput.setStyleSheet(StyleSheets.text_box_read_only)
            Runtime().change_limit("prestige", enabled=False)

    def on_edit_prestige_limit_input(self):
        text = self.prestigeInput.text()
        self.prestigeInput.setStyleSheet(StyleSheets.prestige_input(text))
        Runtime().change_limit("prestige", value=text)

    def on_prestige_signal(self, prestige_total, prestige_limit):
        if not self.runPrestigeProgress.isVisible():
            self.runPrestigeProgress.setVisible(True)
        self.runPrestigeProgress.setText(f"Prestige levels completed: {prestige_total} / {prestige_limit}"
                                         if prestige_limit is not None else
                                         f"Prestige levels completed: {prestige_total}")

    def on_toggle_bloodpoint_limit(self):
        if self.bloodpointCheckBox.isChecked():
            self.bloodpointInput.setReadOnly(False)
            text = self.bloodpointInput.text()
            self.bloodpointInput.setStyleSheet(StyleSheets.bloodpoint_input(text))
            Runtime().change_limit("bloodpoint", enabled=True)
        else:
            self.bloodpointInput.setReadOnly(True)
            self.bloodpointInput.setStyleSheet(StyleSheets.text_box_read_only)
            Runtime().change_limit("bloodpoint", enabled=False)

    def on_edit_bloodpoint_limit_input(self):
        text = self.bloodpointInput.text()
        self.bloodpointInput.setStyleSheet(StyleSheets.bloodpoint_input(text))
        Runtime().change_limit("bloodpoint", value=text)

    def on_bloodpoint_signal(self, bp_total, bp_limit):
        if not self.runBloodpointProgress.isVisible():
            self.runBloodpointProgress.setVisible(True)
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

    def get_debug_options(self):
        return (self.devDebugCheckBox.isChecked(), self.devOutputCheckBox.isChecked()) \
            if self.dev_mode else (False, False)

    def __init__(self, dev_mode):
        super().__init__()
        runtime = Runtime()
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

        self.profileLabel = TextLabel(self, "bloodwebPageProfileLabel", "Preference Profile", Font(12))
        self.profileSelector = Selector(self, "bloodwebPageProfileSelector", QSize(250, 40), Config().profile_names())
        index = self.profileSelector.findText(runtime.profile())
        if index != -1:
            self.profileSelector.setCurrentIndex(index)
        self.profileSelector.currentIndexChanged.connect(
            lambda: Runtime().set_profile(self.profileSelector.currentText()))

        self.characterLabel = TextLabel(self, "bloodwebPageCharacterLabel", "Character", Font(12))
        self.characterDescription = TextLabel(self, "bloodwebPageCharacterDescription",
                                              "Select the character whose bloodweb you are levelling.")
        self.characterSelector = Selector(self, "bloodwebPageCharacterSelector", QSize(150, 40),
                                          Data.get_characters(True))
        index = self.characterSelector.findText(runtime.character())
        if index != -1:
            self.characterSelector.setCurrentIndex(index)
        self.characterSelector.currentIndexChanged.connect(
            lambda: Runtime().set_character(self.characterSelector.currentText()))

        self.runModeLabel = TextLabel(self, "bloodwebPageRunModeLabel", "Selection Mode", Font(12))

        self.naiveRow = QWidget(self)
        self.naiveRow.setObjectName("bloodwebPageNaiveRow")
        self.naiveRowLayout = RowLayout(self.naiveRow, "bloodwebPageNaiveRowLayout")
        self.naiveCheckBox = CheckBox(self.naiveRow, "bloodwebPageNaiveCheckBox")
        self.naiveCheckBox.clicked.connect(lambda: self.on_select_run_mode("naive"))
        self.naiveDescription = TextLabel(self.naiveRow, "bloodwebPageNaiveDescription",
                                          "Naive mode: selected profile will be ignored and auto-buy will be used "
                                          "where possible (use if you do not care about which items are selected).")

        self.awareSingleRow = QWidget(self)
        self.awareSingleRow.setObjectName("bloodwebPageAwareSingleRow")
        self.awareSingleRowLayout = RowLayout(self.awareSingleRow, "bloodwebPageAwareSingleRowLayout")
        self.awareSingleCheckBox = CheckBox(self.awareSingleRow, "bloodwebPageAwareSingleCheckBox")
        self.awareSingleCheckBox.clicked.connect(lambda: self.on_select_run_mode("aware_single"))
        self.awareSingleDescription = TextLabel(self.awareSingleRow, "bloodwebPageAwareSingleDescription",
                                                "Aware mode (single-claim): items will be selected one at a time "
                                                "according to your preference profile.")

        self.awareMultiRow = QWidget(self)
        self.awareMultiRow.setObjectName("bloodwebPageAwareMultiRow")
        self.awareMultiRowLayout = RowLayout(self.awareMultiRow, "bloodwebPageAwareMultiRowLayout")
        self.awareMultiCheckBox = CheckBox(self.awareMultiRow, "bloodwebPageAwareMultiCheckBox")
        self.awareMultiCheckBox.clicked.connect(lambda: self.on_select_run_mode("aware_multi"))
        self.awareMultiDescription = TextLabel(self.awareMultiRow, "bloodwebPageAwareMultiDescription",
                                               "Aware mode (multi-claim): items will be selected along entire paths "
                                               "according to your preference profile (slightly faster but the entity "
                                               "may consume some items before they can be reached).")
        self.on_select_run_mode(runtime.mode())

        self.speedLabel = TextLabel(self, "bloodwebPageSpeedLabel", "Speed", Font(12))

        self.speedSlowRow = QWidget(self)
        self.speedSlowRow.setObjectName("bloodwebPageSpeedSlowRow")
        self.speedSlowRowLayout = RowLayout(self.speedSlowRow, "bloodwebPageSpeedSlowRowLayout")
        self.speedSlowCheckBox = CheckBox(self, "bloodwebPageSpeedSlowCheckBox")
        self.speedSlowCheckBox.clicked.connect(lambda: self.on_select_speed("slow"))
        self.speedSlowLabel = TextLabel(self, "bloodwebPageSpeedSlowLabel",
                                        "Slow: waits for bloodweb to update visually before proceeding "
                                        "(will more accurately select items according to availability and preference).",
                                        Font(10))

        self.speedFastRow = QWidget(self)
        self.speedFastRow.setObjectName("bloodwebPageSpeedFastRow")
        self.speedFastRowLayout = RowLayout(self.speedFastRow, "bloodwebPageSpeedFastRowLayout")
        self.speedFastCheckBox = CheckBox(self, "bloodwebPageSpeedFastCheckBox")
        self.speedFastCheckBox.clicked.connect(lambda: self.on_select_speed("fast"))
        self.speedFastLabel = TextLabel(self, "bloodwebPageSpeedFastLabel",
                                        "Fast: does not wait for bloodweb to update visually before proceeding "
                                        "(may select items suboptimally since changes to the bloodweb will be "
                                        "registered with a delay).",
                                        Font(10))
        self.on_select_speed(runtime.speed())

        self.limitsLabel = TextLabel(self, "bloodwebPageLimitsLabel", "Limits", Font(12))
        self.limitsDescription = TextLabel(self, "bloodwebPageLimitsDescription",
                                           "If multiple of the following limits are selected, the program "
                                           "will terminate when any limit is reached.")

        self.prestigeRow = QWidget(self)
        self.prestigeRow.setObjectName("bloodwebPagePrestigeRow")
        self.prestigeRowLayout = RowLayout(self.prestigeRow, "bloodwebPagePrestigeRowLayout")

        p_enabled, p_value = runtime.limits("prestige", ["enabled", "value"])
        self.prestigeCheckBox = CheckBoxWithFunction(self.prestigeRow, "bloodwebPagePrestigeCheckBox",
                                                     self.on_toggle_prestige_limit)
        self.prestigeCheckBox.setChecked(p_enabled)
        self.prestigeLabel = TextLabel(self.prestigeRow, "bloodwebPagePrestigeLabel", "Prestige Limit")
        self.prestigeInput = TextInputBox(self.prestigeRow, "bloodwebPagePrestigeInput", QSize(94, 40), "Enter levels",
                                          p_value)
        self.prestigeInput.setReadOnly(not p_enabled)
        self.on_toggle_prestige_limit()
        self.prestigeInput.textEdited.connect(self.on_edit_prestige_limit_input)
        self.prestigeDescription = TextLabel(self.prestigeRow, "bloodwebPagePrestigeDescription",
                                             "The number of prestige levels to complete before terminating "
                                             "(any integer from 1 to 100).", Font(10))

        self.bloodpointRow = QWidget(self)
        self.bloodpointRow.setObjectName("bloodwebPageBloodpointRow")
        self.bloodpointRowLayout = RowLayout(self.bloodpointRow, "bloodwebPageBloodpointRowLayout")

        b_enabled, b_value = runtime.limits("bloodpoint", ["enabled", "value"])
        self.bloodpointCheckBox = CheckBoxWithFunction(self.prestigeRow, "bloodwebPageBloodpointCheckBox",
                                                       self.on_toggle_bloodpoint_limit)
        self.bloodpointCheckBox.setChecked(b_enabled)
        self.bloodpointLabel = TextLabel(self.prestigeRow, "bloodwebPageBloodpointLabel", "Bloodpoint Limit")
        self.bloodpointInput = TextInputBox(self.prestigeRow, "bloodwebPageBloodpointInput", QSize(142, 40),
                                            "Enter bloodpoints", b_value)
        self.bloodpointInput.setReadOnly(not b_enabled)
        self.on_toggle_bloodpoint_limit()
        self.bloodpointInput.textEdited.connect(self.on_edit_bloodpoint_limit_input)
        self.bloodpointDescription = TextLabel(self.prestigeRow, "bloodwebPageBloodpointDescription",
                                               "The number of bloodpoints to spend before terminating.", Font(10))
        if dev_mode:
            self.devLabel = TextLabel(self, "bloodwebPageDevLabel", "Dev Options", Font(12))

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
        self.runPrestigeProgress.setVisible(False)
        self.runBloodpointProgress = TextLabel(self, "bloodwebPageRunBloodpointProgress", "", Font(10))
        self.runBloodpointProgress.setVisible(False)

        self.naiveRowLayout.addWidget(self.naiveCheckBox)
        self.naiveRowLayout.addWidget(self.naiveDescription)
        self.naiveRowLayout.addStretch(1)
        self.awareSingleRowLayout.addWidget(self.awareSingleCheckBox)
        self.awareSingleRowLayout.addWidget(self.awareSingleDescription)
        self.awareSingleRowLayout.addStretch(1)
        self.awareMultiRowLayout.addWidget(self.awareMultiCheckBox)
        self.awareMultiRowLayout.addWidget(self.awareMultiDescription)
        self.awareMultiRowLayout.addStretch(1)

        self.speedSlowRowLayout.addWidget(self.speedSlowCheckBox)
        self.speedSlowRowLayout.addWidget(self.speedSlowLabel)
        self.speedSlowRowLayout.addStretch(1)

        self.speedFastRowLayout.addWidget(self.speedFastCheckBox)
        self.speedFastRowLayout.addWidget(self.speedFastLabel)
        self.speedFastRowLayout.addStretch(1)

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
        self.scrollAreaContentLayout.addWidget(self.awareSingleRow)
        self.scrollAreaContentLayout.addWidget(self.awareMultiRow)
        self.scrollAreaContentLayout.addWidget(self.speedLabel)
        self.scrollAreaContentLayout.addWidget(self.speedSlowRow)
        self.scrollAreaContentLayout.addWidget(self.speedFastRow)
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