import sys
sys.path.insert(0, r'd:\Inpage 2026\UrduPage')

try:
    print("Step 1: Importing PyQt6...")
    from PyQt6.QtWidgets import QApplication
    print("✓ PyQt6 imported")
    
    print("\nStep 2: Creating QApplication...")
    app = QApplication(sys.argv)
    print("✓ QApplication created")
    
    print("\nStep 3: Importing MainWindow...")
    from src.ui.main_window import MainWindow
    print("✓ MainWindow imported")
    
    print("\nStep 4: Loading fonts...")
    from PyQt6.QtGui import QFontDatabase
    import os
    font_dir = r'd:\Inpage 2026\installed inpage data'
    loaded_families = []
    if os.path.exists(font_dir):
        for filename in os.listdir(font_dir):
            if filename.lower().endswith(".ttf"):
                font_path = os.path.join(font_dir, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        loaded_families.extend(families)
    print(f"✓ Loaded {len(loaded_families)} fonts")
    
    print("\nStep 5: Creating MainWindow...")
    window = MainWindow("Noori Nastaliq", loaded_families if loaded_families else ["Arial"])
    print("✓ MainWindow created")
    
    print("\nStep 6: Showing window...")
    window.show()
    print("✓ Window shown")
    
    print("\nStep 7: Starting event loop...")
    sys.exit(app.exec())
    
except Exception as e:
    import traceback
    print("\n" + "="*60)
    print("ERROR:")
    print("="*60)
    traceback.print_exc()
    print("="*60)
    input("\nPress Enter to exit...")
