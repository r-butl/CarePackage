from PyQt5.QtWidgets import (
                            QWidget, 
                            QVBoxLayout, 
                            QMenuBar, 
                            QAction,
                            QLabel
                            )
from PyQt5.QtGui import (
                         QPixmap
                         )
from PyQt5.QtCore import Qt

class TopMenuBar(QWidget):
    def __init__(self, parent=None, exit_callback=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Logo
        self.label = QLabel()
        logo = QPixmap('Logo.png')
        logo = logo.scaled(300, 300, Qt.KeepAspectRatio)
        self.label.setPixmap(logo)
        self.layout.addWidget(self.label)

        # Create and add the menu bar to the widget's layout
        self.menuBar = QMenuBar()
        self.layout.addWidget(self.menuBar)

        self.exitApp = exit_callback

        # Set up the menus
        self.setupMenus()

    def setupMenus(self):
        # File Menu
        fileMenu = self.menuBar.addMenu('File')
        exitAction = QAction('Exit', self)
        exitAction.triggered.connect(self.exitApp)
        fileMenu.addAction(exitAction)

