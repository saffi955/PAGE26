from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox, 
                             QLabel, QSpinBox, QFormLayout)

class HyphenationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hyphenation Settings")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        self.enable_check = QCheckBox("Automatically hyphenate document")
        layout.addWidget(self.enable_check)
        
        form_layout = QFormLayout()
        
        self.words_caps_check = QCheckBox("Hyphenate words in CAPS")
        self.words_caps_check.setChecked(True)
        layout.addWidget(self.words_caps_check)
        
        self.zone_spin = QSpinBox()
        self.zone_spin.setRange(0, 50)
        self.zone_spin.setSuffix(" mm")
        self.zone_spin.setValue(10)
        form_layout.addRow("Hyphenation Zone:", self.zone_spin)
        
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(0, 10)
        self.limit_spin.setValue(3)
        form_layout.addRow("Limit consecutive hyphens to:", self.limit_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)

    def get_settings(self):
        return {
            "enabled": self.enable_check.isChecked(),
            "caps": self.words_caps_check.isChecked(),
            "zone": self.zone_spin.value(),
            "limit": self.limit_spin.value()
        }
