from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
                             QLabel, QComboBox, QSpinBox, QCheckBox,
                             QDialogButtonBox, QPushButton, QColorDialog)
from PyQt6.QtGui import QFont

class CharacterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Character Formatting")
        self.resize(400, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Font Section
        font_group = QGroupBox("Font")
        font_layout = QVBoxLayout(font_group)
        
        font_row = QHBoxLayout()
        font_row.addWidget(QLabel("Font:"))
        self.font_combo = QComboBox()
        # Get available fonts from parent window if possible
        if hasattr(self.parent(), 'font_families'):
            self.font_combo.addItems(self.parent().font_families)
        else:
            # Fallback to a basic font combo
            self.font_combo.addItems(["Arial", "Times New Roman", "Jameel Noori Nastaleeq"])
        font_row.addWidget(self.font_combo)
        font_layout.addLayout(font_row)
        
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        self.size_spin.setValue(12)
        size_row.addWidget(self.size_spin)
        font_layout.addLayout(size_row)
        
        layout.addWidget(font_group)
        
        # Style Section
        style_group = QGroupBox("Style")
        style_layout = QHBoxLayout(style_group)
        self.bold_check = QCheckBox("Bold")
        self.italic_check = QCheckBox("Italic")
        self.underline_check = QCheckBox("Underline")
        style_layout.addWidget(self.bold_check)
        style_layout.addWidget(self.italic_check)
        style_layout.addWidget(self.underline_check)
        layout.addWidget(style_group)
        
        # Color Section
        color_group = QGroupBox("Color")
        color_layout = QHBoxLayout(color_group)
        self.color_button = QPushButton("Choose Color...")
        self.color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_button)
        layout.addWidget(color_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_button.setStyleSheet(f"background-color: {color.name()}")
    
    def get_formatting(self):
        return {
            'font_family': self.font_combo.currentText(),
            'font_size': self.size_spin.value(),
            'bold': self.bold_check.isChecked(),
            'italic': self.italic_check.isChecked(),
            'underline': self.underline_check.isChecked()
        }