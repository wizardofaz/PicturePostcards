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
        self.font_size_spinner.setValue(14)
        self.font_size_spinner.valueChanged.connect(self.update_note_font_size)

        self.export_button = QPushButton("Export Postcard")
        self.export_button.clicked.connect(self.export_postcard)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.load_button)
        controls_layout.addWidget(QLabel("Style:"))
        controls_layout.addWidget(self.style_combo)
        controls_layout.addWidget(QLabel("Zoom:"))
        controls_layout.addWidget(self.zoom_spinner)
        controls_layout.addWidget(QLabel("Font:"))
        controls_layout.addWidget(self.font_combo)
        controls_layout.addWidget(QLabel("Size:"))
        controls_layout.addWidget(self.font_size_spinner)
        controls_layout.addWidget(self.export_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(self.view)

        self.setLayout(main_layout)

        self.note_item = MovableTextItem("Your notes here")
        self.note_item.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.note_item.setDefaultTextColor(Qt.black)
        self.note_item.setFont(QFont("Arial", 14))
        self.note_item.setFlag(QGraphicsTextItem.ItemIsMovable)

        self.photo_item = QGraphicsPixmapItem()
        self.photo_item.setFlag(QGraphicsPixmapItem.ItemIsMovable)
        self.scene.addItem(self.photo_item)

        self.map_item = QGraphicsPixmapItem()
        self.map_item.setFlag(QGraphicsPixmapItem.ItemIsMovable)
        self.scene.addItem(self.map_item)

        self.info_item = QGraphicsTextItem()
        self.info_item.setDefaultTextColor(Qt.black)
        self.info_item.setFont(QFont("Arial", 10))
        self.info_item.setFlag(QGraphicsTextItem.ItemIsMovable)
        self.scene.addItem(self.info_item)

        self.scene.addItem(self.note_item)

        self.map_pixmap = None  # Track current map pixmap separately

    def update_note_font(self, font):
        if self.note_item:
            self.note_item.setFont(font)

    def update_note_font_size(self):
        if self.note_item:
            font = self.note_item.font()
            font.setPointSize(self.font_size_spinner.value())
            self.note_item.setFont(font)

    def update_map_style(self):
        if hasattr(self, "image_path") and self.map_pixmap:
            style = self.style_combo.currentText()
            lat = self.metadata["Latitude"]
            lon = self.metadata["Longitude"]
            zoom = self.zoom_spinner.value()
            self.map_pixmap = pil_to_pixmap(MapboxStaticMap(style).get_map_image(lat, lon, zoom=zoom, size=(300, 300)))
            self.map_item.setPixmap(self.map_pixmap)

    def load_photo(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select an image", "", "Images (*.jpg *.jpeg *.png)")
        if not file_name:
            return

        self.image_path = file_name
        self.refresh_preview()

    def refresh_preview(self):
        if not hasattr(self, "image_path"):
            return

        metadata = get_metadata(self.image_path)

        gps = metadata.get("GPSInfo", {})
        if "GPSLatitude" in gps and "GPSLongitude" in gps:
            def dms_to_decimal(dms, ref):
                degrees, minutes, seconds = dms
                decimal = degrees + minutes / 60 + seconds / 3600
                if ref in ['S', 'W']:
                    decimal = -decimal
                return decimal

            lat = dms_to_decimal(gps["GPSLatitude"], gps.get("GPSLatitudeRef", "N"))
            lon = dms_to_decimal(gps["GPSLongitude"], gps.get("GPSLongitudeRef", "E"))
            metadata["Latitude"] = lat
            metadata["Longitude"] = lon

        if "Latitude" not in metadata or "Longitude" not in metadata:
            QMessageBox.warning(self, "No GPS", "No GPS metadata found in image.")
            return

        self.metadata = metadata
        lat = metadata["Latitude"]
        lon = metadata["Longitude"]
        zoom = self.zoom_spinner.value()
        style = self.style_combo.currentText()

        self.map_pixmap = pil_to_pixmap(MapboxStaticMap(style).get_map_image(lat, lon, zoom=zoom, size=(300, 300)))
        photo = Image.open(self.image_path).resize((300, 300))
        photo_pixmap = pil_to_pixmap(photo)

        self.photo_item.setPixmap(photo_pixmap)
        self.map_item.setPixmap(self.map_pixmap)

        # Only reposition if they have not been moved
        if self.photo_item.pos() == QPointF(0, 0):
            self.photo_item.setPos(50, 50)
        if self.map_item.pos() == QPointF(0, 0):
            self.map_item.setPos(400, 50)
        if self.info_item.toPlainText() == "":
            self.info_item.setPlainText(f"Latitude: {lat:.6f}\nLongitude: {lon:.6f}\nModel: {metadata.get('Model', '')}\nDateTime: {metadata.get('DateTime', '')}")
            self.info_item.setPos(50, 360)
        if self.note_item.toPlainText() == "Your notes here":
            self.note_item.setPos(50, 440)

    def export_postcard(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Postcard", "postcard.jpg", "Images (*.jpg *.png)")
        if not file_name:
            return

        rect = self.scene.sceneRect()
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.white)
        painter = QPainter(image)
        self.scene.render(painter, target=QRectF(image.rect()), source=rect)
        painter.end()

        image.save(file_name)

def launch_app():
    app = QApplication(sys.argv)
    window = PhotoMapoApp()
    window.show()
    sys.exit(app.exec_())
