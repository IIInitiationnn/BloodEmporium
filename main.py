import os
import sys
from multiprocessing import freeze_support, Pipe
from threading import Thread

from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QTimer, QRect, QObject, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QFrame, QPushButton, QGridLayout, QVBoxLayout, \
    QGraphicsDropShadowEffect, QStackedWidget, QScrollArea, QScrollBar, \
    QToolButton, QFileDialog, QSizeGrip, QProxyStyle, QStyle
from pynput import keyboard

from frontend.generic import Font, TextLabel, HyperlinkTextLabel, TextInputBox, CheckBox, Selector, Button, \
    CheckBoxWithFunction
from frontend.layouts import RowLayout
from frontend.pages.bloodweb import BloodwebPage

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

from backend.config import Config
from backend.data import Data, Unlockable
from backend.state import State
from backend.utils.text_util import TextUtil
from frontend.stylesheets import StyleSheets

# not so generic
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


# https://forum.qt.io/topic/15068/prevent-flat-qtoolbutton-from-moving-when-clicked/8
class NoShiftStyle(QProxyStyle):
    def pixelMetric(self, metric, option, widget):
        if metric == QStyle.PM_ButtonShiftHorizontal or metric == QStyle.PM_ButtonShiftVertical:
            ret = 0
        else:
            ret = QProxyStyle.pixelMetric(self, metric, option, widget)
        return ret

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

class FilterOptionsCollapsibleBox(CollapsibleBox):
    def __init__(self, parent, object_name, on_click):
        super().__init__(parent, object_name, "Filter Options (Click to Expand)")

        # TODO clear filters button
        # TODO new filter for positive / zero / negative tier, positive / zero / negative subtier, also sort by tier
        self.filters = QScrollArea(self)
        self.filters.setMinimumHeight(0)
        self.filters.setMaximumHeight(0)
        self.filters.setStyleSheet("""
            QScrollArea {
                background: rgba(0, 0, 0, 0);
                border: 0px solid rgba(0, 0, 0, 0);
            }""")

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

    # TODO auto resize rather than fixed number
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
            self.filters.setMinimumHeight(1200)
            self.filters.setMaximumHeight(1200)

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

'''class PromptWindow(QMainWindow):
    def __init__(self, parent, title, object_name):
        super().__init__(parent)

        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(300, 200)
        self.setWindowTitle(title)

        self.centralWidget = QWidget(self)
        self.centralWidget.setObjectName(f"{object_name}CentralWidget")
        self.centralWidget.setAutoFillBackground(False)
        self.setCentralWidget(self.centralWidget)

        # TODO fix background
        # TODO add top bar
        # TODO maybe swap to message popup
        self.background = QFrame(self.centralWidget)
        self.background.setObjectName(f"{object_name}Background")
        self.background.setStyleSheet(f"""
            QFrame#{object_name}Background {{
                background-color: {StyleSheets.passive};
                border-width: 1;
                border-style: solid;
                border-color: rgb(58, 64, 76);
            }}""")
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(10)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(QColor(0, 0, 0, 200))
        self.background.setGraphicsEffect(self.shadow)

    def add_button(self, name, dimensions, on_click):
        pass # TODO'''

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

