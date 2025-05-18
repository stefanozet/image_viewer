from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap, QKeyEvent, QMouseEvent
from PySide6.QtCore import Qt

class ImageViewer(QDialog):
    def __init__(self, image_list, current_index, parent=None):
        super().__init__(parent)
        self.image_list = image_list
        self.current_index = current_index

        self.setWindowTitle("Visualizzatore")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setStyleSheet("background-color: black;")
        self.setMinimumSize(800, 600)

        self.label = QLabel(alignment=Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.update_image()

    def update_image(self):
        path = self.image_list[self.current_index]
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self.label.setText("Immagine non caricabile")
        else:
            self.label.setPixmap(pixmap.scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Left:
            self.prev_image()
        elif event.key() == Qt.Key_Escape:
            self.close()

    def mousePressEvent(self, event: QMouseEvent):
        w = self.width()
        x = event.position().x()
        if x < w * 0.3:
            self.prev_image()
        elif x > w * 0.7:
            self.next_image()
        else:
            self.close()

    def resizeEvent(self, event):
        self.update_image()

    def next_image(self):
        if self.current_index < len(self.image_list) - 1:
            self.current_index += 1
            self.update_image()

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image()
