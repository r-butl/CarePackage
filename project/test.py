from PyQt5.QtWidgets import  QLabel, QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QDial
from PyQt5.QtCore import Qt, QMimeData, QPoint, QByteArray
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QDrag
import uuid
import sys
from PipelineConstructor import *

class DraggableProcessBlock(QWidget):
    def __init__(self, processBlockType, parent=None, id=None):
        super(DraggableProcessBlock, self).__init__(parent)
        self.uuid = id if id is not None else str(uuid.uuid4())
        self.process_block_type = processBlockType

        # Set up the internal layout
        layout = QVBoxLayout(self)
        self.label = QLabel(processBlockType.get_options()['name'])
        self.button = QPushButton("button")

        layout.addWidget(self.label)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setFixedSize(200, 100)

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

        mime_data.setText(self.label.text())
        mime_data.setData("application/x-item-uuid", QByteArray(self.uuid.encode()))
        
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
        self.labels = {}

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasFormat("application/x-item-uuid"):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        uuid = event.mimeData().data("application/x-item-uuid").data().decode()
        text = event.mimeData().text()

        if uuid in self.labels:
            # move existing label
            label = self.labels[uuid]
            label.move(event.pos())
        else:
            # Create new label
            label = DraggableProcessBlock(text, self)
            label.move(event.pos())
            self.labels[uuid] = label
            label.show()

        event.setDropAction(Qt.MoveAction)
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
            label = DraggableProcessBlock(text)
            layout.addWidget(label)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
