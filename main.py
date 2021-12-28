import os
import sys
from multiprocessing import freeze_support

from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QRect, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QKeySequence
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QFrame, QPushButton, QGridLayout, QVBoxLayout, \
    QHBoxLayout, QGraphicsDropShadowEffect, QShortcut, QStackedWidget, QComboBox, QListView, QScrollArea, QScrollBar, \
    QCheckBox, QLineEdit, QToolButton, QFileDialog, QSizeGrip


sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.config import Config
from backend.data import Data, Unlockable
from backend.state import State
from backend.utils.text_util import TextUtil
from frontend.stylesheets import StyleSheets

# TODO new assets for frontend if using vanilla (so people can see rarity) with the full coloured background

# generic
class Font(QFont):
    def __init__(self, font_size):
        QFont.__init__(self)
        self.setFamily("Segoe UI")
        self.setPointSize(font_size)

class TextLabel(QLabel):
    def __init__(self, parent, object_name, text, font=Font(10), style_sheet=StyleSheets.white_text):
        QLabel.__init__(self, parent)
        self.setObjectName(object_name)
        self.setText(text)
        self.setFont(font)
        self.setStyleSheet(style_sheet)
        self.setAlignment(Qt.AlignVCenter)

class HyperlinkTextLabel(QLabel):
    def __init__(self, parent, object_name, text, link, font):
        QLabel.__init__(self, parent)
        self.setObjectName(object_name)
        self.setFont(font)
        self.setText(f"<a style=\"color: white; text-decoration:none;\" href=\"{link}\">{text}</a>")
        self.setAlignment(Qt.AlignVCenter)
        self.setTextFormat(Qt.RichText)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.setOpenExternalLinks(True)

class TextInputBox(QLineEdit):
    def __init__(self, parent, object_name, size, placeholder_text, text=None, font=Font(10), style_sheet=StyleSheets.text_box):
        QLineEdit.__init__(self, parent)
        self.setObjectName(object_name)
        self.setFixedSize(size)
        self.setPlaceholderText(placeholder_text)
        if text is not None:
            self.setText(text)
        self.setFont(font)
        self.setStyleSheet(style_sheet)

class CheckBox(QCheckBox):
    def __init__(self, parent, object_name, style_sheet=StyleSheets.check_box):
        QCheckBox.__init__(self, parent)
        if object_name is not None:
            self.setObjectName(object_name)
        self.setAutoFillBackground(False)
        self.setStyleSheet(style_sheet)

# not so generic
class TopBar(QFrame):
    def __init__(self, parent):
        QFrame.__init__(self, parent)
        self.setObjectName("topBar")
        self.setMinimumSize(QSize(300, 60))
        self.setStyleSheet("QFrame#topBar {background-color: rgb(33, 37, 43);}")

class TopBarButton(QPushButton):
    def __init__(self, parent, object_name, icon, on_click, style_sheet=StyleSheets.top_bar_button):
        QPushButton.__init__(self, parent)
        self.setObjectName(object_name)
        self.setFixedSize(QSize(35, 35))
        self.setStyleSheet(style_sheet)

        # icon
        self.setIconSize(QSize(20, 20))
        self.setIcon(icon)

        self.clicked.connect(on_click)

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

    def __init__(self, parent, object_name, icon, main_window, is_active=False):
        QPushButton.__init__(self, parent)
        self.setObjectName(object_name)
        self.setMinimumSize(QSize(LeftMenuButton.max_width, 60))
        self.setMaximumSize(QSize(LeftMenuButton.max_width, 60))
        self.setIconSize(QSize(30, 30))
        self.setIcon(icon)

        self.main = main_window

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
        QFrame.__init__(self, parent)
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
        QLabel.__init__(self, parent)
        self.setObjectName(object_name)
        self.setFont(Font(8))
        self.setFixedHeight(60)
        self.setText(text)
        self.setStyleSheet(style_sheet)
        self.move(self.geometry().topLeft() - parent.geometry().topLeft() + QPoint(80, 0))

class HomeRow(QWidget):
    def __init__(self, parent, object_number, icon, on_click, text):
        QWidget.__init__(self, parent)
        self.setObjectName(f"homePageRow{object_number}")
        self.button = PageButton(self, f"homePageButton{object_number}", icon, on_click)
        self.label = TextLabel(self, f"homePageLabel{object_number}", text)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addStretch(1)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.label)
        self.layout.addStretch(1)

class HelpRow(QWidget):
    def __init__(self, parent, object_name, icon_path, text):
        QWidget.__init__(self, parent)
        self.setObjectName(object_name)

        self.icon = QLabel(self)
        self.icon.setObjectName(f"{object_name}Icon")
        self.icon.setFixedSize(QSize(60, 60))
        self.icon.setPixmap(QPixmap(icon_path))
        self.icon.setScaledContents(True)

        self.label = TextLabel(self, f"{object_name}Label", text)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.icon)
        self.layout.addWidget(self.label)
        self.layout.addStretch(1)

class ToggleButton(LeftMenuButton):
    def __init__(self, parent, object_name, icon, main_window, on_click):
        LeftMenuButton.__init__(self, parent, object_name, icon, main_window)
        self.clicked.connect(on_click)

    def on_click(self):
        pass # override base method

class PageButton(QPushButton):
    def __init__(self, parent, object_name, icon, on_click):
        QPushButton.__init__(self, parent)
        self.setObjectName(object_name)
        self.setFixedSize(QSize(30, 30))
        self.setIconSize(QSize(30, 30))
        self.setIcon(icon)

        self.setStyleSheet(StyleSheets.page_button)

        self.clicked.connect(on_click)

class Selector(QComboBox):
    def __init__(self, parent, object_name, size, items, active_item=None):
        QComboBox.__init__(self, parent)
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
        QPushButton.__init__(self, parent)
        self.setObjectName(object_name)
        self.setFixedSize(size)
        self.setFont(Font(10))
        self.setText(text)
        self.setStyleSheet(StyleSheets.button)

class CheckBoxWithFunction(CheckBox):
    def __init__(self, parent, object_name, on_click, style_sheet=StyleSheets.check_box):
        CheckBox.__init__(self, parent, object_name, style_sheet)
        self.clicked.connect(on_click)

