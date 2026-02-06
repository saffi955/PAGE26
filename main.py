import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont
from src.ui.main_window import MainWindow

def load_fonts():
    base_dir = os.path.dirname(__file__)
    urdu_font_dir = os.path.join(base_dir, 'assets', 'fonts', 'urdu')
    
    loaded_families = []
    
    # Load only from assets/fonts/urdu
    if os.path.exists(urdu_font_dir):
        for filename in os.listdir(urdu_font_dir):
            if filename.lower().endswith((".ttf", ".otf")):
                font_path = os.path.join(urdu_font_dir, filename)
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    if families:
                        loaded_families.extend(families)
                        print(f"Loaded font: {families[0]} from {filename}")
    
    # Add fallback fonts
    if not loaded_families:
        loaded_families = ["Arial", "Times New Roman"]
        print("No Urdu fonts found, using fallback fonts")
    else:
        print(f"Successfully loaded {len(loaded_families)} Urdu fonts")
    
    return loaded_families

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("page26")
    
    # Load Fonts
    font_families = load_fonts()
    
    # Default Nastaliq
    default_font = "Jameel Noori Nastaleeq" if "Jameel Noori Nastaleeq" in font_families else "Arial"
    if not font_families:
        font_families = ["Arial"]

    window = MainWindow(default_font, font_families)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print("=" * 60)
        print("APPLICATION STARTUP ERROR:")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        input("Press Enter to exit...")
