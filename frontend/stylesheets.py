class StyleSheets:
    pink = "rgb(255, 121, 198)" # #ff79c6
    purple = "rgb(189, 147, 249)" # #bd93f9

    debug = '''
        background-color: rgb(40, 44, 52);
        border: 5px solid black;
    '''

    white_text = "color: rgb(255, 255, 255);"

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

    text_box_positive_tier_subtier = '''
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

    text_box_negative_tier_subtier = '''
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

    text_box_invalid_tier_subtier = f'''
        QLineEdit {{
            background-color: rgb(27, 30, 35);
            color: {purple};
            border-radius: 5px;
            border: 2px solid rgba(0, 0, 0, 0);
            padding-left: 10px;
        }}
        
        QLineEdit:hover {{
            border: 2px solid rgb(47, 52, 61);
        }}'''

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