import os
import sys

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QGridLayout

from frontend.generic import Font, TextLabel, HyperlinkTextLabel, Icons, ScrollBar, ScrollArea, ScrollAreaContent
from frontend.layouts import RowLayout

sys.path.append(os.path.dirname(os.path.realpath("backend/state.py")))

class HelpPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("helpPage")

        self.layout = QGridLayout(self)
        self.layout.setObjectName("helpPageLayout")
        self.layout.setContentsMargins(25, 25, 25, 25)
        self.layout.setSpacing(0)

        self.scrollBar = ScrollBar(self, "helpPage")
        self.scrollArea = ScrollArea(self, "helpPage", self.scrollBar)
        self.scrollAreaContent = ScrollAreaContent(self.scrollArea, "helpPage")
        self.scrollArea.setWidget(self.scrollAreaContent)
        self.scrollAreaContentLayout = QVBoxLayout(self.scrollAreaContent)
        self.scrollAreaContentLayout.setObjectName("helpPageScrollAreaContentLayout")
        self.scrollAreaContentLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaContentLayout.setSpacing(15)

        # TODO unify across README, here, discord server FAQ, and video tutorial
        d = ("<p style=line-height:125%> "
             "First, configure your display resolution and UI scale in the Settings page. "
             "If you have a non-default Dead by Daylight installation, you will also need "
             "to find the folder containing the icons, in case you are using a custom icon pack.<br><br>"
             "You can then set up preferences for what add-ons, items, offerings and perks "
             "you would like to obtain from the bloodweb. Each set of preferences can be "
             "stored in a different profile, for convenient switching as required. "
             "One preset profile comes with the program: cheapskate "
             "(for levelling up the bloodweb as cheaply as possible). "
             "It comes in two variants, one which prioritises perks, and one which ignores them. "
             "You can use this preset as a starting point for your own profile, or "
             "create your own from scratch.<br><br>"
             "Each unlockable you configure will have a tier and a subtier:<br>"
             "    - the higher the tier (or subtier), the higher your preference for that item<br>"
             "    - the lower the tier (or subtier), the lower your preference for that item<br>"
             "    - neutral items will have tier and subtier 0<br>"
             "    - tiers and subtiers can range from -999 to 999<br>"
             "    - tier A item + tier B item are equivalent in preference to a tier A + B item<br>"
             "         - for instance, two tier 1 items is equivalent to a single tier 2 item<br>"
             "         - you can use these numbers to fine tune exactly how much you want each item<br>"
             "    - a similar system applies with negative tiers when specifying how much you dislike an item<br>"
             "    - subtier allows for preference within a tier "
             "e.g. a tier 3 subtier 3 is higher priority than tier 3 subtier 2<br><br>"
             "Then simply select a profile, select the character whose bloodweb you are on, set any limits you want, "
             "and run! Make sure your shaders are off before running, "
             "or the program is very likely to perform in unintended ways.")
        self.instructionsLabel = TextLabel(self, "helpPageInstructionsLabel", "How to Use Blood Emporium", Font(12))
        self.instructionsDescription = TextLabel(self, "helpPageInstructionsDescription", d, Font(10))
        self.instructionsDescription.setWordWrap(True)

        self.contactLabel = TextLabel(self, "helpPageContactLabel", "Contact Me", Font(12))

        self.contactDiscordRow = QWidget(self)
        self.contactDiscordRow.setObjectName("helpPageContactDiscordRow")
        self.contactDiscordRowLayout = RowLayout(self.contactDiscordRow, "helpPageContactDiscordRowLayout")

        self.contactDiscordIcon = QLabel(self.contactDiscordRow)
        self.contactDiscordIcon.setObjectName("helpPageContactDiscordIcon")
        self.contactDiscordIcon.setFixedSize(QSize(20, 20))
        self.contactDiscordIcon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.discord))
        self.contactDiscordIcon.setScaledContents(True)
        self.contactDiscordLabel = HyperlinkTextLabel(self.contactDiscordRow, "helpPageContactDiscordLabel",
                                                      "Discord", "https://discord.gg/J4KCqJJuaM", Font(10))

        self.contactTwitterRow = QWidget(self)
        self.contactTwitterRow.setObjectName("helpPageContactTwitterRow")
        self.contactTwitterRowLayout = RowLayout(self.contactTwitterRow, "helpPageContactTwitterRowLayout")

        self.contactTwitterIcon = QLabel(self.contactTwitterRow)
        self.contactTwitterIcon.setObjectName("helpPageContactTwitterIcon")
        self.contactTwitterIcon.setFixedSize(QSize(20, 20))
        self.contactTwitterIcon.setPixmap(QPixmap(os.getcwd() + "/" + Icons.twitter))
        self.contactTwitterIcon.setScaledContents(True)
        self.contactTwitterLabel = HyperlinkTextLabel(self.contactTwitterRow, "helpPageContactTwitterLabel", "Twitter",
                                                      "https://twitter.com/initiationmusic", Font(10))

        self.contactDiscordRowLayout.addWidget(self.contactDiscordIcon)
        self.contactDiscordRowLayout.addWidget(self.contactDiscordLabel)
        self.contactDiscordRowLayout.addStretch(1)

        self.contactTwitterRowLayout.addWidget(self.contactTwitterIcon)
        self.contactTwitterRowLayout.addWidget(self.contactTwitterLabel)
        self.contactTwitterRowLayout.addStretch(1)

        self.scrollAreaContentLayout.addWidget(self.instructionsLabel)
        self.scrollAreaContentLayout.addWidget(self.instructionsDescription)
        self.scrollAreaContentLayout.addWidget(self.contactLabel)
        self.scrollAreaContentLayout.addWidget(self.contactDiscordRow)
        self.scrollAreaContentLayout.addWidget(self.contactTwitterRow)
        self.scrollAreaContentLayout.addStretch(1)

        self.layout.addWidget(self.scrollArea)
        self.layout.setRowStretch(0, 1)
        self.layout.setColumnStretch(0, 1)