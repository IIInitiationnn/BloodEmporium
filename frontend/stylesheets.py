import os.path


class StyleSheets:
    pink = "rgb(255, 121, 198)" # #ff79c6
    purple = "rgb(189, 147, 249)" # #bd93f9
    darker_purple = "rgb(90, 75, 125)"

    debug = '''
        background-color: rgb(40, 44, 52);
        border: 5px solid black;
    '''

    white_text = "color: rgb(255, 255, 255);"
    pink_text = f"color: {pink};"
    purple_text = f"color: {purple};"

    @staticmethod
    def save_text(is_success):
        return StyleSheets.pink_text if is_success else StyleSheets.purple_text

    page_button = '''
        QPushButton {
            background-color: transparent;
            border: none;
            border-radius: 5;
        }
        QPushButton:hover {
            background-color: rgb(33, 37, 43);
            border: none;
            border-radius: 5;
        }
        QPushButton:pressed {
            background-color: rgb(255, 121, 198);
            border: none;
            border-radius: 5;
        }'''

    check_box = '''
        QCheckBox::indicator {
            width: 15px;
            height: 15px;
            border: 3px solid rgb(94, 104, 122);
            border-radius: 5px;
        }
        
        QCheckBox::indicator:unchecked:hover {
            border: 3px solid rgb(139, 158, 194);
        }
        
        QCheckBox::indicator:checked {
            background: rgb(94, 104, 122);
        }'''

    top_bar_button = '''
        QPushButton {
            background-color: transparent;
            border-radius: 5;
        }
        QPushButton:hover {
            background-color: rgb(40, 44, 52);
            border: none;
            border-radius: 5;
        }
        QPushButton:pressed {
            background-color: rgb(255, 121, 198);
            border: none;
            border-radius: 5;
        }'''

    text_box = '''
        QLineEdit {
            background-color: rgb(33, 37, 43);
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding-left: 10px;
        }
        
        QLineEdit:hover {
            border: 2px solid rgb(47, 52, 61);
        }'''

    tiers_input_positive = '''
        QLineEdit {
            background-color: rgb(37, 41, 48);
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding-left: 10px;
        }
        
        QLineEdit:hover {
            border: 2px solid rgb(47, 52, 61);
        }'''

    tiers_input_negative = '''
        QLineEdit {
            background-color: rgb(27, 30, 35);
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding-left: 10px;
        }
        
        QLineEdit:hover {
            border: 2px solid rgb(47, 52, 61);
        }'''

    text_box_invalid = f'''
        QLineEdit {{
            background-color: {darker_purple};
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding-left: 10px;
        }}
        
        QLineEdit:hover {{
            border: 2px solid {purple};
        }}'''

    @staticmethod
    def tiers_input(tier):
        try:
            int(tier)
        except ValueError:
            return StyleSheets.text_box_invalid

        tier = int(tier)
        if abs(tier) > 999:
            return StyleSheets.text_box_invalid
        elif tier > 0:
            return StyleSheets.tiers_input_positive
        elif tier < 0:
            return StyleSheets.tiers_input_negative
        else:
            return StyleSheets.text_box

    @staticmethod
    def settings_input(width=None, height=None, ui_scale=None, path=None):
        if width is not None:
            try:
                int(width)
                return StyleSheets.text_box
            except ValueError:
                return StyleSheets.text_box_invalid
        elif height is not None:
            try:
                int(width)
                return StyleSheets.text_box
            except ValueError:
                return StyleSheets.text_box_invalid
        elif ui_scale is not None:
            try:
                ui_scale = int(ui_scale)
                return StyleSheets.text_box if 70 <= ui_scale <= 100 else StyleSheets.text_box_invalid
            except ValueError:
                return StyleSheets.text_box_invalid
        elif path is not None:
            return StyleSheets.text_box if os.path.isdir(path) else StyleSheets.text_box_invalid

    @staticmethod
    def left_menu_button_inactive(padding):
        return f'''
        QPushButton {{
            background-color: transparent;
            padding: 0 {padding} 0 -{padding};
            border: none;
        }}
        QPushButton:hover {{
            background-color: rgb(40, 44, 52);
            border: none;
        }}
        QPushButton:pressed {{
            background-color: rgb(189, 147, 249);
            border: none;
        }}'''

    @staticmethod
    def left_menu_button_active(padding):
        return f'''
        QPushButton {{
            background-color: rgb(40, 44, 52);
            padding: 0 {padding} 0 -{padding};
            border: none;
        }}
        QPushButton:hover {{
            border: none;
        }}
        QPushButton:pressed {{
            border: none;
        }}'''

    @staticmethod
    def left_menu_button(padding, is_active):
        if is_active:
            return StyleSheets.left_menu_button_active(padding)
        else:
            return StyleSheets.left_menu_button_inactive(padding)

    collapsible_box_inactive = '''
        QToolButton {
            border: none;
            color: rgb(255, 255, 255);
            background: url("assets/images/icons/icon_down_arrow.png");
        }'''

    collapsible_box_active = '''
        QToolButton {
            border: none;
            color: rgb(255, 255, 255);
            background: url("assets/images/icons/icon_right_arrow.png");
        }'''

    selector = f'''
        QComboBox {{
            background-color: rgb(33, 37, 43);
            color: rgb(255, 255, 255);
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding-left: 10px;
        }}
        
        QComboBox:hover {{
            border: 2px solid rgb(47, 52, 61);
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
            color: rgb(189, 147, 249);
            background-color: rgb(33, 37, 43);
            padding: 10px 0px 10px 10px;
        }}
        
        QComboBox QAbstractItemView::item {{
            min-height: 25px;
        }}
        
        QListView::item:selected {{
            color: rgb(255, 255, 255);
            background-color: rgb(39, 44, 54);
        }}

        QScrollBar:vertical {{
            background: rgb(52, 59, 72);
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
        }}'''

    button = '''
        QPushButton {
            color: rgb(255, 255, 255);
            background-color: rgb(56, 62, 73);
            border: none;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: rgb(94, 104, 122);
            border: none;
        }
        QPushButton:pressed {
            background-color: rgb(139, 158, 194);
            border: none;
        }'''

    scroll_bar = f'''
        QScrollBar:vertical {{
            background: rgb(52, 59, 72);
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
        }}'''