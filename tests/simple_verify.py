import sys
import os
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu, QMenuBar, QStatusBar
from PyQt6.QtGui import QAction

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Starting simple verification...")

try:
    from src.ui.main_window import MainWindow
    print("Imported MainWindow")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def main():
    app = QApplication(sys.argv)
    print("QApplication created")

    # Mock dependencies
    patcher_dialog = patch('PyQt6.QtWidgets.QDialog.exec', return_value=0)
    patcher_dialog.start()
    
    patcher_open = patch('PyQt6.QtWidgets.QFileDialog.getOpenFileName', return_value=('', ''))
    patcher_open.start()
    
    patcher_save = patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName', return_value=('', ''))
    patcher_save.start()
    
    patcher_msg = patch('PyQt6.QtWidgets.QMessageBox.information')
    patcher_msg.start()
    
    patcher_about = patch('PyQt6.QtWidgets.QMessageBox.about')
    patcher_about.start()

    try:
        window = MainWindow("Arial", ["Arial", "Times New Roman"])
        print("MainWindow created")
        
        # Mock StatusBar
        window.statusBar().showMessage = MagicMock()
        
        menu_bar = window.menuBar()
        results = {}
        
        def check_menu(menu, parent_name=""):
            title = menu.title().replace("&", "")
            if parent_name:
                title = f"{parent_name} > {title}"
                
            for action in menu.actions():
                if action.isSeparator():
                    continue
                    
                if action.menu():
                    check_menu(action.menu(), title)
                    continue
                    
                action_text = action.text().replace("&", "")
                full_name = f"{title} > {action_text}"
                
                try:
                    window.statusBar().showMessage.reset_mock()
                    action.trigger()
                    
                    calls = window.statusBar().showMessage.call_args
                    if calls:
                        msg = calls[0][0]
                        if "Not implemented" in msg or "Not fully implemented" in msg:
                            results[full_name] = "Not Implemented"
                        else:
                            results[full_name] = "OK"
                    else:
                        results[full_name] = "OK"
                except Exception as e:
                    results[full_name] = f"Error: {str(e)}"

        for action in menu_bar.actions():
            menu = action.menu()
            if menu:
                check_menu(menu)
                
        # Report
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

    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        patcher_dialog.stop()
        patcher_open.stop()
        patcher_save.stop()
        patcher_msg.stop()
        patcher_about.stop()

if __name__ == "__main__":
    main()
