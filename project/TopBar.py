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
    def __init__(self, parent=None):
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

        # Set up the menus
        self.setupMenus()

    def setupMenus(self):
        # File Menu
        fileMenu = self.menuBar.addMenu('File')
        exitAction = QAction('Exit', self)
        exitAction.triggered.connect(self.exitApp)
        fileMenu.addAction(exitAction)

        # Edit Menu
        editMenu = self.menuBar.addMenu('Edit')
        undoAction = QAction('Undo', self)
        editMenu.addAction(undoAction)

        # View Menu
        viewMenu = self.menuBar.addMenu('View')
        toggleAction = QAction('Toggle Something', self)
        viewMenu.addAction(toggleAction)

    def exitApp(self):
        # Placeholder function for exit action
        print("Exit triggered")

# Note: Connect the exitApp function to actual functionality as needed.