class CollapsibleBox(QWidget):
    def __init__(self, parent, object_name, on_click):
        QWidget.__init__(self, parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        self.toggleButton = QToolButton(self)
        self.toggleButton.setObjectName(object_name)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)
        self.toggleButton.setFont(Font(12))
        self.toggleButton.setStyleSheet(StyleSheets.collapsible_box_inactive)
        self.toggleButton.setText("Filter Options")
        self.toggleButton.setIcon(QIcon(Icons.right_arrow))
        self.toggleButton.setIconSize(QSize(20, 20))
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.pressed.connect(self.on_pressed)

        # TODO clear filters button
        # TODO new filter for positive / zero / negative tier, positive / zero / negative subtier, also sort by tier
        self.filters = QScrollArea(self)
        self.filters.setMinimumHeight(0)
        self.filters.setMaximumHeight(0)
        self.filters.setStyleSheet('''
            QScrollArea {
                background: rgba(0, 0, 0, 0);
                border: 0px solid rgba(0, 0, 0, 0);
            }''')

        self.filtersLayout = QGridLayout(self.filters)
        self.filtersLayout.setContentsMargins(0, 0, 0, 0)
        self.filtersLayout.setSpacing(15)

        # character
        self.characterHeading = TextLabel(self.filters, "characterHeading", "Character")
        self.filtersLayout.addWidget(self.characterHeading, 0, 0, 1, 2)

        self.characterCheckBoxes = {}
        for i, character in enumerate(Data.get_categories(), 1):
            checkbox = CheckBoxWithFunction(self.filters, f"{TextUtil.camel_case(character)}CharacterFilterCheckBox", on_click)
            checkbox.setFixedSize(25, 25)
            self.characterCheckBoxes[character] = checkbox
            self.filtersLayout.addWidget(checkbox, i, 0, 1, 1)

            label = TextLabel(self.filters, f"{TextUtil.camel_case(character)}CharacterFilterLabel", TextUtil.title_case(character))
            self.filtersLayout.addWidget(label, i, 1, 1, 1)

        # rarity
        self.rarityHeading = TextLabel(self.filters, "rarityHeading", "Rarity")
        self.filtersLayout.addWidget(self.rarityHeading, 0, 2, 1, 2)

        self.rarityCheckBoxes = {}
        for i, rarity in enumerate(Data.get_rarities(), 1):
            checkbox = CheckBoxWithFunction(self.filters, f"{TextUtil.camel_case(rarity)}RarityFilterCheckBox", on_click)
            checkbox.setFixedSize(25, 25)
            self.rarityCheckBoxes[rarity] = checkbox
            self.filtersLayout.addWidget(checkbox, i, 2, 1, 1)

            label = TextLabel(self.filters, f"{TextUtil.camel_case(rarity)}RarityFilterLabel", TextUtil.title_case(rarity))
            self.filtersLayout.addWidget(label, i, 3, 1, 1)

        # type
        self.typeHeading = TextLabel(self.filters, "typeHeading", "Type")
        self.filtersLayout.addWidget(self.typeHeading, 0, 4, 1, 2)

        self.typeCheckBoxes = {}
        for i, unlockable_type in enumerate(Data.get_types(), 1):
            checkbox = CheckBoxWithFunction(self.filters, f"{TextUtil.camel_case(unlockable_type)}TypeFilterCheckBox", on_click)
            checkbox.setFixedSize(25, 25)
            self.typeCheckBoxes[unlockable_type] = checkbox
            self.filtersLayout.addWidget(checkbox, i, 4, 1, 1)

            label = TextLabel(self.filters, f"{TextUtil.camel_case(unlockable_type)}TypeFilterLabel", TextUtil.title_case(unlockable_type))
            self.filtersLayout.addWidget(label, i, 5, 1, 1)

        self.filtersLayout.setColumnStretch(999, 1)

        self.layout.addWidget(self.toggleButton, alignment=Qt.AlignTop)
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
            self.filters.setMinimumHeight(0)
            self.filters.setMaximumHeight(0)
        else:
            self.toggleButton.setStyleSheet(StyleSheets.collapsible_box_inactive)
            self.toggleButton.setIcon(QIcon(Icons.down_arrow))
            self.filters.setMinimumHeight(1100)
            self.filters.setMaximumHeight(1100)

