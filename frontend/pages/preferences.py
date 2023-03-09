import os
import sys

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout, QVBoxLayout, QScrollArea, QScrollBar, QToolButton, \
    QInputDialog, QMessageBox

from dialogs import InputDialog, ConfirmDialog
from frontend.generic import Font, TextLabel, TextInputBox, Selector, Button, CheckBoxWithFunction, CheckBox, \
    CollapsibleBox, Icons, NoShiftStyle
from frontend.layouts import RowLayout
from frontend.stylesheets import StyleSheets

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.config import Config
from backend.data import Data, Unlockable
from backend.util.text_util import TextUtil


class FilterOptionsCollapsibleBox(CollapsibleBox):
    def __init__(self, parent, object_name, on_click):
        super().__init__(parent, object_name, "Filter Options (Click to Expand)")

        # TODO clear filters button
        # TODO new filter for positive / zero / negative tier, positive / zero / negative subtier, also sort by tier
        self.filters = QWidget(self)
        self.filters.setMinimumHeight(0)
        self.filters.setMaximumHeight(0)

        self.filtersLayout = QGridLayout(self.filters)
        self.filtersLayout.setContentsMargins(0, 0, 0, 0)
        self.filtersLayout.setSpacing(15)

        # character
        self.characterHeading = TextLabel(self.filters, "characterHeading", "Character")
        self.filtersLayout.addWidget(self.characterHeading, 0, 0, 1, 2)

        self.characterCheckBoxes = {}
        for i, character in enumerate(Data.get_categories(True), 1):
            checkbox = CheckBoxWithFunction(self.filters, f"{TextUtil.camel_case(character)}CharacterFilterCheckBox",
                                            on_click)
            checkbox.setFixedSize(25, 25)
            self.characterCheckBoxes[character] = checkbox
            self.filtersLayout.addWidget(checkbox, i, 0, 1, 1)

            label = TextLabel(self.filters, f"{TextUtil.camel_case(character)}CharacterFilterLabel",
                              TextUtil.title_case(character))
            self.filtersLayout.addWidget(label, i, 1, 1, 1)

        # rarity
        self.rarityHeading = TextLabel(self.filters, "rarityHeading", "Rarity")
        self.filtersLayout.addWidget(self.rarityHeading, 0, 2, 1, 2)

        self.rarityCheckBoxes = {}
        for i, rarity in enumerate(Data.get_rarities(), 1):
            checkbox = CheckBoxWithFunction(self.filters, f"{TextUtil.camel_case(rarity)}RarityFilterCheckBox",
                                            on_click)
            checkbox.setFixedSize(25, 25)
            self.rarityCheckBoxes[rarity] = checkbox
            self.filtersLayout.addWidget(checkbox, i, 2, 1, 1)

            label = TextLabel(self.filters, f"{TextUtil.camel_case(rarity)}RarityFilterLabel",
                              TextUtil.title_case(rarity))
            self.filtersLayout.addWidget(label, i, 3, 1, 1)

        # type
        self.typeHeading = TextLabel(self.filters, "typeHeading", "Type")
        self.filtersLayout.addWidget(self.typeHeading, 0, 4, 1, 2)

        self.typeCheckBoxes = {}
        for i, unlockable_type in enumerate(Data.get_types(), 1):
            checkbox = CheckBoxWithFunction(self.filters, f"{TextUtil.camel_case(unlockable_type)}TypeFilterCheckBox",
                                            on_click)
            checkbox.setFixedSize(25, 25)
            self.typeCheckBoxes[unlockable_type] = checkbox
            self.filtersLayout.addWidget(checkbox, i, 4, 1, 1)

            label = TextLabel(self.filters, f"{TextUtil.camel_case(unlockable_type)}TypeFilterLabel",
                              TextUtil.title_case(unlockable_type))
            self.filtersLayout.addWidget(label, i, 5, 1, 1)

        self.filtersLayout.setColumnStretch(999, 1)

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
            self.filters.setMinimumHeight(40 * len(self.characterCheckBoxes.keys()))
            self.filters.setMaximumHeight(40 * len(self.characterCheckBoxes.keys()))

