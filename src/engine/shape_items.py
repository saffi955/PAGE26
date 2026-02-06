from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsPolygonItem, QFileDialog, QMenu
from PyQt6.QtCore import Qt, QRectF, QPointF, QLineF
from PyQt6.QtGui import QColor, QPen, QBrush, QPolygonF, QCursor, QPixmap, QPainter, QPainterPath
import math

class Handle(QGraphicsRectItem):
    """Resize handle for shapes"""
    def __init__(self, cursor_shape, parent=None, role="resize"):
        super().__init__(-4, -4, 8, 8, parent)
        self.role = role
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QPen(QColor("black")))
        self.setCursor(QCursor(cursor_shape))
        # Don't set any flags - let parent handle all mouse events

class ResizableRectItem(QGraphicsRectItem):
    """Rectangle with resizing handles and image support"""
    def __init__(self, x, y, width, height, parent=None):
        super().__init__(x, y, width, height, parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        # Default styling
        self.setPen(QPen(QColor("black"), 2))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        self.corner_radius = 0  # For rounded corners

        # Image support
        self.image_pixmap = None
        self.image_path = None
        self.image_aspect_mode = Qt.AspectRatioMode.KeepAspectRatio

        # Resize handles
        self.handles = {}
        self.resizing_handle = None
        self.resize_start_pos = None
        self.resize_start_rect = None

        self.create_handles()
        self.update_handles()

    def itemChange(self, change, value):
        """Handle item changes like selection"""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.update_handles()
        return super().itemChange(change, value)

    def set_fill_color(self, color):
        self.setBrush(QBrush(QColor(color)))
    
    def set_stroke_color(self, color):
        pen = self.pen()
        pen.setColor(QColor(color))
        self.setPen(pen)
    
    def set_stroke_width(self, width):
        pen = self.pen()
        pen.setWidth(width)
        self.setPen(pen)
    
    def set_corner_radius(self, radius):
        self.corner_radius = radius
        self.update()

    def set_image(self, image_path):
        """Set an image for this shape"""
        if image_path:
            self.image_path = image_path
            self.image_pixmap = QPixmap(image_path)
            self.update()

    def clear_image(self):
        """Remove the image from this shape"""
        self.image_pixmap = None
        self.image_path = None
        self.update()

    def paint(self, painter, option, widget):
        """Custom paint to handle images and rounded corners"""
        if self.image_pixmap and not self.image_pixmap.isNull():
            # Draw image within the rectangle bounds
            rect = self.boundingRect()
            painter.setClipRect(rect)

            # Calculate scaled image rectangle
            image_rect = self.image_pixmap.rect()
            scaled_rect = rect

            if self.image_aspect_mode == Qt.AspectRatioMode.KeepAspectRatio:
                # Scale image to fit while maintaining aspect ratio
                scale_x = rect.width() / image_rect.width()
                scale_y = rect.height() / image_rect.height()
                scale = min(scale_x, scale_y)

                new_width = image_rect.width() * scale
                new_height = image_rect.height() * scale

                scaled_rect = QRectF(
                    rect.center().x() - new_width / 2,
                    rect.center().y() - new_height / 2,
                    new_width,
                    new_height
                )
            elif self.image_aspect_mode == Qt.AspectRatioMode.KeepAspectRatioByExpanding:
                # Scale image to cover entire area
                scale_x = rect.width() / image_rect.width()
                scale_y = rect.height() / image_rect.height()
                scale = max(scale_x, scale_y)

                new_width = image_rect.width() * scale
                new_height = image_rect.height() * scale

                scaled_rect = QRectF(
                    rect.center().x() - new_width / 2,
                    rect.center().y() - new_height / 2,
                    new_width,
                    new_height
                )

            painter.drawPixmap(scaled_rect.toRect(), self.image_pixmap)

        # Draw the shape outline if no image or if selected
        if not self.image_pixmap or self.isSelected():
            if self.corner_radius > 0:
                # Draw rounded rectangle
                path = QPainterPath()
                path.addRoundedRect(self.rect(), self.corner_radius, self.corner_radius)
                painter.setPen(self.pen())
                painter.setBrush(self.brush())
                painter.drawPath(path)
            else:
                # Draw regular rectangle
                super().paint(painter, option, widget)

        # Update handles visibility
        self.update_handles()

    def contextMenuEvent(self, event):
        """Show context menu for image operations"""
        menu = QMenu()

        if self.image_pixmap:
            clear_action = menu.addAction("Remove Image")
            clear_action.triggered.connect(self.clear_image)
        else:
            add_action = menu.addAction("Add Image...")
            add_action.triggered.connect(self._add_image_from_dialog)

        # Image aspect ratio options
        aspect_menu = menu.addMenu("Image Fit")
        fit_options = [
            ("Fill", Qt.AspectRatioMode.IgnoreAspectRatio),
            ("Fit", Qt.AspectRatioMode.KeepAspectRatio),
            ("Cover", Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        ]

        for name, mode in fit_options:
            action = aspect_menu.addAction(name)
            action.triggered.connect(lambda checked, m=mode: self._set_aspect_mode(m))

        menu.exec(event.screenPos())

    def create_handles(self):
        """Create resize handles for the rectangle"""
        cursors = [
            Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor, Qt.CursorShape.SizeBDiagCursor,
            Qt.CursorShape.SizeHorCursor, Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor,
            Qt.CursorShape.SizeBDiagCursor, Qt.CursorShape.SizeHorCursor
        ]

        for i in range(8):
            h = Handle(cursors[i], self, role="resize")
            h.hide()
            self.handles[i] = h

    def update_handles(self):
        """Update handle positions and visibility"""
        rect = self.rect()  # Use the actual rectangle geometry, not bounding rect
        w, h = rect.width(), rect.height()

        # Only show handles if item has valid size and is selected
        show_handles = self.isSelected() and w > 0 and h > 0

        # Position handles at the corners of the actual rectangle
        positions = [
            rect.topLeft(),                    # Top-left
            QPointF(rect.left() + w/2, rect.top()),  # Top-center
            rect.topRight(),                   # Top-right
            QPointF(rect.right(), rect.top() + h/2),  # Right-center
            rect.bottomRight(),                # Bottom-right
            QPointF(rect.left() + w/2, rect.bottom()),  # Bottom-center
            rect.bottomLeft(),                 # Bottom-left
            QPointF(rect.left(), rect.top() + h/2)   # Left-center
        ]

        for i in range(8):
            self.handles[i].setPos(positions[i])
            # Show/hide handles based on selection and size
            if show_handles:
                self.handles[i].show()
            else:
                self.handles[i].hide()

    def mousePressEvent(self, event):
        """Handle mouse press for resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on a resize handle
            click_pos = event.pos()  # Position in item's local coordinates
            for i, h in self.handles.items():
                if h.isVisible():
                    # Check if click is within handle's bounding rect
                    handle_rect = h.boundingRect().translated(h.pos())
                    if handle_rect.contains(click_pos):
                        self.resizing_handle = i
                        self.resize_start_pos = event.scenePos()
                        self.resize_start_rect = self.rect()
                        event.accept()
                        return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for resizing"""
        if self.resizing_handle is not None and self.resize_start_pos and self.resize_start_rect:
            diff = event.scenePos() - self.resize_start_pos  # Use scene coordinates
            dx = diff.x()
            dy = diff.y()

            orig_rect = self.resize_start_rect
            new_rect = QRectF(orig_rect)

            # Handle different resize directions
            if self.resizing_handle == 0:  # Top-left
                new_rect.setTopLeft(orig_rect.topLeft() + QPointF(dx, dy))
            elif self.resizing_handle == 1:  # Top
                new_rect.setTop(orig_rect.top() + dy)
            elif self.resizing_handle == 2:  # Top-right
                new_rect.setTopRight(orig_rect.topRight() + QPointF(dx, dy))
            elif self.resizing_handle == 3:  # Right
                new_rect.setRight(orig_rect.right() + dx)
            elif self.resizing_handle == 4:  # Bottom-right
                new_rect.setBottomRight(orig_rect.bottomRight() + QPointF(dx, dy))
            elif self.resizing_handle == 5:  # Bottom
                new_rect.setBottom(orig_rect.bottom() + dy)
            elif self.resizing_handle == 6:  # Bottom-left
                new_rect.setBottomLeft(orig_rect.bottomLeft() + QPointF(dx, dy))
            elif self.resizing_handle == 7:  # Left
                new_rect.setLeft(orig_rect.left() + dx)

            # Ensure minimum size
            if new_rect.width() >= 10 and new_rect.height() >= 10:
                self.setRect(new_rect)
                self.update_handles()

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.resizing_handle = None
        self.resize_start_pos = None
        self.resize_start_rect = None
        super().mouseReleaseEvent(event)

    def _add_image_from_dialog(self):
        """Show file dialog to select an image"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            None, "Select Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp)"
        )
        if file_path:
            self.set_image(file_path)

    def _set_aspect_mode(self, mode):
        """Set the image aspect ratio mode"""
        self.image_aspect_mode = mode
        self.update()


class ResizableEllipseItem(QGraphicsEllipseItem):
    """Ellipse/Circle with resizing handles and image support"""
    def __init__(self, x, y, width, height, parent=None):
        super().__init__(x, y, width, height, parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        # Default styling
        self.setPen(QPen(QColor("black"), 2))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        # Image support
        self.image_pixmap = None
        self.image_path = None
        self.image_aspect_mode = Qt.AspectRatioMode.KeepAspectRatio

        # Resize handles
        self.handles = {}
        self.resizing_handle = None
        self.resize_start_pos = None
        self.resize_start_rect = None

        self.create_handles()
        self.update_handles()

    def itemChange(self, change, value):
        """Handle item changes like selection"""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.update_handles()
        return super().itemChange(change, value)

    def create_handles(self):
        """Create resize handles for the ellipse"""
        cursors = [
            Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor, Qt.CursorShape.SizeBDiagCursor,
            Qt.CursorShape.SizeHorCursor, Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor,
            Qt.CursorShape.SizeBDiagCursor, Qt.CursorShape.SizeHorCursor
        ]

        for i in range(8):
            h = Handle(cursors[i], self, role="resize")
            h.hide()
            self.handles[i] = h

    def update_handles(self):
        """Update handle positions and visibility"""
        rect = self.rect()  # Use the actual ellipse geometry, not bounding rect
        w, h = rect.width(), rect.height()

        # Only show handles if item has valid size and is selected
        show_handles = self.isSelected() and w > 0 and h > 0

        # Position handles at the corners of the actual ellipse
        positions = [
            rect.topLeft(),                    # Top-left
            QPointF(rect.left() + w/2, rect.top()),  # Top-center
            rect.topRight(),                   # Top-right
            QPointF(rect.right(), rect.top() + h/2),  # Right-center
            rect.bottomRight(),                # Bottom-right
            QPointF(rect.left() + w/2, rect.bottom()),  # Bottom-center
            rect.bottomLeft(),                 # Bottom-left
            QPointF(rect.left(), rect.top() + h/2)   # Left-center
        ]

        for i in range(8):
            self.handles[i].setPos(positions[i])
            # Show/hide handles based on selection and size
            if show_handles:
                self.handles[i].show()
            else:
                self.handles[i].hide()

    def mousePressEvent(self, event):
        """Handle mouse press for resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on a resize handle
            click_pos = event.pos()  # Position in item's local coordinates
            for i, h in self.handles.items():
                if h.isVisible():
                    # Check if click is within handle's bounding rect
                    handle_rect = h.boundingRect().translated(h.pos())
                    if handle_rect.contains(click_pos):
                        self.resizing_handle = i
                        self.resize_start_pos = event.scenePos()
                        self.resize_start_rect = self.rect()
                        event.accept()
                        return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for resizing"""
        if self.resizing_handle is not None and self.resize_start_pos and self.resize_start_rect:
            diff = event.scenePos() - self.resize_start_pos  # Use scene coordinates
            dx = diff.x()
            dy = diff.y()

            orig_rect = self.resize_start_rect
            new_rect = QRectF(orig_rect)

            # Handle different resize directions
            if self.resizing_handle == 0:  # Top-left
                new_rect.setTopLeft(orig_rect.topLeft() + QPointF(dx, dy))
            elif self.resizing_handle == 1:  # Top
                new_rect.setTop(orig_rect.top() + dy)
            elif self.resizing_handle == 2:  # Top-right
                new_rect.setTopRight(orig_rect.topRight() + QPointF(dx, dy))
            elif self.resizing_handle == 3:  # Right
                new_rect.setRight(orig_rect.right() + dx)
            elif self.resizing_handle == 4:  # Bottom-right
                new_rect.setBottomRight(orig_rect.bottomRight() + QPointF(dx, dy))
            elif self.resizing_handle == 5:  # Bottom
                new_rect.setBottom(orig_rect.bottom() + dy)
            elif self.resizing_handle == 6:  # Bottom-left
                new_rect.setBottomLeft(orig_rect.bottomLeft() + QPointF(dx, dy))
            elif self.resizing_handle == 7:  # Left
                new_rect.setLeft(orig_rect.left() + dx)

            # Ensure minimum size
            if new_rect.width() >= 10 and new_rect.height() >= 10:
                self.setRect(new_rect)
                self.update_handles()

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.resizing_handle = None
        self.resize_start_pos = None
        self.resize_start_rect = None
        super().mouseReleaseEvent(event)

    def set_fill_color(self, color):
        self.setBrush(QBrush(QColor(color)))

    def set_stroke_color(self, color):
        pen = self.pen()
        pen.setColor(QColor(color))
        self.setPen(pen)

    def set_stroke_width(self, width):
        pen = self.pen()
        pen.setWidth(width)
        self.setPen(pen)

    def set_image(self, image_path):
        """Set an image for this shape"""
        if image_path:
            self.image_path = image_path
            self.image_pixmap = QPixmap(image_path)
            self.update()

    def clear_image(self):
        """Remove the image from this shape"""
        self.image_pixmap = None
        self.image_path = None
        self.update()

    def paint(self, painter, option, widget):
        """Custom paint to handle images in ellipse"""
        if self.image_pixmap and not self.image_pixmap.isNull():
            # Create elliptical clipping path
            rect = self.boundingRect()
            path = QPainterPath()
            path.addEllipse(rect)
            painter.setClipPath(path)

            # Calculate scaled image rectangle to fit ellipse
            image_rect = self.image_pixmap.rect()
            scale_x = rect.width() / image_rect.width()
            scale_y = rect.height() / image_rect.height()
            scale = max(scale_x, scale_y)  # Cover the entire ellipse

            new_width = image_rect.width() * scale
            new_height = image_rect.height() * scale

            scaled_rect = QRectF(
                rect.center().x() - new_width / 2,
                rect.center().y() - new_height / 2,
                new_width,
                new_height
            )

            painter.drawPixmap(scaled_rect.toRect(), self.image_pixmap)

        # Draw the shape outline if no image or if selected
        if not self.image_pixmap or self.isSelected():
            super().paint(painter, option, widget)

        self.update_handles()

    def contextMenuEvent(self, event):
        """Show context menu for image operations"""
        menu = QMenu()

        if self.image_pixmap:
            clear_action = menu.addAction("Remove Image")
            clear_action.triggered.connect(self.clear_image)
        else:
            add_action = menu.addAction("Add Image...")
            add_action.triggered.connect(self._add_image_from_dialog)

        menu.exec(event.screenPos())

    def _add_image_from_dialog(self):
        """Show file dialog to select an image"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            None, "Select Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp)"
        )
        if file_path:
            self.set_image(file_path)


