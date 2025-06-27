# Interactive GUI with layout editing and font controls
# file: gui/app.py
import sys
from io import BytesIO
from gui.movable_text_item import MovableTextItem

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QMessageBox,
    QComboBox, QHBoxLayout, QSpinBox, QFontComboBox,
    QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsTextItem
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QFont
from PyQt5.QtCore import Qt, QRectF, QPointF
from PIL import Image
from core.metadata import get_metadata
from maps.mapbox_static import MAPBOX_STYLES, MapboxStaticMap
from core.composer import create_postcard_image

def pil_to_pixmap(pil_image):
    if pil_image.mode != "RGBA":
        pil_image = pil_image.convert("RGBA")
    data = pil_image.tobytes("raw", "RGBA")
    qimg = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
    return QPixmap.fromImage(qimg)

class PhotoMapoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhotoMapo Layout Editor")
        self.setMinimumSize(1000, 700)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)

        self.load_button = QPushButton("Load Photo")
        self.load_button.clicked.connect(self.load_photo)

        self.style_combo = QComboBox()
        self.style_combo.addItems(MAPBOX_STYLES.keys())
        self.style_combo.currentTextChanged.connect(self.update_map_style)

        self.zoom_spinner = QSpinBox()
        self.zoom_spinner.setRange(1, 20)
        self.zoom_spinner.setValue(14)
        self.zoom_spinner.valueChanged.connect(self.refresh_preview)

        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.update_note_font)

        self.font_size_spinner = QSpinBox()
        self.font_size_spinner.setRange(8, 48)
        self.font_size_spinner.setValue(12)
        self.font_size_spinner.valueChanged.connect(self.update_note_font)

        top_controls = QHBoxLayout()
        top_controls.addWidget(self.load_button)
        top_controls.addWidget(QLabel("Style:"))
        top_controls.addWidget(self.style_combo)
        top_controls.addWidget(QLabel("Zoom:"))
        top_controls.addWidget(self.zoom_spinner)
        top_controls.addWidget(QLabel("Font:"))
        top_controls.addWidget(self.font_combo)
        top_controls.addWidget(QLabel("Size:"))
        top_controls.addWidget(self.font_size_spinner)

        layout = QVBoxLayout()
        layout.addLayout(top_controls)
        layout.addWidget(self.view)

        self.setLayout(layout)

        self.map_item = None
        self.image_item = None
        self.note_item = None

    def load_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.jpg *.jpeg *.png)")
        if not path:
            return

        self.image_path = path
        try:
            self.metadata = get_metadata(path)
        except Exception as e:
            QMessageBox.warning(self, "Metadata Error", str(e))
            return

        image = Image.open(path)
        qpix = pil_to_pixmap(image)

        self.scene.clear()
        self.image_item = QGraphicsPixmapItem(qpix)
        self.image_item.setFlags(QGraphicsPixmapItem.ItemIsMovable | QGraphicsPixmapItem.ItemIsSelectable)
        self.scene.addItem(self.image_item)

        style_label = self.style_combo.currentText()
        style = MAPBOX_STYLES[style_label]
        zoom = self.zoom_spinner.value()
        lat = self.metadata["Latitude"]
        lon = self.metadata["Longitude"]

        map_img = MapboxStaticMap(style).get_map_image(lat, lon, zoom=zoom, size=(300, 300))
        self.map_pixmap = pil_to_pixmap(map_img)
        self.map_item = QGraphicsPixmapItem(self.map_pixmap)
        self.map_item.setFlags(QGraphicsPixmapItem.ItemIsMovable | QGraphicsPixmapItem.ItemIsSelectable)
        self.map_item.setOffset(20, 20)
        self.scene.addItem(self.map_item)

        self.note_item = MovableTextItem("Add your notes here")
        font = QFont(self.font_combo.currentFont())
        font.setPointSize(self.font_size_spinner.value())
        self.note_item.setFont(font)
        self.note_item.setDefaultTextColor(Qt.black)
        self.note_item.setPos(350, 50)
        self.scene.addItem(self.note_item)

    def update_map_style(self):
        if self.map_item and hasattr(self, "metadata"):
            style_label = self.style_combo.currentText()
            style = MAPBOX_STYLES[style_label]
            print(f"[DEBUG] Map style changed to: {style}")  # diagnostic
            lat = self.metadata["Latitude"]
            lon = self.metadata["Longitude"]
            zoom = self.zoom_spinner.value()
            map_img = MapboxStaticMap(style).get_map_image(lat, lon, zoom=zoom, size=(300, 300))
            self.map_pixmap = pil_to_pixmap(map_img)
            self.map_item.setPixmap(self.map_pixmap)
            self.view.viewport().update()

    def refresh_preview(self):
        if hasattr(self, "image_path"):
            self.update_map_style()

    def update_note_font(self):
        if self.note_item:
            font = QFont(self.font_combo.currentFont())
            font.setPointSize(self.font_size_spinner.value())
            self.note_item.setFont(font)

def launch_app():
    app = QApplication(sys.argv)
    window = PhotoMapoApp()
    window.show()
    sys.exit(app.exec_())
