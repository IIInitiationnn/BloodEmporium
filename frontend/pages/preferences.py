import json
import math
import os
import sys

from PIL import Image, ImageQt
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout, QVBoxLayout, QToolButton, QInputDialog, QMessageBox, \
    QFileDialog

from frontend.dialogs import InputDialog, ConfirmDialog
from frontend.generic import Font, TextLabel, TextInputBox, Selector, Button, CheckBoxWithFunction, CheckBox, \
    CollapsibleBox, Icons, NoShiftStyle, ScrollBar, ScrollArea, ScrollAreaContent, MultiLineTextInputBox
from frontend.layouts import RowLayout
from frontend.stylesheets import StyleSheets

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.config import Config
from backend.data import Data, Unlockable
from backend.paths import Path
from backend.util.text_util import TextUtil


class FilterOptionsCollapsibleBox(CollapsibleBox):
    def __init__(self, parent, object_name, on_click):
        super().__init__(parent, object_name, "Filter Options (Click to Expand)")
        self.on_click = on_click # when a filter is set

        self.filters = QWidget(self)
        self.filters.setMinimumHeight(0)
        self.filters.setMaximumHeight(0)

        self.filtersLayout = QGridLayout(self.filters)
        self.filtersLayout.setContentsMargins(0, 0, 0, 0)
        self.filtersLayout.setSpacing(15)

        # filter buttons
        self.filterButtonsRow = QWidget(self)
        self.filterButtonsRow.setObjectName("preferencesPageFilterButtonsRow")
        self.filterButtonsRowLayout = RowLayout(self.filterButtonsRow, "preferencesPageFilterButtonsRowLayout")

        self.clearFiltersButton = Button(self.filters, "preferencesPageClearFiltersButton", "Clear Filters",
                                         QSize(100, 35))
        self.clearFiltersButton.clicked.connect(self.clear_filters)

        self.killersFiltersButton = Button(self.filters, "preferencesPageKillersFiltersButton", "Select All Killers",
                                           QSize(125, 35))
        self.killersFiltersButton.clicked.connect(self.filter_killers)

        self.filterButtonsRowLayout.addWidget(self.clearFiltersButton)
        self.filterButtonsRowLayout.addWidget(self.killersFiltersButton)
        self.filterButtonsRowLayout.addStretch(1)
        self.filtersLayout.addWidget(self.filterButtonsRow, 0, 0, 2, 10)
        # 10 is bandaid; should really fix filtersLayout to have 0 horizontal spacing and add gap between boxes and txt

        # character
        self.num_per_row = 10
        categories = Data.get_categories(True)
        num_character_columns = math.ceil(len(categories) / self.num_per_row) * 2 + 1 # extra 1 for a gap
        self.characterHeading = TextLabel(self.filters, "characterHeading", "Character")
        self.filtersLayout.addWidget(self.characterHeading, 2, 0, 1, num_character_columns)

        self.characterCheckBoxes = {}
        for i, character in enumerate(categories):
            checkbox = CheckBoxWithFunction(self.filters, f"{TextUtil.camel_case(character)}CharacterFilterCheckBox",
                                            on_click)
            checkbox.setFixedSize(25, 25)
            self.characterCheckBoxes[character] = checkbox
            self.filtersLayout.addWidget(checkbox, (i % self.num_per_row + 3), (i // self.num_per_row) * 2, 1, 1)

            label = TextLabel(self.filters, f"{TextUtil.camel_case(character)}CharacterFilterLabel",
                              TextUtil.title_case(character))
            self.filtersLayout.addWidget(label, (i % self.num_per_row + 3), (i // self.num_per_row) * 2 + 1, 1, 1)

        # rarity
        self.rarityHeading = TextLabel(self.filters, "rarityHeading", "Rarity")
        self.filtersLayout.addWidget(self.rarityHeading, 2, num_character_columns, 1, 2)

        self.rarityCheckBoxes = {}
        for i, rarity in enumerate(Data.get_rarities(), 3):
            checkbox = CheckBoxWithFunction(self.filters, f"{TextUtil.camel_case(rarity)}RarityFilterCheckBox",
                                            on_click)
            checkbox.setFixedSize(25, 25)
            self.rarityCheckBoxes[rarity] = checkbox
            self.filtersLayout.addWidget(checkbox, i, num_character_columns, 1, 1)

            label = TextLabel(self.filters, f"{TextUtil.camel_case(rarity)}RarityFilterLabel",
                              TextUtil.title_case(rarity))
            self.filtersLayout.addWidget(label, i, num_character_columns + 1, 1, 1)

        # type
        self.typeHeading = TextLabel(self.filters, "typeHeading", "Type")
        self.filtersLayout.addWidget(self.typeHeading, 2, num_character_columns + 2, 1, 2)

        self.typeCheckBoxes = {}
        for i, unlockable_type in enumerate(Data.get_types(), 3):
            checkbox = CheckBoxWithFunction(self.filters, f"{TextUtil.camel_case(unlockable_type)}TypeFilterCheckBox",
                                            on_click)
            checkbox.setFixedSize(25, 25)
            self.typeCheckBoxes[unlockable_type] = checkbox
            self.filtersLayout.addWidget(checkbox, i, num_character_columns + 2, 1, 1)

            label = TextLabel(self.filters, f"{TextUtil.camel_case(unlockable_type)}TypeFilterLabel",
                              TextUtil.title_case(unlockable_type))
            self.filtersLayout.addWidget(label, i, num_character_columns + 3, 1, 1)

        self.filtersLayout.setColumnStretch(999, 1)
        self.filtersLayout.setRowStretch(999, 1)

        self.layout.addWidget(self.filters, alignment=Qt.AlignTop)

    def get_character_filters(self):
        return [name for name, checkbox in self.characterCheckBoxes.items() if checkbox.isChecked()]

    def get_rarity_filters(self):
        return [name for name, checkbox in self.rarityCheckBoxes.items() if checkbox.isChecked()]

    def get_type_filters(self):
        return [name for name, checkbox in self.typeCheckBoxes.items() if checkbox.isChecked()]

    def on_pressed(self):
        if self.toggleButton.isChecked():
            self.toggleButton.setStyleSheet(StyleSheets.collapsible_box_active)
            self.toggleButton.setIcon(QIcon(Icons.right_arrow))
            self.toggleButton.setText("Filter Options (Click to Expand)")
            self.filters.setMinimumHeight(0)
            self.filters.setMaximumHeight(0)
        else:
            self.toggleButton.setStyleSheet(StyleSheets.collapsible_box_inactive)
            self.toggleButton.setIcon(QIcon(Icons.down_arrow))
            self.toggleButton.setText("Filter Options (Click to Collapse)")
            self.filters.setMinimumHeight(round(40 * (self.num_per_row + 1.5)))
            self.filters.setMaximumHeight(round(40 * (self.num_per_row + 1.5)))

    def clear_filters(self):
        for checkboxes in self.characterCheckBoxes, self.rarityCheckBoxes, self.typeCheckBoxes:
            for checkbox in checkboxes.values():
                checkbox.setChecked(False)
        self.on_click()

    def filter_killers(self):
        killers = Data.get_killers(False)
        for character, checkbox in self.characterCheckBoxes.items():
            if character in killers:
                checkbox.setChecked(True)
        self.on_click()

class UnlockableWidget(QWidget):
    def __init__(self, parent, unlockable: Unlockable, tier, subtier, on_unlockable_select):
        name = TextUtil.camel_case(unlockable.name)

        super().__init__(parent)
        self.setObjectName(f"{name}Widget")
        self.unlockable = unlockable

        self.layout = RowLayout(self, f"{name}Layout")

        self.checkBox = CheckBox(self, f"{name}CheckBox")
        self.checkBox.setFixedSize(25, 25)
        self.checkBox.clicked.connect(on_unlockable_select)
        self.layout.addWidget(self.checkBox)

        self.image = QLabel(self)
        self.image.setObjectName(f"{name}Image")
        self.image.setFixedSize(QSize(75, 75))
        self.refresh_icon()
        self.image.setScaledContents(True)
        self.image.setToolTip(f"""Character: {TextUtil.title_case(unlockable.category)}
Rarity: {TextUtil.title_case(unlockable.rarity)}
Type: {TextUtil.title_case(unlockable.type)}""")
        self.layout.addWidget(self.image)

        self.label = QLabel(self)
        self.label.setObjectName(f"{name}Label")
        self.label.setFont(Font(10))
        self.label.setStyleSheet(StyleSheets.white_text)
        self.label.setText(unlockable.name)
        self.layout.addWidget(self.label)

        self.layout.addSpacing(250 - self.label.fontMetrics().boundingRect(self.label.text()).width())

        self.tierLabel = QLabel(self)
        self.tierLabel.setObjectName(f"{name}TierLabel")
        self.tierLabel.setFont(Font(10))
        self.tierLabel.setStyleSheet(StyleSheets.white_text)
        self.tierLabel.setText("Tier")
        self.layout.addWidget(self.tierLabel)

        self.tierInput = TextInputBox(self, f"{name}TierInput", QSize(110, 40), "Enter tier", str(tier),
                                      style_sheet=StyleSheets.tiers_input(tier))
        self.tierInput.textEdited.connect(self.on_tier_update)
        self.layout.addWidget(self.tierInput)

        self.subtierLabel = QLabel(self)
        self.subtierLabel.setObjectName(f"{name}TierLabel")
        self.subtierLabel.setFont(Font(10))
        self.subtierLabel.setStyleSheet(StyleSheets.white_text)
        self.subtierLabel.setText("Subtier")
        self.layout.addWidget(self.subtierLabel)

        self.subtierInput = TextInputBox(self, f"{name}SubtierInput", QSize(110, 40), "Enter subtier", str(subtier),
                                         style_sheet=StyleSheets.tiers_input(tier))
        self.subtierInput.textEdited.connect(self.on_subtier_update)
        self.layout.addWidget(self.subtierInput)

        self.layout.addStretch(1)

    def on_tier_update(self):
        self.tierInput.setStyleSheet(StyleSheets.tiers_input(self.tierInput.text()))

    def on_subtier_update(self):
        self.subtierInput.setStyleSheet(StyleSheets.tiers_input(self.subtierInput.text()))

    def setTiers(self, tier=None, subtier=None):
        if tier is not None:
            self.tierInput.setText(str(tier))
            self.tierInput.setStyleSheet(StyleSheets.tiers_input(tier))
        if subtier is not None:
            self.subtierInput.setText(str(subtier))
            self.subtierInput.setStyleSheet(StyleSheets.tiers_input(subtier))

    def getTiers(self):
        return int(self.tierInput.text()), int(self.subtierInput.text())

    def refresh_icon(self):
        if self.unlockable.is_custom_icon:
            self.image.setPixmap(QPixmap(self.unlockable.image_path))
        else:
            try:
                bg = Image.open(f"{Path.assets_backgrounds}/{self.unlockable.rarity}.png")
                icon = Image.open(self.unlockable.image_path)
                combined = Image.alpha_composite(bg, icon)
                self.image.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(combined)))
            except:
                print(f"error adding background to {self.unlockable.unique_id}")
                self.image.setPixmap(QPixmap(self.unlockable.image_path))

class PreferencesPage(QWidget):
    def get_edit_profile(self):
        return self.profileSelector.currentText() if self.profileSelector.count() > 0 else None

    def update_profiles_from_config(self):
        config = Config()
        while self.profileSelector.count() > 0:
            self.profileSelector.removeItem(0)
        self.profileSelector.addItems(config.profile_names())

        while self.bloodwebPage.profileSelector.count() > 0:
            self.bloodwebPage.profileSelector.removeItem(0)
        self.bloodwebPage.profileSelector.addItems(config.profile_names())

    def has_unsaved_changes(self):
        config = Config()
        profile_id = self.get_edit_profile()
        if profile_id is None:
            return False

        profile = config.get_profile_by_id(profile_id)

        non_integer = Config.verify_tiers(self.unlockableWidgets)
        if len(non_integer) > 0:
            return True

        for widget in self.unlockableWidgets:
            tier, subtier = widget.getTiers()
            config_tier, config_subtier = config.preference_by_profile(widget.unlockable.unique_id, profile)
            if tier != config_tier or subtier != config_subtier:
                return True

        if self.profileNotes.toPlainText() != config.notes_by_id(profile_id):
            return True

        return False

    # TODO optimise?
    def replace_unlockable_widgets(self):
        sort_by = self.sortSelector.currentText()

        if self.lastSortedBy == sort_by:
            # if there was no change in ordering, don't pass in sort_by; the resulting visible list has arbitrary order
            for widget, is_visible in Data.filter(self.unlockableWidgets,
                                                  self.searchBar.text(),
                                                  self.filtersBox.get_character_filters(),
                                                  self.filtersBox.get_rarity_filters(),
                                                  self.filtersBox.get_type_filters()):
                widget.setVisible(is_visible)
        else:
            # lastSortedBy was changed on this event; we need visible to be ordered to insert widgets correctly
            for widget in self.unlockableWidgets:
                self.scrollAreaContentLayout.removeWidget(widget)

            for widget, is_visible in Data.filter(self.unlockableWidgets,
                                                  self.searchBar.text(),
                                                  self.filtersBox.get_character_filters(),
                                                  self.filtersBox.get_rarity_filters(),
                                                  self.filtersBox.get_type_filters(),
                                                  sort_by):
                count = self.scrollAreaContentLayout.count()
                self.scrollAreaContentLayout.insertWidget(count - 1, widget)
                widget.setVisible(is_visible)

        self.lastSortedBy = sort_by
        self.on_unlockable_select()

    def switch_edit_profile(self):
        if not self.ignore_profile_signals:
            # TODO prompt: unsaved changes (save or discard) - override profile selector currentindexchanged method?
            config = Config()
            profile_id = self.get_edit_profile()
            for widget in self.unlockableWidgets:
                widget.setTiers(*config.preference_by_id(widget.unlockable.unique_id, profile_id))
            self.profileNotes.setPlainText(config.notes_by_id(profile_id))

    def new_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True
            if self.has_unsaved_changes():
                save_profile_dialog = ConfirmDialog("You have unsaved changes to the current profile. "
                                                    "Do you wish to save or discard these changes?",
                                                    "Save", "Discard")
                confirmation = save_profile_dialog.exec()
                if confirmation == QMessageBox.AcceptRole:
                    self.save_profile()

            config = Config()
            profile_id = config.get_next_free_profile_name()
            config.add_profile({"id": profile_id, "notes": ""})

            self.update_profiles_from_config()
            index = self.profileSelector.findText(profile_id)
            self.profileSelector.setCurrentIndex(index)
            self.show_preferences_page_save_success(f"New empty profile created: {profile_id}")

            self.ignore_profile_signals = False
            self.switch_edit_profile()

    def save_profile(self):
        profile_id = self.get_edit_profile()
        if profile_id is None:
            return
        updated_profile = Config().get_profile_by_id(profile_id).copy()
        updated_profile["notes"] = self.profileNotes.toPlainText()

        non_integer = Config.verify_tiers(self.unlockableWidgets)
        if len(non_integer) > 0:
            self.show_preferences_page_save_error(f"There are {len(non_integer)} unlockables with invalid "
                                                  "inputs. Inputs must be a number from -999 to 999. Changes "
                                                  "not saved.")
            return

        for widget in self.unlockableWidgets:
            tier, subtier = widget.getTiers()
            if tier != 0 or subtier != 0:
                updated_profile[widget.unlockable.unique_id] = {"tier": tier, "subtier": subtier}
            else:
                updated_profile.pop(widget.unlockable.unique_id, None)
        Config().set_profile(updated_profile)

        self.show_preferences_page_save_success(f"Changes saved to profile: {profile_id}")
        QTimer.singleShot(10000, self.hide_preferences_page_save_text)

    def save_to_profile(self, title, label_text, ok_button_text, index=None):
        # check for invalid tiers
        non_integer = Config.verify_tiers(self.unlockableWidgets)
        if len(non_integer) > 0:
            self.show_preferences_page_save_error(f"There are {len(non_integer)} unlockables with "
                                                  "invalid inputs. Inputs must be a number from -999 to "
                                                  "999. Changes not saved.")
            return

        # save or cancel
        new_profile_dialog = InputDialog(title, label_text, QInputDialog.TextInput, ok_button_text)
        selection = new_profile_dialog.exec()
        if selection != QInputDialog.Accepted:
            return

        # check if user wants to overwrite profile
        profile_id = new_profile_dialog.textValue()
        if Config().is_profile(profile_id):
            overwrite_profile_dialog = ConfirmDialog("This will overwrite an existing profile. Are you "
                                                     "sure you want to save?")
            confirmation = overwrite_profile_dialog.exec()
            if confirmation != QMessageBox.AcceptRole:
                return

        # user either wants to overwrite, or is saving new profile
        new_profile = {"id": profile_id, "notes": self.profileNotes.toPlainText()}

        for widget in self.unlockableWidgets:
            tier, subtier = widget.getTiers()
            if tier != 0 or subtier != 0:
                new_profile[widget.unlockable.unique_id] = {"tier": tier, "subtier": subtier}

        already_existed = Config().add_profile(new_profile, index)

        self.update_profiles_from_config()
        index = self.profileSelector.findText(profile_id)
        self.profileSelector.setCurrentIndex(index)

        if already_existed:
            self.show_preferences_page_save_success(f"Existing profile overridden with changes: {profile_id}")
        else:
            self.show_preferences_page_save_success(f"Changes saved to profile: {profile_id}")
        return profile_id

    def save_as_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True # saving as new profile; don't trigger
            self.save_to_profile("Save As", "Enter your new profile name:", "Save")
            self.ignore_profile_signals = False

    def rename_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True

            old_profile_id = self.get_edit_profile()
            if old_profile_id is None:
                self.ignore_profile_signals = False
                return
            index = self.profileSelector.currentIndex()

            # save as
            new_profile_id = self.save_to_profile("Save and Rename", "Enter your new profile name:", "Save and Rename",
                                                  index)
            if new_profile_id is None:
                self.ignore_profile_signals = False
                return

            # same name
            if old_profile_id == new_profile_id:
                self.ignore_profile_signals = False
                return

            # delete
            Config().delete_profile(old_profile_id)
            self.update_profiles_from_config()
            self.profileSelector.setCurrentIndex(index)

            self.ignore_profile_signals = False
            self.switch_edit_profile()

    def delete_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True
            profile_id = self.get_edit_profile()
            if profile_id is None:
                self.ignore_profile_signals = False
                return

            # confirm if user wants to delete
            delete_profile_dialog = ConfirmDialog("Are you sure you want to delete this profile?")
            confirmation = delete_profile_dialog.exec()
            if confirmation != QMessageBox.AcceptRole:
                self.ignore_profile_signals = False
                return

            Config().delete_profile(profile_id)

            self.update_profiles_from_config()
            self.profileSelector.setCurrentIndex(0)
            self.ignore_profile_signals = False
            self.switch_edit_profile()

            self.show_preferences_page_save_success(f"Profile deleted: {profile_id}")

            self.ignore_profile_signals = False

    def export_profile(self):
        if self.has_unsaved_changes():
            save_profile_dialog = ConfirmDialog("You have unsaved changes to the current profile. "
                                                "Do you wish to save these changes or cancel the export?",
                                                "Save", "Cancel")
            confirmation = save_profile_dialog.exec()
            if confirmation == QMessageBox.AcceptRole:
                self.save_profile()
            else:
                return

        profile_id = self.get_edit_profile()
        Config().export_profile(profile_id)
        self.show_preferences_page_save_success(f"Profile exported to \"{profile_id}.emp\". Share it with friends!")

    def import_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True

            if self.has_unsaved_changes():
                save_profile_dialog = ConfirmDialog("You have unsaved changes to the current profile. "
                                                    "Do you wish to save these changes or cancel the import?",
                                                    "Save", "Cancel")
                confirmation = save_profile_dialog.exec()
                if confirmation == QMessageBox.AcceptRole:
                    self.save_profile()
                else:
                    self.ignore_profile_signals = False
                    return

            path, _ = QFileDialog.getOpenFileName(self, "Select .emp File to Import",
                                                  filter="Blood Emporium Profile Files (*.emp)")
            if path == "":
                self.ignore_profile_signals = False
                return

            try:
                with open(path, "r") as file:
                    profile = dict(json.load(file))
                    profile_id = profile["id"]
                    if Config().is_profile(profile_id):
                        overwrite_profile_dialog = ConfirmDialog("This will overwrite an existing profile. Are you "
                                                                 "sure you want to import?")
                        confirmation = overwrite_profile_dialog.exec()
                        if confirmation != QMessageBox.AcceptRole:
                            self.ignore_profile_signals = False
                            return

                    Config().add_profile(profile)
            except:
                self.show_preferences_page_save_error(f"Profile file ({path}) malformed.")
                self.ignore_profile_signals = False
                return

            self.update_profiles_from_config()
            index = self.profileSelector.findText(profile_id)
            self.profileSelector.setCurrentIndex(index)

            self.show_preferences_page_save_success(f"Profile: {profile_id} successfully imported.")
            self.ignore_profile_signals = False
            self.switch_edit_profile()

    def open_exports_folder(self):
        os.startfile(f"{os.getcwd()}\\exports")

    def show_preferences_page_save_success(self, text):
        self.saveSuccessText.setText(text)
        self.saveSuccessText.setStyleSheet(StyleSheets.pink_text)
        self.saveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_preferences_page_save_text)

    def show_preferences_page_save_error(self, text):
        self.saveSuccessText.setText(text)
        self.saveSuccessText.setStyleSheet(StyleSheets.purple_text)
        self.saveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_preferences_page_save_text)

    def hide_preferences_page_save_text(self):
        self.saveSuccessText.setVisible(False)

    def selected_widgets(self):
        return [widget for widget in self.unlockableWidgets if widget.checkBox.isChecked()]

    def on_unlockable_select(self):
        num_selected = len(self.selected_widgets())
        self.selectedLabel.setText(f"{num_selected} selected")

        self.allCheckbox.setChecked(num_selected > 0)
        self.allCheckbox.setStyleSheet(StyleSheets.check_box_all
                                       if all([widget.checkBox.isChecked() for widget in
                                               [widget for widget in self.unlockableWidgets if widget.isVisible()]])
                                       else StyleSheets.check_box_some)
        self.allCheckbox.setToolTip("Deselect All" if num_selected > 0 else "Select All")

    def on_unlockable_select_all(self):
        checked = self.allCheckbox.isChecked() # whether checkbox is select all (T) or deselect all (F)

        if checked:
            for widget in self.unlockableWidgets:
                if widget.isVisible():
                    widget.checkBox.setChecked(True)
        else:
            for widget in self.unlockableWidgets:
                widget.checkBox.setChecked(False)

        self.on_unlockable_select()

    def expand_edit(self):
        new_pos = self.editDropdownButton.mapTo(self, self.editDropdownButton.pos())
        new_pos.setY(new_pos.y() - 250)
        # TODO move this new_pos into an event handler
        #  (https://stackoverflow.com/questions/15238973/how-do-i-set-a-relative-position-for-a-qt-widget)
        #  - will work for resizing

        if self.editDropdownButton.isChecked():
            self.editDropdownButton.setStyleSheet(StyleSheets.collapsible_box_active)
            self.editDropdownButton.setIcon(QIcon(Icons.right_arrow))
            self.editDropdownContent.setMinimumHeight(0)
            self.editDropdownContent.setMaximumHeight(0)
            self.editDropdownContent.move(new_pos)
        else:
            self.editDropdownButton.setStyleSheet(StyleSheets.collapsible_box_inactive)
            self.editDropdownButton.setIcon(QIcon(Icons.up_arrow))
            self.editDropdownContent.setMinimumHeight(200)
            self.editDropdownContent.setMaximumHeight(200)
            self.editDropdownContent.move(new_pos)

    def on_edit_dropdown_tier(self):
        if self.editDropdownContentTierCheckBox.isChecked():
            self.editDropdownContentTierInput.setReadOnly(False)
            text = self.editDropdownContentTierInput.text()
            self.editDropdownContentTierInput.setStyleSheet(StyleSheets.tiers_input(text))
        else:
            self.editDropdownContentTierInput.setReadOnly(True)

    def on_edit_dropdown_subtier(self):
        if self.editDropdownContentSubtierCheckBox.isChecked():
            self.editDropdownContentSubtierInput.setReadOnly(False)
            text = self.editDropdownContentSubtierInput.text()
            self.editDropdownContentSubtierInput.setStyleSheet(StyleSheets.tiers_input(text))
        else:
            self.editDropdownContentSubtierInput.setReadOnly(True)

    def on_edit_dropdown_tier_input(self):
        text = self.editDropdownContentTierInput.text()
        self.editDropdownContentTierInput.setStyleSheet(StyleSheets.tiers_input(text))

    def on_edit_dropdown_subtier_input(self):
        text = self.editDropdownContentSubtierInput.text()
        self.editDropdownContentSubtierInput.setStyleSheet(StyleSheets.tiers_input(text))

    def on_edit_dropdown_apply(self):
        tier = self.editDropdownContentTierInput.text()
        subtier = self.editDropdownContentSubtierInput.text()
        for widget in self.selected_widgets():
            if self.editDropdownContentTierCheckBox.isChecked():
                widget.setTiers(tier=tier)
            if self.editDropdownContentSubtierCheckBox.isChecked():
                widget.setTiers(subtier=subtier)
        self.on_edit_dropdown_minimise()

    def on_edit_dropdown_minimise(self):
        if self.editDropdownContentTierCheckBox.isChecked():
            self.editDropdownContentTierCheckBox.animateClick()
        if self.editDropdownContentSubtierCheckBox.isChecked():
            self.editDropdownContentSubtierCheckBox.animateClick()
        self.editDropdownContentTierInput.setText("0")
        self.editDropdownContentSubtierInput.setText("0")
        self.editDropdownButton.animateClick()
        self.expand_edit()

    def refresh_unlockables(self):
        icons = Data.get_icons()
        for unlockableWidget in self.unlockableWidgets:
            info = icons[unlockableWidget.unlockable.unique_id]
            unlockableWidget.unlockable.set_image_path(info["image_path"])
            unlockableWidget.unlockable.set_is_custom_icon(info["is_custom_icon"])
            unlockableWidget.refresh_icon()

    def __init__(self, bloodweb_page):
        super().__init__()
        self.ignore_profile_signals = False # used to prevent infinite recursion e.g. when setting dropdown to a profile
        self.bloodwebPage = bloodweb_page # for updating profiles from config; necessary coupling
        self.setObjectName("preferencesPage")
        config = Config()

        self.layout = QGridLayout(self)
        self.layout.setObjectName("preferencesPageLayout")
        self.layout.setContentsMargins(25, 25, 25, 0)
        self.layout.setSpacing(0)

        self.scrollBar = ScrollBar(self, "preferencesPage")
        self.scrollArea = ScrollArea(self, "preferencesPage", self.scrollBar)
        self.scrollAreaContent = ScrollAreaContent(self.scrollArea, "preferencesPage")
        self.scrollArea.setWidget(self.scrollAreaContent)
        self.scrollAreaContentLayout = QVBoxLayout(self.scrollAreaContent)
        self.scrollAreaContentLayout.setObjectName("preferencesPageScrollAreaContentLayout")
        self.scrollAreaContentLayout.setContentsMargins(0, 0, 0, 25)
        self.scrollAreaContentLayout.setSpacing(15)

        # save, rename, delete
        self.profileSaveRow = QWidget(self.scrollAreaContent)
        self.profileSaveRow.setObjectName("preferencesPageProfileSaveRow")
        self.profileSaveRowLayout = RowLayout(self.profileSaveRow, "preferencesPageProfileSaveRowLayout")

        self.profileLabel = TextLabel(self.scrollAreaContent, "preferencesPageProfileLabel", "Preference Profile",
                                      Font(12))

        self.profileSelector = Selector(self.profileSaveRow, "preferencesPageProfileSelector", QSize(250, 40),
                                        config.profile_names())
        self.profileSelector.currentIndexChanged.connect(self.switch_edit_profile)

        self.saveSuccessText = TextLabel(self.profileSaveRow, "preferencesPageSaveSuccessText", "", Font(10))
        self.saveSuccessText.setVisible(False)

        self.profileSaveRow2 = QWidget(self.scrollAreaContent)
        self.profileSaveRow2.setObjectName("preferencesPageProfileSaveRow2")
        self.profileSaveRow2Layout = RowLayout(self.profileSaveRow2, "preferencesPageProfileSaveRow2Layout")

        self.newProfileButton = Button(self.profileSaveRow2, "preferencesPageNewProfileButton", "New Profile",
                                       QSize(95, 35))
        self.newProfileButton.clicked.connect(self.new_profile)

        self.saveButton = Button(self.profileSaveRow2, "preferencesPageSaveButton", "Save", QSize(60, 35))
        self.saveButton.clicked.connect(self.save_profile)

        self.saveAsButton = Button(self.profileSaveRow2, "preferencesPageSaveAsButton", "Save As", QSize(80, 35))
        self.saveAsButton.clicked.connect(self.save_as_profile)

        self.renameButton = Button(self.profileSaveRow2, "preferencesPageRenameButton", "Save and Rename",
                                   QSize(130, 35))
        self.renameButton.clicked.connect(self.rename_profile)

        self.deleteButton = Button(self.profileSaveRow2, "preferencesPageDeleteButton", "Delete", QSize(70, 35))
        self.deleteButton.clicked.connect(self.delete_profile)

        self.profileExchangeRow = QWidget(self.scrollAreaContent)
        self.profileExchangeRow.setObjectName("preferencesPageProfileExchangeRow")
        self.profileExchangeRowLayout = RowLayout(self.profileExchangeRow, "preferencesPageProfileExchangeRowLayout")

        self.exportButton = Button(self.profileExchangeRow, "preferencesExportButton", "Export Profile to File",
                                   QSize(150, 35))
        self.exportButton.clicked.connect(self.export_profile)

        self.importButton = Button(self.profileExchangeRow, "preferencesPageImportButton", "Import Profile from File",
                                   QSize(165, 35))
        self.importButton.clicked.connect(self.import_profile)

        self.openExportsButton = Button(self.profileExchangeRow, "preferencesPageOpenExportsButton",
                                        "Open Folder to Exported Profiles", QSize(220, 35))
        self.openExportsButton.clicked.connect(self.open_exports_folder)

        self.profileNotes = MultiLineTextInputBox(self.scrollAreaContent, "preferencesPageProfileNotes",
                                                  450, 100, 150, "Notes for this profile")
        self.profileNotes.setPlainText(Config().notes_by_id(self.get_edit_profile()))

        # filters
        self.filtersBox = FilterOptionsCollapsibleBox(self.scrollAreaContent, "preferencesPageFiltersBox",
                                                      self.replace_unlockable_widgets)

        # search bar & sort
        self.searchSortRow = QWidget(self.scrollAreaContent)
        self.searchSortRow.setObjectName("preferencesPageSearchSortRow")
        self.searchSortRowLayout = RowLayout(self.searchSortRow, "preferencesPageSearchSortRowLayout")

        self.searchBar = TextInputBox(self.searchSortRow, "preferencesPageSearchBar", QSize(250, 40), "Search by name")
        self.searchBar.textEdited.connect(self.replace_unlockable_widgets)
        self.sortLabel = TextLabel(self.searchSortRow, "preferencesPageSortLabel", "Sort by")
        self.sortSelector = Selector(self.searchSortRow, "preferencesPageSortSelector", QSize(120, 40),
                                     Data.get_sorts())
        self.sortSelector.currentIndexChanged.connect(self.replace_unlockable_widgets)
        self.lastSortedBy = "name" # cache of last sort

        self.refreshIconsButton = Button(self.scrollAreaContent, "preferencesPageRefreshIconsButton", "Refresh Icons",
                                         QSize(105, 35))
        self.refreshIconsButton.clicked.connect(self.refresh_unlockables)

        # all unlockables
        self.unlockableWidgets = [UnlockableWidget(self.scrollAreaContent, unlockable,
                                                   *config.preference_by_id(unlockable.unique_id,
                                                                            self.get_edit_profile()),
                                                   self.on_unlockable_select)
                                  for unlockable in Data.get_unlockables()
                                  if unlockable.category not in ["unused", "retired"]]

        # select all bar
        self.persistentBar = QWidget(self)
        self.persistentBar.setObjectName("preferencesPagePersistentBar")
        self.persistentBar.setStyleSheet(f"""
        QWidget#preferencesPagePersistentBar {{
            border-top: 4px solid {StyleSheets.background};
        }}""")
        self.persistentBar.setMinimumHeight(80)
        self.persistentBarLayout = RowLayout(self.persistentBar, "preferencesPagePersistentBarLayout")

        self.allCheckbox = CheckBoxWithFunction(self.persistentBar, "preferencesPageAllCheckbox",
                                                self.on_unlockable_select_all, style_sheet=StyleSheets.check_box_all)
        self.allCheckbox.setToolTip("Select All")
        self.selectedLabel = TextLabel(self.persistentBar, "preferencesPageSelectedLabel", "0 selected")
        # TODO to the right, confirmation text like with saving

        # edit dropdown
        self.editDropdown = QWidget(self.persistentBar)
        self.editDropdown.setObjectName("preferencesPageEditDropdown")

        self.editDropdownLayout = QGridLayout(self.editDropdown)
        self.editDropdownLayout.setContentsMargins(0, 0, 0, 0)
        self.editDropdownLayout.setSpacing(0)

        self.editDropdownButton = QToolButton(self.editDropdown)
        self.editDropdownButton.setObjectName("preferencesPageEditDropdownButton")
        self.editDropdownButton.setCheckable(True)
        self.editDropdownButton.setChecked(False)
        self.editDropdownButton.setFont(Font(10))
        self.editDropdownButton.setStyleSheet(StyleSheets.collapsible_box_inactive)
        self.editDropdownButton.setText("Edit Selected")
        self.editDropdownButton.setIcon(QIcon(Icons.right_arrow))
        self.editDropdownButton.setIconSize(QSize(20, 20))
        self.editDropdownButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.editDropdownButton.setStyle(NoShiftStyle())
        self.editDropdownButton.pressed.connect(self.expand_edit)
        self.editDropdownButton.setCursor(Qt.PointingHandCursor)

        self.editDropdownContent = QWidget(self)
        self.editDropdownContent.setObjectName("preferencesPageEditDropdownContent")
        self.editDropdownContent.setMinimumHeight(0)
        self.editDropdownContent.setMaximumHeight(0)
        self.editDropdownContent.setFixedWidth(260)
        self.editDropdownContent.setStyleSheet(f"""
            QWidget#preferencesPageEditDropdownContent {{
                background-color: {StyleSheets.passive};
                border: 3px solid {StyleSheets.selection};
                border-radius: 3px;
            }}""")

        self.editDropdownContentLayout = QVBoxLayout(self.editDropdownContent)
        self.editDropdownContentLayout.setContentsMargins(25, 25, 25, 25)
        self.editDropdownContentLayout.setSpacing(15)

        self.editDropdownContentTierRow = QWidget(self.editDropdownContent)
        self.editDropdownContentTierRow.setObjectName("preferencesPageEditDropdownContentTierRow")
        self.editDropdownContentTierRowLayout = RowLayout(self.editDropdownContentTierRow,
                                                          "preferencesPageEditDropdownContentTierRowLayout")

        self.editDropdownContentTierCheckBox = CheckBoxWithFunction(self.editDropdownContentTierRow,
                                                                    "preferencesPageEditDropdownContentTierCheckBox",
                                                                    self.on_edit_dropdown_tier)
        self.editDropdownContentTierLabel = TextLabel(self.editDropdownContentTierRow,
                                                      "preferencesPageEditDropdownContentTierLabel", "Tier")
        self.editDropdownContentTierInput = TextInputBox(self.editDropdownContentTierRow,
                                                         "preferencesPageEditDropdownContentTierInput", QSize(110, 40),
                                                         "Enter tier", "0", style_sheet=StyleSheets.text_box_read_only)
        self.editDropdownContentTierInput.textEdited.connect(self.on_edit_dropdown_tier_input)
        self.editDropdownContentTierInput.setReadOnly(True)

        self.editDropdownContentSubtierRow = QWidget(self.editDropdownContent)
        self.editDropdownContentSubtierRow.setObjectName("preferencesPageEditDropdownContentSubtierRow")
        self.editDropdownContentSubtierRowLayout = RowLayout(self.editDropdownContentSubtierRow,
                                                             "preferencesPageEditDropdownContentSubtierRowLayout")

        self.editDropdownContentSubtierCheckBox = CheckBoxWithFunction(self.editDropdownContentSubtierRow,
                                                                       "preferencesPageEditDropdownContentSubtierCheckBox",
                                                                       self.on_edit_dropdown_subtier)
        self.editDropdownContentSubtierLabel = TextLabel(self.editDropdownContentSubtierRow,
                                                         "preferencesPageEditDropdownContentSubtierLabel",
                                                         "Subtier")
        self.editDropdownContentSubtierInput = TextInputBox(self.editDropdownContentSubtierRow,
                                                            "preferencesPageEditDropdownContentSubtierInput",
                                                            QSize(110, 40), "Enter subtier", "0",
                                                            style_sheet=StyleSheets.text_box_read_only)
        self.editDropdownContentSubtierInput.textEdited.connect(self.on_edit_dropdown_subtier_input)
        self.editDropdownContentSubtierInput.setReadOnly(True)

        self.editDropdownContentApplyRow = QWidget(self.editDropdownContent)
        self.editDropdownContentApplyRow.setObjectName("preferencesPageEditDropdownContentApplyRow")
        self.editDropdownContentApplyRowLayout = RowLayout(self.editDropdownContentApplyRow,
                                                           "preferencesPageEditDropdownContentApplyRowLayout")

        self.editDropdownContentApplyButton = Button(self.editDropdownContentApplyRow,
                                                     "preferencesPageEditDropdownContentApplyButton",
                                                     "Apply", QSize(70, 35))
        self.editDropdownContentApplyButton.clicked.connect(self.on_edit_dropdown_apply)

        self.editDropdownContentCancelButton = Button(self.editDropdownContentApplyRow,
                                                      "preferencesPageEditDropdownContentCancelButton",
                                                      "Cancel", QSize(70, 35))
        self.editDropdownContentCancelButton.clicked.connect(self.on_edit_dropdown_minimise)

        """
        preferencesPage
            -> scrollArea
                -> scrollAreaContent (widget)
                    -> labels, combobox, everything
            -> scrollBar
        """
        # rows comprising the content
        self.profileSaveRowLayout.addWidget(self.profileSelector)
        self.profileSaveRowLayout.addWidget(self.saveSuccessText)
        self.profileSaveRowLayout.addStretch(1)

        self.profileSaveRow2Layout.addWidget(self.newProfileButton)
        self.profileSaveRow2Layout.addWidget(self.saveButton)
        self.profileSaveRow2Layout.addWidget(self.saveAsButton)
        self.profileSaveRow2Layout.addWidget(self.renameButton)
        self.profileSaveRow2Layout.addWidget(self.deleteButton)
        self.profileSaveRow2Layout.addStretch(1)

        self.profileExchangeRowLayout.addWidget(self.exportButton)
        self.profileExchangeRowLayout.addWidget(self.importButton)
        self.profileExchangeRowLayout.addWidget(self.openExportsButton)
        self.profileExchangeRowLayout.addStretch(1)

        self.searchSortRowLayout.addWidget(self.searchBar)
        self.searchSortRowLayout.addWidget(self.sortLabel)
        self.searchSortRowLayout.addWidget(self.sortSelector)
        self.searchSortRowLayout.addStretch(1)

        # putting the rows into the content
        self.scrollAreaContentLayout.addWidget(self.profileLabel)
        self.scrollAreaContentLayout.addWidget(self.profileSaveRow)
        self.scrollAreaContentLayout.addWidget(self.profileSaveRow2)
        self.scrollAreaContentLayout.addWidget(self.profileExchangeRow)
        self.scrollAreaContentLayout.addWidget(self.profileNotes)
        self.scrollAreaContentLayout.addSpacing(10)
        self.scrollAreaContentLayout.addWidget(self.filtersBox)
        self.scrollAreaContentLayout.addWidget(self.searchSortRow)
        self.scrollAreaContentLayout.addWidget(self.refreshIconsButton)
        self.scrollAreaContentLayout.addSpacing(15)
        for unlockableWidget in self.unlockableWidgets:
            self.scrollAreaContentLayout.addWidget(unlockableWidget)
        self.scrollAreaContentLayout.addStretch(1)

        # bottom persistent bar
        self.editDropdownContentTierRowLayout.addWidget(self.editDropdownContentTierCheckBox)
        self.editDropdownContentTierRowLayout.addWidget(self.editDropdownContentTierLabel)
        self.editDropdownContentTierRowLayout.addStretch(1)
        self.editDropdownContentTierRowLayout.addWidget(self.editDropdownContentTierInput)

        self.editDropdownContentSubtierRowLayout.addWidget(self.editDropdownContentSubtierCheckBox)
        self.editDropdownContentSubtierRowLayout.addWidget(self.editDropdownContentSubtierLabel)
        self.editDropdownContentSubtierRowLayout.addStretch(1)
        self.editDropdownContentSubtierRowLayout.addWidget(self.editDropdownContentSubtierInput)

        self.editDropdownContentApplyRowLayout.addStretch(1)
        self.editDropdownContentApplyRowLayout.addWidget(self.editDropdownContentApplyButton)
        self.editDropdownContentApplyRowLayout.addWidget(self.editDropdownContentCancelButton)

        self.editDropdownContentLayout.addWidget(self.editDropdownContentTierRow)
        self.editDropdownContentLayout.addWidget(self.editDropdownContentSubtierRow)
        self.editDropdownContentLayout.addWidget(self.editDropdownContentApplyRow)

        self.editDropdownLayout.addWidget(self.editDropdownButton, 0, 0, 1, 1)

        self.persistentBarLayout.addWidget(self.allCheckbox)
        self.persistentBarLayout.addWidget(self.selectedLabel)
        self.persistentBarLayout.addWidget(self.editDropdown)
        self.persistentBarLayout.addStretch(1)

        # assembling it all together
        self.layout.addWidget(self.scrollArea, 0, 0, 1, 1)
        self.layout.addWidget(self.persistentBar, 1, 0, 1, 1, Qt.AlignBottom)
        self.layout.setRowStretch(0, 1)
        self.layout.setColumnStretch(0, 1)

        self.sortSelector.setCurrentIndex(1) # self.lastSortedBy becomes "character"