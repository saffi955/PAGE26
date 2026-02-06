from PyQt6.QtWidgets import QMdiSubWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from src.ui.document_view import DocumentView
from src.ui.ruler import Ruler

class DocumentWindow(QMdiSubWindow):
    def __init__(self, default_font, font_families, page_settings=None, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # Main widget for the subwindow
        self.widget = QWidget()
        self.setWidget(self.widget)
        
        # Grid Layout for Rulers and View
        self.layout = QGridLayout(self.widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Rulers
        self.h_ruler = Ruler(Qt.Orientation.Horizontal)
        self.v_ruler = Ruler(Qt.Orientation.Vertical)
        
        # Corner widget (empty)
        self.corner = QWidget()
        self.corner.setFixedSize(18, 18)  # Match smaller ruler size
        self.corner.setStyleSheet("background-color: #f0f0f0; border-right: 1px solid #ccc; border-bottom: 1px solid #ccc;")
        
        # Document View
        self.document_view = DocumentView(default_font, page_settings=page_settings)
        
        # Add to layout
        # Row 0: Corner, H-Ruler
        self.layout.addWidget(self.corner, 0, 0)
        self.layout.addWidget(self.h_ruler, 0, 1)
        
        # Row 1: V-Ruler, View
        self.layout.addWidget(self.v_ruler, 1, 0)
        self.layout.addWidget(self.document_view, 1, 1)
        
        # Connect Scrollbars to Rulers with custom update
        self.document_view.horizontalScrollBar().valueChanged.connect(self.update_h_ruler)
        self.document_view.verticalScrollBar().valueChanged.connect(self.update_v_ruler)
        
        # Connect Zoom
        self.document_view.on_zoom_changed = self.update_ruler_zoom
        
        # Set window title based on document name (todo)
        self.setWindowTitle("Untitled")
        
    def update_h_ruler(self, scroll_val):
        # Ruler should show 0 at the page's left edge, not the scene's left edge
        # Since page starts at (0,0) in scene, offset is just the scroll value
        self.h_ruler.set_offset(scroll_val)
        
    def update_v_ruler(self, scroll_val):
        # Ruler should show 0 at the page's top edge, not the scene's top edge
        self.v_ruler.set_offset(scroll_val)
        
    def update_ruler_zoom(self, zoom):
        self.h_ruler.set_zoom(zoom)
        self.v_ruler.set_zoom(zoom)
        
    def closeEvent(self, event):
        # Todo: Check for unsaved changes
        super().closeEvent(event)
