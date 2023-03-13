import os

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QGridLayout

from frontend.generic import Font, TextLabel, HyperlinkTextLabel, Icons, ScrollBar, ScrollArea, ScrollAreaContent
from frontend.layouts import RowLayout

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

        # TODO maybe split into different subsections with headings
        s = "&nbsp;" # html space
        d = ("<p style=line-height:140%>"
             "If you are using a custom icon pack, navigate to the Settings page. Here you can browse for your Dead by "
             "Daylight installation (specifically, the folder containing your icons).<br>"
             "In the Preferences page, you can set up preferences for what add-ons, items, offerings and perks "
             "you would like to obtain from the bloodweb. Each set of preferences can be "
             "stored in a different profile, for convenient switching as required. "
             "One preset profile comes with the program: cheapskate "
             "(for levelling up the bloodweb as cheaply as possible). "
             "It comes in two variants, one which prioritises perks, and one which ignores them. "
             "You can use this preset as a starting point for your own profile, or "
             "create your own from scratch.<br>"
             "Each unlockable you configure will have a tier and a subtier:<br>"
             f"{s*8}- the higher the tier (or subtier), the higher your preference for that unlockable<br>"
             f"{s*8}- the lower the tier (or subtier), the lower your preference for that unlockable<br>"
             f"{s*8}- you do not need to configure unlockables for which you have a neutral preference "
             "(tier and subtier are both automatically 0 in this case)<br>"
             f"{s*16}- any unlockables not in the profile will be assumed to be neutral "
             f"(tier and subtier 0)<br>"
             f"{s*8}- tiers and subtiers can range from -999 to 999<br>"
             f"{s*8}- tier (A + B) unlockable is equivalent in preference to a tier A unlockable + tier B unlockable<br>"
             f"{s*16}- for instance, two tier 1 unlockables is equivalent to a single tier 2 unlockable<br>"
             f"{s*16}- you can use these numbers to fine tune exactly how much you want each unlockable<br>"
             f"{s*8}- similar mechanics apply with negative tiers to specify how much you dislike an unlockable<br>"
             f"{s*8}- subtier allows for preference within a tier "
             "e.g. tier 3 subtier 3 is higher priority than tier 3 subtier 2<br>"
             "Each profile can store a different set of preferences, for easy switching when required.<br>"
             "You can import and export profiles as .emp files to share with others.<br><br>"
             "In the Run page, there are two modes you can run: naive and aware. Aware is the default - this means "
             "you can select a preference profile, and the app will choose unlockables according to that profile. "
             "If you do not care about what you obtain, naive mode will randomly select unlockables instead. "
             "Select a profile, character to level, run mode, set any limits you want, and run! "
             "Make sure any shaders or game filters are off before running, and that your game is unobstructed "
             "on your primary monitor, or the program is very likely to perform in unintended ways.</p>")
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