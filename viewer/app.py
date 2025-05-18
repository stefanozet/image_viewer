import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTreeView, QVBoxLayout, QFileSystemModel,
    QSplitter, QLabel
)
from PySide6.QtCore import Qt, QDir
from PySide6.QtWidgets import QScrollArea, QGridLayout, QPushButton
from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction
from PySide6.QtGui import QPixmap, QIcon

from viewer.image_viewer import ImageViewer
from viewer.fs import list_images_in_folder
from viewer.thumbs import generate_thumbnail

from viewer.config import load_config

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.resize(1000, 700)

        self.config = load_config()
        self.start_dir = self.config.get("start_directory", QDir.rootPath())

        self.fullscreen_in_main = self.config.get("fullscreen_in_main", False)
        self.image_paths = []

        # Contenitore griglia
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(10)

        # Contenitore immagine singola
        self.image_container = QWidget()
        self.image_layout = QVBoxLayout(self.image_container)
        self.image_label = QLabel(alignment=Qt.AlignCenter)
        self.image_layout.addWidget(self.image_label)

        # ScrollArea come wrapper
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.grid_container)  # inizialmente mostra la griglia

        self.init_ui()

    def init_ui(self):
        self.toolbar = QToolBar("Funzioni")
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Azione: Torna alla griglia
        self.action_back_to_grid = QAction("Torna alla griglia", self)
        self.action_back_to_grid.triggered.connect(self.show_grid_view)

        # Azione: Avanti
        self.action_next = QAction("Successiva", self)
        self.action_next.triggered.connect(lambda: self.show_image_in_main(self.current_image_index + 1))

        # Azione: Indietro
        self.action_prev = QAction("Precedente", self)
        self.action_prev.triggered.connect(lambda: self.show_image_in_main(self.current_image_index - 1))

        # Azione: Cartella padre
        self.action_up = QAction("↑ Cartella padre", self)
        self.action_up.triggered.connect(self.go_up_directory)

        splitter = QSplitter(Qt.Horizontal)

        # === File system tree ===
        self.dir_model = QFileSystemModel()
        self.dir_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        self.dir_model.setRootPath(self.start_dir)

        self.tree = QTreeView()
        self.tree.setModel(self.dir_model)
        self.tree.setRootIndex(self.dir_model.index(self.start_dir))
        self.tree.setHeaderHidden(True)

        # Mostra solo la colonna 0 (nome cartella), nasconde le altre
        for col in range(1, self.dir_model.columnCount()):
            self.tree.hideColumn(col)

        self.tree.clicked.connect(self.on_folder_selected)

        # === Placeholder area destra ===
        # self.viewer_area = QLabel("Seleziona una cartella")
        # self.viewer_area.setAlignment(Qt.AlignCenter)

        # Scroll area per contenere la griglia di immagini
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.scroll_area.setWidget(self.grid_container)

        # Layout
        splitter.addWidget(self.tree)
        # splitter.addWidget(self.viewer_area)
        splitter.addWidget(self.scroll_area)
        splitter.setSizes([250, 750])

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(splitter)

        self.setCentralWidget(central)

    def on_folder_selected(self, index):
        folder_path = self.dir_model.filePath(index)
        self.image_paths = list_images_in_folder(folder_path)

        # Svuota la griglia
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)  # <-- questo va bene, NON distrugge self.grid_container

        # Inserisce le miniature
        for i, img_path in enumerate(self.image_paths):
            thumb_path = generate_thumbnail(img_path)
            if thumb_path:
                btn = QPushButton()
                btn.setIcon(QIcon(QPixmap(thumb_path)))
                btn.setIconSize(QPixmap(thumb_path).size())
                btn.setToolTip(img_path)
                btn.setFixedSize(140, 140)
                btn.clicked.connect(lambda _, idx=i: self.on_thumbnail_click(idx))
                self.grid_layout.addWidget(btn, i // 5, i % 5)

    def on_thumbnail_click(self, idx):
        if self.fullscreen_in_main:
            self.show_image_in_main(idx)
        else:
            viewer = ImageViewer(self.image_paths, idx, self)
            viewer.exec()

    def show_image_in_main(self, index):
        if not (0 <= index < len(self.image_paths)):
            return

        image_path = self.image_paths[index]
        pixmap = QPixmap(image_path)

        self.image_label.setPixmap(
            pixmap.scaled(
                self.scroll_area.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

        self.scroll_area.setWidget(self.image_container)
        self.current_image_index = index
        self.update_toolbar("image")

    def show_grid_view(self):
        self.scroll_area.setWidget(self.grid_container)
        self.update_toolbar("grid")
        if hasattr(self, "current_image_index"):
            del self.current_image_index




    def go_up_directory(self):
        current = self.dir_view.currentIndex()
        parent = self.dir_model.parent(current)
        if parent.isValid():
            self.dir_view.setCurrentIndex(parent)
            self.on_folder_selected(parent)

    def update_toolbar(self, mode="grid"):
        self.toolbar.clear()
        if mode == "grid":
            self.toolbar.addAction(self.action_up)
        elif mode == "image":
            self.toolbar.addAction(self.action_prev)
            self.toolbar.addAction(self.action_next)
            self.toolbar.addAction(self.action_back_to_grid)

    def keyPressEvent(self, event):
        if hasattr(self, "current_image_index"):
            if event.key() == Qt.Key_Right:
                self.show_image_in_main(self.current_image_index + 1)
            elif event.key() == Qt.Key_Left:
                self.show_image_in_main(self.current_image_index - 1)
            elif event.key() == Qt.Key_Escape:
                self.show_grid_view()



def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
