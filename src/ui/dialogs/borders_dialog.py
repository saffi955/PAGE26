from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QComboBox, QDialogButtonBox, QToolButton, 
                             QColorDialog, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class BordersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Borders and Shading")
        self.current_color = QColor("black")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Border Settings
        border_group = QGroupBox("Border")
        form_layout = QFormLayout()
        
        # Style
        self.style_combo = QComboBox()
        self.style_combo.addItems(["None", "Solid", "Dashed", "Dotted", "Double"])
        form_layout.addRow("Style:", self.style_combo)
        
        # Width
        self.width_spin = QSpinBox()
        self.width_spin.setRange(0, 20)
        self.width_spin.setSuffix(" pt")
        self.width_spin.setValue(1)
        form_layout.addRow("Width:", self.width_spin)
        
        # Color
        color_layout = QHBoxLayout()
        self.color_btn = QToolButton()
        self.color_btn.setFixedSize(50, 25)
        self.color_btn.setStyleSheet(f"background-color: {self.current_color.name()}; border: 1px solid #999;")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        form_layout.addRow("Color:", color_layout)
        
        border_group.setLayout(form_layout)
        layout.addWidget(border_group)
        
        # Position (Inside/Outside) - Placeholder for now
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def choose_color(self):
        color = QColorDialog.getColor(self.current_color, self, "Select Border Color")
        if color.isValid():
            self.current_color = color
            self.color_btn.setStyleSheet(f"background-color: {color.name()}; border: 1px solid #999;")

    def get_settings(self):
        return {
            "style": self.style_combo.currentText(),
            "width": self.width_spin.value(),
            "color": self.current_color
        }
