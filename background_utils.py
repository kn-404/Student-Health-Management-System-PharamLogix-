import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt

def set_background(widget: QWidget):
    """
    Sets the background image for any QWidget.
    The background image is loaded from the same directory as this script.
    
    Args:
        widget (QWidget): The widget to set the background for
    """
    bg_path = os.path.join(os.path.dirname(__file__), "Bg (1).jpg")
    widget.setAutoFillBackground(True)
    
    # Scale the image to the widget size while maintaining aspect ratio
    pixmap = QPixmap(bg_path).scaled(
        widget.size(),
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )
    
    # Create and set the palette
    palette = widget.palette()
    palette.setBrush(QPalette.Window, QBrush(pixmap))
    widget.setPalette(palette)
    
    # Make sure the background updates when the widget is resized
    widget.resizeEvent = lambda event: update_background(widget, event)

def update_background(widget: QWidget, event):
    """
    Updates the background when the widget is resized.
    
    Args:
        widget (QWidget): The widget being resized
        event: The resize event
    """
    bg_path = os.path.join(os.path.dirname(__file__), "Bg (1).jpg")
    pixmap = QPixmap(bg_path).scaled(
        event.size(),
        Qt.KeepAspectRatioByExpanding,
        Qt.SmoothTransformation
    )
    palette = widget.palette()
    palette.setBrush(QPalette.Window, QBrush(pixmap))
    widget.setPalette(palette)