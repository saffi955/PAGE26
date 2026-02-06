from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QFileDialog, QGraphicsRectItem, QGraphicsPixmapItem, QGraphicsLineItem, QGraphicsProxyWidget, QGraphicsItem, QGraphicsItemGroup
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen, QPixmap, QTextCursor, QAction
from PyQt6.QtPrintSupport import QPrinter
from src.engine.input_handler import InputHandler
from src.engine.text_box import TextBox
from src.engine.page_manager import PageManager
from src.engine.shape_items import ResizableRectItem, ResizableEllipseItem, ResizableLineItem, PolygonItem

class DocumentView(QGraphicsView):
    def __init__(self, font_family, page_settings=None, parent=None):
        super().__init__(parent)
        self.font_family = font_family
        self.input_handler = InputHandler()
        
        # Undo/Redo Stack
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_steps = 50
        
        # Page Manager
        self.page_manager = PageManager()
        self.scene = self.page_manager.get_current_page().scene
        self.setScene(self.scene)
        
        # Default Page dimensions (A4)
        self.page_width = 794
        self.page_height = 1123
        self.margin_left = 50
        self.margin_right = 50
        self.margin_top = 50
        self.margin_bottom = 50
        
        # Apply page settings if provided
        if page_settings:
            # Convert mm to pixels (approx 96 DPI: 1mm = 3.78px)
            mm_to_px = 3.78
            self.page_width = int(page_settings['width'] * mm_to_px)
            self.page_height = int(page_settings['height'] * mm_to_px)
            
            margins = page_settings['margins']
            self.margin_left = int(margins['left'] * mm_to_px)
            self.margin_right = int(margins['right'] * mm_to_px)
            self.margin_top = int(margins['top'] * mm_to_px)
            self.margin_bottom = int(margins['bottom'] * mm_to_px)
            
            # Update PageManager's page size (assuming it supports resizing, or just resize the scene rect)
            self.scene.setSceneRect(0, 0, self.page_width, self.page_height)
            # Also update the white background item if PageManager creates one
            # For now, we'll assume PageManager handles the scene rect or we force it here.
        
        # Current formatting settings (for new text boxes) - MUST be set before init_ui()
        self.current_font_family = font_family
        self.current_font_size = 24
        
        # Initialize language to Urdu
        self.current_language = 'UR'
        self.input_handler.set_language('UR')

        self.init_ui()
        
        self.current_tool = "text" # ptr, text, pic, rect, ellipse, line, star
        self.temp_item = None
        self.linking_source = None
        self.active_text_box = None # Track focused text box
        
        # For shape drawing
        self.drawing_shape = None
        self.shape_start_pos = None
        
        # Zoom
        self.zoom_level = 1.0

    def save_state(self):
        """Save current state to undo stack"""
        if len(self.undo_stack) >= self.max_undo_steps:
            self.undo_stack.pop(0)
        self.undo_stack.append(self.get_content())
        self.redo_stack.clear()

    def undo(self):
        """Undo last action"""
        if self.undo_stack:
            current_state = self.get_content()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack.pop()
            self.set_content(previous_state)

    def redo(self):
        """Redo last undone action"""
        if self.redo_stack:
            current_state = self.get_content()
            self.undo_stack.append(current_state)
            next_state = self.redo_stack.pop()
            self.set_content(next_state)

    def init_ui(self):
        # Set background
        self.setBackgroundBrush(QBrush(QColor("#D3D3D3"))) # Dark workspace
        
        # Draw Margin Guides
        self.draw_guides()
        
        # Initial page already has white background from PageManager
        # Add initial text box (Body Text)
        body_width = self.page_width - self.margin_left - self.margin_right
        body_height = self.page_height - self.margin_top - self.margin_bottom
        
        text_box = self.add_text_box(self.margin_left, self.margin_top, width=body_width, height=body_height, locked=True)
        
        # Clear any initial text selection to avoid grey disabled selection
        self.clear_text_selections()
        
        # Set default tool to text
        self.set_tool("text")
        
        # Ensure scroll bar is at top
        self.verticalScrollBar().setValue(0)
        
        # Connect selection change to main window update
        self.scene.selectionChanged.connect(self.on_selection_changed)

    def on_selection_changed(self):
        # Notify main window to update ribbon
        window = self.window()
        if hasattr(window, 'update_ribbon_context'):
            window.update_ribbon_context()
        
    def draw_guides(self):
        """Draws grey dashed lines for margins"""
        pen = QPen(QColor("#999999"), 1, Qt.PenStyle.DashLine)
        
        # Left Margin
        line_left = QGraphicsLineItem(self.margin_left, 0, self.margin_left, self.page_height)
        line_left.setPen(pen)
        self.scene.addItem(line_left)
        
        # Right Margin
        line_right = QGraphicsLineItem(self.page_width - self.margin_right, 0, self.page_width - self.margin_right, self.page_height)
        line_right.setPen(pen)
        self.scene.addItem(line_right)
        
        # Top Margin
        line_top = QGraphicsLineItem(0, self.margin_top, self.page_width, self.margin_top)
        line_top.setPen(pen)
        self.scene.addItem(line_top)
        
        # Bottom Margin
        line_bottom = QGraphicsLineItem(0, self.page_height - self.margin_bottom, self.page_width, self.page_height - self.margin_bottom)
        line_bottom.setPen(pen)
        self.scene.addItem(line_bottom)
    
    def switch_page(self, page_index):
        """Switch to a different page - FIXED: Proper implementation"""
        if self.page_manager.set_current_page(page_index):
            self.scene = self.page_manager.get_current_page().scene
            self.setScene(self.scene)
            
            # Ensure guides are drawn on the new page
            # We check if guides exist by looking for QGraphicsLineItem with specific pen
            # Or simpler: just try to draw them. To avoid duplicates, we can clear lines first or check.
            # Since Page objects persist, we should check if guides are already there.
            # For now, let's just clear all QGraphicsLineItems that match our guide style and redraw.
            # Actually, Page scene items persist. Let's add a flag to Page or just check.
            
            # Simple check: count line items. If < 4, draw guides.
            line_count = sum(1 for item in self.scene.items() if isinstance(item, QGraphicsLineItem))
            if line_count < 4:
                self.draw_guides()
                
            return True
        return False
        
    def delete_current_page(self):
        """Delete current page"""
        current_index = self.page_manager.current_page_index
        if self.page_manager.delete_page(current_index):
            # Refresh view with new current page
            self.scene = self.page_manager.get_current_page().scene
            self.setScene(self.scene)
            
            # Ensure guides are drawn
            line_count = sum(1 for item in self.scene.items() if isinstance(item, QGraphicsLineItem))
            if line_count < 4:
                self.draw_guides()
                
            return True
        return False
    
    def set_zoom(self, zoom_factor):
        """Set zoom level (1.0 = 100%)"""
        self.resetTransform()
        self.scale(zoom_factor, zoom_factor)
        self.zoom_level = zoom_factor
        
        # Notify listener (e.g. DocumentWindow for rulers)
        if hasattr(self, 'on_zoom_changed') and self.on_zoom_changed:
            self.on_zoom_changed(zoom_factor)

    def add_text_box(self, x, y, width=300, height=200, locked=True):
        """Create text box with lock option"""
        urdu_text = "یہ اردو متن ہے۔ آپ اس میں کسی بھی حرف یا لفظ کو منتخب کر سکتے ہیں۔"
        tb = TextBox(urdu_text, self.current_font_family, locked=locked)
        tb.setPos(x, y)
        tb.setTextWidth(width)
        tb.box_height = height  # Set the height for the text box
        tb.update_handles()  # Update handles with new dimensions
        
        # Apply current font settings
        font = tb.font()
        font.setPointSize(int(self.current_font_size))
        tb.setFont(font)
        
        
        # Set text format
        cursor = tb.textCursor()
        cursor.select(cursor.SelectionType.Document)  # Use cursor's SelectionType, not QTextCursor
        fmt = cursor.charFormat()
        fmt.setFontFamily(self.current_font_family)
        fmt.setFontPointSize(self.current_font_size)
        cursor.mergeCharFormat(fmt)
        tb.setTextCursor(cursor)
        
        
        # Install event filter for input handling
        tb.installEventFilter(self)
        
        # Set up linking callback
        tb.on_link_clicked = self.start_linking
        
        self.scene.addItem(tb)
        return tb
    
    def start_linking(self, source_box):
        self.linking_source = source_box
        self.setCursor(Qt.CursorShape.CrossCursor)

    def finish_linking(self, target_box):
        if self.linking_source and self.linking_source != target_box:
            self.linking_source.next_box = target_box
            target_box.prev_box = self.linking_source
            self.linking_source.update_handles()
        
        self.linking_source = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_tool(self, tool_name):
        self.current_tool = tool_name
        self.linking_source = None

        # Clear text selections and item selections only when switching to tools that don't involve text
        if tool_name in ["hand", "rotate"]:
            self.clear_text_selections()
            self.scene.clearSelection()

        if tool_name == "ptr":
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif tool_name == "hand":
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif tool_name == "link":
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif tool_name == "unlink":
            # Handle unlinking logic - select a text box to unlink
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif tool_name == "text":
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.IBeamCursor)
        elif tool_name in ["rect_text", "title_text", "rect", "round_rect", "ellipse", "line", "polygon", "rotate"]:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.ArrowCursor)

    # --- I/O Methods ---
    # Note: Save/Load now needs to serialize the SCENE items, not just HTML.
    # For backward compatibility with the previous step's simple HTML save, 
    # we might need to rethink or just dump the text of all boxes.
    # For this step, I will implement a basic JSON serializer for the boxes.

    def get_content(self):
        # Serialize scene to JSON
        import json
        data = []
        for item in self.scene.items():
            if isinstance(item, TextBox):
                data.append({
                    "type": "text",
                    "x": item.x(),
                    "y": item.y(),
                    "content": item.toHtml(),
                    "width": item.textWidth()
                })
            # Add image handling later
        return json.dumps(data)

    def set_content(self, content):
        # Deserialize
        import json
        try:
            data = json.loads(content)
            self.scene.clear()
            
            # Re-add page background
            page_item = QGraphicsRectItem(0, 0, self.page_width, self.page_height)
            page_item.setBrush(QBrush(QColor("white")))
            page_item.setPen(QPen(Qt.GlobalColor.black))
            self.scene.addItem(page_item)
            
            for item_data in data:
                if item_data["type"] == "text":
                    tb = self.add_text_box(item_data["x"], item_data["y"])
                    tb.setHtml(item_data["content"])
                    tb.setTextWidth(item_data["width"])
        except:
            # Fallback for old HTML files
            self.scene.clear()
            # Re-add page background
            page_item = QGraphicsRectItem(0, 0, self.page_width, self.page_height)
            page_item.setBrush(QBrush(QColor("white")))
            self.scene.addItem(page_item)
            
            tb = self.add_text_box(50, 50)
            tb.setHtml(content)

    def export_pdf(self, file_path):
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(file_path)
        
        # Render the scene
        painter = QPainter(printer)
        self.scene.render(painter)
        painter.end()

    def set_language(self, lang):
        """FIXED: Properly set language for input handler"""
        self.input_handler.set_language(lang)
        self.current_language = lang

    def eventFilter(self, obj, event):
        # Input handling for TextBox documents
        if event.type() == event.Type.KeyPress:
            # DEBUG: Print language state
            print(f"DEBUG: KeyPress event, language={self.input_handler.current_language}, key='{event.text()}'")
            
            # Use input handler's language setting
            if self.input_handler.current_language == 'UR':
                # Ignore modifier keys alone
                if event.key() in (Qt.Key.Key_Shift, Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
                    return False
                    
                # Allow control shortcuts (Copy/Paste/Select All)
                if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    if event.key() in (Qt.Key.Key_A, Qt.Key.Key_C, Qt.Key.Key_V, Qt.Key.Key_X):
                        return False
                        
                mapped_char = self.input_handler.process_key(event)
                print(f"DEBUG: Mapped '{event.text()}' to '{mapped_char}'")
                
                if mapped_char and mapped_char != event.text():  # Only if mapping changed
                    focus_item = self.scene.focusItem()
                    print(f"DEBUG: Focus item: {type(focus_item)}")
                    
                    if isinstance(focus_item, TextBox):
                        cursor = focus_item.textCursor()
                        
                        # CRITICAL FIX: Set cursor format to use Urdu font BEFORE inserting
                        fmt = cursor.charFormat()
                        fmt.setFontFamily(self.current_font_family)
                        fmt.setFontPointSize(self.current_font_size)
                        cursor.setCharFormat(fmt)
                        
                        # Insert the Urdu character
                        cursor.insertText(mapped_char)
                        focus_item.setTextCursor(cursor)
                        print(f"DEBUG: Successfully inserted '{mapped_char}'")
                        return True  # Block default handler
                        
                # If no mapping or same character, let default handler process
                return False
        
        elif event.type() == event.Type.FocusIn:
            if isinstance(obj, TextBox):
                self.active_text_box = obj
                
        return super().eventFilter(obj, event)

    # Formatting proxies
    def _apply_char_format(self, format_func):
        # Use active_text_box if available, otherwise focusItem
        item = self.active_text_box if self.active_text_box else self.scene.focusItem()
        
        if isinstance(item, TextBox):
            # Restore focus to ensure selection is valid and visible
            item.setFocus()
            
            cursor = item.textCursor()
            if not cursor.hasSelection():
                # If no selection, apply to the whole word or future typing? 
                # For now let's apply to selection or if empty, set the char format for insertion
                pass
            
            fmt = cursor.charFormat()
            format_func(fmt)
            cursor.mergeCharFormat(fmt)
            item.setTextCursor(cursor)
            
    def _apply_block_format(self, format_func):
        # Use active_text_box if available, otherwise focusItem
        item = self.active_text_box if self.active_text_box else self.scene.focusItem()
        
        if isinstance(item, TextBox):
            item.setFocus()
            cursor = item.textCursor()
            fmt = cursor.blockFormat()
            format_func(fmt)
            cursor.mergeBlockFormat(fmt)
            item.setTextCursor(cursor)

    def set_bold(self, enabled):
        def func(fmt):
            fmt.setFontWeight(QFont.Weight.Bold if enabled else QFont.Weight.Normal)
        self._apply_char_format(func)

    def set_italic(self, enabled):
        def func(fmt):
            fmt.setFontItalic(enabled)
        self._apply_char_format(func)

    def set_underline(self, enabled):
        def func(fmt):
            fmt.setFontUnderline(enabled)
        self._apply_char_format(func)

    def set_font_family(self, family):
        """Apply font family to selected text only"""
        self.current_font_family = family
        item = self.active_text_box if self.active_text_box else self.scene.focusItem()
        
        if isinstance(item, TextBox):
            item.setFocus()
            cursor = item.textCursor()
            if cursor.hasSelection():
                fmt = cursor.charFormat()
                fmt.setFontFamily(family)
                cursor.mergeCharFormat(fmt)
            else:
                fmt = cursor.charFormat()
                fmt.setFontFamily(family)
                cursor.setCharFormat(fmt)
            item.setTextCursor(cursor)
            # DO NOT clear text selection after formatting - keep selection active

    def set_font_size(self, size):
        """Apply font size to selected text only"""
        self.current_font_size = float(size)
        item = self.active_text_box if self.active_text_box else self.scene.focusItem()
        
        if isinstance(item, TextBox):
            item.setFocus()
            cursor = item.textCursor()
            if cursor.hasSelection():
                fmt = cursor.charFormat()
                fmt.setFontPointSize(float(size))
                cursor.mergeCharFormat(fmt)
            else:
                fmt = cursor.charFormat()
                fmt.setFontPointSize(float(size))
                cursor.setCharFormat(fmt)
            item.setTextCursor(cursor)
            # DO NOT clear text selection after formatting - keep selection active

    def set_alignment(self, alignment):
        """Set text alignment for selected text box"""
        # Fix for RTL inversion: Use Absolute alignment to force visual Left/Right
        if alignment == Qt.AlignmentFlag.AlignLeft:
            alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignAbsolute
        elif alignment == Qt.AlignmentFlag.AlignRight:
            alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignAbsolute

        def func(fmt):
            fmt.setAlignment(alignment)
        self._apply_block_format(func)

    def set_text_color(self, color):
        """Set text color for selected text box"""
        if self.temp_item and isinstance(self.temp_item, TextBox):
            self.temp_item.set_text_color(color)
        else:
            item = self.active_text_box if self.active_text_box else self.scene.focusItem()
            if isinstance(item, TextBox):
                item.setFocus()
                item.set_text_color(color)
                # DO NOT clear text selection after formatting - keep selection active
            else:
                for item in self.scene.selectedItems():
                    if isinstance(item, TextBox):
                        item.set_text_color(color)

    def set_word_spacing(self, spacing):
        """Set word spacing for selected text box"""
        if self.temp_item and isinstance(self.temp_item, TextBox):
            self.temp_item.set_word_spacing(spacing)
        else:
            item = self.active_text_box if self.active_text_box else self.scene.focusItem()
            if isinstance(item, TextBox):
                item.setFocus()
                item.set_word_spacing(spacing)

    def keyPressEvent(self, event):
        """Handle key events for the view"""
        if event.key() == Qt.Key.Key_Delete:
            self.delete_selected()
            event.accept()
            return
            
        super().keyPressEvent(event)

    def set_line_height(self, height):
        """Set line height for selected text box"""
        item = self.active_text_box if self.active_text_box else self.scene.focusItem()
        if isinstance(item, TextBox):
            item.setFocus()
            cursor = item.textCursor()
            fmt = cursor.blockFormat()
            fmt.setLineHeight(height, QTextCursor.LineHeightType.ProportionalHeight)
            cursor.mergeBlockFormat(fmt)
            item.setTextCursor(cursor)

    def apply_paragraph_formatting(self, formatting):
        """Apply paragraph formatting from dialog"""
        item = self.active_text_box if self.active_text_box else self.scene.focusItem()
        if isinstance(item, TextBox):
            item.setFocus()
            cursor = item.textCursor()
            fmt = cursor.blockFormat()
            
            # Alignment
            align_map = {
                "Left": Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignAbsolute,
                "Center": Qt.AlignmentFlag.AlignCenter,
                "Right": Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignAbsolute,
                "Justify": Qt.AlignmentFlag.AlignJustify
            }
            if formatting["alignment"] in align_map:
                fmt.setAlignment(align_map[formatting["alignment"]])
            
            # Indentation (mm to px approx)
            mm_to_px = 3.78
            fmt.setLeftMargin(formatting["indent_left"] * mm_to_px)
            fmt.setRightMargin(formatting["indent_right"] * mm_to_px)
            fmt.setTextIndent(formatting["indent_first"] * mm_to_px)
            
            # Spacing
            fmt.setTopMargin(formatting["space_before"])
            fmt.setBottomMargin(formatting["space_after"])
            fmt.setLineHeight(formatting["line_spacing"], QTextCursor.LineHeightType.ProportionalHeight)
            
            cursor.mergeBlockFormat(fmt)
            item.setTextCursor(cursor)

    def apply_hyphenation_settings(self, settings):
        """Apply hyphenation settings"""
        # Store settings for future use during text layout
        self.hyphenation_settings = settings
        # In a real implementation, this would trigger a re-layout of the text
        # For now, we just store it.
        pass

    def apply_border_settings(self, settings):
        """Apply border settings to selected item"""
        item = self.active_text_box if self.active_text_box else self.scene.focusItem()
        
        # Also check selected items if no focus item
        if not item and self.scene.selectedItems():
            item = self.scene.selectedItems()[0]
            
        if item:
            # If it's a TextBox or Shape
            if hasattr(item, 'setPen'): # Shapes
                pen = item.pen()
                
                # Style
                style_map = {
                    "None": Qt.PenStyle.NoPen,
                    "Solid": Qt.PenStyle.SolidLine,
                    "Dashed": Qt.PenStyle.DashLine,
                    "Dotted": Qt.PenStyle.DotLine,
                    "Double": Qt.PenStyle.SolidLine # Qt doesn't have native Double, would need custom drawing
                }
                
                if settings["style"] in style_map:
                    pen.setStyle(style_map[settings["style"]])
                
                pen.setWidth(settings["width"])
                pen.setColor(settings["color"])
                item.setPen(pen)
                
            elif isinstance(item, TextBox):
                # TextBox border
                # TextBox usually has a border via its rect item or we draw it
                # For now, let's assume TextBox has a set_border method or we access its internal rect
                # But TextBox inherits from QGraphicsRectItem (or similar) in some implementations
                # In this codebase, TextBox inherits QGraphicsRectItem
                pen = item.pen()
                
                style_map = {
                    "None": Qt.PenStyle.NoPen,
                    "Solid": Qt.PenStyle.SolidLine,
                    "Dashed": Qt.PenStyle.DashLine,
                    "Dotted": Qt.PenStyle.DotLine,
                    "Double": Qt.PenStyle.SolidLine 
                }
                
                if settings["style"] in style_map:
                    pen.setStyle(style_map[settings["style"]])
                
                pen.setWidth(settings["width"])
                pen.setColor(settings["color"])
                item.setPen(pen)

    def set_char_width(self, width):
        """Set character width for selected text box"""
        item = self.active_text_box if self.active_text_box else self.scene.focusItem()
        if isinstance(item, TextBox):
            item.setFocus()
            cursor = item.textCursor()
            if cursor.hasSelection():
                fmt = cursor.charFormat()
                # Character width is typically handled via font stretching
                # width is in percentage (100 = normal)
                fmt.setFontStretch(int(value))
                cursor.mergeCharFormat(fmt)
            else:
                fmt = cursor.charFormat()
                fmt.setFontStretch(int(value))
                cursor.setCharFormat(fmt)
            item.setTextCursor(cursor)

    def insert_text_box(self):
        """Insert new text box at mouse position"""
        # Get current mouse position in scene coordinates
        pos = self.mapToScene(self.viewport().rect().center())
        self.add_text_box(pos.x(), pos.y(), width=200, height=100, locked=False)

    def set_show_invisibles(self, enabled):
        """Toggle visibility of invisible characters (spaces, tabs, etc.)"""
        # For now, just store the flag. 
        # In a real implementation, this would update text layout options.
        self.show_invisibles = enabled
        # Trigger redraw or update text documents
        
    def set_snap_to_guides(self, enabled):
        """Toggle snap to guides"""
        self.snap_to_guides = enabled
        
    def insert_table(self, rows=3, cols=3):
        """Insert a table"""
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
        
        pos = self.mapToScene(self.viewport().rect().center())
        table = QTableWidget(rows, cols)
        # Fill with dummy data
        for r in range(rows):
            for c in range(cols):
                table.setItem(r, c, QTableWidgetItem(f"Cell {r},{c}"))
                
        table_item = QGraphicsProxyWidget()
        table_item.setWidget(table)
        table_item.setPos(pos)
        table_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        table_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.scene.addItem(table_item)
        self.save_state()

    def insert_image(self, file_path):
        """Insert an image from file"""
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return
            
        pos = self.mapToScene(self.viewport().rect().center())
        
        # Create a pixmap item
        # We might want to wrap it in a resizable item or just add it directly
        # For now, let's use a simple QGraphicsPixmapItem but make it movable/selectable
        
        # Better: Use a custom ResizableImageItem if we had one, or just a QGraphicsPixmapItem
        item = QGraphicsPixmapItem(pixmap)
        item.setPos(pos)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.scene.addItem(item)
        self.save_state()

    def select_all(self):
        """Select all items in the scene"""
        for item in self.scene.items():
            # Don't select the page background or guides if possible
            # Assuming page background is the first item or locked
            if item.flags() & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable:
                item.setSelected(True)

    def delete_selected(self):
        """Delete selected items"""
        # Collect items to delete first to avoid issues while iterating
        items_to_delete = self.scene.selectedItems()
        
        # Also check for active text box if it's not selected but focused
        if self.active_text_box and self.active_text_box not in items_to_delete:
             # Only delete if it's not in text editing mode? 
             # Actually, if we are editing text, Delete key deletes character.
             # So this method should only be called if we are NOT editing text, 
             # OR if we explicitly want to delete the box (e.g. with a specific command).
             # The keyPressEvent handles the distinction.
             pass

        for item in items_to_delete:
            self.scene.removeItem(item)
            
        self.save_state()

    def duplicate_selected(self):
        """Duplicate selected items"""
        offset = 20
        new_items = []
        for item in self.scene.selectedItems():
            if isinstance(item, TextBox):
                # Clone text box
                new_tb = self.add_text_box(item.x() + offset, item.y() + offset, item.textWidth(), locked=item.locked)
                new_tb.setHtml(item.toHtml())
                new_items.append(new_tb)
            elif isinstance(item, ResizableRectItem):
                from src.engine.shape_items import ResizableRectItem
                new_item = ResizableRectItem(item.rect().x(), item.rect().y(), item.rect().width(), item.rect().height())
                new_item.setPos(item.pos() + QPointF(offset, offset))
                new_item.setPen(item.pen())
                new_item.setBrush(item.brush())
                self.scene.addItem(new_item)
                new_items.append(new_item)
            # Add other item types here
            
        # Select new items
        self.scene.clearSelection()
        for item in new_items:
            item.setSelected(True)
        self.save_state()

    def bring_to_front(self):
        """Bring selected items one step forward"""
        for item in self.scene.selectedItems():
            z = item.zValue()
            item.setZValue(z + 1)
        self.save_state()

    def send_to_back(self):
        """Send selected items one step backward"""
        for item in self.scene.selectedItems():
            z = item.zValue()
            item.setZValue(z - 1)
        self.save_state()

    def top_most(self):
        """Bring selected items to the very top"""
        # Find max Z
        max_z = 0
        for item in self.scene.items():
            max_z = max(max_z, item.zValue())
        
        for item in self.scene.selectedItems():
            item.setZValue(max_z + 1)
        self.save_state()

    def bottom_most(self):
        """Send selected items to the very bottom"""
        # Find min Z
        min_z = 0
        for item in self.scene.items():
            min_z = min(min_z, item.zValue())
            
        for item in self.scene.selectedItems():
            item.setZValue(min_z - 1)
        self.save_state()

    def group_selected(self):
        """Group selected items"""
        selected = self.scene.selectedItems()
        if len(selected) > 1:
            group = self.scene.createItemGroup(selected)
            group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
            group.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
            group.setSelected(True)
            self.save_state()

    def ungroup_selected(self):
        """Ungroup selected items"""
        for item in self.scene.selectedItems():
            if isinstance(item, QGraphicsItemGroup):
                self.scene.destroyItemGroup(item)
        self.save_state()
        
    def lock_guides(self):
        """Lock/Unlock guides"""
        # Implementation depends on how guides are stored.
        # Currently guides are just lines. We can make them unselectable.
        # They are already unselectable by default if we didn't set ItemIsSelectable.
        pass

    def clear_text_selections(self):
        """Clear text selections/cursors in all text boxes"""
        for item in self.scene.items():
            if isinstance(item, TextBox):
                # Clear focus first
                if item.hasFocus():
                    item.clearFocus()
                
                # Clear text selection
                cursor = item.textCursor()
                cursor.clearSelection()
                # Move cursor to end to avoid showing cursor
                cursor.movePosition(cursor.MoveOperation.End)
                item.setTextCursor(cursor)
                
                # Force update
                item.update()
        
        # Clear scene and view focus
        self.scene.clearFocus()
        self.clearFocus()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        scene_pos = self.mapToScene(event.pos())          # QPointF in scene coords
        view_pos = event.pos()                             # QPoint in view coords (for itemAt)

        # Correct way to get item under cursor
        item_at_pos = self.scene.itemAt(scene_pos, self.transform())

        # === FIX: Clear gray selection when clicking outside active text box ===
        if self.active_text_box:
            # If we clicked somewhere else (or on background), clear selection fully
            if not item_at_pos or item_at_pos != self.active_text_box:
                cursor = self.active_text_box.textCursor()
                cursor.clearSelection()
                self.active_text_box.setTextCursor(cursor)
                self.active_text_box.clearFocus()
                self.active_text_box = None

        # Special case: clicking on locked main text box with pointer tool → treat as "empty space"
        is_locked_textbox = isinstance(item_at_pos, TextBox) and getattr(item_at_pos, 'is_locked', False)

        # If clicking on empty area OR on locked textbox while not in text tool → clear all selections
        if not item_at_pos or (is_locked_textbox and self.current_tool != "text"):
            self.scene.clearSelection()
            # Optional: also clear focus from any text box
            for item in self.scene.items():
                if isinstance(item, TextBox):
                    item.clearFocus()

        # Prevent event from reaching locked text box if we're just deselecting
        if is_locked_textbox and self.current_tool != "text":
            event.accept()
            return

        # === TOOL: Shape / Text Box Creation ===
        if self.current_tool == "rect":
            from src.engine.shape_items import ResizableRectItem
            self.temp_item = ResizableRectItem(0, 0, 1, 1)
            self.temp_item.setPos(scene_pos)
            self.scene.addItem(self.temp_item)
            self.shape_start_pos = scene_pos
            event.accept()
            return

        elif self.current_tool == "round_rect":
            from src.engine.shape_items import ResizableRectItem
            self.temp_item = ResizableRectItem(0, 0, 1, 1)
            self.temp_item.setPos(scene_pos)
            self.temp_item.set_corner_radius(20)
            self.scene.addItem(self.temp_item)
            self.shape_start_pos = scene_pos
            event.accept()
            return

        elif self.current_tool == "ellipse":
            from src.engine.shape_items import ResizableEllipseItem
            self.temp_item = ResizableEllipseItem(0, 0, 1, 1)
            self.temp_item.setPos(scene_pos)
            self.scene.addItem(self.temp_item)
            self.shape_start_pos = scene_pos
            event.accept()
            return

        elif self.current_tool == "line":
            from src.engine.shape_items import ResizableLineItem
            self.temp_item = ResizableLineItem(0, 0, 1, 1)
            self.temp_item.setPos(scene_pos)
            self.scene.addItem(self.temp_item)
            self.shape_start_pos = scene_pos
            event.accept()
            return

        elif self.current_tool == "polygon":
            from src.engine.shape_items import PolygonItem
            points = PolygonItem.create_triangle(0, 0, 50)
            self.temp_item = PolygonItem(points)
            self.temp_item.setPos(scene_pos)
            self.scene.addItem(self.temp_item)
            self.shape_start_pos = scene_pos
            event.accept()
            return

        elif self.current_tool in ("rect_text", "title_text"):
            self.temp_item = self.current_tool
            self.shape_start_pos = scene_pos
            event.accept()
            return

        # Let Qt handle selection/move/resize for pointer tool and other cases
        super().mousePressEvent(event)

    def find_text(self, text, case_sensitive, backward):
        """Find text in text boxes"""
        flags = QTextCursor.FindFlag(0)
        if case_sensitive:
            flags |= QTextCursor.FindFlag.FindCaseSensitively
        if backward:
            flags |= QTextCursor.FindFlag.FindBackward

        # Start from active text box or first text box
        start_item = self.active_text_box if self.active_text_box else None
        
        # If no active item, find the first text box
        if not start_item:
            for item in self.scene.items():
                if isinstance(item, TextBox):
                    start_item = item
                    break
        
        if not start_item:
            return False

        # Search in current item
        cursor = start_item.textCursor()
        found = start_item.find(text, flags)
        
        if found:
            self.active_text_box = start_item
            start_item.setFocus()
            return True
            
        # If not found in current, search other boxes?
        # For now, just return False or implement global search later
        return False

    def replace_text(self, find_text, replace_text, case_sensitive, backward):
        """Replace current selection if it matches, then find next"""
        if self.active_text_box and self.active_text_box.textCursor().hasSelection():
            cursor = self.active_text_box.textCursor()
            selected = cursor.selectedText()
            
            # Verify selection matches find_text (handling case)
            match = selected == find_text if case_sensitive else selected.lower() == find_text.lower()
            
            if match:
                cursor.insertText(replace_text)
                return True
        
        return False

    def replace_all_text(self, find_text, replace_text, case_sensitive):
        """Replace all occurrences in all text boxes"""
        count = 0
        flags = QTextCursor.FindFlag(0)
        if case_sensitive:
            flags |= QTextCursor.FindFlag.FindCaseSensitively
            
        for item in self.scene.items():
            if isinstance(item, TextBox):
                # Move cursor to start
                cursor = item.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                item.setTextCursor(cursor)
                
                while item.find(find_text, flags):
                    cursor = item.textCursor()
                    cursor.insertText(replace_text)
                    count += 1
        return count

    def mouseMoveEvent(self, event):
        """Handle mouse move for shape resizing during creation"""
        if self.temp_item and self.shape_start_pos:
            scene_pos = self.mapToScene(event.pos())
            
            # Calculate size relative to start position
            width = abs(scene_pos.x() - self.shape_start_pos.x())
            height = abs(scene_pos.y() - self.shape_start_pos.y())
            
            # Determine top-left (though we use setPos for origin, we might need to adjust pos if dragging up/left)
            # For simplicity, let's keep pos at start_pos and just grow right/down, 
            # OR allow dragging in any direction by adjusting pos and rect.
            
            x = min(scene_pos.x(), self.shape_start_pos.x())
            y = min(scene_pos.y(), self.shape_start_pos.y())
            
            if isinstance(self.temp_item, ResizableRectItem):
                self.temp_item.setPos(x, y)
                self.temp_item.setRect(0, 0, width, height)
                self.temp_item.update_handles()

            elif isinstance(self.temp_item, ResizableEllipseItem):
                self.temp_item.setPos(x, y)
                self.temp_item.setRect(0, 0, width, height)
                self.temp_item.update_handles()

            elif isinstance(self.temp_item, ResizableLineItem):
                # Line uses local coords relative to pos
                self.temp_item.setPos(self.shape_start_pos)
                self.temp_item.setLine(0, 0, scene_pos.x() - self.shape_start_pos.x(), scene_pos.y() - self.shape_start_pos.y())

            elif isinstance(self.temp_item, PolygonItem):
                # Recreate polygon with new size
                # from src.engine.shape_items import PolygonItem
                
                # Use stored sides or default
                sides_str = getattr(self, 'polygon_sides', "3")
                
                radius = max(width, height) / 2
                center_x = width / 2
                center_y = height / 2
                
                points = []
                if sides_str == "Star":
                    points = PolygonItem.create_star(center_x, center_y, radius, radius/2, 5)
                else:
                    sides = int(sides_str)
                    if sides == 3:
                        points = PolygonItem.create_triangle(center_x, center_y, radius*2)
                    elif sides == 4:
                        points = [
                            QPointF(0, 0), QPointF(width, 0),
                            QPointF(width, height), QPointF(0, height)
                        ]
                    else:
                        # Regular polygon
                        for i in range(sides):
                            angle = math.radians(i * (360/sides) - 90)
                            px = center_x + radius * math.cos(angle)
                            py = center_y + radius * math.sin(angle)
                            points.append(QPointF(px, py))
                
                self.temp_item.setPos(x, y)
                self.temp_item.setPolygon(QPolygonF(points))
                self.temp_item.update_handles()

            elif isinstance(self.temp_item, str) and self.temp_item in ["rect_text", "title_text"]:
                # Show preview rectangle for text box creation
                pass  # Could add visual feedback here

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to finalize shape creation"""
        if self.temp_item and event.button() == Qt.MouseButton.LeftButton:
            scene_pos = self.mapToScene(event.pos())

            if isinstance(self.temp_item, str) and self.temp_item in ["rect_text", "title_text"]:
                # Create text box with dragged size
                width = abs(scene_pos.x() - self.shape_start_pos.x())
                height = abs(scene_pos.y() - self.shape_start_pos.y())

                # Minimum size
                width = max(width, 50)
                height = max(height, 30)

                # Use start position as top-left (or min of start/end)
                x = min(self.shape_start_pos.x(), scene_pos.x())
                y = min(self.shape_start_pos.y(), scene_pos.y())

                if self.temp_item == "rect_text":
                    tb = self.add_text_box(x, y, width=width, height=height, locked=False)
                    # Select the text box
                    self.scene.clearSelection()
                    tb.setSelected(True)
                elif self.temp_item == "title_text":
                    tb = self.add_text_box(x, y, width=width, height=max(height, 60), locked=False)
                    # Select the text box
                    self.scene.clearSelection()
                    tb.setSelected(True)

                self.save_state()

            elif isinstance(self.temp_item, (ResizableRectItem, ResizableEllipseItem, ResizableLineItem, PolygonItem)):
                # Finalize the shape and select it so handles show
                self.scene.clearSelection()
                self.temp_item.setSelected(True)
                self.save_state()

            self.temp_item = None
            self.shape_start_pos = None

            # Reset to selection tool after creating a shape/text box
            if self.current_tool in ["rect", "round_rect", "ellipse", "line", "polygon", "rect_text", "title_text"]:
                self.set_tool("ptr")

            event.accept()
            return

        super().mouseReleaseEvent(event)

    def set_shape_width(self, width):
        """Set width for selected shape"""
        for item in self.scene.selectedItems():
            if hasattr(item, 'setRect'):
                rect = item.rect()
                item.setRect(rect.x(), rect.y(), width, rect.height())
                item.update_handles()

    def set_shape_height(self, height):
        """Set height for selected shape"""
        for item in self.scene.selectedItems():
            if hasattr(item, 'setRect'):
                rect = item.rect()
                item.setRect(rect.x(), rect.y(), rect.width(), height)
                item.update_handles()

    def set_border_width(self, width):
        """Set border width for selected shape"""
        for item in self.scene.selectedItems():
            if hasattr(item, 'setPen'):
                pen = item.pen()
                pen.setWidth(width)
                item.setPen(pen)

    def set_border_color(self, color):
        """Set border color for selected shape"""
        for item in self.scene.selectedItems():
            if hasattr(item, 'setPen'):
                pen = item.pen()
                pen.setColor(color)
                item.setPen(pen)

    def set_border_style(self, style):
        """Set border style for selected shape"""
        style_map = {
            "Solid": Qt.PenStyle.SolidLine,
            "Dashed": Qt.PenStyle.DashLine,
            "Dotted": Qt.PenStyle.DotLine,
            "None": Qt.PenStyle.NoPen
        }
        for item in self.scene.selectedItems():
            if hasattr(item, 'setPen'):
                pen = item.pen()
                pen.setStyle(style_map.get(style, Qt.PenStyle.SolidLine))
                item.setPen(pen)

    def set_rotation(self, angle):
        """Set rotation angle for selected shape"""
        for item in self.scene.selectedItems():
            item.setRotation(angle)

    def set_polygon_sides(self, sides):
        """Set polygon sides for future polygon creation"""
        self.polygon_sides = sides