class UnlockableWidget(QWidget):
    def __init__(self, parent, unlockable: Unlockable, tier, subtier, on_unlockable_select):
        name = TextUtil.camel_case(unlockable.name)

        QWidget.__init__(self, parent)
        self.setObjectName(f"{name}Widget")

        self.layout = QHBoxLayout(self)
        self.layout.setObjectName(f"{name}Layout")
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)

        self.checkBox = CheckBox(self, f"{name}CheckBox")
        self.checkBox.setFixedSize(25, 25)
        self.checkBox.clicked.connect(on_unlockable_select)
        self.layout.addWidget(self.checkBox)

        self.image = QLabel(self)
        self.image.setObjectName(f"{name}Image")
        self.image.setFixedSize(QSize(75, 75))
        self.image.setPixmap(QPixmap(unlockable.image_path))
        self.image.setScaledContents(True)
        self.image.setToolTip(f'''Character: {TextUtil.title_case(unlockable.category)}
Rarity: {TextUtil.title_case(unlockable.rarity)}
Type: {TextUtil.title_case(unlockable.type)}''')
        self.layout.addWidget(self.image)

        self.label = QLabel(self)
        self.label.setObjectName(f"{name}Label")
        self.label.setFont(Font(10))
        self.label.setStyleSheet(StyleSheets.white_text)
        self.label.setText(unlockable.name)
        self.layout.addWidget(self.label)

        self.layout.addSpacing(200 - self.label.fontMetrics().boundingRect(self.label.text()).width())

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

    def setTiers(self, tier, subtier):
        self.tierInput.setText(str(tier))
        self.tierInput.setStyleSheet(StyleSheets.tiers_input(tier))
        self.subtierInput.setText(str(subtier))
        self.subtierInput.setStyleSheet(StyleSheets.tiers_input(subtier))

    def getTiers(self):
        return int(self.tierInput.text()), int(self.subtierInput.text())

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

    def update_profiles_from_config(self):
        while self.preferencesPageProfileSelector.count() > 0:
            self.preferencesPageProfileSelector.removeItem(0)
        self.preferencesPageProfileSelector.addItems(Config().profile_names() + ["blank"])

        while self.bloodwebPageProfileSelector.count() > 0:
            self.bloodwebPageProfileSelector.removeItem(0)
        self.bloodwebPageProfileSelector.addItems(Config().profile_names() + ["blank"])

    def replace_unlockable_widgets(self):
        sort_by = self.preferencesPageSortSelector.currentText()

        if self.lastSortedBy == sort_by:
            # if there was no change in ordering, we don't pass in sort_by; the resulting visible list has arbitrary order
            for widget, is_visible in Data.filter(self.preferencesPageUnlockableWidgets,
                                                  self.preferencesPageSearchBar.text(),
                                                  self.preferencesPageFiltersBox.get_character_filters(),
                                                  self.preferencesPageFiltersBox.get_rarity_filters(),
                                                  self.preferencesPageFiltersBox.get_type_filters()):
                widget.setVisible(is_visible)
        else:
            # lastSortedBy was changed on this event; we need visible to be ordered to insert widgets correctly
            for widget in self.preferencesPageUnlockableWidgets:
                self.preferencesPageScrollAreaContentLayout.removeWidget(widget)

            for widget, is_visible in Data.filter(self.preferencesPageUnlockableWidgets,
                                                  self.preferencesPageSearchBar.text(),
                                                  self.preferencesPageFiltersBox.get_character_filters(),
                                                  self.preferencesPageFiltersBox.get_rarity_filters(),
                                                  self.preferencesPageFiltersBox.get_type_filters(),
                                                  sort_by):
                self.preferencesPageScrollAreaContentLayout.insertWidget(self.preferencesPageScrollAreaContentLayout.count() - 1, widget)
                widget.setVisible(is_visible)

        self.lastSortedBy = sort_by
        self.on_unlockable_select()

    def switch_edit_profile(self):
        if not self.ignore_profile_signals:
            # TODO prompt: unsaved changes (save or discard)
            profile_id = self.preferencesPageProfileSelector.currentText()

            if profile_id == "blank":
                for widget in self.preferencesPageUnlockableWidgets:
                    widget.setTiers(0, 0)
            else:
                config = Config()
                for widget in self.preferencesPageUnlockableWidgets:
                    widget.setTiers(*config.preference(widget.unlockable.unique_id, profile_id))

    def save_profile(self):
        profile_id = self.preferencesPageProfileSelector.currentText()
        if profile_id == "blank":
            self.show_preferences_page_save_fail_text("You cannot save to the blank profile. Use Save As below to create a new profile.")
        else:
            updated_profile = Config().get_profile_by_id(profile_id).copy()

            non_integer = Data.verify_tiers(self.preferencesPageUnlockableWidgets)
            if len(non_integer) > 0:
                self.show_preferences_page_save_fail_text(f"There are {len(non_integer)} unlockables with invalid inputs. "
                                                          f"Inputs must be a number from -999 to 999. Changes not saved.")
                return

            for widget in self.preferencesPageUnlockableWidgets:
                tier, subtier = widget.getTiers()
                if tier != 0 or subtier != 0:
                    updated_profile[widget.unlockable.unique_id] = {"tier": tier, "subtier": subtier}
            Config().set_profile(updated_profile)

            self.show_preferences_page_save_success_text(f"Changes saved to profile: {profile_id}")
            QTimer.singleShot(10000, self.hide_preferences_page_save_as_success_text)

    def delete_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True
            profile_id = self.preferencesPageProfileSelector.currentText()
            if profile_id == "blank":
                self.show_preferences_page_save_fail_text("You cannot delete the blank profile.")
            else:
                # TODO "are you sure" for deleting
                Config().delete_profile(profile_id)

                self.update_profiles_from_config()
                self.preferencesPageProfileSelector.setCurrentIndex(0)
                self.ignore_profile_signals = False
                self.switch_edit_profile()

                self.show_preferences_page_save_success_text(f"Profile deleted: {profile_id}")
            self.ignore_profile_signals = False

    def show_preferences_page_save_success_text(self, text):
        self.preferencesPageSaveSuccessText.setText(text)
        self.preferencesPageSaveSuccessText.setStyleSheet(StyleSheets.pink_text)
        self.preferencesPageSaveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_preferences_page_save_success_text)

    def show_preferences_page_save_fail_text(self, text):
        self.preferencesPageSaveSuccessText.setText(text)
        self.preferencesPageSaveSuccessText.setStyleSheet(StyleSheets.purple_text)
        self.preferencesPageSaveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_preferences_page_save_success_text)

    def hide_preferences_page_save_success_text(self):
        self.preferencesPageSaveSuccessText.setVisible(False)

    def save_as_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True # saving as new profile; don't trigger

            profile_id = self.preferencesPageSaveAsInput.text()
            self.preferencesPageSaveAsInput.setText("")
            if profile_id == "blank":
                self.show_preferences_page_save_as_fail_text("You cannot save to a profile named \"blank\". Try a different name.")
            else:
                # TODO "are you sure" for overwriting existing profile "this will overwrite an existing profile. are you sure you want to save?"
                new_profile = {"id": profile_id}

                non_integer = Data.verify_tiers(self.preferencesPageUnlockableWidgets)
                if len(non_integer) > 0:
                    self.show_preferences_page_save_as_fail_text(f"There are {len(non_integer)} unlockables with invalid inputs. "
                                                                 f"Inputs must be a number from -999 to 999. Changes not saved.")
                    return

                for widget in self.preferencesPageUnlockableWidgets:
                    tier, subtier = widget.getTiers()
                    if tier != 0 or subtier != 0:
                        new_profile[widget.unlockable.unique_id] = {"tier": tier, "subtier": subtier}

                already_existed = Config().add_profile(new_profile)

                self.update_profiles_from_config()
                self.preferencesPageProfileSelector.setCurrentIndex(self.preferencesPageProfileSelector.findText(profile_id))

                if already_existed:
                    self.show_preferences_page_save_as_success_text(f"Existing profile overridden with changes: {profile_id}")
                else:
                    self.show_preferences_page_save_as_success_text(f"Changes saved to new profile: {profile_id}")

            self.ignore_profile_signals = False

    def show_preferences_page_save_as_success_text(self, text):
        self.preferencesPageSaveAsSuccessText.setText(text)
        self.preferencesPageSaveAsSuccessText.setStyleSheet(StyleSheets.pink_text)
        self.preferencesPageSaveAsSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_preferences_page_save_as_success_text)

    def show_preferences_page_save_as_fail_text(self, text):
        self.preferencesPageSaveAsSuccessText.setText(text)
        self.preferencesPageSaveAsSuccessText.setStyleSheet(StyleSheets.purple_text)
        self.preferencesPageSaveAsSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_preferences_page_save_as_success_text)

    def hide_preferences_page_save_as_success_text(self):
        self.preferencesPageSaveAsSuccessText.setVisible(False)

    def on_unlockable_select(self):
        num_selected = sum([1 for widget in self.preferencesPageUnlockableWidgets if widget.checkBox.isChecked()])
        self.preferencesPageSelectedLabel.setText(f"{num_selected} selected")

        self.preferencesPageAllCheckbox.setChecked(num_selected > 0)
        self.preferencesPageAllCheckbox.setStyleSheet(StyleSheets.check_box_all
                                                      if all([widget.checkBox.isChecked() for widget in [widget for widget in self.preferencesPageUnlockableWidgets if widget.isVisible()]])
                                                      else StyleSheets.check_box_some)

    def on_unlockable_select_all(self):
        checked = self.preferencesPageAllCheckbox.isChecked() # whether checkbox is select all (True) or deselect all (False)

        if checked:
            for widget in self.preferencesPageUnlockableWidgets:
                if widget.isVisible():
                    widget.checkBox.setChecked(True)
        else:
            for widget in self.preferencesPageUnlockableWidgets:
                widget.checkBox.setChecked(False)

        self.on_unlockable_select()

    # bloodweb
    def switch_run_profile(self):
        if not self.ignore_profile_signals:
            profile_id = self.bloodwebPageProfileSelector.currentText()
            Config().set_active_profile(profile_id)

    def switch_character(self):
        character = self.bloodwebPageCharacterSelector.currentText()
        Config().set_character(character)

    def run_terminate(self):
        if self.state.is_active():
            self.state.terminate()
            self.bloodwebPageRunButton.setText("Run")
            self.bloodwebPageRunButton.setFixedSize(QSize(60, 35))
        else:
            # self.minimize()
            self.state.run_regular_mode()
            self.bloodwebPageRunButton.setText("Terminate")
            self.bloodwebPageRunButton.setFixedSize(QSize(92, 35))

    # settings
    def on_width_update(self):
        self.settingsPageResolutionWidthInput.setStyleSheet(StyleSheets.settings_input(width=self.settingsPageResolutionWidthInput.text()))

    def on_height_update(self):
        self.settingsPageResolutionHeightInput.setStyleSheet(StyleSheets.settings_input(height=self.settingsPageResolutionHeightInput.text()))

    def on_ui_scale_update(self):
        self.settingsPageResolutionUIInput.setStyleSheet(StyleSheets.settings_input(ui_scale=self.settingsPageResolutionUIInput.text()))

    def set_path(self):
        icon_dir = QFileDialog.getExistingDirectory(self, "Select Icon Folder", self.settingsPagePathText.text())
        if icon_dir != "":
            self.settingsPagePathText.setText(icon_dir)

    def show_settings_page_save_success_text(self, text):
        self.settingsPageSaveSuccessText.setText(text)
        self.settingsPageSaveSuccessText.setStyleSheet(StyleSheets.pink_text)
        self.settingsPageSaveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_settings_page_save_success_text)

    def show_settings_page_save_fail_text(self, text):
        self.settingsPageSaveSuccessText.setText(text)
        self.settingsPageSaveSuccessText.setStyleSheet(StyleSheets.purple_text)
        self.settingsPageSaveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_settings_page_save_success_text)

    def hide_settings_page_save_success_text(self):
        self.settingsPageSaveSuccessText.setVisible(False)

    def save_settings(self):
        width = self.settingsPageResolutionWidthInput.text()
        height = self.settingsPageResolutionHeightInput.text()
        ui_scale = self.settingsPageResolutionUIInput.text()
        if not Data.verify_settings_res(width, height, ui_scale):
            self.show_settings_page_save_fail_text("Ensure width, height and UI scale are all numbers. "
                                                   "UI scale must be a number between 70 and 100. Changes not saved.")
            return

        path = self.settingsPagePathText.text()
        if not Data.verify_path(path):
            self.show_settings_page_save_fail_text("Ensure path is an actual folder. Changes not saved.")
            return

        Config().set_resolution(int(width), int(height), int(ui_scale))
        Config().set_path(path)
        self.show_settings_page_save_success_text("Settings changed.")

    def top_resize(self):
        print("hi")

    def __init__(self):
        QMainWindow.__init__(self)
        # TODO windows up + windows down; resize areas; cursor when hovering over buttons
        # TODO resize areas
        # TODO a blank profile which cannot be saved to, all 0s

        self.is_maximized = False
        self.ignore_profile_signals = False # used to prevent infinite recursion e.g. when setting dropdown to a profile
        self.state = State(True)

        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.setBaseSize(1230, 670)
        self.setMinimumSize(1100, 600)
        self.setWindowTitle("Blood Emporium")
        self.setWindowIcon(QIcon(Icons.icon))

        # self.shortcut = QShortcut(QKeySequence(Qt.Key_Meta), self) # TODO
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

        # self.topResize = QWidget(self.centralWidget)
        # self.topResize.setCursor(Qt.SizeVerCursor)
        # # self.topResize.resizeEvent = lambda e: print("hi")
        # self.centralLayout.addWidget(self.topResize, 0, 0)

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

        self.toggleButton = ToggleButton(self.leftMenu, "toggleButton", QIcon(Icons.menu), self, self.animate)
        self.toggleLabel = LeftMenuLabel(self.toggleButton, "toggleLabel", "Hide", "color: rgb(150, 150, 150);")

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

        self.buttons = [self.homeButton, self.preferencesButton, self.bloodwebButton, self.helpButton, self.settingsButton]

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
        self.homePageIcon.setObjectName("homePageIcon") # TODO large icon with Blood Emporium text like in Github splash
        self.homePageIcon.setFixedSize(QSize(200, 200))
        self.homePageIcon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.icon))
        self.homePageIcon.setScaledContents(True)

        self.homePageRow1 = HomeRow(self.homePage, 1, QIcon(Icons.settings), self.settingsButton.on_click,
                                    "First time here? Recently change your game / display settings? Set up your config.")
        self.homePageRow2 = HomeRow(self.homePage, 2, QIcon(Icons.preferences), self.preferencesButton.on_click,
                                    "What would you like from the bloodweb? Set up your preferences.")
        self.homePageRow3 = HomeRow(self.homePage, 3, QIcon(Icons.bloodweb), self.bloodwebButton.on_click,
                                    "Ready? Start clearing your bloodweb!")
        self.homePageRow4 = HomeRow(self.homePage, 4, QIcon(Icons.help), self.helpButton.on_click,
                                    "Instructions & contact details here.")

        # stack: preferencesPage
        self.preferencesPage = QWidget()
        self.preferencesPage.setObjectName("preferencesPage")
        self.preferencesButton.setPage(self.preferencesPage)

        self.preferencesPageLayout = QGridLayout(self.preferencesPage)
        self.preferencesPageLayout.setObjectName("preferencesPageLayout")
        self.preferencesPageLayout.setContentsMargins(25, 25, 25, 0)
        self.preferencesPageLayout.setSpacing(0)

        self.preferencesPageScrollBar = QScrollBar(self.preferencesPage)
        self.preferencesPageScrollBar.setObjectName("preferencesPageScrollBar")
        self.preferencesPageScrollBar.setOrientation(Qt.Vertical)
        self.preferencesPageScrollBar.setStyleSheet(StyleSheets.scroll_bar)

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

        # save
        self.preferencesPageProfileSaveRow = QWidget(self.preferencesPageScrollAreaContent)
        self.preferencesPageProfileSaveRow.setObjectName("preferencesPageProfileSaveRow")
        self.preferencesPageProfileSaveRowLayout = QHBoxLayout(self.preferencesPageProfileSaveRow)
        self.preferencesPageProfileSaveRowLayout.setContentsMargins(0, 0, 0, 0)
        self.preferencesPageProfileSaveRowLayout.setSpacing(15)

        self.preferencesPageProfileLabel = TextLabel(self.preferencesPageScrollAreaContent, "preferencesPageProfileLabel",
                                                     "Profile", Font(12))

        self.preferencesPageProfileSelector = Selector(self.preferencesPageProfileSaveRow,
                                                       "preferencesPageProfileSelector",
                                                       QSize(150, 40), Config().profile_names() + ["blank"],
                                                       Config().active_profile_name())
        self.preferencesPageProfileSelector.currentIndexChanged.connect(self.switch_edit_profile)

        self.preferencesPageSaveButton = Button(self.preferencesPageProfileSaveRow, "preferencesPageSaveButton", "Save", QSize(60, 35))
        self.preferencesPageSaveButton.clicked.connect(self.save_profile)

        self.preferencesPageDeleteButton = Button(self.preferencesPageProfileSaveRow, "preferencesPageDeleteButton", "Delete", QSize(75, 35))
        self.preferencesPageDeleteButton.clicked.connect(self.delete_profile)

        self.preferencesPageSaveSuccessText = TextLabel(self.preferencesPageProfileSaveRow, "preferencesPageSaveSuccessText", "", Font(10))
        self.preferencesPageSaveSuccessText.setVisible(False)

        # TODO rename profile

        # save as
        self.preferencesPageProfileSaveAsRow = QWidget(self.preferencesPageScrollAreaContent)
        self.preferencesPageProfileSaveAsRow.setObjectName("preferencesPageProfileSaveAsRow")
        self.preferencesPageProfileSaveAsRowLayout = QHBoxLayout(self.preferencesPageProfileSaveAsRow)
        self.preferencesPageProfileSaveAsRowLayout.setContentsMargins(0, 0, 0, 0)
        self.preferencesPageProfileSaveAsRowLayout.setSpacing(15)

        self.preferencesPageSaveAsInput = TextInputBox(self.preferencesPageProfileSaveAsRow, "preferencesPageSaveAsInput",
                                                       QSize(150, 40), "Enter profile name")

        self.preferencesPageSaveAsButton = Button(self.preferencesPageProfileSaveAsRow, "preferencesPageSaveAsButton",
                                                  "Save As", QSize(80, 35))
        self.preferencesPageSaveAsButton.clicked.connect(self.save_as_profile)

        self.preferencesPageSaveAsSuccessText = TextLabel(self.preferencesPageProfileSaveAsRow, "preferencesPageSaveAsSuccessText",
                                                          "", Font(10))
        self.preferencesPageSaveAsSuccessText.setVisible(False)

        # filters
        self.preferencesPageFiltersBox = CollapsibleBox(self.preferencesPageScrollAreaContent,
                                                        "preferencesPageScrollAreaContent", self.replace_unlockable_widgets)

        # search bar & sort
        self.preferencesPageSearchSortRow = QWidget(self.preferencesPageScrollAreaContent)
        self.preferencesPageSearchSortRow.setObjectName("preferencesPageSearchSortRow")
        self.preferencesPageSearchSortRowLayout = QHBoxLayout(self.preferencesPageSearchSortRow)
        self.preferencesPageSearchSortRowLayout.setContentsMargins(0, 0, 0, 0)
        self.preferencesPageSearchSortRowLayout.setSpacing(15)

        self.preferencesPageSearchBar = TextInputBox(self.preferencesPageSearchSortRow, "preferencesPageSearchBar",
                                                     QSize(200, 40), "Search by name")
        self.preferencesPageSearchBar.textEdited.connect(self.replace_unlockable_widgets)
        self.preferencesPageSortLabel = TextLabel(self.preferencesPageSearchSortRow, "preferencesPageSortLabel", "Sort by")
        self.preferencesPageSortSelector = Selector(self.preferencesPageSearchSortRow, "preferencesPageSortSelector",
                                                    QSize(225, 40), Data.get_sorts())
        self.preferencesPageSortSelector.currentIndexChanged.connect(self.replace_unlockable_widgets)
        self.lastSortedBy = "default (usually does the job)" # cache of last sort

        # all unlockables
        self.preferencesPageUnlockableWidgets = []
        config = Config()
        for unlockable in Data.get_unlockables():
            if unlockable.category in ["unused", "retired"]:
                continue
            self.preferencesPageUnlockableWidgets.append(UnlockableWidget(self.preferencesPageScrollAreaContent,
                                                                          unlockable, *config.preference(unlockable.unique_id),
                                                                          self.on_unlockable_select))

        self.preferencesPagePersistentBar = QWidget(self.preferencesPage)
        self.preferencesPagePersistentBar.setObjectName("preferencesPagePersistentBar")
        self.preferencesPagePersistentBar.setStyleSheet('''
        QWidget#preferencesPagePersistentBar {
            border-top: 6px solid rgb(47, 52, 61);
            border-radius: 3px;           
        }''')
        self.preferencesPagePersistentBar.setMinimumHeight(80)
        self.preferencesPagePersistentBarLayout = QHBoxLayout(self.preferencesPagePersistentBar)
        self.preferencesPagePersistentBarLayout.setContentsMargins(0, 0, 0, 0)
        self.preferencesPagePersistentBarLayout.setSpacing(15)

        self.preferencesPageAllCheckbox = CheckBoxWithFunction(self.preferencesPagePersistentBar, "preferencesPageAllCheckbox", self.on_unlockable_select_all, style_sheet=StyleSheets.check_box_all)
        # TODO hover over says select all / deselect all ^
        self.preferencesPageSelectedLabel = TextLabel(self.preferencesPagePersistentBar, "preferencesPageSelectedLabel", "0 selected")

        # stack: bloodwebPage
        self.bloodwebPage = QWidget()
        self.bloodwebPage.setObjectName("bloodwebPage")
        self.bloodwebButton.setPage(self.bloodwebPage)

        self.bloodwebPageLayout = QVBoxLayout(self.bloodwebPage)
        self.bloodwebPageLayout.setObjectName("bloodwebPageLayout")
        self.bloodwebPageLayout.setContentsMargins(25, 25, 25, 25)
        self.bloodwebPageLayout.setSpacing(15)

        self.bloodwebPageProfileLabel = TextLabel(self.bloodwebPage, "bloodwebPageProfileLabel", "Profile", Font(12))
        self.bloodwebPageProfileSelector = Selector(self.bloodwebPage, "bloodwebPageProfileSelector", QSize(150, 40),
                                                    Config().profile_names(), Config().active_profile_name())
        self.bloodwebPageProfileSelector.currentIndexChanged.connect(self.switch_run_profile)

        self.bloodwebPageCharacterLabel = TextLabel(self.bloodwebPage, "bloodwebPageProfileLabel", "Character", Font(12))
        self.bloodwebPageCharacterSelector = Selector(self.bloodwebPage, "bloodwebPageCharacterSelector", QSize(150, 40),
                                                      Data.get_characters(), Config().character())
        self.bloodwebPageCharacterSelector.currentIndexChanged.connect(self.switch_character)

        self.bloodwebPageRunRow = QWidget(self.bloodwebPage)
        self.bloodwebPageRunRow.setObjectName("bloodwebPageRunRow")
        self.bloodwebPageRunRowLayout = QHBoxLayout(self.bloodwebPageRunRow)
        self.bloodwebPageRunRowLayout.setObjectName("bloodwebPageRunRowLayout")
        self.bloodwebPageRunRowLayout.setContentsMargins(0, 0, 0, 0)
        self.bloodwebPageRunRowLayout.setSpacing(15)

        self.bloodwebPageRunButton = Button(self.bloodwebPageRunRow, "bloodwebPageRunButton", "Run", QSize(60, 35))
        self.bloodwebPageRunButton.clicked.connect(self.run_terminate)
        self.bloodwebPageRunLabel = TextLabel(self.bloodwebPageRunRow, "bloodwebPageRunLabel",
                                              "Make sure your game is open on your monitor, and any shaders "
                                              "and visual effects are off.", Font(10))

        # stack: helpPage
        self.helpPage = QWidget()
        self.helpPage.setObjectName("helpPage")
        self.helpButton.setPage(self.helpPage)

        self.helpPageLayout = QVBoxLayout(self.helpPage)
        self.helpPageLayout.setContentsMargins(25, 25, 25, 25)
        self.helpPageLayout.setSpacing(15)

        self.helpPageInstructionsLabel = TextLabel(self.helpPage, "helpPageInstructionsLabel", "How to Use Blood Emporium", Font(12))
        self.helpPageInstructionsDescription = TextLabel(self.helpPage, "helpPageInstructionsDescription",
                                                         "<p style=line-height:125%> First, configure your display resolution and UI scale in the settings page. "
                                                         "This will ensure that the correct region of your screen is used for the algorithm. "
                                                         "If you have a non-default Dead by Daylight installation, you will also need "
                                                         "to find the folder containing the icons, in case you are using a custom icon pack.<br><br>"
                                                         "You can then set up preferences for what add-ons, items, offerings and perks "
                                                         "you would like to obtain from the bloodweb. Each set of preferences can be "
                                                         "stored in a different profile, for convenient switching as required. "
                                                         "Three preset profiles come with the program: default (meta items), "
                                                         "initiation (the creator's personal preferences) and cheapskate "
                                                         "(for levelling up the bloodweb as cheaply as possible). "
                                                         "You can use these as a starting point for your own profile, or "
                                                         "create your own from scratch using the blank profile.<br><br>"
                                                         "Each unlockable you configure will have a tier and a subtier:<br>"
                                                         "    - the higher the tier (or subtier), the higher your preference for that item<br>"
                                                         "    - the lower the tier (or subtier), the lower your preference for that item<br>"
                                                         "    - neutral items will have tier and subtier 0<br>"
                                                         "    - tiers and subtiers can range from -999 to 999<br>"
                                                         "    - tier A item + tier B item are equivalent in preference to a tier A + B item<br>"
                                                         "         - for instance, two tier 1 items is equivalent to a single tier 2 item<br>"
                                                         "         - you can use these numbers to fine tune exactly how much you want each item<br>"
                                                         "    - a similar system applies with negative tiers when specifying how much you dislike an item<br>"
                                                         "    - subtier allows for preference within a tier e.g. a tier 3 subtier 3 is higher priority than tier 3 subtier 2<br><br>"
                                                         "Then simply select a profile, select the character whose bloodweb you are on, and run! "
                                                         "Make sure your shaders are off before running, or the program is very likely to perform in unintended ways.",
                                                         Font(10))
        self.helpPageInstructionsDescription.setWordWrap(True)

        self.helpPageContactLabel = TextLabel(self.helpPage, "helpPageContactLabel", "Contact Me", Font(12))

        self.helpPageContactDiscordRow = QWidget(self.helpPage)
        self.helpPageContactDiscordRow.setObjectName("helpPageContactDiscordRow")
        self.helpPageContactDiscordRowLayout = QHBoxLayout(self.helpPageContactDiscordRow)
        self.helpPageContactDiscordRowLayout.setContentsMargins(0, 0, 0, 0)

        self.helpPageContactDiscordIcon = QLabel(self.helpPageContactDiscordRow)
        self.helpPageContactDiscordIcon.setObjectName("helpPageContactDiscordIcon")
        self.helpPageContactDiscordIcon.setFixedSize(QSize(20, 20))
        self.helpPageContactDiscordIcon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.discord))
        self.helpPageContactDiscordIcon.setScaledContents(True)
        self.helpPageContactDiscordLabel = TextLabel(self.helpPageContactDiscordRow, "helpPageContactDiscordLabel", "Initiation#2031")

        self.helpPageContactTwitterRow = QWidget(self.helpPage)
        self.helpPageContactTwitterRow.setObjectName("helpPageContactTwitterRow")
        self.helpPageContactTwitterRowLayout = QHBoxLayout(self.helpPageContactTwitterRow)
        self.helpPageContactTwitterRowLayout.setContentsMargins(0, 0, 0, 0)

        self.helpPageContactTwitterIcon = QLabel(self.helpPageContactTwitterRow)
        self.helpPageContactTwitterIcon.setObjectName("helpPageContactTwitterIcon")
        self.helpPageContactTwitterIcon.setFixedSize(QSize(20, 20))
        self.helpPageContactTwitterIcon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.twitter))
        self.helpPageContactTwitterIcon.setScaledContents(True)
        self.helpPageContactTwitterLabel = HyperlinkTextLabel(self.helpPageContactTwitterRow, "helpPageContactTwitterLabel",
                                                              "Twitter", "https://twitter.com/initiationmusic", Font(10))

        # stack: settingsPage
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName("settingsPage")
        self.settingsButton.setPage(self.settingsPage)

        self.settingsPageLayout = QVBoxLayout(self.settingsPage)
        self.settingsPageLayout.setObjectName("settingsPageLayout")
        self.settingsPageLayout.setContentsMargins(25, 25, 25, 25)
        self.settingsPageLayout.setSpacing(15)

        res = Config().resolution()
        self.settingsPageResolutionLabel = TextLabel(self.settingsPage, "settingsPageResolutionLabel", "Display Resolution", Font(12))
        self.settingsPageResolutionUIDescription = TextLabel(self.settingsPage,
                                                             "settingsPageResolutionUIDescription",
                                                             "You can find your UI scale in your Dead by Daylight "
                                                             "settings under Graphics -> UI / HUD -> UI Scale.", Font(10))
        self.settingsPageResolutionWidthRow = QWidget(self.settingsPage)
        self.settingsPageResolutionWidthRow.setObjectName("settingsPageResolutionWidthRow")

        self.settingsPageResolutionWidthRowLayout = QHBoxLayout(self.settingsPageResolutionWidthRow)
        self.settingsPageResolutionWidthRowLayout.setContentsMargins(0, 0, 0, 0)
        self.settingsPageResolutionWidthRowLayout.setSpacing(15)

        self.settingsPageResolutionWidthLabel = TextLabel(self.settingsPageResolutionWidthRow,
                                                          "settingsPageResolutionWidthLabel", "Width", Font(10))
        self.settingsPageResolutionWidthInput = TextInputBox(self.settingsPageResolutionWidthRow,
                                                             "settingsPageResolutionWidthInput", QSize(60, 40),
                                                             "Width", str(res.width))
        self.settingsPageResolutionWidthInput.textEdited.connect(self.on_width_update)

        self.settingsPageResolutionHeightRow = QWidget(self.settingsPage)
        self.settingsPageResolutionHeightRow.setObjectName("settingsPageResolutionHeightRow")
        self.settingsPageResolutionHeightRowLayout = QHBoxLayout(self.settingsPageResolutionHeightRow)
        self.settingsPageResolutionHeightRowLayout.setContentsMargins(0, 0, 0, 0)
        self.settingsPageResolutionHeightRowLayout.setSpacing(15)

        self.settingsPageResolutionHeightLabel = TextLabel(self.settingsPageResolutionHeightRow,
                                                          "settingsPageResolutionHeightLabel", "Height", Font(10))
        self.settingsPageResolutionHeightInput = TextInputBox(self.settingsPageResolutionHeightRow,
                                                              "settingsPageResolutionHeightInput", QSize(60, 40),
                                                              "Height", str(res.height))
        self.settingsPageResolutionHeightInput.textEdited.connect(self.on_height_update)

        self.settingsPageResolutionUIRow = QWidget(self.settingsPage)
        self.settingsPageResolutionUIRow.setObjectName("settingsPageResolutionUIRow")
        self.settingsPageResolutionUIRowLayout = QHBoxLayout(self.settingsPageResolutionUIRow)
        self.settingsPageResolutionUIRowLayout.setContentsMargins(0, 0, 0, 0)
        self.settingsPageResolutionUIRowLayout.setSpacing(15)

        self.settingsPageResolutionUILabel = TextLabel(self.settingsPageResolutionUIRow,
                                                       "settingsPageResolutionUILabel", "UI Scale", Font(10))
        self.settingsPageResolutionUIInput = TextInputBox(self.settingsPageResolutionUIRow,
                                                          "settingsPageResolutionUIInput", QSize(50, 40),
                                                          "UI Scale", str(res.ui_scale))
        self.settingsPageResolutionUIInput.textEdited.connect(self.on_ui_scale_update)

        self.settingsPagePathLabel = TextLabel(self.settingsPage, "settingsPagePathLabel", "Installation Path", Font(12))
        self.settingsPagePathLabelDefaultLabel = TextLabel(self.settingsPage, "settingsPagePathLabelDefaultLabel",
                                                           "Default path on Steam is C:/Program Files (x86)"
                                                           "/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/"
                                                           "Content/UI/Icons", Font(10))

        self.settingsPagePathRow = QWidget(self.settingsPage)
        self.settingsPagePathRow.setObjectName("settingsPagePathRow")
        self.settingsPagePathRowLayout = QHBoxLayout(self.settingsPagePathRow)
        self.settingsPagePathRowLayout.setObjectName("settingsPagePathRowLayout")
        self.settingsPagePathRowLayout.setContentsMargins(0, 0, 0, 0)
        self.settingsPagePathRowLayout.setSpacing(15)

        self.settingsPagePathText = TextInputBox(self.settingsPage, "settingsPagePathText", QSize(600, 40),
                                                 "Path to Dead by Daylight game icon files", str(Config().path()))
        self.settingsPagePathButton = Button(self.settingsPage, "settingsPagePathButton", "Set path to game icon files", QSize(180, 35))
        self.settingsPagePathButton.clicked.connect(self.set_path)

        self.settingsPageSaveRow = QWidget(self.settingsPage)
        self.settingsPageSaveRow.setObjectName("settingsPageSaveRow")
        self.settingsPageSaveRowLayout = QHBoxLayout(self.settingsPageSaveRow)
        self.settingsPageSaveRowLayout.setContentsMargins(0, 0, 0, 0)
        self.settingsPageSaveRowLayout.setSpacing(15)

        self.settingsPageSaveButton = Button(self.settingsPageSaveRow, "settingsPageSaveButton", "Save", QSize(60, 35))
        self.settingsPageSaveButton.clicked.connect(self.save_settings)

        self.settingsPageSaveSuccessText = TextLabel(self.settingsPageSaveRow, "settingsPageSaveSuccessText", "", Font(10))
        self.settingsPageSaveSuccessText.setVisible(False)

        # TODO reset to last saved settings button

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

        self.authorLabel = HyperlinkTextLabel(self.bottomBar, "authorLabel", "Made by IIInitiationnn",
                                              "https://github.com/IIInitiationnn/BloodEmporium", Font(8))
        self.versionLabel = TextLabel(self.bottomBar, "versionLabel", State.version, Font(8))

        '''
        central
            -> background
        '''

        self.centralLayout.addWidget(self.background, 1, 1)

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
            -> helpButton
            -> settingsButton
        '''
        self.leftMenuLayout.addWidget(self.menuColumn, 0, Qt.AlignTop)
        self.leftMenuLayout.addWidget(self.helpButton)
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
            -> helpPage
            -> settingsPage
        '''
        self.stack.addWidget(self.homePage)
        self.stack.addWidget(self.preferencesPage)
        self.stack.addWidget(self.bloodwebPage)
        self.stack.addWidget(self.helpPage)
        self.stack.addWidget(self.settingsPage)
        self.stack.setCurrentWidget(self.homePage)

        '''
        homePage
        '''
        self.homePageLayout.addStretch(1)
        self.homePageLayout.addWidget(self.homePageIcon, alignment=Qt.AlignHCenter)
        self.homePageLayout.addWidget(self.homePageRow1)
        self.homePageLayout.addWidget(self.homePageRow2)
        self.homePageLayout.addWidget(self.homePageRow3)
        self.homePageLayout.addWidget(self.homePageRow4)
        self.homePageLayout.addStretch(1)

        '''
        preferencesPage
            -> scrollArea
                -> scrollAreaContent (widget)
                    -> labels, combobox, everything
            -> scrollBar
        '''
        # rows comprising the content
        self.preferencesPageProfileSaveRowLayout.addWidget(self.preferencesPageProfileSelector)
        self.preferencesPageProfileSaveRowLayout.addWidget(self.preferencesPageSaveButton)
        self.preferencesPageProfileSaveRowLayout.addWidget(self.preferencesPageDeleteButton)
        self.preferencesPageProfileSaveRowLayout.addWidget(self.preferencesPageSaveSuccessText)
        self.preferencesPageProfileSaveRowLayout.addStretch(1)

        self.preferencesPageProfileSaveAsRowLayout.addWidget(self.preferencesPageSaveAsInput)
        self.preferencesPageProfileSaveAsRowLayout.addWidget(self.preferencesPageSaveAsButton)
        self.preferencesPageProfileSaveAsRowLayout.addWidget(self.preferencesPageSaveAsSuccessText)
        self.preferencesPageProfileSaveAsRowLayout.addStretch(1)

        self.preferencesPageSearchSortRowLayout.addWidget(self.preferencesPageSearchBar)
        self.preferencesPageSearchSortRowLayout.addWidget(self.preferencesPageSortLabel)
        self.preferencesPageSearchSortRowLayout.addWidget(self.preferencesPageSortSelector)
        self.preferencesPageSearchSortRowLayout.addStretch(1)

        # putting the rows into the content
        self.preferencesPageScrollAreaContentLayout.addWidget(self.preferencesPageProfileLabel)
        self.preferencesPageScrollAreaContentLayout.addWidget(self.preferencesPageProfileSaveRow)
        self.preferencesPageScrollAreaContentLayout.addWidget(self.preferencesPageProfileSaveAsRow)
        self.preferencesPageScrollAreaContentLayout.addSpacing(15)
        self.preferencesPageScrollAreaContentLayout.addWidget(self.preferencesPageFiltersBox)
        self.preferencesPageScrollAreaContentLayout.addWidget(self.preferencesPageSearchSortRow)
        self.preferencesPageScrollAreaContentLayout.addSpacing(15)
        for unlockableWidget in self.preferencesPageUnlockableWidgets:
            self.preferencesPageScrollAreaContentLayout.addWidget(unlockableWidget)
        self.preferencesPageScrollAreaContentLayout.addStretch(1)

        # bottom persistent bar
        self.preferencesPagePersistentBarLayout.addWidget(self.preferencesPageAllCheckbox)
        self.preferencesPagePersistentBarLayout.addWidget(self.preferencesPageSelectedLabel)
        self.preferencesPagePersistentBarLayout.addStretch(1)

        # assembling it all together
        self.preferencesPageLayout.addWidget(self.preferencesPageScrollArea, 0, 0, 1, 1)
        self.preferencesPageLayout.addWidget(self.preferencesPageScrollBar, 0, 1, 1, 1)
        self.preferencesPageLayout.addWidget(self.preferencesPagePersistentBar, 1, 0, 1, 1, Qt.AlignBottom)
        self.preferencesPageLayout.setRowStretch(0, 1)
        self.preferencesPageLayout.setColumnStretch(0, 1)

        '''
        bloodwebPage
        '''
        self.bloodwebPageRunRowLayout.addWidget(self.bloodwebPageRunButton)
        self.bloodwebPageRunRowLayout.addWidget(self.bloodwebPageRunLabel)

        self.bloodwebPageLayout.addWidget(self.bloodwebPageProfileLabel)
        self.bloodwebPageLayout.addWidget(self.bloodwebPageProfileSelector)
        self.bloodwebPageLayout.addWidget(self.bloodwebPageCharacterLabel)
        self.bloodwebPageLayout.addWidget(self.bloodwebPageCharacterSelector)
        self.bloodwebPageLayout.addWidget(self.bloodwebPageRunRow)
        self.bloodwebPageLayout.addStretch(1)

        '''
        helpPage
        '''
        self.helpPageContactDiscordRowLayout.addWidget(self.helpPageContactDiscordIcon)
        self.helpPageContactDiscordRowLayout.addWidget(self.helpPageContactDiscordLabel)
        self.helpPageContactDiscordRowLayout.addStretch(1)

        self.helpPageContactTwitterRowLayout.addWidget(self.helpPageContactTwitterIcon)
        self.helpPageContactTwitterRowLayout.addWidget(self.helpPageContactTwitterLabel)
        self.helpPageContactTwitterRowLayout.addStretch(1)

        self.helpPageLayout.addWidget(self.helpPageInstructionsLabel)
        self.helpPageLayout.addWidget(self.helpPageInstructionsDescription)
        self.helpPageLayout.addWidget(self.helpPageContactLabel)
        self.helpPageLayout.addWidget(self.helpPageContactDiscordRow)
        self.helpPageLayout.addWidget(self.helpPageContactTwitterRow)
        self.helpPageLayout.addStretch(1)

        '''
        settingsPage
        '''
        self.settingsPageResolutionWidthRowLayout.addWidget(self.settingsPageResolutionWidthLabel)
        self.settingsPageResolutionWidthRowLayout.addWidget(self.settingsPageResolutionWidthInput)
        self.settingsPageResolutionWidthRowLayout.addStretch(1)

        self.settingsPageResolutionHeightRowLayout.addWidget(self.settingsPageResolutionHeightLabel)
        self.settingsPageResolutionHeightRowLayout.addWidget(self.settingsPageResolutionHeightInput)
        self.settingsPageResolutionHeightRowLayout.addStretch(1)

        self.settingsPageResolutionUIRowLayout.addWidget(self.settingsPageResolutionUILabel)
        self.settingsPageResolutionUIRowLayout.addWidget(self.settingsPageResolutionUIInput)
        self.settingsPageResolutionUIRowLayout.addStretch(1)

        self.settingsPagePathRowLayout.addWidget(self.settingsPagePathText)
        self.settingsPagePathRowLayout.addWidget(self.settingsPagePathButton)
        self.settingsPagePathRowLayout.addStretch(1)

        self.settingsPageSaveRowLayout.addWidget(self.settingsPageSaveButton)
        self.settingsPageSaveRowLayout.addWidget(self.settingsPageSaveSuccessText)
        self.settingsPageSaveRowLayout.addStretch(1)

        self.settingsPageLayout.addWidget(self.settingsPageResolutionLabel)
        self.settingsPageLayout.addWidget(self.settingsPageResolutionUIDescription)
        self.settingsPageLayout.addWidget(self.settingsPageResolutionWidthRow)
        self.settingsPageLayout.addWidget(self.settingsPageResolutionHeightRow)
        self.settingsPageLayout.addWidget(self.settingsPageResolutionUIRow)
        self.settingsPageLayout.addWidget(self.settingsPagePathLabel)
        self.settingsPageLayout.addWidget(self.settingsPagePathLabelDefaultLabel)
        self.settingsPageLayout.addWidget(self.settingsPagePathRow)
        self.settingsPageLayout.addWidget(self.settingsPageSaveRow)
        self.settingsPageLayout.addStretch(1)



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
    help = __base + "/icon_help.png"
    down_arrow = __base + "/icon_down_arrow.png"
    right_arrow = __base + "/icon_right_arrow.png"
    discord = __base + "/icon_discord.png"
    twitter = __base + "/icon_twitter.png"

if __name__ == "__main__":
    freeze_support() # --onedir (for exe)

    os.environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    os.environ["QT_SCALE_FACTOR"] = "1"

    app = QApplication([])
    window = MainWindow()
    sys.exit(app.exec_())