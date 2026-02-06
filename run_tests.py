# Simple test to verify the basic application works
import sys
import os
sys.path.insert(0, r'd:\Inpage 2026\UrduPage')

print("TEST 1: Import modules")
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
    print("  [OK] PyQt6 imports work")
except Exception as e:
    print(f"  [FAIL] PyQt6 import failed: {e}")
    sys.exit(1)

print("\nTEST 2: Create simple Qt window")
try:
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Qt Test Window")
    button = QPushButton("Test Button", window)
    window.setCentralWidget(button)
    window.resize(400, 300)
    print("  [OK] Simple Qt window created")
    window.show()
    print("  [OK] Window shown - you should see a window with a button")
    print("\nClose the window to continue tests...")
    app.exec()
except Exception as e:
    print(f"  [FAIL] Qt window failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTEST 3: Import our modules")
try:
    from src.engine.text_box import TextBox
    print("  [OK] TextBox imports")
    from src.engine.page_manager import PageManager
    print("  [OK] PageManager imports")
    from src.ui.document_view import DocumentView
    print("  [OK] DocumentView imports")
    from src.ui.main_window import MainWindow
    print("  [OK] MainWindow imports")
except Exception as e:
    print(f"  [FAIL] Module import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTEST 4: Create PageManager")
try:
    pm = PageManager()
    print(f"  [OK] PageManager created with {pm.page_count()} page(s)")
except Exception as e:
    print(f"  [FAIL] PageManager creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTEST 5: Create DocumentView")
try:
    app2 = QApplication.instance() or QApplication(sys.argv)
    dv = DocumentView("Arial")
    print("  [OK] DocumentView created")
    print(f"     - Has page_manager: {hasattr(dv, 'page_manager')}")
    print(f"     - Has drawing_shape: {hasattr(dv, 'drawing_shape')}")
    print(f"     - Has linking_source: {hasattr(dv, 'linking_source')}")
except Exception as e:
    print(f"  [FAIL] DocumentView creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTEST 6: Create MainWindow")
try:
    app3 = QApplication.instance() or QApplication(sys.argv)
    mw = MainWindow("Arial", ["Arial", "Times New Roman"])
    print("  [OK] MainWindow created")
    mw.show()
    print("  [OK] MainWindow shown - you should see the full page26 interface")
    print("\nClose the window or press Ctrl+C to exit")
    sys.exit(app3.exec())
except Exception as e:
    print(f"  [FAIL] MainWindow failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
