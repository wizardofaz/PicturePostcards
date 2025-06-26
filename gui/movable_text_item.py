
from PyQt5.QtWidgets import QGraphicsTextItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

class MovableTextItem(QGraphicsTextItem):
    def __init__(self, text=""):
        super().__init__(text)
        self.setFlags(
            QGraphicsTextItem.ItemIsMovable |
            QGraphicsTextItem.ItemIsSelectable |
            QGraphicsTextItem.ItemIsFocusable
        )
        self.setAcceptHoverEvents(True)
        self.setTextInteractionFlags(Qt.NoTextInteraction)

    def mouseDoubleClickEvent(self, event):
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus()
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event):
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        super().focusOutEvent(event)