class ResizableLineItem(QGraphicsLineItem):
    """Line with arrow options"""
    def __init__(self, x1, y1, x2, y2, parent=None):
        super().__init__(x1, y1, x2, y2, parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        
        # Default styling
        self.setPen(QPen(QColor("black"), 2))
        
        self.start_arrow = False
        self.end_arrow = False
        
        # Handles
        self.handles = {}
        self.resizing_handle = None
        self.resize_start_pos = None
        self.create_handles()
        self.update_handles()
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.update_handles()
        return super().itemChange(change, value)

    def create_handles(self):
        # 0: Start, 1: End
        self.handles[0] = Handle(Qt.CursorShape.SizeAllCursor, self)
        self.handles[1] = Handle(Qt.CursorShape.SizeAllCursor, self)
        self.handles[0].hide()
        self.handles[1].hide()

    def update_handles(self):
        line = self.line()
        self.handles[0].setPos(line.p1())
        self.handles[1].setPos(line.p2())
        
        show = self.isSelected()
        if show:
            self.handles[0].show()
            self.handles[1].show()
        else:
            self.handles[0].hide()
            self.handles[1].hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            for i, h in self.handles.items():
                if h.isVisible() and h.isUnderMouse():
                    self.resizing_handle = i
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.resizing_handle is not None:
            pos = event.pos() # Local pos
            line = self.line()
            if self.resizing_handle == 0:
                line.setP1(pos)
            else:
                line.setP2(pos)
            self.setLine(line)
            self.update_handles()
            event.accept()
            return
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        self.resizing_handle = None
        super().mouseReleaseEvent(event)
    
    def set_stroke_color(self, color):
        pen = self.pen()
        pen.setColor(QColor(color))
        self.setPen(pen)
    
    def set_stroke_width(self, width):
        pen = self.pen()
        pen.setWidth(width)
        self.setPen(pen)
    
    def set_start_arrow(self, enabled):
        self.start_arrow = enabled
        self.update()
    
    def set_end_arrow(self, enabled):
        self.end_arrow = enabled
        self.update()


class PolygonItem(QGraphicsPolygonItem):
    """Custom polygon shape with image support"""
    def __init__(self, points, parent=None):
        polygon = QPolygonF(points)
        super().__init__(polygon, parent)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)

        # Default styling
        self.setPen(QPen(QColor("black"), 2))
        self.setBrush(QBrush(Qt.BrushStyle.NoBrush))

        # Image support
        self.image_pixmap = None
        self.image_path = None

        # Resize handles
        self.handles = {}
        self.resizing_handle = None
        self.resize_start_pos = None
        self.resize_start_rect = None

        self.create_handles()
        self.update_handles()

    def itemChange(self, change, value):
        """Handle item changes like selection"""
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            self.update_handles()
        return super().itemChange(change, value)

    def create_handles(self):
        """Create resize handles for the polygon"""
        cursors = [
            Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor, Qt.CursorShape.SizeBDiagCursor,
            Qt.CursorShape.SizeHorCursor, Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor,
            Qt.CursorShape.SizeBDiagCursor, Qt.CursorShape.SizeHorCursor
        ]

        for i in range(8):
            h = Handle(cursors[i], self, role="resize")
            h.hide()
            self.handles[i] = h

    def update_handles(self):
        """Update handle positions and visibility"""
        rect = self.boundingRect()
        w, h = rect.width(), rect.height()

        # Only show handles if item has valid size and is selected
        show_handles = self.isSelected() and w > 0 and h > 0

        # Position handles at the corners of the bounding rectangle
        positions = [
            rect.topLeft(),                    # Top-left
            QPointF(rect.left() + w/2, rect.top()),  # Top-center
            rect.topRight(),                   # Top-right
            QPointF(rect.right(), rect.top() + h/2),  # Right-center
            rect.bottomRight(),                # Bottom-right
            QPointF(rect.left() + w/2, rect.bottom()),  # Bottom-center
            rect.bottomLeft(),                 # Bottom-left
            QPointF(rect.left(), rect.top() + h/2)   # Left-center
        ]

        for i in range(8):
            self.handles[i].setPos(positions[i])
            # Show/hide handles based on selection and size
            if show_handles:
                self.handles[i].show()
            else:
                self.handles[i].hide()

    def mousePressEvent(self, event):
        """Handle mouse press for resizing"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Check if clicking on a resize handle
            click_pos = event.pos()  # Position in item's local coordinates
            for i, h in self.handles.items():
                if h.isVisible():
                    # Check if click is within handle's bounding rect
                    handle_rect = h.boundingRect().translated(h.pos())
                    if handle_rect.contains(click_pos):
                        self.resizing_handle = i
                        self.resize_start_pos = event.scenePos()
                        self.resize_start_rect = self.boundingRect()
                        event.accept()
                        return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move for resizing"""
        if self.resizing_handle is not None and self.resize_start_pos and self.resize_start_rect:
            diff = event.scenePos() - self.resize_start_pos  # Use scene coordinates
            dx = diff.x()
            dy = diff.y()

            orig_rect = self.resize_start_rect
            scale_x = 1.0 + (dx / orig_rect.width()) if orig_rect.width() > 0 else 1.0
            scale_y = 1.0 + (dy / orig_rect.height()) if orig_rect.height() > 0 else 1.0

            # For polygons, we'll scale uniformly for simplicity
            scale = max(scale_x, scale_y)
            if scale < 0.1: scale = 0.1  # Minimum scale

            # Scale the polygon
            center = orig_rect.center()
            current_polygon = self.polygon()

            new_points = []
            for point in current_polygon:
                # Scale relative to center
                dx = point.x() - center.x()
                dy = point.y() - center.y()
                new_point = QPointF(center.x() + dx * scale, center.y() + dy * scale)
                new_points.append(new_point)

            self.setPolygon(QPolygonF(new_points))
            self.update_handles()

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.resizing_handle = None
        self.resize_start_pos = None
        self.resize_start_rect = None
        super().mouseReleaseEvent(event)

    def set_fill_color(self, color):
        self.setBrush(QBrush(QColor(color)))
    
    def set_stroke_color(self, color):
        pen = self.pen()
        pen.setColor(QColor(color))
        self.setPen(pen)
    
    def set_stroke_width(self, width):
        pen = self.pen()
        pen.setWidth(width)
        self.setPen(pen)

    def set_image(self, image_path):
        """Set an image for this polygon (fills the polygon)"""
        if image_path:
            self.image_path = image_path
            self.image_pixmap = QPixmap(image_path)
            self.update()

    def clear_image(self):
        """Remove the image from this polygon"""
        self.image_pixmap = None
        self.image_path = None
        self.update()

    def paint(self, painter, option, widget):
        """Custom paint to handle images in polygon"""
        # Hide/show handles based on selection
        if self.isSelected():
            for h in self.handles.values():
                h.show()
        else:
            for h in self.handles.values():
                h.hide()

        if self.image_pixmap and not self.image_pixmap.isNull():
            # Set clipping to polygon shape
            painter.setClipPath(self.shape())

            # Draw image scaled to fit the polygon bounding rect
            rect = self.boundingRect()
            painter.drawPixmap(rect.toRect(), self.image_pixmap)

        # Draw the shape outline if no image or if selected
        if not self.image_pixmap or self.isSelected():
            super().paint(painter, option, widget)

        self.update_handles()

    def contextMenuEvent(self, event):
        """Show context menu for image operations"""
        menu = QMenu()

        if self.image_pixmap:
            clear_action = menu.addAction("Remove Image")
            clear_action.triggered.connect(self.clear_image)
        else:
            add_action = menu.addAction("Add Image...")
            add_action.triggered.connect(self._add_image_from_dialog)

        menu.exec(event.screenPos())

    def _add_image_from_dialog(self):
        """Show file dialog to select an image"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            None, "Select Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp)"
        )
        if file_path:
            self.set_image(file_path)

    @staticmethod
    def create_star(x, y, outer_radius, inner_radius, points=5):
        """Create a star polygon"""
        star_points = []
        angle_step = 360.0 / points
        
        for i in range(points):
            # Outer point
            angle_outer = math.radians(i * angle_step - 90)
            star_points.append(QPointF(
                x + outer_radius * math.cos(angle_outer),
                y + outer_radius * math.sin(angle_outer)
            ))
            
            # Inner point
            angle_inner = math.radians((i + 0.5) * angle_step - 90)
            star_points.append(QPointF(
                x + inner_radius * math.cos(angle_inner),
                y + inner_radius * math.sin(angle_inner)
            ))
        
        return star_points
    
    @staticmethod
    def create_triangle(x, y, size):
        """Create an equilateral triangle"""
        height = size * math.sqrt(3) / 2
        return [
            QPointF(x, y - 2*height/3),
            QPointF(x - size/2, y + height/3),
            QPointF(x + size/2, y + height/3)
        ]
