from PyQt6.QtWidgets import QGraphicsScene, QGraphicsRectItem
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QPen, QBrush, QImage, QPainter
import json

class Page:
    """Represents a single page in the document"""
    def __init__(self, width=794, height=1123, page_number=1):
        self.width = width
        self.height = height
        self.page_number = page_number
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, width, height)
        
        # Add page background
        self.background = QGraphicsRectItem(0, 0, width, height)
        self.background.setBrush(QBrush(QColor("white")))
        self.background.setPen(QPen(Qt.GlobalColor.black))
        self.scene.addItem(self.background)
        
    def get_thumbnail(self, width=150):
        """Generate thumbnail image of the page"""
        aspect_ratio = self.height / self.width
        height = int(width * aspect_ratio)
        
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.white)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.scene.render(painter)
        painter.end()
        
        return image
    
    def to_dict(self):
        """Serialize page data"""
        items_data = []
        for item in self.scene.items():
            # Skip background
            if item == self.background:
                continue
            
            # Import here to avoid circular dependency
            from src.engine.text_box import TextBox
            
            if isinstance(item, TextBox):
                items_data.append({
                    "type": "text",
                    "x": item.x(),
                    "y": item.y(),
                    "content": item.toHtml(),
                    "width": item.textWidth(),
                    "rotation": item.rotation()
                })
        
        return {
            "width": self.width,
            "height": self.height,
            "page_number": self.page_number,
            "items": items_data
        }
    
    def from_dict(self, data):
        """Deserialize page data"""
        from src.engine.text_box import TextBox
        
        self.width = data.get("width", 794)
        self.height = data.get("height", 1123)
        self.page_number = data.get("page_number", 1)
        
        # Clear scene (except background)
        for item in list(self.scene.items()):
            if item != self.background:
                self.scene.removeItem(item)
        
        # Recreate items
        for item_data in data.get("items", []):
            if item_data["type"] == "text":
                tb = TextBox(font_family="Noorin Nastaleeq")
                tb.setPos(item_data["x"], item_data["y"])
                tb.setHtml(item_data["content"])
                tb.setTextWidth(item_data["width"])
                if "rotation" in item_data:
                    tb.setRotation(item_data["rotation"])
                self.scene.addItem(tb)


class PageManager:
    """Manages multiple pages in a document"""
    def __init__(self):
        self.pages = []
        self.current_page_index = 0
        
        # Create initial page
        self.add_page()
    
    def add_page(self, index=None):
        """Add a new page at the specified index (or at the end)"""
        page_number = len(self.pages) + 1
        page = Page(page_number=page_number)
        
        if index is None:
            self.pages.append(page)
        else:
            self.pages.insert(index, page)
            self._renumber_pages()
        
        return page
    
    def delete_page(self, index):
        """Delete page at the specified index"""
        if len(self.pages) <= 1:
            return False  # Can't delete the last page
        
        if 0 <= index < len(self.pages):
            del self.pages[index]
            self._renumber_pages()
            
            # Adjust current page if needed
            if self.current_page_index >= len(self.pages):
                self.current_page_index = len(self.pages) - 1
            
            return True
        return False
    
    def move_page(self, from_index, to_index):
        """Move a page from one position to another"""
        if 0 <= from_index < len(self.pages) and 0 <= to_index < len(self.pages):
            page = self.pages.pop(from_index)
            self.pages.insert(to_index, page)
            self._renumber_pages()
            return True
        return False
    
    def get_page(self, index):
        """Get page at the specified index"""
        if 0 <= index < len(self.pages):
            return self.pages[index]
        return None
    
    def get_current_page(self):
        """Get the currently active page"""
        return self.pages[self.current_page_index]
    
    def set_current_page(self, index):
        """Set the current page by index"""
        if 0 <= index < len(self.pages):
            self.current_page_index = index
            return True
        return False
    
    def next_page(self):
        """Navigate to next page"""
        if self.current_page_index < len(self.pages) - 1:
            self.current_page_index += 1
            return True
        return False
    
    def prev_page(self):
        """Navigate to previous page"""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            return True
        return False
    
    def first_page(self):
        """Navigate to first page"""
        self.current_page_index = 0
    
    def last_page(self):
        """Navigate to last page"""
        self.current_page_index = len(self.pages) - 1
    
    def page_count(self):
        """Get total number of pages"""
        return len(self.pages)
    
    def _renumber_pages(self):
        """Renumber all pages sequentially"""
        for i, page in enumerate(self.pages):
            page.page_number = i + 1
    
    def to_dict(self):
        """Serialize all pages"""
        return {
            "current_page": self.current_page_index,
            "pages": [page.to_dict() for page in self.pages]
        }
    
    def from_dict(self, data):
        """Deserialize all pages"""
        self.pages = []
        for page_data in data.get("pages", []):
            page = Page()
            page.from_dict(page_data)
            self.pages.append(page)
        
        self.current_page_index = data.get("current_page", 0)
        
        # Ensure at least one page
        if not self.pages:
            self.add_page()
