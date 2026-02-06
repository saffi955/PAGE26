import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QStatusBar
from PyQt6.QtGui import QAction

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Starting test script...")
try:
    from src.ui.main_window import MainWindow
    print("Imported MainWindow successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)

class TestMenus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication if it doesn't exist
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        # Mock dependencies to prevent UI blocking
        self.patches = []
        
        # Mock Dialogs
        self.mock_dialog = patch('PyQt6.QtWidgets.QDialog.exec', return_value=0)
        self.patches.append(self.mock_dialog)
        
        self.mock_file_open = patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=('', ''))
        self.patches.append(self.mock_file_open)
        
        self.mock_file_save = patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=('', ''))
        self.patches.append(self.mock_file_save)
        
        self.mock_msg_box = patch('PyQt6.QtWidgets.QMessageBox.information')
        self.patches.append(self.mock_msg_box)
        
        self.mock_msg_about = patch('PyQt6.QtWidgets.QMessageBox.about')
        self.patches.append(self.mock_msg_about)
        
        # Start patches
        for p in self.patches:
            p.start()

        # Initialize MainWindow
        self.window = MainWindow("Arial", ["Arial", "Times New Roman"])
        
        # Mock StatusBar to capture messages
        self.window.statusBar().showMessage = MagicMock()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.window.close()

    def test_all_menus(self):
        menu_bar = self.window.menuBar()
        results = {}

        for action in menu_bar.actions():
            menu = action.menu()
            if menu:
                self.check_menu(menu, results)
        
        # Print results
        print("\n" + "="*60)
        print("MENU VERIFICATION RESULTS")
        print("="*60)
        
        working = []
        not_implemented = []
        crashed = []
        
        for name, status in results.items():
            if status == "OK":
                working.append(name)
            elif status == "Not Implemented":
                not_implemented.append(name)
            else:
                crashed.append(f"{name} ({status})")
                
        print(f"\n[ WORKING: {len(working)} ]")
        for item in working:
            print(f"  OK  {item}")
            
        print(f"\n[ NOT IMPLEMENTED: {len(not_implemented)} ]")
        for item in not_implemented:
            print(f"  --  {item}")
            
        print(f"\n[ CRASHED/ERROR: {len(crashed)} ]")
        for item in crashed:
            print(f"  XX  {item}")
            
        print("="*60)

    def check_menu(self, menu, results, parent_name=""):
        title = menu.title().replace("&", "")
        if parent_name:
            title = f"{parent_name} > {title}"
            
        for action in menu.actions():
            if action.isSeparator():
                continue
                
            if action.menu():
                self.check_menu(action.menu(), results, title)
                continue
                
            action_text = action.text().replace("&", "")
            full_name = f"{title} > {action_text}"
            
            try:
                # Reset mock
                self.window.statusBar().showMessage.reset_mock()
                
                # Trigger action
                action.trigger()
                
                # Check status bar
                calls = self.window.statusBar().showMessage.call_args
                if calls:
                    msg = calls[0][0]
                    if "Not implemented" in msg or "Not fully implemented" in msg:
                        results[full_name] = "Not Implemented"
                    else:
                        results[full_name] = "OK"
                else:
                    # No message means it probably did something (like open a dialog) or just worked silently
                    results[full_name] = "OK"
                    
            except Exception as e:
                results[full_name] = f"Error: {str(e)}"

if __name__ == '__main__':
    unittest.main()
