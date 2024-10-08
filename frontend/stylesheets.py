import os.path


class StyleSheets:
    pink = "#ff79c6"
    purple = "#bd93f9"
    darker_purple = "rgb(90, 75, 125)"
    background = "#282a36"
    passive = "#383a50"
    selection = "#44475a"
    navy = "#6272a4"
    light_selection = "rgb(139, 158, 194)"

    debug = f"""
        background-color: {passive};
        border: 5px solid black;
    """

    white_text = "color: rgb(255, 255, 255);"
    pink_text = f"color: {pink};"
    purple_text = f"color: {purple};"

    @staticmethod
    def save_text(is_success):
        return StyleSheets.pink_text if is_success else StyleSheets.purple_text

    scroll_area = """
        QScrollArea {
            background: transparent;
            border: 0px;
        }"""

    page_button = f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: 5;
        }}
        QPushButton:hover {{
            background-color: {background};
            border: none;
            border-radius: 5;
        }}
        QPushButton:pressed {{
            background-color: {pink};
            border: none;
            border-radius: 5;
        }}"""

    check_box = f"""
        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
            border: 3px solid {navy};
            border-radius: 5px;
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border: 3px solid {light_selection};
        }}
        
        QCheckBox::indicator:checked {{
            background: {navy};
        }}"""

    check_box_some = f"""
        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
            border: 3px solid {navy};
            border-radius: 5px;
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border: 3px solid {light_selection};
        }}
        
        QCheckBox::indicator:checked {{
            background: {navy};
            image: url("assets/images/icons/icon_selected_some.png");
        }}"""

    check_box_all = f"""
        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
            border: 3px solid {navy};
            border-radius: 5px;
        }}
        
        QCheckBox::indicator:unchecked:hover {{
            border: 3px solid {light_selection};
        }}
        
        QCheckBox::indicator:checked {{
            background: {navy};
            image: url("assets/images/icons/icon_selected_all.png");
        }}"""

    check_box_read_only = f"""
        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
            background-color: {background};
            border: 3px solid {background};
            border-radius: 5px;
        }}"""

    top_bar_button = f"""
        QPushButton {{
            background-color: transparent;
            border-radius: 5;
        }}
        QPushButton:hover {{
            background-color: {passive};
            border: none;
            border-radius: 5;
        }}
        QPushButton:pressed {{
            background-color: {pink};
            border: none;
            border-radius: 5;
        }}"""

    text_box = f"""
        QLineEdit {{
            background-color: {background};
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding: 0 10px 0 10px;
            selection-background-color: {purple};
        }}
        
        QLineEdit:hover {{
            border: 2px solid {selection};
        }}"""

    text_box_read_only = f"""
        QLineEdit {{
            background-color: {background};
            color: rgb(125, 125, 125);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding: 0 10px 0 10px;
        }}
        
        QLineEdit:hover {{
            border: 2px solid {selection};
        }}"""

    multiline_text_box = f"""
        QPlainTextEdit {{
            background-color: {background};
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding: 10px 10px 0 10px;
            selection-background-color: {purple};
        }}

        QPlainTextEdit:hover {{
            border: 2px solid {selection};
        }}

        QScrollBar:vertical {{
            background: {selection};
            width: 4px;
            border: 0px solid white;
            margin: 10px 0 10px 0;
            border-radius: 4px;
        }}

        QScrollBar::handle:vertical {{
            background: {purple};
            border-radius: 2px;
        }}

        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
        }}"""

    multiline_text_box_read_only = f"""
        QPlainTextEdit {{
            background-color: {background};
            color: rgb(125, 125, 125);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding: 10px 10px 0 10px;
            selection-background-color: {purple};
        }}

        QPlainTextEdit:hover {{
            border: 2px solid {selection};
        }}

        QScrollBar:vertical {{
            background: {selection};
            width: 4px;
            border: 0px solid white;
            margin: 10px 0 10px 0;
            border-radius: 4px;
        }}

        QScrollBar::handle:vertical {{
            background: {purple};
            border-radius: 2px;
        }}

        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
        }}"""

    tiers_input_positive = f"""
        QLineEdit {{
            background-color: #323543;
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding: 0 10px 0 10px;
            selection-background-color: {purple};
        }}
        
        QLineEdit:hover {{
            border: 2px solid {selection};
        }}"""

    tiers_input_negative = f"""
        QLineEdit {{
            background-color: #1e1f29;
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding: 0 10px 0 10px;
            selection-background-color: {purple};
        }}
        
        QLineEdit:hover {{
            border: 2px solid {selection};
        }}"""

    text_box_invalid = f"""
        QLineEdit {{
            background-color: {darker_purple};
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding: 0 10px 0 10px;
            selection-background-color: {purple};
        }}
        
        QLineEdit:hover {{
            border: 2px solid {purple};
        }}"""

    @staticmethod
    def threshold_input(threshold):
        try:
            threshold = int(threshold)
        except ValueError:
            return StyleSheets.text_box_invalid

        if abs(threshold) > 999:
            return StyleSheets.text_box_invalid
        else:
            return StyleSheets.text_box

    @staticmethod
    def prestige_input(prestige_limit):
        try:
            prestige_limit = int(prestige_limit)
        except ValueError:
            return StyleSheets.text_box_invalid

        if prestige_limit > 100:
            return StyleSheets.text_box_invalid
        elif prestige_limit > 0:
            return StyleSheets.text_box
        else:
            return StyleSheets.text_box_invalid

    @staticmethod
    def bloodpoint_input(bloodpoint_limit):
        try:
            bloodpoint_limit = int(bloodpoint_limit)
        except ValueError:
            return StyleSheets.text_box_invalid

        return StyleSheets.text_box_invalid if bloodpoint_limit <= 0 else StyleSheets.text_box

    @staticmethod
    def tiers_input(tier):
        try:
            tier = int(tier)
        except ValueError:
            return StyleSheets.text_box_invalid

        if abs(tier) > 999:
            return StyleSheets.text_box_invalid
        elif tier > 0:
            return StyleSheets.tiers_input_positive
        elif tier < 0:
            return StyleSheets.tiers_input_negative
        else:
            return StyleSheets.text_box

    @staticmethod
    def settings_input(path):
        return StyleSheets.text_box if os.path.isdir(path) else StyleSheets.text_box_invalid

    @staticmethod
    def left_menu_button_inactive(padding):
        return f"""
        QPushButton {{
            background-color: transparent;
            padding: 0 {padding} 0 -{padding};
            border: none;
        }}
        QPushButton:hover {{
            background-color: {StyleSheets.passive};
            border: none;
        }}
        QPushButton:pressed {{
            background-color: {StyleSheets.purple};
            border: none;
        }}"""

    @staticmethod
    def left_menu_button_active(padding):
        return f"""
        QPushButton {{
            background-color: {StyleSheets.passive};
            padding: 0 {padding} 0 -{padding};
            border: none;
        }}
        QPushButton:hover {{
            border: none;
        }}
        QPushButton:pressed {{
            border: none;
        }}"""

    @staticmethod
    def left_menu_button(padding, is_active):
        if is_active:
            return StyleSheets.left_menu_button_active(padding)
        else:
            return StyleSheets.left_menu_button_inactive(padding)

    collapsible_box_inactive = """
        QToolButton {
            border: none;
            color: rgb(255, 255, 255);
            background: url("assets/images/icons/icon_down_arrow.png");
        }"""

    collapsible_box_active = """
        QToolButton {
            border: none;
            color: rgb(255, 255, 255);
            background: url("assets/images/icons/icon_right_arrow.png");
        }"""

    selector = f"""
        QComboBox {{
            background-color: {background};
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding: 0 10px 0 10px;
        }}

        QComboBox::disabled {{
            color: rgb(125, 125, 125);
        }}

        QComboBox:hover {{
            border: 2px solid {selection};
        }}
        
        QComboBox::drop-down {{
            width: 30px;
            border: transparent;
        }}
        
        QComboBox::down-arrow {{
            image: url("assets/images/icons/icon_down_arrow.png");
            width: 15;
            height: 15;
        }}
        
        QComboBox QAbstractItemView {{
            outline: 0px;
            color: {purple};
            background-color: {background};
            padding: 10px 10px 10px 10px;
        }}
        
        QComboBox QAbstractItemView::item {{
            min-height: 25px;
        }}
        
        QListView::item {{
            background-color: {background};
        }}
        
        QListView::item:selected {{
            color: rgb(255, 255, 255);
            background-color: {selection};
        }}

        QScrollBar:vertical {{
            background: {selection};
            width: 4px;
            border: 0px solid white;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {purple};
            min-height: 25px;
            border-radius: 2px;
        }}
        
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
        }}"""

    button = f"""
        QPushButton {{
            color: rgb(255, 255, 255);
            background-color: {background};
            border: none;
            border-radius: 5px;
        }}
        QPushButton:hover {{
            background-color: {selection};
            border: none;
        }}
        QPushButton:pressed {{
            background-color: {light_selection};
            border: none;
        }}
        QPushButton:disabled {{
            color: {selection};
        }}"""

    button_recording = f"""
        QPushButton {{
            color: {purple};
            background-color: {darker_purple};
            border: none;
            border-radius: 5px;
        }}
        QPushButton:hover {{
            background-color: {selection};
            border: none;
        }}
        QPushButton:pressed {{
            background-color: {light_selection};
            border: none;
        }}"""

    scroll_bar = f"""
        QScrollBar:vertical {{
            background: {selection};
            width: 8px;
            border: 0px solid white;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical {{
            background: {purple};
            min-height: 25px;
            border-radius: 4px;
        }}
        
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
        }}"""