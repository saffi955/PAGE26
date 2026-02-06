from PyQt6.QtWidgets import (QMainWindow, QMdiArea, QStatusBar, QLabel, QPushButton, 
                             QMessageBox, QFileDialog, QDockWidget, QToolBar, 
                             QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QFontComboBox, 
                             QSpinBox, QDoubleSpinBox, QToolButton, QFrame, QButtonGroup, 
                             QApplication, QGraphicsView, QColorDialog, QSlider)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QIcon, QKeySequence, QActionGroup, QFont, QAction
from src.ui.dialogs.new_document_dialog import NewDocumentDialog
from src.ui.document_window import DocumentWindow
from src.ui.dialogs.character_dialog import CharacterDialog
from src.ui.dialogs.paragraph_dialog import ParagraphDialog
from src.ui.dialogs.character_dialog import CharacterDialog
from src.ui.dialogs.paragraph_dialog import ParagraphDialog
from src.ui.dialogs.find_replace_dialog import FindReplaceDialog
import qtawesome as qta

class MainWindow(QMainWindow):
    def __init__(self, default_font, font_families):
        super().__init__()
        self.default_font = default_font
        self.font_families = font_families
        self.setWindowTitle("page26 - Modern Urdu DTP")
        self.resize(1200, 800)
        self.showMaximized()

        # recent files
        self.recent_files = []
        self.max_recent_files = 5
        
        # Load recent files from settings
        self.load_recent_files()
        
        self.current_lang = 'UR'
        
        self.init_ui()
        
    def init_ui(self):
        # Central Widget (MDI Area)
        self.mdi_area = QMdiArea()
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdi_area)
        
        # 0. Menu Bar
        self.create_menu()

        # 1. Toolbox (Left)
        self.create_toolbox()
        
        # 3. Property Ribbon (Top) - Implemented as a Toolbar for now
        self.create_ribbon()
        
        # 4. Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setMaximumHeight(24)  # Smaller height
        self.setStatusBar(self.status_bar)
        # Don't show message - it hides widgets
        
        # Page Navigation (LEFT SIDE)
        self.page_label = QLabel(" Page 1/1 ")
        self.status_bar.addWidget(self.page_label)
        
        # Create navigation buttons and save as instance variables
        self.btn_first = QPushButton("<<")
        self.btn_prev = QPushButton("<")
        self.btn_next = QPushButton(">")
        self.btn_last = QPushButton(">>")
        self.btn_add = QPushButton("+")
        
        self.btn_first.clicked.connect(self.first_page)
        self.btn_prev.clicked.connect(self.prev_page)
        self.btn_next.clicked.connect(self.next_page)
        self.btn_last.clicked.connect(self.last_page)
        self.btn_add.clicked.connect(self.add_page)
        
        
        # Style page navigation buttons - make them more visible
        nav_style = """
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 2px;
                color: #333;
                font-size: 11px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
                border: 1px solid #999;
            }
            QPushButton:pressed {
                background-color: #e0e0e0;
            }
        """
        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last, self.btn_add]:
            btn.setFixedSize(26, 22)  # Slightly larger
            btn.setStyleSheet(nav_style)
        
        for btn in [self.btn_first, self.btn_prev, self.btn_next, self.btn_last, self.btn_add]:
            self.status_bar.addWidget(btn)
        
        # Add spacer after page nav
        spacer = QLabel("  ")
        self.status_bar.addWidget(spacer)
        
        # Ruler Unit Selector - REMOVED as per user request (rely on menu)
        
        # Add larger spacer
        spacer2 = QLabel("    ")
        self.status_bar.addWidget(spacer2)
        
        # Word Count Label
        self.word_count_label = QLabel(" Words: 0 ")
        self.status_bar.addWidget(self.word_count_label)
        
        # Zoom Controls (RIGHT SIDE)
        zoom_label = QLabel(" Zoom: ")
        self.status_bar.addPermanentWidget(zoom_label)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 400)
        self.zoom_slider.setValue(100)
        self.zoom_slider.setFixedWidth(100)
        self.zoom_slider.setStyleSheet("QSlider::handle:horizontal { background-color: #999; }")
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        self.status_bar.addPermanentWidget(self.zoom_slider)
        
        self.zoom_value_label = QLabel(" 100% ")
        self.status_bar.addPermanentWidget(self.zoom_value_label)
        
        # Language Toggle (RIGHT SIDE)
        self.lang_button = QLabel(" URDU ")
        self.lang_button.setStyleSheet("background-color: #ddd; padding: 2px 5px; border-radius: 3px; font-weight: bold;")
        self.lang_button.mousePressEvent = self.toggle_language
        self.status_bar.addPermanentWidget(self.lang_button)
        
        self.current_lang = 'UR'
        
        # Connect MDI subwindow activation to update UI
        self.mdi_area.subWindowActivated.connect(self.update_ui_from_active_window)

    def get_active_document_view(self):
        active_sub = self.mdi_area.activeSubWindow()
        if active_sub and isinstance(active_sub, DocumentWindow):
            return active_sub.document_view
        return None

    def update_ui_from_active_window(self, window):
        if window and isinstance(window, DocumentWindow):
            # Update zoom slider
            self.zoom_slider.blockSignals(True)
            self.zoom_slider.setValue(int(window.document_view.zoom_level * 100))
            self.zoom_slider.blockSignals(False)
            self.zoom_value_label.setText(f" {int(window.document_view.zoom_level * 100)}% ")
            
            # Update page label
            self.update_page_label()
            
            # Update word count
            self.update_word_count()
            
            # Connect to selection changes if not already connected
            # We need a way to know when selection changes in the active view
            # For now, we'll update on window activation and maybe add a timer or signal later
            try:
                # Disconnect first to avoid duplicates if possible, or check connection
                # Ideally DocumentView should have a signal 'selectionChanged'
                # Let's assume we can connect to the scene's selectionChanged
                window.document_view.scene.selectionChanged.connect(self.update_word_count)
            except:
                pass
            
            # Update language state if needed (though it's global for now)
            # window.document_view.set_language(self.current_lang)
            
        self.update_menus_state()

    def on_zoom_changed(self, value):
        doc_view = self.get_active_document_view()
        if doc_view:
            zoom_factor = value / 100.0
            doc_view.set_zoom(zoom_factor)
            self.zoom_value_label.setText(f" {value}% ")
    
    def update_page_label(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            current = doc_view.page_manager.current_page_index + 1
            total = doc_view.page_manager.page_count()
            self.page_label.setText(f" Page {current}/{total} ")
        else:
            self.page_label.setText(" Page 0/0 ")

    def update_word_count(self):
        doc_view = self.get_active_document_view()
        if not doc_view:
            self.word_count_label.setText(" Words: 0 ")
            return

        word_count = 0
        is_selection = False
        
        # Check for selected text boxes
        selected_items = doc_view.scene.selectedItems()
        from src.engine.text_box import TextBox
        
        # If text is selected within a text box (requires access to text cursor)
        # This is tricky without direct access to the active text cursor
        # But we can check if any text box has focus and selection
        
        focus_item = doc_view.scene.focusItem()
        if isinstance(focus_item, TextBox) and focus_item.textCursor().hasSelection():
            # Count words in selection
            text = focus_item.textCursor().selectedText()
            # Simple split by whitespace
            words = text.split()
            word_count = len(words)
            is_selection = True
        else:
            # Count words in all text boxes on current page
            # We need to iterate items on the current page
            # Assuming doc_view.page_manager.get_current_page_items() exists or we iterate scene items
            # For now, iterate scene items and check if they are TextBoxes
            for item in doc_view.scene.items():
                if isinstance(item, TextBox):
                    text = item.toPlainText()
                    words = text.split()
                    word_count += len(words)
        
        prefix = "Selected Words:" if is_selection else "Words:"
        self.word_count_label.setText(f" {prefix} {word_count} ")

    def new_document(self):
        # Show New Document Dialog
        dialog = NewDocumentDialog(self)
        if dialog.exec():
            settings = dialog.get_settings()
            
            # Create new document window with settings
            sub = DocumentWindow(self.default_font, self.font_families, page_settings=settings)
            self.mdi_area.addSubWindow(sub)
            sub.showMaximized()  # Maximize the window
            
            # Apply current language setting
            sub.document_view.set_language(self.current_lang)

    def create_menu(self):
        menu_bar = self.menuBar()
        
        # File Menu
        self.file_menu = menu_bar.addMenu("&File")
        
        self.action_new = QAction("&New...", self)
        self.action_new.setShortcut("Ctrl+N")
        self.action_open = QAction("&Open...", self)
        self.action_open.setShortcut("Ctrl+O")
        self.action_close = QAction("&Close", self)
        self.action_close.setShortcut("Ctrl+W")
        self.action_save = QAction("&Save", self)
        self.action_save.setShortcut("Ctrl+S")
        self.action_save_as = QAction("Save &As...", self)
        self.action_save_as.setShortcut("Ctrl+Shift+S")
        self.action_revert = QAction("&Revert", self)
        self.action_import = QAction("&Import...", self)
        self.action_import.setShortcut("Ctrl+I")
        self.action_export = QAction("&Export...", self)
        self.action_export.setShortcut("Ctrl+E")
        self.action_place = QAction("&Place...", self)
        self.action_place.setShortcut("Ctrl+P")
        self.action_print = QAction("&Print...", self)
        self.action_print.setShortcut("Ctrl+P")
        self.action_printer_setup = QAction("Printer &Setup...", self)
        self.action_exit = QAction("E&xit", self)
        self.action_exit.setShortcut("Alt+F4")
        
        # Recent files submenu
        self.recent_menu = self.file_menu.addMenu("&Recent files")
        
        # Connect actions
        self.action_new.triggered.connect(self.new_document)
        self.action_open.triggered.connect(self.open_document)
        self.action_close.triggered.connect(self.close_document)
        self.action_save.triggered.connect(self.save_document)
        self.action_save_as.triggered.connect(self.save_document_as)
        self.action_revert.triggered.connect(self.revert_document)
        self.action_import.triggered.connect(self.import_document)
        self.action_export.triggered.connect(self.export_document)
        self.action_place.triggered.connect(self.place_content)
        self.action_print.triggered.connect(self.print_document)
        self.action_printer_setup.triggered.connect(self.printer_setup)
        self.action_exit.triggered.connect(self.close)
        
        # Add to menu
        self.file_menu.addAction(self.action_new)
        self.file_menu.addAction(self.action_open)
        self.file_menu.addAction(self.action_close)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_save)
        self.file_menu.addAction(self.action_save_as)
        self.file_menu.addAction(self.action_revert)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_import)
        self.file_menu.addAction(self.action_export)
        self.file_menu.addAction(self.action_place)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_print)
        self.file_menu.addAction(self.action_printer_setup)
        self.file_menu.addSeparator()
        self.file_menu.addMenu(self.recent_menu)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.action_exit)
        
        # Create other menus
        self.create_edit_menu(menu_bar)
        self.create_view_menu(menu_bar)
        self.create_insert_menu(menu_bar)
        self.create_format_menu(menu_bar)
        self.create_symbols_menu(menu_bar)
        self.create_utilities_menu(menu_bar)
        self.create_language_menu(menu_bar)
        self.create_window_menu(menu_bar)
        self.create_help_menu(menu_bar)
        
        self.update_menus_state()

    def create_edit_menu(self, menu_bar):
        self.edit_menu = menu_bar.addMenu("&Edit")
        
        self.action_undo = QAction("&Undo the last action", self)
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_cut = QAction("Cu&t", self)
        self.action_cut.setShortcut("Ctrl+X")
        self.action_copy = QAction("&Copy", self)
        self.action_copy.setShortcut("Ctrl+C")
        self.action_paste = QAction("&Paste", self)
        self.action_paste.setShortcut("Ctrl+V")
        self.action_duplicate = QAction("&Duplicate", self)
        self.action_duplicate.setShortcut("Ctrl+D")
        self.action_clear = QAction("&Clear", self)
        self.action_clear.setShortcut("Del")
        self.action_select_all = QAction("Select &All", self)
        self.action_select_all.setShortcut("Ctrl+A")
        self.action_find_replace = QAction("Find and &Replace...", self)
        self.action_find_replace.setShortcut("Ctrl+F")
        
        self.action_top_most = QAction("&Top Most", self)
        self.action_bring_front = QAction("&Bring to Front", self)
        self.action_bring_front.setShortcut("F2")
        self.action_send_back = QAction("&Send to Back", self)
        self.action_send_back.setShortcut("Alt+F2")
        self.action_lock_guides = QAction("&Lock Guides", self)
        self.action_lock_guides.setShortcut("F3")
        self.action_story_editor = QAction("&Story Editor", self)
        self.action_story_editor.setShortcut("Ctrl+Y")
        self.action_delete_page = QAction("&Delete Page", self)
        self.action_delete_page.setShortcut("Alt+Del")
        
        # Preferences submenu
        self.prefs_menu = self.edit_menu.addMenu("&Preferences")
        self.action_app_prefs = QAction("&Application...", self)
        self.action_app_prefs.setShortcut("Alt+F11")
        self.action_doc_prefs = QAction("&Document...", self)
        self.action_doc_prefs.setShortcut("Ctrl+F11")
        self.action_type_prefs = QAction("&Typographic...", self)
        self.action_type_prefs.setShortcut("F11")
        self.action_kb_prefs = QAction("&Keyboard Preferences...", self)
        
        # Connect actions
        self.action_undo.triggered.connect(self.undo)
        self.action_cut.triggered.connect(self.cut)
        self.action_copy.triggered.connect(self.copy)
        self.action_paste.triggered.connect(self.paste)
        self.action_duplicate.triggered.connect(self.duplicate)
        self.action_clear.triggered.connect(self.clear)
        self.action_select_all.triggered.connect(self.select_all)
        self.action_find_replace.triggered.connect(self.find_replace)
        self.action_top_most.triggered.connect(self.top_most)
        self.action_bring_front.triggered.connect(self.bring_front)
        self.action_send_back.triggered.connect(self.send_back)
        self.action_lock_guides.triggered.connect(self.lock_guides)
        self.action_story_editor.triggered.connect(self.story_editor)
        self.action_delete_page.triggered.connect(self.delete_page)
        self.action_app_prefs.triggered.connect(self.app_preferences)
        self.action_doc_prefs.triggered.connect(self.doc_preferences)
        self.action_type_prefs.triggered.connect(self.type_preferences)
        self.action_kb_prefs.triggered.connect(self.kb_preferences)
        
        # Add to menu
        self.edit_menu.addAction(self.action_undo)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_cut)
        self.edit_menu.addAction(self.action_copy)
        self.edit_menu.addAction(self.action_paste)
        self.edit_menu.addAction(self.action_duplicate)
        self.edit_menu.addAction(self.action_clear)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_select_all)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_find_replace)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.action_top_most)
        self.edit_menu.addAction(self.action_bring_front)
        self.edit_menu.addAction(self.action_send_back)
        self.edit_menu.addAction(self.action_lock_guides)
        self.edit_menu.addAction(self.action_story_editor)
        self.edit_menu.addAction(self.action_delete_page)
        self.edit_menu.addSeparator()
        self.edit_menu.addMenu(self.prefs_menu)
        
        # Add preferences submenu items
        self.prefs_menu.addAction(self.action_app_prefs)
        self.prefs_menu.addAction(self.action_doc_prefs)
        self.prefs_menu.addAction(self.action_type_prefs)
        self.prefs_menu.addAction(self.action_kb_prefs)

    def create_view_menu(self, menu_bar):
        self.view_menu = menu_bar.addMenu("&View")
        
        # Zoom Shortcuts - F5-F8
        self.action_fit_window = QAction("Fit in &Window", self)
        self.action_fit_window.setShortcut("F5")
        self.action_fit_window.triggered.connect(lambda: self.set_zoom_level(30))
        
        self.action_zoom_50 = QAction("&50%", self)
        self.action_zoom_50.setShortcut("F6")
        self.action_zoom_50.triggered.connect(lambda: self.set_zoom_level(50))
        
        self.action_actual_size = QAction("&Actual", self)
        self.action_actual_size.setShortcut("F7")
        self.action_actual_size.triggered.connect(lambda: self.set_zoom_level(100))
        
        self.action_zoom_200 = QAction("&200%", self)
        self.action_zoom_200.setShortcut("F8")
        self.action_zoom_200.triggered.connect(lambda: self.set_zoom_level(200))
        
        # Font Size Shortcuts - Ctrl+F9/F10
        self.action_inc_font = QAction("Increase Font Size", self)
        self.action_inc_font.setShortcut("Ctrl+F10")
        self.action_inc_font.triggered.connect(self.increase_font_size)
        
        self.action_dec_font = QAction("Decrease Font Size", self)
        self.action_dec_font.setShortcut("Ctrl+F9")
        self.action_dec_font.triggered.connect(self.decrease_font_size)
        
        # Add shortcuts to window so they work globally
        self.addAction(self.action_fit_window)
        self.addAction(self.action_zoom_50)
        self.addAction(self.action_actual_size)
        self.addAction(self.action_zoom_200)
        self.addAction(self.action_inc_font)
        self.addAction(self.action_dec_font)
        self.action_facing_pages = QAction("&Facing Pages", self, checkable=True)
        self.action_hide_ribbon = QAction("Hide &Ribbon", self, checkable=True)
        self.action_hide_tools = QAction("Hide &Tools", self, checkable=True)
        self.action_hide_rulers = QAction("Hide &Rulers", self, checkable=True)
        self.action_hide_guides = QAction("Hide &Guides", self, checkable=True)
        self.action_show_invisibles = QAction("Show &Invisibles", self, checkable=True)
        self.action_snap_guides = QAction("Snap to &Guides", self, checkable=True)
        self.action_snap_guides.setShortcut("F9")
        
        # Connect actions
        self.action_facing_pages.toggled.connect(self.toggle_facing_pages)
        self.action_hide_ribbon.toggled.connect(self.toggle_ribbon)
        self.action_hide_tools.toggled.connect(self.toggle_tools)
        self.action_hide_rulers.toggled.connect(self.toggle_rulers)
        self.action_hide_guides.toggled.connect(self.toggle_guides)
        self.action_show_invisibles.toggled.connect(self.toggle_invisibles)
        self.action_snap_guides.toggled.connect(self.toggle_snap_guides)
        
        # Add to menu
        self.view_menu.addAction(self.action_fit_window)
        self.view_menu.addAction(self.action_zoom_50)
        self.view_menu.addAction(self.action_actual_size)
        self.view_menu.addAction(self.action_zoom_200)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.action_facing_pages)
        self.view_menu.addSeparator()
        self.view_menu.addAction(self.action_hide_ribbon)
        self.view_menu.addAction(self.action_hide_tools)
        self.view_menu.addAction(self.action_hide_rulers)
        self.view_menu.addAction(self.action_hide_guides)
        self.view_menu.addAction(self.action_show_invisibles)
        self.view_menu.addAction(self.action_snap_guides)

    def create_insert_menu(self, menu_bar):
        self.insert_menu = menu_bar.addMenu("&Insert")
        
        self.action_page = QAction("&Page", self)
        self.action_text_box = QAction("&Text Box", self)
        self.action_picture = QAction("&Picture", self)
        self.action_symbol = QAction("&Symbol", self)
        self.action_table = QAction("&Table", self)
        
        # Connect actions
        self.action_page.triggered.connect(self.insert_page)
        self.action_text_box.triggered.connect(self.insert_text_box)
        self.action_picture.triggered.connect(self.insert_picture)
        self.action_symbol.triggered.connect(self.show_symbol_gallery)
        self.action_table.triggered.connect(self.insert_table)
        
        # Add to menu
        self.insert_menu.addAction(self.action_page)
        self.insert_menu.addAction(self.action_text_box)
        self.insert_menu.addAction(self.action_picture)
        self.insert_menu.addAction(self.action_symbol)
        self.insert_menu.addAction(self.action_table)

    def create_format_menu(self, menu_bar):
        self.format_menu = menu_bar.addMenu("&Format")
        
        self.action_character = QAction("&Character...", self)
        self.action_paragraph = QAction("&Paragraph...", self)
        self.action_hyphenation = QAction("&Hyphenation...", self)
        self.action_borders = QAction("&Borders...", self)
        self.action_page_setup = QAction("&Page Setup...", self)
        self.action_guides = QAction("&Guides...", self)
        self.action_style_sheets = QAction("&Style Sheets...", self)
        self.action_colors = QAction("&Colors...", self)
        
        # Connect actions
        self.action_character.triggered.connect(self.show_character_dialog)
        self.action_paragraph.triggered.connect(self.show_paragraph_dialog)
        self.action_hyphenation.triggered.connect(self.show_hyphenation_dialog)
        self.action_borders.triggered.connect(self.show_borders_dialog)
        self.action_page_setup.triggered.connect(self.show_page_setup_dialog)
        self.action_guides.triggered.connect(self.show_guides_dialog)
        self.action_style_sheets.triggered.connect(self.show_style_sheets_dialog)
        self.action_colors.triggered.connect(self.show_colors_dialog)
        
        # Add to menu
        self.format_menu.addAction(self.action_character)
        self.format_menu.addAction(self.action_paragraph)
        self.format_menu.addAction(self.action_hyphenation)
        self.format_menu.addAction(self.action_borders)
        self.format_menu.addAction(self.action_page_setup)
        self.format_menu.addAction(self.action_guides)
        self.format_menu.addAction(self.action_style_sheets)
        self.format_menu.addAction(self.action_colors)

    def delete_selected(self):
        doc_view = self.get_active_document_view()
        if doc_view and hasattr(doc_view, 'delete_selected'):
            doc_view.delete_selected()

    def create_symbols_menu(self, menu_bar):
        self.symbols_menu = menu_bar.addMenu("&Symbols")
        
        # Add symbol items with shortcuts
        symbols = [
            ("(", "Alt+="),
            (")", "Alt+-"),
            ("×", "Alt+*"),
            ("÷", "Alt+/"),
            ("•", "Alt+7"),
            ("/", "Alt+8"),
            ("~", "Alt+9"),
            ("^", "Alt+0")
        ]
        
        for symbol, shortcut in symbols:
            action = QAction(symbol, self)
            action.setShortcut(shortcut)
            action.triggered.connect(lambda checked, s=symbol: self.insert_symbol(s))
            self.symbols_menu.addAction(action)

    def create_utilities_menu(self, menu_bar):
        self.utilities_menu = menu_bar.addMenu("&Utilities")
        
        self.action_spelling = QAction("&Spelling", self)
        self.action_word_count = QAction("&Word Count", self)
        self.action_group = QAction("&Group", self)
        self.action_ungroup = QAction("&Ungroup", self)
        self.action_auto_index = QAction("&Auto Index", self)
        self.action_generate_index = QAction("&Generate Index", self)
        self.action_table_of_contents = QAction("Table of &Contents", self)
        self.action_edit_links = QAction("&Edit Links", self)
        
        # Connect actions
        self.action_spelling.triggered.connect(self.check_spelling)
        self.action_word_count.triggered.connect(self.show_word_count)
        self.action_group.triggered.connect(self.group_objects)
        self.action_ungroup.triggered.connect(self.ungroup_objects)
        self.action_auto_index.triggered.connect(self.auto_index)
        self.action_generate_index.triggered.connect(self.generate_index)
        self.action_table_of_contents.triggered.connect(lambda: self.statusBar().showMessage("Table of Contents - Not implemented yet"))
        self.action_edit_links.triggered.connect(self.edit_links)
        
        self.utilities_menu.addAction(self.action_spelling)
        self.utilities_menu.addAction(self.action_word_count)
        self.utilities_menu.addSeparator()
        self.utilities_menu.addAction(self.action_group)
        self.utilities_menu.addAction(self.action_ungroup)
        self.utilities_menu.addSeparator()
        self.utilities_menu.addAction(self.action_auto_index)
        self.utilities_menu.addAction(self.action_generate_index)
        self.utilities_menu.addAction(self.action_table_of_contents)
        self.utilities_menu.addAction(self.action_edit_links)

    def create_language_menu(self, menu_bar):
        self.language_menu = menu_bar.addMenu("&Language")
        
        self.action_toggle_urdu = QAction("Toggle &Urdu/English", self)
        self.action_toggle_urdu.setShortcut("Ctrl+Space")
        self.action_keyboard_prefs = QAction("&Keyboard Preferences...", self)
        
        self.action_toggle_urdu.triggered.connect(self.toggle_language_keyboard)
        self.action_keyboard_prefs.triggered.connect(self.show_keyboard_preferences)
        
        self.language_menu.addAction(self.action_toggle_urdu)
        self.language_menu.addAction(self.action_keyboard_prefs)

    def create_window_menu(self, menu_bar):
        self.window_menu = menu_bar.addMenu("&Window")
        
        self.action_cascade = QAction("&Cascade", self)
        self.action_tile = QAction("&Tile", self)
        self.action_close_all = QAction("Close &All", self)
        self.action_close_all.setShortcut("F12")
        self.action_window_page = QAction("&Page", self)
        self.action_window_page.setShortcut("Ctrl+F12")
        
        # Connect actions
        self.action_cascade.triggered.connect(self.cascade_windows)
        self.action_tile.triggered.connect(self.tile_windows)
        self.action_close_all.triggered.connect(self.close_all_windows)
        self.action_window_page.triggered.connect(self.show_page_window)
        
        self.window_menu.addAction(self.action_cascade)
        self.window_menu.addAction(self.action_tile)
        self.window_menu.addAction(self.action_close_all)
        self.window_menu.addAction(self.action_window_page)
        
        # Will be populated with open windows
        self.windows_menu = self.window_menu

    def create_help_menu(self, menu_bar):
        self.help_menu = menu_bar.addMenu("&Help")
        
        self.action_contents = QAction("&Contents", self)
        self.action_index = QAction("&Index", self)
        self.action_using_help = QAction("&Using help...", self)
        self.action_about = QAction("&About", self)
        
        self.action_contents.triggered.connect(self.show_help_contents)
        self.action_index.triggered.connect(self.show_help_index)
        self.action_using_help.triggered.connect(self.show_using_help)
        self.action_about.triggered.connect(self.show_about)
        
        self.help_menu.addAction(self.action_contents)
        self.help_menu.addAction(self.action_index)
        self.help_menu.addAction(self.action_using_help)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.action_about)

    def update_menus_state(self):
        """Enable/Disable menus based on document state"""
        has_doc = self.get_active_document_view() is not None
        
        # File Menu items
        self.action_close.setEnabled(has_doc)
        self.action_save.setEnabled(has_doc)
        self.action_save_as.setEnabled(has_doc)
        self.action_revert.setEnabled(has_doc)
        self.action_import.setEnabled(has_doc)
        self.action_export.setEnabled(has_doc)
        self.action_place.setEnabled(has_doc)
        self.action_print.setEnabled(has_doc)
        self.action_printer_setup.setEnabled(True) # Always enabled?
        
        # Edit Menu - Entire menu logic
        # InPage moves Preferences to top level when no doc, but here we'll just enable/disable
        # or hide/show the main Edit menu items.
        
        # If we want to strictly follow "Edit [only when document open]", we can disable the whole menu
        # BUT Preferences is inside Edit.
        # User said: "Preferences [only when no document open; moves under Edit when document open]"
        # This is complex to implement exactly with standard QMenuBar without removing/adding menus.
        # A simpler approach:
        # 1. Always show Edit menu.
        # 2. If no doc: Disable all except Preferences (if it was there).
        # But Preferences is a submenu.
        
        # Let's try to toggle visibility of the menus themselves
        self.edit_menu.menuAction().setVisible(has_doc)
        self.view_menu.menuAction().setVisible(has_doc)
        self.insert_menu.menuAction().setVisible(has_doc)
        self.format_menu.menuAction().setVisible(has_doc)
        self.symbols_menu.menuAction().setVisible(has_doc)
        self.utilities_menu.menuAction().setVisible(has_doc)
        self.language_menu.menuAction().setVisible(has_doc)
        self.window_menu.menuAction().setVisible(has_doc)
        
        # Handle Preferences
        # If has_doc is False, we need a top-level Preferences menu.
        # If has_doc is True, Preferences is under Edit.
        
        if not hasattr(self, 'top_prefs_menu'):
            self.create_top_level_prefs_menu()
            
        self.top_prefs_menu.menuAction().setVisible(not has_doc)
        
    def create_top_level_prefs_menu(self):
        self.top_prefs_menu = self.menuBar().addMenu("&Preferences")
        self.top_prefs_menu.addAction(self.action_app_prefs)
        self.top_prefs_menu.addAction(self.action_doc_prefs)
        self.top_prefs_menu.addAction(self.action_type_prefs)
        self.top_prefs_menu.addAction(self.action_kb_prefs)
        
        # Position it correctly (e.g., after File or Edit)
        # QMenuBar doesn't easily support inserting at specific index without clear action reference
        # But addMenu adds to the end.
        # We might need to clear and recreate menu bar to get exact order, or just accept it at the end.
        # Or use insertMenu if we have the action of the next menu.
        # For now, let's just add it. It will appear at the end or we can try to insert it.
        
        # To insert before Help (which is usually last)
        # self.menuBar().insertMenu(self.help_menu.menuAction(), self.top_prefs_menu)
        pass

    def open_document(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Document", "", "page26 Files (*.upg);;All Files (*)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Create new window
                    sub = DocumentWindow(self.default_font, self.font_families)
                    self.mdi_area.addSubWindow(sub)
                    sub.show()
                    
                    # Set content
                    sub.document_view.set_content(content)
                    sub.setWindowTitle(file_path)
                    
                self.statusBar().showMessage(f"Opened: {file_path}")
            except Exception as e:
                self.statusBar().showMessage(f"Error opening file: {str(e)}")

    def save_document(self):
        """Save current document"""
        window = self.get_active_document_window()
        if not window:
            return
            
        # If document already has a path, save directly
        if hasattr(window, 'file_path') and window.file_path:
            try:
                content = window.document_view.get_content()
                with open(window.file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.statusBar().showMessage(f"Saved: {window.file_path}")
            except Exception as e:
                self.statusBar().showMessage(f"Error saving: {str(e)}")
        else:
            self.save_document_as()

    def save_document_as(self):
        doc_view = self.get_active_document_view()
        if not doc_view:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Document", "", "page26 Files (*.upg)")
        if file_path:
            self._save_to_path(file_path, doc_view)

    def _save_to_path(self, path, doc_view):
        try:
            content = doc_view.get_content()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.statusBar().showMessage(f"Saved: {path}")
        except Exception as e:
            self.statusBar().showMessage(f"Error saving file: {str(e)}")

    def export_pdf(self):
        doc_view = self.get_active_document_view()
        if not doc_view:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                doc_view.export_pdf(file_path)
                self.statusBar().showMessage(f"Exported PDF: {file_path}")
            except Exception as e:
                self.statusBar().showMessage(f"Error exporting PDF: {str(e)}")
    
    def load_recent_files(self):
        """Load recent files from settings"""
        # In a real app, load from QSettings or file
        self.recent_files = []  # Placeholder

    def update_recent_files(self, file_path):
        """Update recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        
        # Keep only max recent files
        if len(self.recent_files) > self.max_recent_files:
            self.recent_files = self.recent_files[:self.max_recent_files]
        
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Update recent files submenu"""
        # Clear existing recent files
        for action in self.recent_files_actions:
            self.file_menu.removeAction(action)
        
        self.recent_files_actions = []
        
        # Add recent files
        for file_path in self.recent_files:
            action = QAction(os.path.basename(file_path), self)
            action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
            self.recent_files_actions.append(action)
            self.file_menu.addAction(action)
            
    def toggle_language(self, event):
        if self.current_lang == 'UR':
            self.current_lang = 'EN'
            self.lang_button.setText(" ENG ")
        else:
            self.current_lang = 'UR' 
            self.lang_button.setText(" URDU ")
        
        # Update active document view language
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_language(self.current_lang)
            print(f"DEBUG: MainWindow language toggled to {self.current_lang}")
    
    def on_unit_changed(self, unit_text):
        """Handle ruler unit change"""
        # Map UI text to ruler unit names
        unit_map = {
            "Inches": "inches",
            "MM": "mm",
            "CM": "cm",
            "Feet": "feet",
            "Pixels": "pixels"
        }
        unit = unit_map.get(unit_text, "inches")
        
        # Update all document window rulers
        for window in self.mdi_area.subWindowList():
            if isinstance(window, DocumentWindow):
                window.h_ruler.set_unit(unit)
                window.v_ruler.set_unit(unit)

    def set_ruler_unit(self, unit_text):
        """Set ruler unit from menu"""
        # self.unit_combo.setCurrentText(unit_text) # Combo removed
        self.on_unit_changed(unit_text)




    def create_toolbox(self):
        self.toolbox = QToolBar("Tools")
        self.toolbox.setOrientation(Qt.Orientation.Vertical)
        self.toolbox.setMovable(False)
        self.toolbox.setIconSize(QSize(15, 15))  # Smaller icons
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbox)
        
        # Tool group for radio button behavior
        self.tool_group = QActionGroup(self)
        self.tool_group.setExclusive(True)
        
        # 1. Selection Tool (Arrow) - F2
        icon_sel = qta.icon('mdi.cursor-default-outline')
        self.action_sel = self.toolbox.addAction(icon_sel, "Selection")
        self.action_sel.setCheckable(True)
        self.action_sel.setShortcut("F2")
        self.tool_group.addAction(self.action_sel)
        
        # 2. Text Tool (I-beam) - F3
        icon_text = qta.icon('mdi.format-text')
        self.action_text = self.toolbox.addAction(icon_text, "Text")
        self.action_text.setCheckable(True)
        self.action_text.setShortcut("F3")
        self.tool_group.addAction(self.action_text)
        
        # 3. Rotate Tool - Shift+F3
        icon_rotate = qta.icon('mdi.rotate-right')
        self.action_rotate = self.toolbox.addAction(icon_rotate, "Rotate")
        self.action_rotate.setCheckable(True)
        self.action_rotate.setShortcut("Shift+F3")
        self.tool_group.addAction(self.action_rotate)
        
        # 4. Link Text Box Tool - F4
        icon_link = qta.icon('mdi.link-variant')
        self.action_link = self.toolbox.addAction(icon_link, "Link Text Boxes")
        self.action_link.setCheckable(True)
        self.action_link.setShortcut("F4")
        self.tool_group.addAction(self.action_link)
        
        # 5. Unlink Text Box Tool - Shift+F4
        icon_unlink = qta.icon('mdi.link-variant-off')
        self.action_unlink = self.toolbox.addAction(icon_unlink, "Unlink Text Boxes")
        self.action_unlink.setCheckable(True)
        self.action_unlink.setShortcut("Shift+F4")
        self.tool_group.addAction(self.action_unlink)
        
        self.toolbox.addSeparator()
        
        # 6. Rectangular Text Box - Ctrl+T
        icon_rect_text = qta.icon('mdi.rectangle-outline')
        self.action_rect_text = self.toolbox.addAction(icon_rect_text, "Rectangular Text Box")
        self.action_rect_text.setCheckable(True)
        self.action_rect_text.setShortcut("Ctrl+T")
        self.tool_group.addAction(self.action_rect_text)

        # 7. Title Text Box (flag) - Ctrl+Shift+T
        icon_title_text = qta.icon('mdi.flag-outline')
        self.action_title_text = self.toolbox.addAction(icon_title_text, "Title Text Box")
        self.action_title_text.setCheckable(True)
        self.action_title_text.setShortcut("Ctrl+Shift+T")
        self.tool_group.addAction(self.action_title_text)

        self.toolbox.addSeparator()

        # 8. Rectangular Shape Box - Ctrl+R
        icon_rect_graphic = qta.icon('mdi.square-outline')
        self.action_rect_graphic = self.toolbox.addAction(icon_rect_graphic, "Rectangular Shape Box")
        self.action_rect_graphic.setCheckable(True)
        self.action_rect_graphic.setShortcut("Ctrl+R")
        self.tool_group.addAction(self.action_rect_graphic)

        # 9. Round-Corner Shape Box - Ctrl+Shift+R
        icon_round_graphic = qta.icon('mdi.square-rounded-outline')
        self.action_round_graphic = self.toolbox.addAction(icon_round_graphic, "Round-Corner Shape Box")
        self.action_round_graphic.setCheckable(True)
        self.action_round_graphic.setShortcut("Ctrl+Shift+R")
        self.tool_group.addAction(self.action_round_graphic)

        # 10. Elliptical Shape Box - Ctrl+E
        icon_ellipse_graphic = qta.icon('mdi.circle-outline')
        self.action_ellipse_graphic = self.toolbox.addAction(icon_ellipse_graphic, "Elliptical Shape Box")
        self.action_ellipse_graphic.setCheckable(True)
        self.action_ellipse_graphic.setShortcut("Ctrl+E")
        self.tool_group.addAction(self.action_ellipse_graphic)

        self.toolbox.addSeparator()

        # 11. Line Tool - Ctrl+L
        icon_line = qta.icon('mdi.minus')
        self.action_line = self.toolbox.addAction(icon_line, "Line")
        self.action_line.setCheckable(True)
        self.action_line.setShortcut("Ctrl+L")
        self.tool_group.addAction(self.action_line)

        # 12. Polygon Tool - Ctrl+P
        icon_polygon = qta.icon('mdi.vector-polygon')
        self.action_polygon = self.toolbox.addAction(icon_polygon, "Polygon")
        self.action_polygon.setCheckable(True)
        self.action_polygon.setShortcut("Ctrl+P")
        self.tool_group.addAction(self.action_polygon)

        # 13. Hand Tool (panning) - Ctrl+H
        icon_hand = qta.icon('mdi.hand')
        self.action_hand = self.toolbox.addAction(icon_hand, "Hand")
        self.action_hand.setCheckable(True)
        self.action_hand.setShortcut("Ctrl+H")
        self.tool_group.addAction(self.action_hand)
        
        # Set default tool
        # Set default tool
        self.action_text.setChecked(True)
        
        # Connect actions to document view methods - FIXED: Use get_active_document_view
        self.action_sel.triggered.connect(lambda: self.set_tool_active("ptr"))
        self.action_text.triggered.connect(lambda: self.set_tool_active("text"))
        self.action_rotate.triggered.connect(lambda: self.set_tool_active("rotate"))
        self.action_link.triggered.connect(lambda: self.set_tool_active("link"))
        self.action_unlink.triggered.connect(lambda: self.set_tool_active("unlink"))
        self.action_rect_text.triggered.connect(lambda: self.set_tool_active("rect_text"))
        self.action_title_text.triggered.connect(lambda: self.set_tool_active("title_text"))
        self.action_rect_graphic.triggered.connect(lambda: self.set_tool_active("rect"))
        self.action_round_graphic.triggered.connect(lambda: self.set_tool_active("round_rect"))
        self.action_ellipse_graphic.triggered.connect(lambda: self.set_tool_active("ellipse"))
        self.action_line.triggered.connect(lambda: self.set_tool_active("line"))
        self.action_polygon.triggered.connect(lambda: self.set_tool_active("polygon"))
        self.action_hand.triggered.connect(lambda: self.set_tool_active("hand"))
        
        # More compact styling
        self.toolbox.setStyleSheet("""
            QToolBar {
                background-color: #f0f0f0;
                border-right: 1px solid #ccc;
                spacing: 2px;
                padding: 4px;
            }
            QToolButton {
                background-color: #e0e0e0;
                border-radius: 2px;
                padding: 4px;
                width: 18px;
                height: 18px;
                margin: 1px;
            }
            QToolButton:hover {
                background-color: #d0d0d0;
            }
            QToolButton:checked {
                background-color: #a0a0a0;
                color: white;
            }
            QToolButton:disabled {
                background-color: #f8f8f8;
                color: #999;
            }
        """)

    def set_tool_active(self, tool_name):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_tool(tool_name)
            self.update_ribbon_context()

    def insert_image_active(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.insert_image()

    def create_ribbon(self):
        self.ribbon = QToolBar("Properties")
        
        # Group text widgets for easy hiding
        self.text_widgets = []
        
        # Font Selector
        self.font_label_action = self.ribbon.addWidget(QLabel("Font:"))
        self.font_combo = QComboBox()
        self.font_combo.addItems(self.font_families)
        self.font_combo.setCurrentText(self.default_font)
        self.font_combo.setMaximumWidth(150)
        self.font_combo.currentTextChanged.connect(self.on_font_changed)
        self.font_combo.blockSignals(True)  # Block signals during initialization
        self.font_combo.setCurrentText(self.default_font)
        self.font_combo.blockSignals(False)  # Re-enable signals
        self.font_combo_action = self.ribbon.addWidget(self.font_combo)
        
        # Font Size
        self.size_label_action = self.ribbon.addWidget(QLabel("Size:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["8", "9", "10", "11", "12", "14", "16", "18", "20", "24", "28", "32", "36", "48", "72"])
        self.font_size_combo.setCurrentText("24")
        self.font_size_combo.setFixedWidth(60)
        self.font_size_combo.activated.connect(self.on_font_size_changed)
        self.ribbon.addWidget(self.font_size_combo)
        
        self.ribbon.addSeparator()
        
        # Formatting buttons (Bold, Italic, Underline)
        # Formatting buttons (Bold, Italic, Underline)
        self.action_bold = self.ribbon.addAction(qta.icon('fa5s.bold', color='#333'), "Bold")
        self.action_italic = self.ribbon.addAction(qta.icon('fa5s.italic', color='#333'), "Italic")
        self.action_underline = self.ribbon.addAction(qta.icon('fa5s.underline', color='#333'), "Underline")
        
        self.action_bold.setCheckable(True)
        self.action_italic.setCheckable(True)
        self.action_underline.setCheckable(True)
        
        self.action_bold.toggled.connect(lambda c: self.set_bold_active(c))
        self.action_italic.toggled.connect(lambda c: self.set_italic_active(c))
        self.action_underline.toggled.connect(lambda c: self.set_underline_active(c))
        
        self.ribbon.addSeparator()
        
        # Color Picker
        self.action_color = self.ribbon.addAction(qta.icon('fa5s.palette', color='#333'), "Color")
        self.action_color.triggered.connect(self.choose_color)
        
        self.ribbon.addSeparator()
        
        # Line Height
        self.line_height_label_action = self.ribbon.addWidget(QLabel("Line Height:"))
        self.line_height_spin = QDoubleSpinBox()
        self.line_height_spin.setRange(0.5, 5.0)
        self.line_height_spin.setSingleStep(0.1)
        self.line_height_spin.setValue(1.0)
        self.line_height_spin.setToolTip("Line Height")
        self.line_height_spin.setFixedWidth(50)
        self.line_height_spin.valueChanged.connect(self.on_line_height_changed)
        self.ribbon.addWidget(self.line_height_spin)
        
        # Word Spacing
        self.word_spacing_label_action = self.ribbon.addWidget(QLabel("Word:"))
        self.word_spacing_spin = QDoubleSpinBox()
        self.word_spacing_spin.setRange(-10.0, 50.0)
        self.word_spacing_spin.setSingleStep(0.5)
        self.word_spacing_spin.setValue(0.0)
        self.word_spacing_spin.setToolTip("Word Spacing")
        self.word_spacing_spin.setFixedWidth(50)
        self.word_spacing_spin.valueChanged.connect(self.on_word_spacing_changed)
        self.ribbon.addWidget(self.word_spacing_spin)
        
        # Character Width/Spacing
        self.char_width_label_action = self.ribbon.addWidget(QLabel("Char:"))
        self.char_width_spin = QDoubleSpinBox()
        self.char_width_spin.setRange(50.0, 200.0)
        self.char_width_spin.setSingleStep(5.0)
        self.char_width_spin.setValue(100.0)
        self.char_width_spin.setToolTip("Character Width %")
        self.char_width_spin.setFixedWidth(50)
        self.char_width_spin.valueChanged.connect(self.on_char_width_changed)
        self.ribbon.addWidget(self.char_width_spin)
        
        self.ribbon.addSeparator()
        
        # Text Direction (RTL/LTR) - Grey/Black icons
        self.action_rtl = self.ribbon.addAction(qta.icon('mdi.arrow-right', color='#333'), "RTL")
        self.action_ltr = self.ribbon.addAction(qta.icon('mdi.arrow-left', color='#333'), "LTR")
        self.action_rtl.triggered.connect(self.set_direction_rtl)
        self.action_ltr.triggered.connect(self.set_direction_ltr)
        
        self.ribbon.addSeparator()
        
        # Alignment buttons
        self.action_left = self.ribbon.addAction(qta.icon('fa5s.align-left', color='#333'), "Left")
        self.action_center = self.ribbon.addAction(qta.icon('fa5s.align-center', color='#333'), "Center")
        self.action_right = self.ribbon.addAction(qta.icon('fa5s.align-right', color='#333'), "Right")
        self.action_justify = self.ribbon.addAction(qta.icon('fa5s.align-justify', color='#333'), "Justify")
        
        self.action_left.triggered.connect(lambda: self.set_alignment_active(Qt.AlignmentFlag.AlignLeft))
        self.action_center.triggered.connect(lambda: self.set_alignment_active(Qt.AlignmentFlag.AlignCenter))
        self.action_right.triggered.connect(lambda: self.set_alignment_active(Qt.AlignmentFlag.AlignRight))
        self.action_justify.triggered.connect(lambda: self.set_alignment_active(Qt.AlignmentFlag.AlignJustify))
        
        # Add all text actions to text_widgets list (widgets only, actions are in toolbar)
        # We need to store the QAction objects returned by addAction/addWidget to hide them?
        # QToolBar.addWidget returns the QAction.
        # Let's refactor to store the actions/widgets we want to hide.
        
        # Actually, simpler: we can just hide the widgets we added. 
        # For actions (buttons), we need to hide the action.
        
        # Re-collecting text widgets for hiding:
        self.text_widgets.extend([
            self.font_label_action, self.font_combo_action,
            self.size_label_action, self.font_size_combo,
            self.action_bold, self.action_italic, self.action_underline,
            self.action_color, 
            self.line_height_label_action, self.line_height_spin, 
            self.word_spacing_label_action, self.word_spacing_spin, 
            self.char_width_label_action, self.char_width_spin,
            self.action_rtl, self.action_ltr,
            self.action_left, self.action_center, self.action_right, self.action_justify
        ])
        
        # Shape Properties Section (for when shapes are selected)
        self.ribbon.addSeparator()
        
        self.shape_label = QLabel("  Shape:  ")
        self.shape_label.setStyleSheet("font-weight: bold; color: #555;")
        self.ribbon.addWidget(self.shape_label)
        
        # Width control
        self.shape_width_label = QLabel("Width:")
        self.ribbon.addWidget(self.shape_width_label)
        self.shape_width_spin = QSpinBox()
        self.shape_width_spin.setRange(10, 2000)
        self.shape_width_spin.setValue(100)
        self.shape_width_spin.setFixedWidth(50)
        self.shape_width_spin.valueChanged.connect(self.on_shape_width_changed)
        self.ribbon.addWidget(self.shape_width_spin)
        
        # Height control
        self.shape_height_label = QLabel("Height:")
        self.ribbon.addWidget(self.shape_height_label)
        self.shape_height_spin = QSpinBox()
        self.shape_height_spin.setRange(10, 2000)
        self.shape_height_spin.setValue(100)
        self.shape_height_spin.setFixedWidth(50)
        self.shape_height_spin.valueChanged.connect(self.on_shape_height_changed)
        self.ribbon.addWidget(self.shape_height_spin)
        
        # Border controls
        self.border_label = QLabel("Border:")
        self.ribbon.addWidget(self.border_label)
        self.border_width_spin = QSpinBox()
        self.border_width_spin.setRange(0, 20)
        self.border_width_spin.setValue(2)
        self.border_width_spin.setFixedWidth(40)
        self.border_width_spin.valueChanged.connect(self.on_border_width_changed)
        self.ribbon.addWidget(self.border_width_spin)
        
        self.border_color_button = QToolButton()
        self.border_color_button.setFixedSize(18, 18)
        self.border_color_button.setStyleSheet("background-color: black; border: 1px solid #999;")
        self.border_color_button.clicked.connect(self.choose_border_color)
        self.ribbon.addWidget(self.border_color_button)
        
        self.border_style_combo = QComboBox()
        self.border_style_combo.addItems(["Solid", "Dashed", "Dotted", "None"])
        self.border_style_combo.setFixedWidth(60)
        self.border_style_combo.currentTextChanged.connect(self.on_border_style_changed)
        self.ribbon.addWidget(self.border_style_combo)
        
        # Rotation control
        self.rotate_label = QLabel("Rotate:")
        self.ribbon.addWidget(self.rotate_label)
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(0, 360)
        self.rotation_spin.setValue(0)
        self.rotation_spin.setFixedWidth(45)
        self.rotation_spin.valueChanged.connect(self.on_rotation_changed)
        self.ribbon.addWidget(self.rotation_spin)
        
        # Polygon sides selector
        self.polygon_sides_label = QLabel("Sides:")
        self.ribbon.addWidget(self.polygon_sides_label)
        self.polygon_sides_combo = QComboBox()
        self.polygon_sides_combo.addItems(["3", "4", "5", "6", "8", "Star"])
        self.polygon_sides_combo.setFixedWidth(50)
        self.polygon_sides_combo.currentTextChanged.connect(self.on_polygon_sides_changed)
        self.ribbon.addWidget(self.polygon_sides_combo)

        # Initially hide shape properties (they'll be shown when shapes are selected)
        self.hide_shape_properties()
        
        self.ribbon.addSeparator()
        
        # Compact ribbon styling
        self.ribbon.setStyleSheet("""
            QToolBar {
                background-color: #f8f8f8;
                border-bottom: 1px solid #ccc;
                padding: 2px;
                spacing: 3px;
            }
            QToolButton {
                padding: 2px;
                margin: 1px;
                width: 24px;
                height: 24px;
            }
            QComboBox {
                max-height: 20px;
                font-size: 11px;
            }
            QSpinBox, QDoubleSpinBox {
                max-height: 20px;
                font-size: 11px;
            }
            QLabel {
                font-size: 11px;
            }
        """)
        
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.ribbon)

    def update_ribbon_context(self):
        """Show/Hide ribbon tools based on selection"""
        doc_view = self.get_active_document_view()
        if not doc_view:
            return

        selected_items = doc_view.scene.selectedItems()
        has_shape_selection = False
        has_text_selection = False
        
        # Check what is selected
        from src.engine.shape_items import ResizableRectItem, ResizableEllipseItem, ResizableLineItem, PolygonItem
        from src.engine.text_box import TextBox
        
        for item in selected_items:
            if isinstance(item, (ResizableRectItem, ResizableEllipseItem, ResizableLineItem, PolygonItem)):
                has_shape_selection = True
            elif isinstance(item, TextBox):
                # Text box selection can be treated as shape if we are resizing, 
                # but usually we want text tools if we are editing text.
                # If the text box is selected (handles visible), we might want shape tools too?
                # User said: "show the shapes style tools only when a shape tool is picked or any shape is selected otherwise only show text style tools"
                # So for TextBox, we probably stick to text tools unless we want to style the box itself.
                # Let's assume TextBox = Text Tools for now, unless we add box styling.
                has_text_selection = True

        # Also check active tool
        current_tool = doc_view.current_tool
        is_shape_tool = current_tool in ["rect", "round_rect", "ellipse", "line", "polygon"]
        
        if has_shape_selection or is_shape_tool:
            self.show_shape_properties()
            self.hide_text_properties()
            
            # Update shape values if a shape is selected
            if has_shape_selection and len(selected_items) == 1:
                item = selected_items[0]
                if hasattr(item, 'rect'):
                    rect = item.rect()
                    self.shape_width_spin.blockSignals(True)
                    self.shape_height_spin.blockSignals(True)
                    self.shape_width_spin.setValue(int(rect.width()))
                    self.shape_height_spin.setValue(int(rect.height()))
                    self.shape_width_spin.blockSignals(False)
                    self.shape_height_spin.blockSignals(False)
                    
                if hasattr(item, 'pen'):
                    self.border_width_spin.blockSignals(True)
                    self.border_width_spin.setValue(item.pen().width())
                    self.border_width_spin.blockSignals(False)
                    
                if hasattr(item, 'rotation'):
                    self.rotation_spin.blockSignals(True)
                    self.rotation_spin.setValue(int(item.rotation()))
                    self.rotation_spin.blockSignals(False)
                    
        else:
            self.show_text_properties()
            self.hide_shape_properties()

    def show_shape_properties(self):
        # Show shape related widgets
        self.shape_label.show()
        self.shape_width_label.show()
        self.shape_width_spin.show()
        self.shape_height_label.show()
        self.shape_height_spin.show()
        self.border_label.show()
        self.border_width_spin.show()
        self.border_color_button.show()
        self.border_style_combo.show()
        self.rotate_label.show()
        self.rotation_spin.show()
        self.polygon_sides_label.show()
        self.polygon_sides_combo.show()

    def hide_shape_properties(self):
        # Hide shape related widgets
        self.shape_label.hide()
        self.shape_width_label.hide()
        self.shape_width_spin.hide()
        self.shape_height_label.hide()
        self.shape_height_spin.hide()
        self.border_label.hide()
        self.border_width_spin.hide()
        self.border_color_button.hide()
        self.border_style_combo.hide()
        self.rotate_label.hide()
        self.rotation_spin.hide()
        self.polygon_sides_label.hide()
        self.polygon_sides_combo.hide()

    def show_text_properties(self):
        # Show text related widgets
        for widget in self.text_widgets:
            widget.setVisible(True)

    def hide_text_properties(self):
        # Hide text related widgets
        for widget in self.text_widgets:
            widget.setVisible(False)

    def increase_font_size(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            current = doc_view.current_font_size
            new_size = current + 1
            self.font_size_combo.setCurrentText(str(int(new_size))) # This triggers change

    def decrease_font_size(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            current = doc_view.current_font_size
            new_size = max(1, current - 1)
            self.font_size_combo.setCurrentText(str(int(new_size)))

    def on_font_family_changed(self, font):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_font_family(font.family())

    def on_polygon_sides_changed(self, value):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_polygon_sides(value)

    def set_bold_active(self, enabled):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_bold(enabled)

    def set_italic_active(self, enabled):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_italic(enabled)

    def set_underline_active(self, enabled):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_underline(enabled)

    def set_alignment_active(self, alignment):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_alignment(alignment)

    def on_font_changed(self, font_family=None):
        doc_view = self.get_active_document_view()
        if doc_view:
            # Get the font family from the combo box directly
            current_font = self.font_combo.currentText()
            doc_view.set_font_family(current_font)

    def on_font_size_changed(self, size):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_font_size(size)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            doc_view = self.get_active_document_view()
            if doc_view:
                doc_view.set_text_color(color)

    def on_word_spacing_changed(self, value):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_word_spacing(value)

    def on_line_height_changed(self, value):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_line_height(value)

    def on_char_width_changed(self, value):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_char_width(value)

    def set_direction_rtl(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_text_direction("rtl")

    def set_direction_ltr(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_text_direction("ltr")

    def on_line_spacing_changed(self, value):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_line_spacing(value)


    def create_canvas(self):
        # Deprecated: Canvas is now created in DocumentWindow
        pass

    # Placeholder methods for menu actions
    def close_document(self):
        active_sub = self.mdi_area.activeSubWindow()
        if active_sub:
            active_sub.close()

    def revert_document(self):
        self.statusBar().showMessage("Revert - Not implemented yet")

    def import_document(self):
        """Import text or image"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import File", "", 
                                                 "Text Files (*.txt);;Images (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)")
        if not file_path:
            return
            
        doc_view = self.get_active_document_view()
        if not doc_view:
            return
            
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            # Image import
            # We need to implement insert_image in DocumentView or use existing logic
            # For now, let's assume insert_image exists or we create a text box with image
            # Actually, let's check if insert_image is available
            if hasattr(doc_view, 'insert_image'):
                doc_view.insert_image(file_path)
            else:
                # Fallback: Create text box and insert image HTML? Or just show message
                 QMessageBox.information(self, "Import", "Image import not fully implemented in view.")
        else:
            # Text import
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                # Insert into active text box or new one
                if doc_view.active_text_box:
                    cursor = doc_view.active_text_box.textCursor()
                    cursor.insertText(text)
                else:
                    # Create new text box
                    tb = doc_view.add_text_box(50, 50)
                    tb.setPlainText(text)
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import file: {str(e)}")

    def export_document(self):
        """Export document to PDF"""
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Document", "", "PDF Files (*.pdf)")
        if not file_path:
            return
            
        if not file_path.lower().endswith('.pdf'):
            file_path += '.pdf'
            
        doc_view = self.get_active_document_view()
        if doc_view:
            try:
                doc_view.export_pdf(file_path)
                self.statusBar().showMessage(f"Exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def place_content(self):
        self.statusBar().showMessage("Place - Not implemented yet")

    def print_document(self):
        """Print document"""
        doc_view = self.get_active_document_view()
        if not doc_view:
            return
            
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            try:
                # Render scene to printer
                painter = QPainter(printer)
                doc_view.scene.render(painter)
                painter.end()
                self.statusBar().showMessage("Printing completed")
            except Exception as e:
                QMessageBox.critical(self, "Print Error", f"Failed to print: {str(e)}")

    def printer_setup(self):
        """Printer setup dialog"""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPageSetupDialog(printer, self)
        
        if dialog.exec() == QPageSetupDialog.DialogCode.Accepted:
            # Apply settings to current document view if needed
            # For now, just show success as we don't persist printer settings globally yet
            self.statusBar().showMessage("Printer setup updated")
        
    def check_spelling(self):
        self.statusBar().showMessage("Spelling - Not implemented yet")
        
    def show_word_count(self):
        self.statusBar().showMessage("Word Count - Not implemented yet")
        
    def edit_links(self):
        self.statusBar().showMessage("Edit Links - Not implemented yet")
        
    def show_keyboard_preferences(self):
        self.statusBar().showMessage("Keyboard Preferences - Not implemented yet")
        
    def cascade_windows(self):
        self.mdi_area.cascadeSubWindows()
        
    def tile_windows(self):
        self.mdi_area.tileSubWindows()
        
    def close_all_windows(self):
        self.mdi_area.closeAllSubWindows()
        
    def show_page_window(self):
        self.statusBar().showMessage("Page Window - Not implemented yet")
        
    def show_help_contents(self):
        self.statusBar().showMessage("Help Contents - Not implemented yet")
        
    def show_help_index(self):
        self.statusBar().showMessage("Help Index - Not implemented yet")
        
    def show_using_help(self):
        self.statusBar().showMessage("Using Help - Not implemented yet")
        
    def show_about(self):
        QMessageBox.about(self, "About page26", "page26 - Modern Urdu DTP Application\nVersion 1.0")
        
    def auto_index(self):
        self.statusBar().showMessage("Auto Index - Not implemented yet")

    def generate_index(self):
        self.statusBar().showMessage("Generate Index - Not implemented yet")

    def find_replace(self):
        if not hasattr(self, 'find_dialog'):
            self.find_dialog = FindReplaceDialog(self)
            self.find_dialog.find_next.connect(self.on_find_next)
            self.find_dialog.replace.connect(self.on_replace)
            self.find_dialog.replace_all.connect(self.on_replace_all)
        
        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()

    def on_find_next(self, text, case_sensitive, backward):
        doc_view = self.get_active_document_view()
        if doc_view:
            found = doc_view.find_text(text, case_sensitive, backward)
            if not found:
                self.statusBar().showMessage(f"Text '{text}' not found.")
            else:
                self.statusBar().showMessage(f"Found '{text}'")

    def on_replace(self, find_text, replace_text, case_sensitive, backward):
        doc_view = self.get_active_document_view()
        if doc_view:
            success = doc_view.replace_text(find_text, replace_text, case_sensitive, backward)
            if success:
                self.statusBar().showMessage("Replaced")
                # Find next occurrence
                self.on_find_next(find_text, case_sensitive, backward)
            else:
                self.statusBar().showMessage(f"Text '{find_text}' not found.")

    def on_replace_all(self, find_text, replace_text, case_sensitive):
        doc_view = self.get_active_document_view()
        if doc_view:
            count = doc_view.replace_all_text(find_text, replace_text, case_sensitive)
            self.statusBar().showMessage(f"Replaced {count} occurrences.")

    def app_preferences(self):
        self.statusBar().showMessage("Application Preferences - Not implemented yet")

    def doc_preferences(self):
        self.statusBar().showMessage("Document Preferences - Not implemented yet")

    def type_preferences(self):
        self.statusBar().showMessage("Typographic Preferences - Not implemented yet")

    def kb_preferences(self):
        self.statusBar().showMessage("Keyboard Preferences - Not implemented yet")

    def delete_page(self):
        """Delete current page"""
        doc_view = self.get_active_document_view()
        if not doc_view:
            return
            
        # Check if it's the only page
        if doc_view.page_manager.page_count() <= 1:
            QMessageBox.warning(self, "Delete Page", "Cannot delete the only page in the document.")
            return
            
        reply = QMessageBox.question(self, "Delete Page", 
                                   "Are you sure you want to delete the current page?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                                   
        if reply == QMessageBox.StandardButton.Yes:
            if doc_view.delete_current_page():
                self.update_page_label()
                self.statusBar().showMessage("Page deleted")
            else:
                self.statusBar().showMessage("Failed to delete page")

    def character_settings(self):
        self.show_character_dialog()

    def hyphenation_settings(self):
        self.statusBar().showMessage("Hyphenation - Not implemented yet")

    def borders_settings(self):
        self.statusBar().showMessage("Borders - Not implemented yet")

    def page_setup(self):
        self.statusBar().showMessage("Page Setup - Not implemented yet")

    def guides_settings(self):
        self.statusBar().showMessage("Guides - Not implemented yet")

    def style_sheets_settings(self):
        self.statusBar().showMessage("Style Sheets - Not implemented yet")

    def colors_settings(self):
        self.statusBar().showMessage("Colors - Not implemented yet")

    def insert_page(self):
        self.statusBar().showMessage("Insert Page - Not implemented yet")

    def insert_picture(self):
        self.statusBar().showMessage("Insert Picture - Not implemented yet")

    def insert_text_box(self):
        self.statusBar().showMessage("Insert Text Box - Not implemented yet")
        
    def insert_symbol(self, symbol):
        doc_view = self.get_active_document_view()
        if doc_view:
            # Insert symbol at cursor
            # This requires access to the text cursor of the active text box
            # For now, just show message
            self.statusBar().showMessage(f"Insert Symbol {symbol} - Not implemented yet")

    def import_text(self):
        """Import text from file"""
        doc_view = self.get_active_document_view()
        if not doc_view:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Text", "", 
            "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    
                # Add to active text box or create new one
                active_item = doc_view.scene.focusItem()
                if isinstance(active_item, TextBox):
                    cursor = active_item.textCursor()
                    cursor.insertText(text_content)
                else:
                    # Create new text box with imported text
                    tb = doc_view.add_text_box(100, 100, locked=False)
                    tb.setPlainText(text_content)
                    
                self.statusBar().showMessage(f"Imported: {file_path}")
            except Exception as e:
                self.statusBar().showMessage(f"Import error: {str(e)}")

    def import_picture(self):
        self.insert_image_active()

    def export_text(self):
        self.statusBar().showMessage("Export text - Not implemented yet")

    def export_picture(self):
        self.statusBar().showMessage("Export picture - Not implemented yet")

    def export_epub(self):
        self.statusBar().showMessage("Export EPUB - Not implemented yet")

    def print_document(self):
        """Print current document"""
        from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
        
        doc_view = self.get_active_document_view()
        if not doc_view:
            return
            
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            # Render scene to printer
            painter = QPainter(printer)
            doc_view.scene.render(painter)
            painter.end()
            self.statusBar().showMessage("Document sent to printer")

    def print_setup(self):
        self.statusBar().showMessage("Print setup - Not implemented yet")

    def undo(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.undo()
            self.statusBar().showMessage("Undo")

    def redo(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.redo()
            self.statusBar().showMessage("Redo")

    def cut(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            focus_item = doc_view.scene.focusItem()
            if isinstance(focus_item, TextBox):
                focus_item.cut()

    def copy(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            focus_item = doc_view.scene.focusItem()
            if isinstance(focus_item, TextBox):
                focus_item.copy()

    def paste(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            focus_item = doc_view.scene.focusItem()
            if isinstance(focus_item, TextBox):
                focus_item.paste()

    def paste_special(self):
        self.statusBar().showMessage("Paste special - Not implemented yet")

    def duplicate(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.duplicate_selected()
            self.statusBar().showMessage("Duplicated selected items")

    def clear(self):
        self.delete_selected()
        self.statusBar().showMessage("Cleared selected items")

    def delete(self):
        self.delete_selected()

    def select_all(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.select_all()
            self.statusBar().showMessage("Selected all items")

    def find(self):
        self.statusBar().showMessage("Find - Not implemented yet")

    def replace(self):
        self.statusBar().showMessage("Replace - Not implemented yet")

    def zoom_in(self):
        """FIXED: Zoom in by 25%"""
        current_zoom = self.zoom_slider.value()
        new_zoom = min(400, current_zoom + 25)
        self.zoom_slider.setValue(new_zoom)

    def zoom_out(self):
        """FIXED: Zoom out by 25%"""
        current_zoom = self.zoom_slider.value()
        new_zoom = max(10, current_zoom - 25)
        self.zoom_slider.setValue(new_zoom)

    def fit_window(self):
        """Fit to window (30% zoom)"""
        self.zoom_slider.setValue(30)

    def actual_size(self):
        """FIXED: Actual size (100%)"""
        self.zoom_slider.setValue(100)

    def zoom_50(self):
        """Zoom to 50%"""
        self.zoom_slider.setValue(50)

    def zoom_200(self):
        """Zoom to 200%"""
        self.zoom_slider.setValue(200)

    def toggle_ribbon(self, checked):
        """Hide/Show Ribbon"""
        # Action is "Hide Ribbon", so if checked, hide it.
        self.ribbon.setVisible(not checked)

    def toggle_tools(self, checked):
        """Hide/Show Tools"""
        self.toolbox.setVisible(not checked)

    def toggle_rulers(self, checked):
        """Hide/Show Rulers"""
        # Action is "Hide Rulers"
        window = self.get_active_document_window()
        if window:
            window.h_ruler.setVisible(not checked)
            window.v_ruler.setVisible(not checked)
        self.statusBar().showMessage(f"Rulers {'hidden' if checked else 'shown'}")

    def toggle_guides(self, checked):
        """Hide/Show Guides"""
        doc_view = self.get_active_document_view()
        if doc_view:
            # Toggle guide visibility
            for item in doc_view.scene.items():
                if isinstance(item, QGraphicsLineItem):
                    item.setVisible(not checked)
        self.statusBar().showMessage(f"Guides {'hidden' if checked else 'shown'}")

    def toggle_invisibles(self, checked):
        """Show/Hide Invisibles"""
        # Action is "Show Invisibles", so if checked, show them.
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_show_invisibles(checked)
            self.statusBar().showMessage(f"Invisibles {'shown' if checked else 'hidden'}")

    def toggle_snap_guides(self, checked):
        """Snap to Guides"""
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_snap_to_guides(checked)
            self.statusBar().showMessage(f"Snap to guides {'enabled' if checked else 'disabled'}")
            
    def toggle_facing_pages(self, checked):
        self.statusBar().showMessage(f"Facing pages {'enabled' if checked else 'disabled'} - Not implemented yet")

    def toggle_grid(self, checked):
        self.statusBar().showMessage(f"Grid {'shown' if checked else 'hidden'} - Not implemented yet")

    def toggle_master_pages(self, checked):
        self.statusBar().showMessage(f"Master pages {'shown' if checked else 'hidden'} - Not implemented yet")

    def toggle_non_printing(self, checked):
        self.statusBar().showMessage(f"Non-printing characters {'shown' if checked else 'hidden'} - Not implemented yet")

    def set_page_display(self, mode):
        self.statusBar().showMessage(f"Page display: {mode} - Not implemented yet")

    def cut(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            # Get selected items and cut them
            # This would require clipboard support
            self.statusBar().showMessage("Cut - Not fully implemented yet")

    def copy(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            # Copy selected items to clipboard
            self.statusBar().showMessage("Copy - Not fully implemented yet")

    def paste(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            # Paste from clipboard
            self.statusBar().showMessage("Paste - Not fully implemented yet")

    def clear(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.delete_selected()
            self.statusBar().showMessage("Cleared selected items")

    def top_most(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.top_most()
            self.statusBar().showMessage("Moved to top most")

    def send_back(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.send_to_back()
            self.statusBar().showMessage("Sent to back")

    def lock_guides(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.lock_guides()
            self.statusBar().showMessage("Guides locked")

    def show_character_dialog(self):
        """Show character formatting dialog"""
        from src.ui.dialogs.character_dialog import CharacterDialog
        
        dialog = CharacterDialog(self)
        if dialog.exec():
            formatting = dialog.get_formatting()
            # Apply formatting to selected text
            doc_view = self.get_active_document_view()
            if doc_view:
                doc_view.set_font_family(formatting['font_family'])
                doc_view.set_font_size(formatting['font_size'])
                doc_view.set_bold(formatting['bold'])
                doc_view.set_italic(formatting['italic'])
                doc_view.set_underline(formatting['underline'])

    def show_paragraph_dialog(self):
        """Show paragraph formatting dialog"""
        from src.ui.dialogs.paragraph_dialog import ParagraphDialog
        
        dialog = ParagraphDialog(self)
        if dialog.exec():
            formatting = dialog.get_formatting()
            doc_view = self.get_active_document_view()
            if doc_view:
                doc_view.apply_paragraph_formatting(formatting)
                
    def insert_page(self):
        self.add_page()

    def delete_page(self):
        self.statusBar().showMessage("Delete page - Not implemented yet")

    def insert_page_number(self):
        self.statusBar().showMessage("Insert page number - Not implemented yet")

    def insert_picture(self, box_type):
        self.insert_image_active()

    def insert_table(self):
        """Insert table"""
        from src.ui.dialogs.table_dialog import TableDialog
        
        dialog = TableDialog(self)
        if dialog.exec():
            rows, cols = dialog.get_dimensions()
            doc_view = self.get_active_document_view()
            if doc_view:
                doc_view.insert_table(rows, cols)
            self.statusBar().showMessage("Inserted table")

    def insert_index(self):
        self.statusBar().showMessage("Insert index - Not implemented yet")

    def insert_footnote(self):
        self.statusBar().showMessage("Insert footnote - Not implemented yet")

    def object_lock(self):
        self.statusBar().showMessage("Object lock - Not implemented yet")

    def show_symbol_gallery(self):
        self.statusBar().showMessage("Symbol gallery - Not implemented yet")

    def show_symbol_box(self):
        self.statusBar().showMessage("Symbol box - Not implemented yet")

    def check_spelling(self):
        self.statusBar().showMessage("Spelling check - Not implemented yet")

    def show_word_count(self):
        self.statusBar().showMessage("Word count - Not implemented yet")

    def group_objects(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.group_selected()
            self.statusBar().showMessage("Grouped objects")

    def ungroup_objects(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.ungroup_selected()
            self.statusBar().showMessage("Ungrouped objects")

    def auto_index(self):
        self.statusBar().showMessage("Auto index - Not implemented yet")

    def generate_index(self):
        self.statusBar().showMessage("Generate index - Not implemented yet")

    def edit_links(self):
        self.statusBar().showMessage("Edit links - Not implemented yet")

    def toggle_language_keyboard(self):
        self.toggle_language(None)

    def show_keyboard_preferences(self):
        self.statusBar().showMessage("Keyboard preferences - Not implemented yet")

    def show_hyphenation_dialog(self):
        """Show hyphenation settings dialog"""
        from src.ui.dialogs.hyphenation_dialog import HyphenationDialog
        
        dialog = HyphenationDialog(self)
        if dialog.exec():
            settings = dialog.get_settings()
            doc_view = self.get_active_document_view()
            if doc_view:
                doc_view.apply_hyphenation_settings(settings)
                self.statusBar().showMessage("Hyphenation settings applied")

    def show_borders_dialog(self):
        """Show borders and shading dialog"""
        from src.ui.dialogs.borders_dialog import BordersDialog
        
        dialog = BordersDialog(self)
        if dialog.exec():
            settings = dialog.get_settings()
            doc_view = self.get_active_document_view()
            if doc_view:
                doc_view.apply_border_settings(settings)

    def show_page_setup_dialog(self):
        self.statusBar().showMessage("Page Setup - Not implemented yet")

    def show_guides_dialog(self):
        self.statusBar().showMessage("Guides - Not implemented yet")

    def show_style_sheets_dialog(self):
        self.statusBar().showMessage("Style Sheets - Not implemented yet")

    def show_colors_dialog(self):
        self.statusBar().showMessage("Colors - Not implemented yet")

    def show_symbol_gallery(self):
        self.statusBar().showMessage("Symbol Gallery - Not implemented yet")

    def story_editor(self):
        self.statusBar().showMessage("Story Editor - Not implemented yet")

    def ungroup_objects(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.ungroup_selected()
            self.statusBar().showMessage("Ungrouped objects")

    def show_using_help(self):
        self.statusBar().showMessage("Using help - Not implemented yet")

    def cascade_windows(self):
        self.mdi_area.cascadeSubWindows()

    def tile_windows(self):
        self.mdi_area.tileSubWindows()

    def close_all_windows(self):
        self.mdi_area.closeAllSubWindows()

    def show_help_contents(self):
        self.statusBar().showMessage("Help contents - Not implemented yet")

    def show_help_index(self):
        self.statusBar().showMessage("Help index - Not implemented yet")

    def show_using_help(self):
        self.statusBar().showMessage("Using help - Not implemented yet")

    def show_about(self):
        self.statusBar().showMessage("About page26 - Not implemented yet")
    
    def first_page(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            if doc_view.switch_page(0):
                self.update_page_label()
    
    def prev_page(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            if doc_view.switch_page(doc_view.page_manager.current_page_index - 1):
                self.update_page_label()
    
    def next_page(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            if doc_view.switch_page(doc_view.page_manager.current_page_index + 1):
                self.update_page_label()
    
    def last_page(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            if doc_view.switch_page(doc_view.page_manager.page_count() - 1):
                self.update_page_label()
    
    def add_page(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.page_manager.add_page()
            doc_view.switch_page(doc_view.page_manager.page_count() - 1)
            self.update_page_label()

    def top_most(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.top_most()

    def bring_front(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.bring_to_front()

    def send_back(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.send_to_back()

    def lock_guides(self):
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.lock_guides()

    def on_shape_width_changed(self, value):
        """Handle shape width change from ribbon"""
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_shape_width(value)

    def on_shape_height_changed(self, value):
        """Handle shape height change from ribbon"""
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_shape_height(value)

    def on_border_width_changed(self, value):
        """Handle border width change from ribbon"""
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_border_width(value)

    def choose_border_color(self):
        """Show color dialog for border color"""
        color = QColorDialog.getColor()
        if color.isValid():
            doc_view = self.get_active_document_view()
            if doc_view:
                doc_view.set_border_color(color)

    def on_border_style_changed(self, style):
        """Handle border style change from ribbon"""
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_border_style(style)

    def on_rotation_changed(self, angle):
        """Handle rotation angle change from ribbon"""
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_rotation(angle)

    def on_polygon_sides_changed(self, sides):
        """Handle polygon sides change from ribbon"""
        doc_view = self.get_active_document_view()
        if doc_view:
            doc_view.set_polygon_sides(sides)

    def hide_shape_properties(self):
        """Hide shape properties in ribbon"""
        # Hide all shape-related controls
        for widget in [self.shape_width_spin, self.shape_height_spin,
                      self.border_width_spin, self.border_color_button,
                      self.border_style_combo, self.rotation_spin,
                      self.polygon_sides_combo]:
            widget.setVisible(False)

    def show_shape_properties(self):
        """Show shape properties in ribbon"""
        # Show all shape-related controls
        for widget in [self.shape_width_spin, self.shape_height_spin,
                      self.border_width_spin, self.border_color_button,
                      self.border_style_combo, self.rotation_spin,
                      self.polygon_sides_combo]:
            widget.setVisible(True)