class HotkeyInput(QPushButton):
    def __init__(self, parent, object_name, size, on_activate, on_deactivate):
        super().__init__(parent)
        self.on_activate = on_activate # on activating THIS button
        self.on_deactivate = on_deactivate # on deactivating THIS button
        self.pressed_keys = []
        self.setObjectName(object_name)
        self.setFixedSize(size)
        self.setStyleSheet(StyleSheets.button)
        self.pressed_keys = Config().hotkey()
        self.setText(" + ".join([TextUtil.title_case(k) for k in self.pressed_keys]))
        self.setFont(Font(10))
        self.clicked.connect(self.on_click)
        self.active = False

    def on_click(self):
        if not self.active:
            self.pressed_keys = []
            self.setStyleSheet(StyleSheets.button_recording)
            self.setText("Recording keystrokes...")
            self.on_activate()
            self.start_keyboard_listener()
            self.active = True

    def start_keyboard_listener(self):
        self.listener = keyboard.Listener(on_press=self.on_key_down, on_release=self.on_key_up)
        self.listener.start()

    def stop_keyboard_listener(self):
        self.listener.stop()
        self.listener = None

    def on_key_down(self, key):
        key = TextUtil.pynput_to_key_string(self.listener, key)
        self.pressed_keys = list(dict.fromkeys(self.pressed_keys + [key]))
        self.setText(" + ".join([TextUtil.title_case(k) for k in self.pressed_keys]))

    def on_key_up(self, key):
        self.setText(" + ".join([TextUtil.title_case(k) for k in self.pressed_keys]))

        self.active = False
        self.stop_keyboard_listener()
        self.on_deactivate()
        self.setStyleSheet(StyleSheets.button)

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

    def get_edit_profile(self):
        return self.preferencesPageProfileSelector.currentText()

    def update_profiles_from_config(self):
        while self.preferencesPageProfileSelector.count() > 0:
            self.preferencesPageProfileSelector.removeItem(0)
        self.preferencesPageProfileSelector.addItems(Config().profile_names() + ["blank"])

        while self.bloodwebPage.profileSelector.count() > 0:
            self.bloodwebPage.profileSelector.removeItem(0)
        self.bloodwebPage.profileSelector.addItems(Config().profile_names() + ["blank"])

    def replace_unlockable_widgets(self):
        sort_by = self.preferencesPageSortSelector.currentText()

        if self.lastSortedBy == sort_by:
            # if there was no change in ordering, don't pass in sort_by; the resulting visible list has arbitrary order
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
                count = self.preferencesPageScrollAreaContentLayout.count()
                self.preferencesPageScrollAreaContentLayout.insertWidget(count - 1, widget)
                widget.setVisible(is_visible)

        self.lastSortedBy = sort_by
        self.on_unlockable_select()

    def switch_edit_profile(self):
        if not self.ignore_profile_signals:
            # TODO prompt: unsaved changes (save or discard)
            config = Config()
            for widget in self.preferencesPageUnlockableWidgets:
                widget.setTiers(*config.preference(widget.unlockable.unique_id, self.get_edit_profile()))

    def save_profile(self):
        profile_id = self.get_edit_profile()
        if profile_id == "blank":
            self.show_preferences_page_save_error("You cannot save to the blank profile. "
                                                  "Use Save As below to create a new profile.")
        else:
            updated_profile = Config().get_profile_by_id(profile_id).copy()

            non_integer = Data.verify_tiers(self.preferencesPageUnlockableWidgets)
            if len(non_integer) > 0:
                self.show_preferences_page_save_error(f"There are {len(non_integer)} unlockables with invalid "
                                                      "inputs. Inputs must be a number from -999 to 999. Changes "
                                                      "not saved.")
                return

            for widget in self.preferencesPageUnlockableWidgets:
                tier, subtier = widget.getTiers()
                if tier != 0 or subtier != 0:
                    updated_profile[widget.unlockable.unique_id] = {"tier": tier, "subtier": subtier}
                else:
                    updated_profile.pop(widget.unlockable.unique_id, None)
            Config().set_profile(updated_profile)

            self.show_preferences_page_save_success(f"Changes saved to profile: {profile_id}")
            QTimer.singleShot(10000, self.hide_preferences_page_save_as_success_text)

    # def rename_profile(self):
    #     rename_prompt = PromptWindow(self, "Rename", "renamePrompt")
    #     rename_prompt.show()

    def delete_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True
            profile_id = self.get_edit_profile()
            if profile_id == "blank":
                self.show_preferences_page_save_error("You cannot delete the blank profile.")
            else:
                # TODO "are you sure" for deleting
                Config().delete_profile(profile_id)

                self.update_profiles_from_config()
                self.preferencesPageProfileSelector.setCurrentIndex(0)
                self.ignore_profile_signals = False
                self.switch_edit_profile()

                self.show_preferences_page_save_success(f"Profile deleted: {profile_id}")
            self.ignore_profile_signals = False

    def show_preferences_page_save_success(self, text):
        self.preferencesPageSaveSuccessText.setText(text)
        self.preferencesPageSaveSuccessText.setStyleSheet(StyleSheets.pink_text)
        self.preferencesPageSaveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_preferences_page_save_text)

    def show_preferences_page_save_error(self, text):
        self.preferencesPageSaveSuccessText.setText(text)
        self.preferencesPageSaveSuccessText.setStyleSheet(StyleSheets.purple_text)
        self.preferencesPageSaveSuccessText.setVisible(True)
        QTimer.singleShot(10000, self.hide_preferences_page_save_text)

    def hide_preferences_page_save_text(self):
        self.preferencesPageSaveSuccessText.setVisible(False)

    def save_as_profile(self):
        if not self.ignore_profile_signals:
            self.ignore_profile_signals = True # saving as new profile; don't trigger

            profile_id = self.preferencesPageSaveAsInput.text()
            self.preferencesPageSaveAsInput.setText("")
            if profile_id == "blank":
                self.show_preferences_page_save_as_fail_text("You cannot save to a profile named \"blank\". "
                                                             "Try a different name.")
            else:
                # TODO "are you sure" for overwriting existing profile "this will overwrite an existing profile.
                #  are you sure you want to save?"
                new_profile = {"id": profile_id}

                non_integer = Data.verify_tiers(self.preferencesPageUnlockableWidgets)
                if len(non_integer) > 0:
                    self.show_preferences_page_save_as_fail_text(f"There are {len(non_integer)} unlockables with "
                                                                 "invalid inputs. Inputs must be a number from -999 to "
                                                                 "999. Changes not saved.")
                    return

                for widget in self.preferencesPageUnlockableWidgets:
                    tier, subtier = widget.getTiers()
                    if tier != 0 or subtier != 0:
                        new_profile[widget.unlockable.unique_id] = {"tier": tier, "subtier": subtier}

                already_existed = Config().add_profile(new_profile)

                self.update_profiles_from_config()
                index = self.preferencesPageProfileSelector.findText(profile_id)
                self.preferencesPageProfileSelector.setCurrentIndex(index)

                if already_existed:
                    self.show_preferences_page_save_as_success_text("Existing profile overridden with changes: "
                                                                    f"{profile_id}")
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

    def selected_widgets(self):
        return [widget for widget in self.preferencesPageUnlockableWidgets if widget.checkBox.isChecked()]

    def on_unlockable_select(self):
        num_selected = len(self.selected_widgets())
        self.preferencesPageSelectedLabel.setText(f"{num_selected} selected")

        self.preferencesPageAllCheckbox.setChecked(num_selected > 0)
        self.preferencesPageAllCheckbox.setStyleSheet(StyleSheets.check_box_all
                                                      if all([widget.checkBox.isChecked() for widget in
                                                              [widget for widget in
                                                               self.preferencesPageUnlockableWidgets
                                                               if widget.isVisible()]])
                                                      else StyleSheets.check_box_some)

    def on_unlockable_select_all(self):
        checked = self.preferencesPageAllCheckbox.isChecked() # whether checkbox is select all (T) or deselect all (F)

        if checked:
            for widget in self.preferencesPageUnlockableWidgets:
                if widget.isVisible():
                    widget.checkBox.setChecked(True)
        else:
            for widget in self.preferencesPageUnlockableWidgets:
                widget.checkBox.setChecked(False)

        self.on_unlockable_select()

    def expand_edit(self):
        new_pos = self.preferencesPageEditDropdownButton.mapTo(self.preferencesPage,
                                                               self.preferencesPageEditDropdownButton.pos())
        new_pos.setY(new_pos.y() - 250)
        # TODO move this new_pos into an event handler
        #  (https://stackoverflow.com/questions/15238973/how-do-i-set-a-relative-position-for-a-qt-widget)
        #  - will work for resizing

        if self.preferencesPageEditDropdownButton.isChecked():
            self.preferencesPageEditDropdownButton.setStyleSheet(StyleSheets.collapsible_box_active)
            self.preferencesPageEditDropdownButton.setIcon(QIcon(Icons.right_arrow))
            self.preferencesPageEditDropdownContent.setMinimumHeight(0)
            self.preferencesPageEditDropdownContent.setMaximumHeight(0)
            self.preferencesPageEditDropdownContent.move(new_pos)
        else:
            self.preferencesPageEditDropdownButton.setStyleSheet(StyleSheets.collapsible_box_inactive)
            self.preferencesPageEditDropdownButton.setIcon(QIcon(Icons.up_arrow))
            self.preferencesPageEditDropdownContent.setMinimumHeight(200)
            self.preferencesPageEditDropdownContent.setMaximumHeight(200)
            self.preferencesPageEditDropdownContent.move(new_pos)

    def on_edit_dropdown_tier(self):
        if self.preferencesPageEditDropdownContentTierCheckBox.isChecked():
            self.preferencesPageEditDropdownContentTierInput.setReadOnly(False)
            text = self.preferencesPageEditDropdownContentTierInput.text()
            self.preferencesPageEditDropdownContentTierInput.setStyleSheet(StyleSheets.tiers_input(text))
        else:
            self.preferencesPageEditDropdownContentTierInput.setReadOnly(True)
            self.preferencesPageEditDropdownContentTierInput.setStyleSheet(StyleSheets.text_box_read_only)

    def on_edit_dropdown_subtier(self):
        if self.preferencesPageEditDropdownContentSubtierCheckBox.isChecked():
            self.preferencesPageEditDropdownContentSubtierInput.setReadOnly(False)
            text = self.preferencesPageEditDropdownContentSubtierInput.text()
            self.preferencesPageEditDropdownContentSubtierInput.setStyleSheet(StyleSheets.tiers_input(text))
        else:
            self.preferencesPageEditDropdownContentSubtierInput.setReadOnly(True)
            self.preferencesPageEditDropdownContentSubtierInput.setStyleSheet(StyleSheets.text_box_read_only)

    def on_edit_dropdown_tier_input(self):
        text = self.preferencesPageEditDropdownContentTierInput.text()
        self.preferencesPageEditDropdownContentTierInput.setStyleSheet(StyleSheets.tiers_input(text))

    def on_edit_dropdown_subtier_input(self):
        text = self.preferencesPageEditDropdownContentSubtierInput.text()
        self.preferencesPageEditDropdownContentSubtierInput.setStyleSheet(StyleSheets.tiers_input(text))

    def on_edit_dropdown_apply(self):
        tier = self.preferencesPageEditDropdownContentTierInput.text()
        subtier = self.preferencesPageEditDropdownContentSubtierInput.text()
        for widget in self.selected_widgets():
            if self.preferencesPageEditDropdownContentTierCheckBox.isChecked():
                widget.setTiers(tier=tier)
            if self.preferencesPageEditDropdownContentSubtierCheckBox.isChecked():
                widget.setTiers(subtier=subtier)
        self.on_edit_dropdown_minimise()

    def on_edit_dropdown_minimise(self):
        if self.preferencesPageEditDropdownContentTierCheckBox.isChecked():
            self.preferencesPageEditDropdownContentTierCheckBox.animateClick()
        if self.preferencesPageEditDropdownContentSubtierCheckBox.isChecked():
            self.preferencesPageEditDropdownContentSubtierCheckBox.animateClick()
        self.preferencesPageEditDropdownContentTierInput.setText("0")
        self.preferencesPageEditDropdownContentSubtierInput.setText("0")
        self.preferencesPageEditDropdownButton.animateClick()
        self.expand_edit()

    # bloodweb
    def get_runtime_profile(self):
        return self.bloodwebPage.profileSelector.currentText()

    def get_runtime_character(self):
        return self.bloodwebPage.characterSelector.currentText()

    def get_runtime_prestige_limit(self) -> str or None:
        return self.bloodwebPage.prestigeInput.text() if self.bloodwebPage.prestigeCheckBox.isChecked() else None

    def get_runtime_bloodpoint_limit(self) -> str or None:
        return self.bloodwebPage.bloodpointInput.text() if self.bloodwebPage.bloodpointCheckBox.isChecked() else None

    def run_terminate(self, debug=False, write_to_output=False):
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
                            prestige_limit, bp_limit))
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

    # settings
    def on_width_update(self):
        text = self.settingsPageResolutionWidthInput.text()
        self.settingsPageResolutionWidthInput.setStyleSheet(StyleSheets.settings_input(width=text))

    def on_height_update(self):
        text = self.settingsPageResolutionHeightInput.text()
        self.settingsPageResolutionHeightInput.setStyleSheet(StyleSheets.settings_input(height=text))

    def on_ui_scale_update(self):
        text = self.settingsPageResolutionUIInput.text()
        self.settingsPageResolutionUIInput.setStyleSheet(StyleSheets.settings_input(ui_scale=text))

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
                                                   "UI scale must be an integer between 70 and 100. Changes not saved.")
            return

        path = self.settingsPagePathText.text()
        if not Data.verify_path(path):
            self.show_settings_page_save_fail_text("Ensure path is an actual folder. Changes not saved.")
            return

        hotkey = self.settingsPageHotkeyInput.pressed_keys

        Config().set_resolution(int(width), int(height), int(ui_scale))
        Config().set_path(path)
        Config().set_hotkey(hotkey)
        self.show_settings_page_save_success_text("Settings changed.")

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

    def __init__(self, state_pipe_, emitter):
        super().__init__()
        # TODO windows up + windows down; cursor when hovering over buttons

        TextInputBox.on_focus_in_callback = self.stop_keyboard_listener
        TextInputBox.on_focus_out_callback = self.start_keyboard_listener
        self.pressed_keys = []
        self.start_keyboard_listener()

        self.is_maximized = False
        self.ignore_profile_signals = False # used to prevent infinite recursion e.g. when setting dropdown to a profile
        self.state = State(state_pipe_)

        self.emitter = emitter
        self.emitter.start() # start the thread, calling Emitter.run()

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setBaseSize(1230, 670)
        self.setMinimumSize(1100, 600)
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
                                    "First time here? Recently change your game / display settings? "
                                    "Set up your config.")
        self.homePageRow2 = HomeRow(self.homePage, 2, QIcon(Icons.preferences), self.preferencesButton.on_click,
                                    "What would you like from the bloodweb? Set up your preferences.")
        self.homePageRow3 = HomeRow(self.homePage, 3, QIcon(Icons.bloodweb), self.bloodwebButton.on_click,
                                    "Ready? Start clearing your bloodweb (with optional spending limits)!")
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
        self.preferencesPageScrollArea.setStyleSheet("""
            QScrollArea#preferencesPageScrollArea {
                background: transparent;
                border: 0px;
            }""")

        self.preferencesPageScrollAreaContent = QWidget(self.preferencesPageScrollArea)
        self.preferencesPageScrollAreaContent.setObjectName("preferencesPageScrollAreaContent")
        self.preferencesPageScrollAreaContent.setStyleSheet("""
            QWidget#preferencesPageScrollAreaContent {
                background: transparent;
            }""")
        self.preferencesPageScrollArea.setWidget(self.preferencesPageScrollAreaContent)

        self.preferencesPageScrollAreaContentLayout = QVBoxLayout(self.preferencesPageScrollAreaContent)
        self.preferencesPageScrollAreaContentLayout.setObjectName("preferencesPageScrollAreaContentLayout")
        self.preferencesPageScrollAreaContentLayout.setContentsMargins(0, 0, 0, 0)
        self.preferencesPageScrollAreaContentLayout.setSpacing(15)

        # save, rename, delete
        self.preferencesPageProfileSaveRow = QWidget(self.preferencesPageScrollAreaContent)
        self.preferencesPageProfileSaveRow.setObjectName("preferencesPageProfileSaveRow")
        self.preferencesPageProfileSaveRowLayout = RowLayout(self.preferencesPageProfileSaveRow,
                                                             "preferencesPageProfileSaveRowLayout")

        self.preferencesPageProfileLabel = TextLabel(self.preferencesPageScrollAreaContent,
                                                     "preferencesPageProfileLabel", "Profile", Font(12))

        self.preferencesPageProfileSelector = Selector(self.preferencesPageProfileSaveRow,
                                                       "preferencesPageProfileSelector",
                                                       QSize(200, 40), Config().profile_names() + ["blank"])
        self.preferencesPageProfileSelector.currentIndexChanged.connect(self.switch_edit_profile)

        self.preferencesPageSaveButton = Button(self.preferencesPageProfileSaveRow, "preferencesPageSaveButton",
                                                "Save", QSize(60, 35))
        self.preferencesPageSaveButton.clicked.connect(self.save_profile)

        # self.preferencesPageRenameButton = Button(self.preferencesPageProfileSaveRow,
        #                                           "preferencesPageRenameButton", "Rename", QSize(75, 35))
        # self.preferencesPageRenameButton.clicked.connect(self.rename_profile)

        self.preferencesPageDeleteButton = Button(self.preferencesPageProfileSaveRow, "preferencesPageDeleteButton",
                                                  "Delete", QSize(75, 35))
        self.preferencesPageDeleteButton.clicked.connect(self.delete_profile)

        self.preferencesPageSaveSuccessText = TextLabel(self.preferencesPageProfileSaveRow,
                                                        "preferencesPageSaveSuccessText", "", Font(10))
        self.preferencesPageSaveSuccessText.setVisible(False)

        # save as
        self.preferencesPageProfileSaveAsRow = QWidget(self.preferencesPageScrollAreaContent)
        self.preferencesPageProfileSaveAsRow.setObjectName("preferencesPageProfileSaveAsRow")
        self.preferencesPageProfileSaveAsRowLayout = RowLayout(self.preferencesPageProfileSaveAsRow,
                                                               "preferencesPageProfileSaveAsRowLayout")

        self.preferencesPageSaveAsInput = TextInputBox(self.preferencesPageProfileSaveAsRow,
                                                       "preferencesPageSaveAsInput",
                                                       QSize(200, 40), "Enter profile name")

        self.preferencesPageSaveAsButton = Button(self.preferencesPageProfileSaveAsRow, "preferencesPageSaveAsButton",
                                                  "Save As", QSize(80, 35))
        self.preferencesPageSaveAsButton.clicked.connect(self.save_as_profile)

        self.preferencesPageSaveAsSuccessText = TextLabel(self.preferencesPageProfileSaveAsRow,
                                                          "preferencesPageSaveAsSuccessText",
                                                          "", Font(10))
        self.preferencesPageSaveAsSuccessText.setVisible(False)

        # filters
        self.preferencesPageFiltersBox = FilterOptionsCollapsibleBox(self.preferencesPageScrollAreaContent,
                                                                     "preferencesPageFiltersBox",
                                                                     self.replace_unlockable_widgets)

        # search bar & sort
        self.preferencesPageSearchSortRow = QWidget(self.preferencesPageScrollAreaContent)
        self.preferencesPageSearchSortRow.setObjectName("preferencesPageSearchSortRow")
        self.preferencesPageSearchSortRowLayout = RowLayout(self.preferencesPageSearchSortRow,
                                                            "preferencesPageSearchSortRowLayout")

        self.preferencesPageSearchBar = TextInputBox(self.preferencesPageSearchSortRow, "preferencesPageSearchBar",
                                                     QSize(200, 40), "Search by name")
        self.preferencesPageSearchBar.textEdited.connect(self.replace_unlockable_widgets)
        self.preferencesPageSortLabel = TextLabel(self.preferencesPageSearchSortRow, "preferencesPageSortLabel",
                                                  "Sort by")
        self.preferencesPageSortSelector = Selector(self.preferencesPageSearchSortRow, "preferencesPageSortSelector",
                                                    QSize(150, 40), Data.get_sorts())
        self.preferencesPageSortSelector.currentIndexChanged.connect(self.replace_unlockable_widgets)
        self.lastSortedBy = "name" # cache of last sort

        # all unlockables
        self.preferencesPageUnlockableWidgets = []
        config = Config()
        for unlockable in Data.get_unlockables():
            if unlockable.category in ["unused", "retired"]:
                continue
            self.preferencesPageUnlockableWidgets.append(UnlockableWidget(self.preferencesPageScrollAreaContent,
                                                                          unlockable,
                                                                          *config.preference(unlockable.unique_id,
                                                                                             self.get_edit_profile()),
                                                                          self.on_unlockable_select))

        # select all bar
        self.preferencesPagePersistentBar = QWidget(self.preferencesPage)
        self.preferencesPagePersistentBar.setObjectName("preferencesPagePersistentBar")
        self.preferencesPagePersistentBar.setStyleSheet(f"""
        QWidget#preferencesPagePersistentBar {{
            border-top: 6px solid {StyleSheets.selection};
            border-radius: 3px;           
        }}""")
        self.preferencesPagePersistentBar.setMinimumHeight(80)
        self.preferencesPagePersistentBarLayout = RowLayout(self.preferencesPagePersistentBar,
                                                            "preferencesPagePersistentBarLayout")

        self.preferencesPageAllCheckbox = CheckBoxWithFunction(self.preferencesPagePersistentBar,
                                                               "preferencesPageAllCheckbox",
                                                               self.on_unlockable_select_all,
                                                               style_sheet=StyleSheets.check_box_all)
        # TODO hover over says select all / deselect all ^
        self.preferencesPageSelectedLabel = TextLabel(self.preferencesPagePersistentBar,
                                                      "preferencesPageSelectedLabel", "0 selected")
        # TODO to the right, confirmation text like with saving

        # edit dropdown
        self.preferencesPageEditDropdown = QWidget(self.preferencesPagePersistentBar)
        self.preferencesPageEditDropdown.setObjectName("preferencesPageEditDropdown")

        self.preferencesPageEditDropdownLayout = QGridLayout(self.preferencesPageEditDropdown)
        self.preferencesPageEditDropdownLayout.setContentsMargins(0, 0, 0, 0)
        self.preferencesPageEditDropdownLayout.setSpacing(0)

        self.preferencesPageEditDropdownButton = QToolButton(self.preferencesPageEditDropdown)
        self.preferencesPageEditDropdownButton.setObjectName("preferencesPageEditDropdownButton")
        self.preferencesPageEditDropdownButton.setCheckable(True)
        self.preferencesPageEditDropdownButton.setChecked(False)
        self.preferencesPageEditDropdownButton.setFont(Font(10))
        self.preferencesPageEditDropdownButton.setStyleSheet(StyleSheets.collapsible_box_inactive)
        self.preferencesPageEditDropdownButton.setText("Edit")
        self.preferencesPageEditDropdownButton.setIcon(QIcon(Icons.right_arrow))
        self.preferencesPageEditDropdownButton.setIconSize(QSize(20, 20))
        self.preferencesPageEditDropdownButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.preferencesPageEditDropdownButton.setStyle(NoShiftStyle())
        self.preferencesPageEditDropdownButton.pressed.connect(self.expand_edit)

        self.preferencesPageEditDropdownContent = QWidget(self.preferencesPage)
        self.preferencesPageEditDropdownContent.setObjectName("preferencesPageEditDropdownContent")
        self.preferencesPageEditDropdownContent.setMinimumHeight(0)
        self.preferencesPageEditDropdownContent.setMaximumHeight(0)
        self.preferencesPageEditDropdownContent.setFixedWidth(260)
        self.preferencesPageEditDropdownContent.setStyleSheet(f"""
            QWidget#preferencesPageEditDropdownContent {{
                background-color: {StyleSheets.passive};
                border: 3px solid {StyleSheets.selection};
                border-radius: 3px;
            }}""")

        self.preferencesPageEditDropdownContentLayout = QVBoxLayout(self.preferencesPageEditDropdownContent)
        self.preferencesPageEditDropdownContentLayout.setContentsMargins(25, 25, 25, 25)
        self.preferencesPageEditDropdownContentLayout.setSpacing(15)

        self.preferencesPageEditDropdownContentTierRow = QWidget(self.preferencesPageEditDropdownContent)
        self.preferencesPageEditDropdownContentTierRow.setObjectName("preferencesPageEditDropdownContentTierRow")
        self.preferencesPageEditDropdownContentTierRowLayout = RowLayout(self.preferencesPageEditDropdownContentTierRow,
                                                                         "preferencesPageEditDropdownContentTierRowLayout")

        self.preferencesPageEditDropdownContentTierCheckBox = CheckBoxWithFunction(self.preferencesPageEditDropdownContentTierRow,
                                                                                   "preferencesPageEditDropdownContentTierCheckBox",
                                                                                   self.on_edit_dropdown_tier)
        self.preferencesPageEditDropdownContentTierLabel = TextLabel(self.preferencesPageEditDropdownContentTierRow,
                                                                     "preferencesPageEditDropdownContentTierLabel",
                                                                     "Tier")
        self.preferencesPageEditDropdownContentTierInput = TextInputBox(self.preferencesPageEditDropdownContentTierRow,
                                                                        "preferencesPageEditDropdownContentTierInput",
                                                                        QSize(110, 40), "Enter tier", "0",
                                                                        style_sheet=StyleSheets.text_box_read_only)
        self.preferencesPageEditDropdownContentTierInput.textEdited.connect(self.on_edit_dropdown_tier_input)
        self.preferencesPageEditDropdownContentTierInput.setReadOnly(True)

        self.preferencesPageEditDropdownContentSubtierRow = QWidget(self.preferencesPageEditDropdownContent)
        self.preferencesPageEditDropdownContentSubtierRow.setObjectName("preferencesPageEditDropdownContentSubtierRow")
        self.preferencesPageEditDropdownContentSubtierRowLayout = RowLayout(self.preferencesPageEditDropdownContentSubtierRow,
                                                                            "preferencesPageEditDropdownContentSubtierRowLayout")

        self.preferencesPageEditDropdownContentSubtierCheckBox = CheckBoxWithFunction(self.preferencesPageEditDropdownContentSubtierRow,
                                                                                      "preferencesPageEditDropdownContentSubtierCheckBox",
                                                                                      self.on_edit_dropdown_subtier)
        self.preferencesPageEditDropdownContentSubtierLabel = TextLabel(self.preferencesPageEditDropdownContentSubtierRow,
                                                                        "preferencesPageEditDropdownContentSubtierLabel",
                                                                        "Subtier")
        self.preferencesPageEditDropdownContentSubtierInput = TextInputBox(self.preferencesPageEditDropdownContentSubtierRow,
                                                                           "preferencesPageEditDropdownContentSubtierInput",
                                                                           QSize(110, 40), "Enter subtier", "0",
                                                                           style_sheet=StyleSheets.text_box_read_only)
        self.preferencesPageEditDropdownContentSubtierInput.textEdited.connect(self.on_edit_dropdown_subtier_input)
        self.preferencesPageEditDropdownContentSubtierInput.setReadOnly(True)

        self.preferencesPageEditDropdownContentApplyRow = QWidget(self.preferencesPageEditDropdownContent)
        self.preferencesPageEditDropdownContentApplyRow.setObjectName("preferencesPageEditDropdownContentApplyRow")
        self.preferencesPageEditDropdownContentApplyRowLayout = RowLayout(self.preferencesPageEditDropdownContentApplyRow,
                                                                          "preferencesPageEditDropdownContentApplyRowLayout")

        self.preferencesPageEditDropdownContentApplyButton = Button(self.preferencesPageEditDropdownContentApplyRow,
                                                                    "preferencesPageEditDropdownContentApplyButton",
                                                                    "Apply", QSize(70, 35))
        self.preferencesPageEditDropdownContentApplyButton.clicked.connect(self.on_edit_dropdown_apply)

        self.preferencesPageEditDropdownContentCancelButton = Button(self.preferencesPageEditDropdownContentApplyRow,
                                                                     "preferencesPageEditDropdownContentCancelButton",
                                                                     "Cancel", QSize(70, 35))
        self.preferencesPageEditDropdownContentCancelButton.clicked.connect(self.on_edit_dropdown_minimise)

        # stack: bloodwebPage
        self.bloodwebPage = BloodwebPage()
        self.bloodwebButton.setPage(self.bloodwebPage)
        self.bloodwebPage.runButton.clicked.connect(self.run_terminate)

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
                                                         "One preset profile comes with the program: cheapskate (for levelling up the bloodweb as cheaply as possible). "
                                                         "It comes in two variants, one which prioritises perks, and one which ignores them. "
                                                         "You can use this preset as a starting point for your own profile, or "
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
                                                         "Then simply select a profile, select the character whose bloodweb you are on, set any limits you want, and run! "
                                                         "Make sure your shaders are off before running, or the program is very likely to perform in unintended ways.",
                                                         Font(10))
        self.helpPageInstructionsDescription.setWordWrap(True)

        self.helpPageContactLabel = TextLabel(self.helpPage, "helpPageContactLabel", "Contact Me", Font(12))

        self.helpPageContactDiscordRow = QWidget(self.helpPage)
        self.helpPageContactDiscordRow.setObjectName("helpPageContactDiscordRow")
        self.helpPageContactDiscordRowLayout = RowLayout(self.helpPageContactDiscordRow,
                                                         "helpPageContactDiscordRowLayout")

        self.helpPageContactDiscordIcon = QLabel(self.helpPageContactDiscordRow)
        self.helpPageContactDiscordIcon.setObjectName("helpPageContactDiscordIcon")
        self.helpPageContactDiscordIcon.setFixedSize(QSize(20, 20))
        self.helpPageContactDiscordIcon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.discord))
        self.helpPageContactDiscordIcon.setScaledContents(True)
        self.helpPageContactDiscordLabel = HyperlinkTextLabel(self.helpPageContactDiscordRow,
                                                              "helpPageContactDiscordLabel",
                                                              "Discord", "https://discord.gg/bGdJTnF2hr", Font(10))

        self.helpPageContactTwitterRow = QWidget(self.helpPage)
        self.helpPageContactTwitterRow.setObjectName("helpPageContactTwitterRow")
        self.helpPageContactTwitterRowLayout = RowLayout(self.helpPageContactTwitterRow,
                                                         "helpPageContactTwitterRowLayout")

        self.helpPageContactTwitterIcon = QLabel(self.helpPageContactTwitterRow)
        self.helpPageContactTwitterIcon.setObjectName("helpPageContactTwitterIcon")
        self.helpPageContactTwitterIcon.setFixedSize(QSize(20, 20))
        self.helpPageContactTwitterIcon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.twitter))
        self.helpPageContactTwitterIcon.setScaledContents(True)
        self.helpPageContactTwitterLabel = HyperlinkTextLabel(self.helpPageContactTwitterRow,
                                                              "helpPageContactTwitterLabel", "Twitter",
                                                              "https://twitter.com/initiationmusic", Font(10))

        # stack: settingsPage
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName("settingsPage")
        self.settingsButton.setPage(self.settingsPage)

        self.settingsPageLayout = QVBoxLayout(self.settingsPage)
        self.settingsPageLayout.setObjectName("settingsPageLayout")
        self.settingsPageLayout.setContentsMargins(25, 25, 25, 25)
        self.settingsPageLayout.setSpacing(15)

        res = Config().resolution()
        self.settingsPageResolutionLabel = TextLabel(self.settingsPage, "settingsPageResolutionLabel",
                                                     "Display Resolution", Font(12))
        self.settingsPageResolutionUIDescription = TextLabel(self.settingsPage,
                                                             "settingsPageResolutionUIDescription",
                                                             "You can find your UI scale in your Dead by Daylight "
                                                             "settings under Graphics -> UI / HUD -> UI Scale.",
                                                             Font(10))
        self.settingsPageResolutionWidthRow = QWidget(self.settingsPage)
        self.settingsPageResolutionWidthRow.setObjectName("settingsPageResolutionWidthRow")

        self.settingsPageResolutionWidthRowLayout = RowLayout(self.settingsPageResolutionWidthRow,
                                                              "settingsPageResolutionWidthRowLayout")

        self.settingsPageResolutionWidthLabel = TextLabel(self.settingsPageResolutionWidthRow,
                                                          "settingsPageResolutionWidthLabel", "Width", Font(10))
        self.settingsPageResolutionWidthInput = TextInputBox(self.settingsPageResolutionWidthRow,
                                                             "settingsPageResolutionWidthInput", QSize(70, 40),
                                                             "Width", str(res.width))
        self.settingsPageResolutionWidthInput.textEdited.connect(self.on_width_update)

        self.settingsPageResolutionHeightRow = QWidget(self.settingsPage)
        self.settingsPageResolutionHeightRow.setObjectName("settingsPageResolutionHeightRow")
        self.settingsPageResolutionHeightRowLayout = RowLayout(self.settingsPageResolutionHeightRow,
                                                               "settingsPageResolutionHeightRowLayout")

        self.settingsPageResolutionHeightLabel = TextLabel(self.settingsPageResolutionHeightRow,
                                                           "settingsPageResolutionHeightLabel", "Height", Font(10))
        self.settingsPageResolutionHeightInput = TextInputBox(self.settingsPageResolutionHeightRow,
                                                              "settingsPageResolutionHeightInput", QSize(70, 40),
                                                              "Height", str(res.height))
        self.settingsPageResolutionHeightInput.textEdited.connect(self.on_height_update)

        self.settingsPageResolutionUIRow = QWidget(self.settingsPage)
        self.settingsPageResolutionUIRow.setObjectName("settingsPageResolutionUIRow")
        self.settingsPageResolutionUIRowLayout = RowLayout(self.settingsPageResolutionUIRow,
                                                           "settingsPageResolutionUIRowLayout")

        self.settingsPageResolutionUILabel = TextLabel(self.settingsPageResolutionUIRow,
                                                       "settingsPageResolutionUILabel", "UI Scale", Font(10))
        self.settingsPageResolutionUIInput = TextInputBox(self.settingsPageResolutionUIRow,
                                                          "settingsPageResolutionUIInput", QSize(70, 40),
                                                          "UI Scale", str(res.ui_scale))
        self.settingsPageResolutionUIInput.textEdited.connect(self.on_ui_scale_update)

        self.settingsPagePathLabel = TextLabel(self.settingsPage, "settingsPagePathLabel", "Installation Path",
                                               Font(12))
        self.settingsPagePathLabelDefaultLabel = TextLabel(self.settingsPage, "settingsPagePathLabelDefaultLabel",
                                                           "Default path on Steam is C:/Program Files (x86)"
                                                           "/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/"
                                                           "Content/UI/Icons", Font(10))

        self.settingsPagePathRow = QWidget(self.settingsPage)
        self.settingsPagePathRow.setObjectName("settingsPagePathRow")
        self.settingsPagePathRowLayout = RowLayout(self.settingsPagePathRow, "settingsPagePathRowLayout")

        self.settingsPagePathText = TextInputBox(self.settingsPage, "settingsPagePathText", QSize(550, 40),
                                                 "Path to Dead by Daylight game icon files", str(Config().path()))
        self.settingsPagePathButton = Button(self.settingsPage, "settingsPagePathButton", "Set path to game icon files",
                                             QSize(180, 35))
        self.settingsPagePathButton.clicked.connect(self.set_path)

        self.settingsPageHotkeyLabel = TextLabel(self.settingsPage, "settingsPageHotkeyLabel", "Hotkey",
                                                 Font(12))
        self.settingsPageHotkeyDescription = TextLabel(self.settingsPage, "settingsPageHotkeyDescription",
                                                       "Shortcut to run or terminate the automatic bloodweb process.",
                                                       Font(10))

        self.settingsPageHotkeyInput = HotkeyInput(self.settingsPage, "settingsPageHotkeyInput", QSize(300, 40),
                                                   self.stop_keyboard_listener, self.start_keyboard_listener)

        self.settingsPageSaveRow = QWidget(self.settingsPage)
        self.settingsPageSaveRow.setObjectName("settingsPageSaveRow")
        self.settingsPageSaveRowLayout = RowLayout(self.settingsPageSaveRow, "settingsPageSaveRowLayout")

        self.settingsPageSaveButton = Button(self.settingsPageSaveRow, "settingsPageSaveButton", "Save", QSize(60, 35))
        self.settingsPageSaveButton.clicked.connect(self.save_settings)

        self.settingsPageSaveSuccessText = TextLabel(self.settingsPageSaveRow, "settingsPageSaveSuccessText", "",
                                                     Font(10))
        self.settingsPageSaveSuccessText.setVisible(False)

        # TODO reset to last saved settings button

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

        """
        preferencesPage
            -> scrollArea
                -> scrollAreaContent (widget)
                    -> labels, combobox, everything
            -> scrollBar
        """
        # rows comprising the content
        self.preferencesPageProfileSaveRowLayout.addWidget(self.preferencesPageProfileSelector)
        self.preferencesPageProfileSaveRowLayout.addWidget(self.preferencesPageSaveButton)
        # self.preferencesPageProfileSaveRowLayout.addWidget(self.preferencesPageRenameButton)
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
        self.preferencesPageEditDropdownContentTierRowLayout.addWidget(self.preferencesPageEditDropdownContentTierCheckBox)
        self.preferencesPageEditDropdownContentTierRowLayout.addWidget(self.preferencesPageEditDropdownContentTierLabel)
        self.preferencesPageEditDropdownContentTierRowLayout.addStretch(1)
        self.preferencesPageEditDropdownContentTierRowLayout.addWidget(self.preferencesPageEditDropdownContentTierInput)

        self.preferencesPageEditDropdownContentSubtierRowLayout.addWidget(self.preferencesPageEditDropdownContentSubtierCheckBox)
        self.preferencesPageEditDropdownContentSubtierRowLayout.addWidget(self.preferencesPageEditDropdownContentSubtierLabel)
        self.preferencesPageEditDropdownContentSubtierRowLayout.addStretch(1)
        self.preferencesPageEditDropdownContentSubtierRowLayout.addWidget(self.preferencesPageEditDropdownContentSubtierInput)

        self.preferencesPageEditDropdownContentApplyRowLayout.addStretch(1)
        self.preferencesPageEditDropdownContentApplyRowLayout.addWidget(self.preferencesPageEditDropdownContentApplyButton)
        self.preferencesPageEditDropdownContentApplyRowLayout.addWidget(self.preferencesPageEditDropdownContentCancelButton)

        self.preferencesPageEditDropdownContentLayout.addWidget(self.preferencesPageEditDropdownContentTierRow)
        self.preferencesPageEditDropdownContentLayout.addWidget(self.preferencesPageEditDropdownContentSubtierRow)
        self.preferencesPageEditDropdownContentLayout.addWidget(self.preferencesPageEditDropdownContentApplyRow)

        self.preferencesPageEditDropdownLayout.addWidget(self.preferencesPageEditDropdownButton, 0, 0, 1, 1)

        self.preferencesPagePersistentBarLayout.addWidget(self.preferencesPageAllCheckbox)
        self.preferencesPagePersistentBarLayout.addWidget(self.preferencesPageSelectedLabel)
        self.preferencesPagePersistentBarLayout.addWidget(self.preferencesPageEditDropdown)
        self.preferencesPagePersistentBarLayout.addStretch(1)

        # assembling it all together
        self.preferencesPageLayout.addWidget(self.preferencesPageScrollArea, 0, 0, 1, 1)
        self.preferencesPageLayout.addWidget(self.preferencesPageScrollBar, 0, 1, 1, 1)
        self.preferencesPageLayout.addWidget(self.preferencesPagePersistentBar, 1, 0, 1, 1, Qt.AlignBottom)
        self.preferencesPageLayout.setRowStretch(0, 1)
        self.preferencesPageLayout.setColumnStretch(0, 1)

        """
        helpPage
        """
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

        """
        settingsPage
        """
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
        self.settingsPageLayout.addWidget(self.settingsPageHotkeyLabel)
        self.settingsPageLayout.addWidget(self.settingsPageHotkeyDescription)
        self.settingsPageLayout.addWidget(self.settingsPageHotkeyInput)
        self.settingsPageLayout.addWidget(self.settingsPageSaveRow)
        self.settingsPageLayout.addStretch(1)

        self.preferencesPageSortSelector.setCurrentIndex(1) # self.lastSortedBy becomes "character"

        self.emitter.prestige.connect(self.bloodwebPage.on_prestige_signal)
        self.emitter.bloodpoint.connect(self.bloodwebPage.on_bloodpoint_signal)
        self.emitter.terminate.connect(self.state.terminate)
        self.emitter.toggle_text.connect(self.toggle_run_terminate_text)

        self.show()

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
    window = MainWindow(state_pipe, main_emitter)
    sys.exit(app.exec_())