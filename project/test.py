from PyQt5.QtWidgets import QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QFrame
from PyQt5.QtCore import Qt, QMimeData, QPoint
from PyQt5.QtGui import QDrag

class DraggableLabel(QLabel):
    def __init__(self, text, parent=None):
        super(DraggableLabel, self).__init__(text, parent)
        self.setFixedSize(100, 30)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.text())
        drag.setMimeData(mime_data)

        drag.exec_(Qt.CopyAction)

class DropZone(QWidget):
    def __init__(self, parent=None):
        super(DropZone, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedSize(400, 400)
        self.setStyleSheet("""
            background-color: lightgrey;
            border: 2px solid black;
            border-radius: 10px;
        """)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        position = event.pos()
        text = event.mimeData().text()
        new_label = DraggableLabel(text, self)
        new_label.move(position)
        new_label.show()
        event.setDropAction(Qt.CopyAction)
        event.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Drag and Drop Example')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Sandbox zone
        self.drop_zone = DropZone()
        layout.addWidget(self.drop_zone)

        # List of draggable elements
        for text in ["Element 1", "Element 2", "Element 3"]:
            label = DraggableLabel(text)
            layout.addWidget(label)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
