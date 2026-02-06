from PyQt6.QtWidgets import QWidget, QMenu
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics, QAction

class Ruler(QWidget):
    # Unit conversion factors (to pixels at 96 DPI)
    UNITS = {
        'inches': 96.0,      # 96 pixels per inch
        'mm': 3.78,          # ~3.78 pixels per mm
        'cm': 37.8,          # ~37.8 pixels per cm  
        'feet': 1152.0,      # 1152 pixels per foot (12 inches)
        'pixels': 1.0        # 1:1
    }
    
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.zoom = 1.0
        self.offset = 0
        self.unit = 'inches'  # Default unit
        self.page_offset = 0  # Offset to page origin in scene coordinates
        
        if self.orientation == Qt.Orientation.Horizontal:
            self.setFixedHeight(18)
        else:
            self.setFixedWidth(18)
            
        self.setMouseTracking(True)
        
    def set_unit(self, unit):
        """Set measurement unit"""
        if unit in self.UNITS:
            self.unit = unit
            self.update()
    
    def set_zoom(self, zoom):
        self.zoom = zoom
        self.update()
        
    def set_offset(self, offset):
        """Set scroll offset"""
        self.offset = offset
        self.update()
    
    def set_page_offset(self, page_offset):
        """Set the position of page origin in scene coordinates"""
        self.page_offset = page_offset
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Background
        painter.fillRect(self.rect(), QColor("#f8f8f8"))
        
        # Border
        painter.setPen(QPen(QColor("#ddd")))
        if self.orientation == Qt.Orientation.Horizontal:
            painter.drawLine(0, self.height()-1, self.width(), self.height()-1)
        else:
            painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
            
        # Ticks and Numbers
        painter.setPen(QPen(QColor("#888")))
        font = self.font()
        font.setPointSize(6)
        painter.setFont(font)
        
        # Pixels per unit at current zoom
        px_per_unit = self.UNITS[self.unit] * self.zoom
        
        # Determine tick spacing based on unit
        if self.unit == 'inches':
            major_step = 1.0  # 1 inch
            medium_step = 0.5  # 1/2 inch
            minor_step = 0.125  # 1/8 inch
        elif self.unit == 'mm':
            major_step = 10.0  # 1 cm
            medium_step = 5.0  # 5 mm
            minor_step = 1.0  # 1 mm
        elif self.unit == 'cm':
            major_step = 1.0  # 1 cm
            medium_step = 0.5  # 0.5 cm
            minor_step = 0.1  # 1 mm
        elif self.unit == 'feet':
            major_step = 1.0  # 1 foot
            medium_step = 0.5  # 6 inches
            minor_step = 0.0833  # 1 inch
        else:  # pixels
            major_step = 100.0
            medium_step = 50.0
            minor_step = 10.0
        
        if self.orientation == Qt.Orientation.Horizontal:
            # Calculate range including negative values
            # visible_start in scene pixels = offset
            # page_origin in scene pixels = page_offset (usually 0)
            # unit_position = (scene_pixel - page_offset) / px_per_unit
            
            scene_start = self.offset
            scene_end = self.offset + self.width()
            
            # Convert to unit positions relative to page origin
            start_unit = (scene_start - self.page_offset) / px_per_unit
            end_unit = (scene_end - self.page_offset) / px_per_unit
            
            # Find tick range
            start_tick = int(start_unit / minor_step) - 1
            end_tick = int(end_unit / minor_step) + 2
            
            for i in range(start_tick, end_tick):
                unit_val = i * minor_step
                scene_px = (unit_val * px_per_unit) + self.page_offset
                px_pos = scene_px - self.offset
                
                if px_pos < -10 or px_pos > self.width() + 10:
                    continue
                
                # Determine tick type
                is_major = abs(unit_val % major_step) < 0.001
                is_medium = abs(unit_val % medium_step) < 0.001
                
                if is_major:
                    painter.drawLine(int(px_pos), 0, int(px_pos), 12)
                    # Draw number
                    if self.unit in ['inches', 'feet', 'cm']:
                        text = f"{int(unit_val)}" if unit_val == int(unit_val) else f"{unit_val:.1f}"
                    else:
                        text = str(int(unit_val))
                    painter.drawText(int(px_pos) + 2, 9, text)
                elif is_medium:
                    painter.drawLine(int(px_pos), 8, int(px_pos), 12)
                # Skip minor ticks for cleaner look
                    
        else:  # Vertical
            scene_start = self.offset
            scene_end = self.offset + self.height()
            
            start_unit = (scene_start - self.page_offset) / px_per_unit
            end_unit = (scene_end - self.page_offset) / px_per_unit
            
            start_tick = int(start_unit / minor_step) - 1
            end_tick = int(end_unit / minor_step) + 2
            
            for i in range(start_tick, end_tick):
                unit_val = i * minor_step
                scene_px = (unit_val * px_per_unit) + self.page_offset
                px_pos = scene_px - self.offset
                
                if px_pos < -10 or px_pos > self.height() + 10:
                    continue
                
                is_major = abs(unit_val % major_step) < 0.001
                is_medium = abs(unit_val % medium_step) < 0.001
                
                if is_major:
                    painter.drawLine(0, int(px_pos), 12, int(px_pos))
                    if self.unit in ['inches', 'feet', 'cm']:
                        text = f"{int(unit_val)}" if unit_val == int(unit_val) else f"{unit_val:.1f}"
                    else:
                        text = str(int(unit_val))
                    painter.drawText(2, int(px_pos) + 7, text)
                elif is_medium:
                    painter.drawLine(8, int(px_pos), 12, int(px_pos))
    
    def contextMenuEvent(self, event):
        """Show context menu for unit selection"""
        menu = QMenu(self)
        
        # Add unit options
        units = [("Inches", "inches"), ("Millimeters", "mm"), ("Centimeters", "cm"), 
                 ("Feet", "feet"), ("Pixels", "pixels")]
        
        for label, unit in units:
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(self.unit == unit)
            action.triggered.connect(lambda checked, u=unit: self.set_unit(u))
            menu.addAction(action)
        
        menu.exec(event.globalPos())
