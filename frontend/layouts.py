from PyQt5.QtWidgets import QHBoxLayout


class RowLayout(QHBoxLayout):
    def __init__(self, parent, object_name, margin=0, spacing=15):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)