class UnlockableWidget(QWidget):
    def __init__(self, parent, unlockable: Unlockable, tier, subtier, on_unlockable_select):
        name = TextUtil.camel_case(unlockable.name)

        super().__init__(parent)
        self.setObjectName(f"{name}Widget")

        self.layout = RowLayout(self, f"{name}Layout")

        self.checkBox = CheckBox(self, f"{name}CheckBox")
        self.checkBox.setFixedSize(25, 25)
        self.checkBox.clicked.connect(on_unlockable_select)
        self.layout.addWidget(self.checkBox)

        self.image = QLabel(self)
        self.image.setObjectName(f"{name}Image")
        self.image.setFixedSize(QSize(75, 75))
        self.image.setPixmap(QPixmap(unlockable.image_path))
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

        self.unlockable = unlockable

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
        self.image.setPixmap(QPixmap(self.unlockable.image_path))

class PreferencesPage(QWidget):
    def get_edit_profile(self):
        return self.profileSelector.currentText()

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
        profile = config.get_profile_by_id(profile_id)

        non_integer = Data.verify_tiers(self.unlockableWidgets)
        if len(non_integer) > 0:
            return True

        for widget in self.unlockableWidgets:
            tier, subtier = widget.getTiers()
            config_tier, config_subtier = config.preference_by_profile(widget.unlockable.unique_id, profile)
            if tier != config_tier or subtier != config_subtier:
                return True
        return False

    # TODO optimise?
    def replace_unlockable_widgets(self, force_sort=False):
        sort_by = self.sortSelector.currentText()

        if not force_sort and self.lastSortedBy == sort_by:
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
            # TODO prompt: unsaved changes (save or discard)
            config = Config()
            for widget in self.unlockableWidgets:
                widget.setTiers(*config.preference_by_id(widget.unlockable.unique_id, self.get_edit_profile()))

    def new_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True
            config = Config()
            profile_id = config.get_next_free_profile_name()
            config.add_profile({"id": profile_id})

            self.update_profiles_from_config()
            index = self.profileSelector.findText(profile_id)
            self.profileSelector.setCurrentIndex(index)
            self.show_preferences_page_save_success(f"New empty profile created: {profile_id}")

            self.ignore_profile_signals = False
            self.switch_edit_profile()

    def save_profile(self):
        profile_id = self.get_edit_profile()
        updated_profile = Config().get_profile_by_id(profile_id).copy()

        non_integer = Data.verify_tiers(self.unlockableWidgets)
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

    # TODO unsaved changes
    def create_profile(self, title, label_text, ok_button_text):
        # check for invalid tiers
        non_integer = Data.verify_tiers(self.unlockableWidgets)
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
        new_profile = {"id": profile_id}

        for widget in self.unlockableWidgets:
            tier, subtier = widget.getTiers()
            if tier != 0 or subtier != 0:
                new_profile[widget.unlockable.unique_id] = {"tier": tier, "subtier": subtier}

        already_existed = Config().add_profile(new_profile)

        self.update_profiles_from_config()
        index = self.profileSelector.findText(profile_id)
        self.profileSelector.setCurrentIndex(index)

        if already_existed:
            self.show_preferences_page_save_success(f"Existing profile overridden with changes: {profile_id}")
        else:
            self.show_preferences_page_save_success(f"Changes saved to new profile: {profile_id}")
        return profile_id

    def save_as_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True # saving as new profile; don't trigger
            self.create_profile("Save As", "Enter your new profile name:", "Save")
            self.ignore_profile_signals = False

    def rename_profile(self):
        # TODO maybe rename instead of save and delete - preserve config order
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True

            old_profile_id = self.get_edit_profile()

            # save as
            new_profile_id = self.create_profile("Save and Rename", "Enter your new profile name:", "Save and Rename")
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
            index = self.profileSelector.findText(new_profile_id)
            self.profileSelector.setCurrentIndex(index)

            self.ignore_profile_signals = False
            self.switch_edit_profile()

    def delete_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True
            profile_id = self.get_edit_profile()

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
            self.editDropdownContentTierInput.setStyleSheet(StyleSheets.text_box_read_only)

    def on_edit_dropdown_subtier(self):
        if self.editDropdownContentSubtierCheckBox.isChecked():
            self.editDropdownContentSubtierInput.setReadOnly(False)
            text = self.editDropdownContentSubtierInput.text()
            self.editDropdownContentSubtierInput.setStyleSheet(StyleSheets.tiers_input(text))
        else:
            self.editDropdownContentSubtierInput.setReadOnly(True)
            self.editDropdownContentSubtierInput.setStyleSheet(StyleSheets.text_box_read_only)

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
            unlockableWidget.unlockable.set_image_path(icons[unlockableWidget.unlockable.unique_id])
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

        self.scrollBar = QScrollBar(self)
        self.scrollBar.setObjectName("preferencesPageScrollBar")
        self.scrollBar.setOrientation(Qt.Vertical)
        self.scrollBar.setStyleSheet(StyleSheets.scroll_bar)

        self.scrollArea = QScrollArea(self)
        self.scrollArea.setObjectName("preferencesPageScrollArea")
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBar(self.scrollBar)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("""
            QScrollArea#preferencesPageScrollArea {
                background: transparent;
                border: 0px;
            }""")

        self.scrollAreaContent = QWidget(self.scrollArea)
        self.scrollAreaContent.setObjectName("preferencesPageScrollAreaContent")
        self.scrollAreaContent.setStyleSheet("""
            QWidget#preferencesPageScrollAreaContent {
                background: transparent;
            }""")
        self.scrollArea.setWidget(self.scrollAreaContent)

        self.scrollAreaContentLayout = QVBoxLayout(self.scrollAreaContent)
        self.scrollAreaContentLayout.setObjectName("preferencesPageScrollAreaContentLayout")
        self.scrollAreaContentLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaContentLayout.setSpacing(15)

        # save, rename, delete
        self.profileSaveRow = QWidget(self.scrollAreaContent)
        self.profileSaveRow.setObjectName("preferencesPageProfileSaveRow")
        self.profileSaveRowLayout = RowLayout(self.profileSaveRow, "preferencesPageProfileSaveRowLayout")

        self.profileLabel = TextLabel(self.scrollAreaContent, "preferencesPageProfileLabel", "Profile", Font(12))

        self.profileSelector = Selector(self.profileSaveRow, "preferencesPageProfileSelector", QSize(200, 40),
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


        # filters
        self.filtersBox = FilterOptionsCollapsibleBox(self.scrollAreaContent, "preferencesPageFiltersBox",
                                                      self.replace_unlockable_widgets)

        # search bar & sort
        self.searchSortRow = QWidget(self.scrollAreaContent)
        self.searchSortRow.setObjectName("preferencesPageSearchSortRow")
        self.searchSortRowLayout = RowLayout(self.searchSortRow, "preferencesPageSearchSortRowLayout")

        self.searchBar = TextInputBox(self.searchSortRow, "preferencesPageSearchBar", QSize(200, 40), "Search by name")
        self.searchBar.textEdited.connect(self.replace_unlockable_widgets)
        self.sortLabel = TextLabel(self.searchSortRow, "preferencesPageSortLabel", "Sort by")
        self.sortSelector = Selector(self.searchSortRow, "preferencesPageSortSelector", QSize(150, 40),
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
        self.editDropdownButton.setText("Edit")
        self.editDropdownButton.setIcon(QIcon(Icons.right_arrow))
        self.editDropdownButton.setIconSize(QSize(20, 20))
        self.editDropdownButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.editDropdownButton.setStyle(NoShiftStyle())
        self.editDropdownButton.pressed.connect(self.expand_edit)

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

        self.searchSortRowLayout.addWidget(self.searchBar)
        self.searchSortRowLayout.addWidget(self.sortLabel)
        self.searchSortRowLayout.addWidget(self.sortSelector)
        self.searchSortRowLayout.addStretch(1)

        # putting the rows into the content
        self.scrollAreaContentLayout.addWidget(self.profileLabel)
        self.scrollAreaContentLayout.addWidget(self.profileSaveRow2)
        self.scrollAreaContentLayout.addWidget(self.profileSaveRow)
        self.scrollAreaContentLayout.addSpacing(15)
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
        self.layout.addWidget(self.scrollBar, 0, 1, 1, 1)
        self.layout.addWidget(self.persistentBar, 1, 0, 1, 1, Qt.AlignBottom)
        self.layout.setRowStretch(0, 1)
        self.layout.setColumnStretch(0, 1)

        self.sortSelector.setCurrentIndex(1) # self.lastSortedBy becomes "character"