from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QCheckBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal

class FindReplaceDialog(QDialog):
    find_next = pyqtSignal(str, bool, bool) # text, case_sensitive, backward
    replace = pyqtSignal(str, str, bool, bool) # find_text, replace_text, case, backward
    replace_all = pyqtSignal(str, str, bool) # find_text, replace_text, case

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.setWindowFlags(Qt.WindowType.Window) # Non-modal
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Find
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find what:"))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Replace
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace with:"))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        self.case_check = QCheckBox("Match case")
        self.backward_check = QCheckBox("Search backward")
        options_layout.addWidget(self.case_check)
        options_layout.addWidget(self.backward_check)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_find = QPushButton("Find Next")
        self.btn_replace = QPushButton("Replace")
        self.btn_replace_all = QPushButton("Replace All")
        self.btn_close = QPushButton("Close")
        
        btn_layout.addWidget(self.btn_find)
        btn_layout.addWidget(self.btn_replace)
        btn_layout.addWidget(self.btn_replace_all)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Connections
        self.btn_find.clicked.connect(self.on_find)
        self.btn_replace.clicked.connect(self.on_replace)
        self.btn_replace_all.clicked.connect(self.on_replace_all)
        self.btn_close.clicked.connect(self.close)

    def on_find(self):
        text = self.find_input.text()
        if text:
            self.find_next.emit(text, self.case_check.isChecked(), self.backward_check.isChecked())

    def on_replace(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if find_text:
            self.replace.emit(find_text, replace_text, self.case_check.isChecked(), self.backward_check.isChecked())

    def on_replace_all(self):
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if find_text:
            self.replace_all.emit(find_text, replace_text, self.case_check.isChecked())
