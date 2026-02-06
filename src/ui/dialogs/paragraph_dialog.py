from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSpinBox, QDoubleSpinBox, QComboBox, QDialogButtonBox, 
                             QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt

class ParagraphDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paragraph Formatting")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Alignment
        align_group = QGroupBox("Alignment")
        align_layout = QHBoxLayout()
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Left", "Center", "Right", "Justify"])
        align_layout.addWidget(QLabel("Alignment:"))
        align_layout.addWidget(self.align_combo)
        align_group.setLayout(align_layout)
        layout.addWidget(align_group)
        
        # Indentation
        indent_group = QGroupBox("Indentation")
        indent_layout = QFormLayout()
        
        self.indent_left = QDoubleSpinBox()
        self.indent_left.setRange(0, 100)
        self.indent_left.setSuffix(" mm")
        
        self.indent_right = QDoubleSpinBox()
        self.indent_right.setRange(0, 100)
        self.indent_right.setSuffix(" mm")
        
        self.indent_first = QDoubleSpinBox()
        self.indent_first.setRange(0, 100)
        self.indent_first.setSuffix(" mm")
        
        indent_layout.addRow("Left:", self.indent_left)
        indent_layout.addRow("Right:", self.indent_right)
        indent_layout.addRow("First Line:", self.indent_first)
        indent_group.setLayout(indent_layout)
        layout.addWidget(indent_group)
        
        # Spacing
        spacing_group = QGroupBox("Spacing")
        spacing_layout = QFormLayout()
        
        self.space_before = QDoubleSpinBox()
        self.space_before.setRange(0, 100)
        self.space_before.setSuffix(" pt")
        
        self.space_after = QDoubleSpinBox()
        self.space_after.setRange(0, 100)
        self.space_after.setSuffix(" pt")
        
        self.line_spacing = QDoubleSpinBox()
        self.line_spacing.setRange(0.5, 5.0)
        self.line_spacing.setSingleStep(0.1)
        self.line_spacing.setValue(1.0)
        
        spacing_layout.addRow("Before:", self.space_before)
        spacing_layout.addRow("After:", self.space_after)
        spacing_layout.addRow("Line Spacing:", self.line_spacing)
        spacing_group.setLayout(spacing_layout)
        layout.addWidget(spacing_group)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def get_formatting(self):
        return {
            "alignment": self.align_combo.currentText(),
            "indent_left": self.indent_left.value(),
            "indent_right": self.indent_right.value(),
            "indent_first": self.indent_first.value(),
            "space_before": self.space_before.value(),
            "space_after": self.space_after.value(),
            "line_spacing": self.line_spacing.value()
        }