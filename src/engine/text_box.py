from PyQt6.QtWidgets import QGraphicsTextItem, QGraphicsItem, QGraphicsRectItem, QGraphicsLineItem, QMenu, QApplication
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QFont, QColor, QPen, QBrush, QCursor, QTextCursor, QAction
import math

class Handle(QGraphicsRectItem):
    def __init__(self, cursor_shape, parent=None, role="resize"):
        super().__init__(-4, -4, 8, 8, parent)
        self.role = role
        
        if role == "link":
            self.setBrush(QBrush(QColor("blue")))
            self.setRect(-6, -6, 12, 12)
        elif role == "rotate":
            self.setBrush(QBrush(QColor("green")))
            self.setRect(-5, -5, 10, 10)
        else:
            self.setBrush(QBrush(QColor("white")))
            self.setPen(QPen(QColor("black")))
            
        self.setCursor(QCursor(cursor_shape))
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

class TextBox(QGraphicsTextItem):
    def __init__(self, text="", font_family="Arial", parent=None, locked=True):
        super().__init__(text, parent)
        self.font_family = font_family
        self.is_locked = locked
        
        # Setup Font
        font = QFont(self.font_family, 24)
        self.setFont(font)
        self.setDefaultTextColor(QColor("black"))
        self.setTextWidth(300)
        
        # Box dimensions
        self.box_height = 200 # Default height
        
        # NEW: Different behavior based on locked state
        if self.is_locked:
            # Locked text box - can edit text but not move/resize
            self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        else:
            # Unlocked text box - can move and resize
            self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | 
                         QGraphicsItem.GraphicsItemFlag.ItemIsSelectable | 
                         QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        
        # Linking State
        self.next_box = None
        self.prev_box = None
        self.link_line = None
        
        # Handles (only for unlocked boxes)
        self.handles = {}
        self.link_handle = None
        self.rotate_handle = None
        self.create_handles()
        self.update_handles()
        
        # State variables
        self.resizing_handle = None
        self.resize_start_pos = None
        self.resize_start_rect = None
        self.start_rotation = 0
        
        # Selection preservation
        self.saved_cursor = None

    def create_handles(self):
        if self.is_locked:
            return  # No handles for locked boxes
            
        cursors = [
            Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor, Qt.CursorShape.SizeBDiagCursor,
            Qt.CursorShape.SizeHorCursor, Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeVerCursor,
            Qt.CursorShape.SizeBDiagCursor, Qt.CursorShape.SizeHorCursor
        ]
        
        for i in range(8):
            h = Handle(cursors[i], self, role="resize")
            h.hide()
            self.handles[i] = h
            
        # Link Handle
        self.link_handle = Handle(Qt.CursorShape.PointingHandCursor, self, role="link")
        self.link_handle.hide()
        
        # Rotate Handle
        self.rotate_handle = Handle(Qt.CursorShape.PointingHandCursor, self, role="rotate")
        self.rotate_handle.hide()

    def update_handles(self):
        if self.is_locked:
            return  # No handles for locked boxes
            
        rect = self.boundingRect()
        w, h = rect.width(), rect.height()
        
        # Position handles at the actual corners of the text box
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
            
        # Position link handle below the text box
        self.link_handle.setPos(rect.center().x(), rect.bottom() + 15)
        
        # Position rotate handle at top-right corner
        self.rotate_handle.setPos(rect.topRight() + QPointF(15, -15))
        
        # Show/hide handles based on selection
        show_handles = self.isSelected()
        for handle in list(self.handles.values()) + [self.link_handle, self.rotate_handle]:
            if show_handles:
                handle.show()
            else:
                handle.hide()

    def boundingRect(self):
        # Override to use box_height if set, or text height if larger (or just box_height for DTP style)
        # For DTP, we want the box to be the authority.
        return QRectF(0, 0, self.textWidth(), self.box_height)

    def paint(self, painter, option, widget):
        # Remove the dashed focus border drawn by QGraphicsTextItem when it has focus
        from PyQt6.QtWidgets import QStyle
        option.state &= ~QStyle.StateFlag.State_HasFocus
        option.state &= ~QStyle.StateFlag.State_Selected

        # Draw text
        super().paint(painter, option, widget)

        # Draw selection border and handles
        if not self.is_locked and self.isSelected():
            # Draw dashed border for unlocked selected boxes
            pen = QPen(QColor("blue"), 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())
            
            # Show handles
            for h in self.handles.values():
                h.show()
            if self.link_handle:
                self.link_handle.show()
            if self.rotate_handle:
                self.rotate_handle.show()
            
            # Draw line to rotate handle
            painter.drawLine(int(self.boundingRect().width()/2), 0, int(self.boundingRect().width()/2), -25)
        elif self.is_locked:
            # Draw light dotted border for locked text boxes so they're visible
            pen = QPen(QColor("#CCCCCC"), 1, Qt.PenStyle.DotLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect())
        else:
            # Hide handles
            for h in self.handles.values():
                h.hide()
            if self.link_handle:
                self.link_handle.hide()
            if self.rotate_handle:
                self.rotate_handle.hide()

    def mouseMoveEvent(self, event):
        if self.is_locked:
            super().mouseMoveEvent(event)
            return
            
        # Handle rotation
        if self.resizing_handle == "rotate":
            center = self.sceneBoundingRect().center()
            pos = event.scenePos()
            dx = pos.x() - center.x()
            dy = pos.y() - center.y()
            angle = math.degrees(math.atan2(dy, dx)) + 90
            self.setRotation(angle)
            return

        # Handle resizing
        if self.resizing_handle is not None:
            scene_pos = event.scenePos()
            # We need to calculate change relative to the item's current state or start state
            # Using scenePos allows us to handle rotation better if we map correctly, 
            # but for simple resizing we can use local coords or diffs.
            # Let's use diff from start screen pos for simplicity, but we need to be careful with rotation.
            
            # Better approach: map mouse pos to item coords?
            # If item is rotated, resizing is tricky.
            # For now, let's assume no rotation or handle it simply.
            
            diff = event.screenPos() - self.resize_start_pos
            dx = diff.x()
            dy = diff.y()
            
            # Adjust dx/dy based on rotation? 
            # If rotated, screen dx/dy doesn't map to width/height directly.
            # We should map scene pos to item pos.
            
            local_start = self.mapFromScene(self.mapToScene(self.resize_start_rect.topLeft())) # This is just 0,0
            local_mouse = self.mapFromScene(event.scenePos())
            
            # This is getting complex. Let's stick to the simple rect update logic 
            # assuming the user drags handles in the direction of the handle.
            
            orig_rect = self.resize_start_rect
            new_rect = QRectF(orig_rect)
            
            # Note: QGraphicsTextItem position is top-left.
            
            if self.resizing_handle == 0: # Top-Left
                # Move pos, change size
                # This is hard because setPos is in parent coords.
                # Let's just change width/height and move pos if needed.
                # For TextItem, moving top-left means changing pos.
                pass 
                # Implementing full multi-direction resizing for TextItem is complex 
                # because text flow depends on width.
                
            # Simplified resizing:
            # Right handles (2, 3, 4) change width.
            # Bottom handles (4, 5, 6) change height.
            # Left/Top handles are harder because they shift content.
            
            if self.resizing_handle in [2, 3, 4]: # Right side
                new_width = max(50, orig_rect.width() + dx)
                self.setTextWidth(new_width)
                
            if self.resizing_handle in [4, 5, 6]: # Bottom side
                new_height = max(50, orig_rect.height() + dy)
                self.box_height = new_height
                
            self.update_handles()
            return

        # Snap to Guides Logic
        if not self.is_locked and self.resizing_handle is None:
            # Check if snapping is enabled in the view
            views = self.scene().views()
            if views and hasattr(views[0], 'snap_to_guides') and views[0].snap_to_guides:
                # Let super handle move first
                super().mouseMoveEvent(event)
                
                # Now check position and snap
                pos = self.pos()
                x, y = pos.x(), pos.y()
                snap_distance = 10
                
                # Find guides
                snapped_x = x
                snapped_y = y
                
                for item in self.scene().items():
                    if isinstance(item, QGraphicsLineItem):
                        line = item.line()
                        # Vertical guide
                        if line.x1() == line.x2():
                            if abs(x - line.x1()) < snap_distance:
                                snapped_x = line.x1()
                        # Horizontal guide
                        elif line.y1() == line.y2():
                            if abs(y - line.y1()) < snap_distance:
                                snapped_y = line.y1()
                                
                if snapped_x != x or snapped_y != y:
                    self.setPos(snapped_x, snapped_y)
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.resizing_handle = None
        super().mouseReleaseEvent(event)

    def focusOutEvent(self, event):
        # Keep text interaction enabled for both locked and unlocked
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
        super().focusOutEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.setFocus()
        super().mouseDoubleClickEvent(event)

    def cut(self):
        """Cut selected text"""
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_text)
            cursor.removeSelectedText()

    def copy(self):
        """Copy selected text"""
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_text)

    def paste(self):
        """Paste text from clipboard"""
        cursor = self.textCursor()
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            cursor.insertText(text)

    def set_text_color(self, color):
        """Set text color for selected text or future typing"""
        cursor = self.textCursor()
        if cursor.hasSelection():
            fmt = cursor.charFormat()
            fmt.setForeground(color)
            cursor.mergeCharFormat(fmt)
        else:
            fmt = cursor.charFormat()
            fmt.setForeground(color)
            cursor.setCharFormat(fmt)
        self.setTextCursor(cursor)