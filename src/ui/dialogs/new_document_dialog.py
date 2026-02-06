from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QComboBox, QLineEdit, QRadioButton, 
                             QCheckBox, QDialogButtonBox, QButtonGroup)
from PyQt6.QtCore import Qt

class NewDocumentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Document")
        self.resize(400, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Page Settings Group
        page_group = QGroupBox("Page")
        page_layout = QVBoxLayout(page_group)
        
        # Page Size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Page Size:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A4 (210x297mm)", "A3 (297x420mm)", "Letter (216x279mm)", "Custom"])
        size_layout.addWidget(self.page_size_combo)
        page_layout.addLayout(size_layout)
        
        # Custom Size
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(QLabel("Width:"))
        self.width_edit = QLineEdit("210")
        self.width_edit.setMaximumWidth(60)
        custom_layout.addWidget(self.width_edit)
        custom_layout.addWidget(QLabel("mm"))
        
        custom_layout.addWidget(QLabel("Height:"))
        self.height_edit = QLineEdit("297")
        self.height_edit.setMaximumWidth(60)
        custom_layout.addWidget(self.height_edit)
        custom_layout.addWidget(QLabel("mm"))
        page_layout.addLayout(custom_layout)
        
        # Orientation
        orientation_layout = QHBoxLayout()
        orientation_layout.addWidget(QLabel("Orientation:"))
        self.portrait_radio = QRadioButton("Portrait")
        self.landscape_radio = QRadioButton("Landscape")
        self.portrait_radio.setChecked(True)
        orientation_layout.addWidget(self.portrait_radio)
        orientation_layout.addWidget(self.landscape_radio)
        page_layout.addLayout(orientation_layout)
        
        # Pages
        pages_layout = QHBoxLayout()
        pages_layout.addWidget(QLabel("Pages:"))
        self.pages_edit = QLineEdit("1")
        self.pages_edit.setMaximumWidth(40)
        pages_layout.addWidget(self.pages_edit)
        pages_layout.addStretch()
        page_layout.addLayout(pages_layout)
        
        layout.addWidget(page_group)
        
        # Margins Group
        margins_group = QGroupBox("Margins")
        margins_layout = QVBoxLayout(margins_group)
        
        margins_grid = QHBoxLayout()
        # Left margin
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Left:"))
        self.left_margin = QLineEdit("12.7")
        self.left_margin.setMaximumWidth(50)
        left_layout.addWidget(self.left_margin)
        left_layout.addWidget(QLabel("mm"))
        margins_grid.addLayout(left_layout)
        
        # Right margin
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Right:"))
        self.right_margin = QLineEdit("12.7")
        self.right_margin.setMaximumWidth(50)
        right_layout.addWidget(self.right_margin)
        right_layout.addWidget(QLabel("mm"))
        margins_grid.addLayout(right_layout)
        
        # Top margin
        top_layout = QVBoxLayout()
        top_layout.addWidget(QLabel("Top:"))
        self.top_margin = QLineEdit("12.7")
        self.top_margin.setMaximumWidth(50)
        top_layout.addWidget(self.top_margin)
        top_layout.addWidget(QLabel("mm"))
        margins_grid.addLayout(top_layout)
        
        # Bottom margin
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(QLabel("Bottom:"))
        self.bottom_margin = QLineEdit("12.7")
        self.bottom_margin.setMaximumWidth(50)
        bottom_layout.addWidget(self.bottom_margin)
        bottom_layout.addWidget(QLabel("mm"))
        margins_grid.addLayout(bottom_layout)
        
        margins_layout.addLayout(margins_grid)
        layout.addWidget(margins_group)
        
        # Direction Group
        direction_group = QGroupBox("Direction")
        direction_layout = QHBoxLayout(direction_group)
        self.ltr_radio = QRadioButton("Left To Right")
        self.rtl_radio = QRadioButton("Right To Left")
        self.rtl_radio.setChecked(True)  # Default for Urdu
        direction_layout.addWidget(self.ltr_radio)
        direction_layout.addWidget(self.rtl_radio)
        layout.addWidget(direction_group)
        
        # Columns Group
        columns_group = QGroupBox("Columns")
        columns_layout = QHBoxLayout(columns_group)
        columns_layout.addWidget(QLabel("Columns:"))
        self.columns_combo = QComboBox()
        self.columns_combo.addItems(["1", "2", "3", "4"])
        columns_layout.addWidget(self.columns_combo)
        
        columns_layout.addWidget(QLabel("Gutter:"))
        self.gutter_edit = QLineEdit("4.23")
        self.gutter_edit.setMaximumWidth(50)
        columns_layout.addWidget(self.gutter_edit)
        columns_layout.addWidget(QLabel("mm"))
        columns_layout.addStretch()
        layout.addWidget(columns_group)
        
        # Automatic Text Box Options
        auto_text_group = QGroupBox("Automatic Text Box")
        auto_text_layout = QVBoxLayout(auto_text_group)
        self.double_sided_check = QCheckBox("Double Sided")
        self.facing_pages_check = QCheckBox("Facing Pages")
        auto_text_layout.addWidget(self.double_sided_check)
        auto_text_layout.addWidget(self.facing_pages_check)
        layout.addWidget(auto_text_group)
        
        # Save as Default
        self.save_default_check = QCheckBox("Save as Default")
        layout.addWidget(self.save_default_check)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                     QDialogButtonBox.StandardButton.Cancel |
                                     QDialogButtonBox.StandardButton.Help)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_settings(self):
        return {
            'page_size': self.page_size_combo.currentText(),
            'width': float(self.width_edit.text()),
            'height': float(self.height_edit.text()),
            'orientation': 'portrait' if self.portrait_radio.isChecked() else 'landscape',
            'pages': int(self.pages_edit.text()),
            'margins': {
                'left': float(self.left_margin.text()),
                'right': float(self.right_margin.text()),
                'top': float(self.top_margin.text()),
                'bottom': float(self.bottom_margin.text())
            },
            'direction': 'ltr' if self.ltr_radio.isChecked() else 'rtl',
            'columns': int(self.columns_combo.currentText()),
            'gutter': float(self.gutter_edit.text()),
            'double_sided': self.double_sided_check.isChecked(),
            'facing_pages': self.facing_pages_check.isChecked()
        }