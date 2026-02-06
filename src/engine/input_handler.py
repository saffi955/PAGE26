from PyQt6.QtCore import Qt

class InputHandler:
    def __init__(self):
        self.phonetic_map = {
            'a': 'ا', 'A': 'آ', 'b': 'ب', 'B': 'ب', 'c': 'چ', 'C': 'ث',
            'd': 'د', 'D': 'ڈ', 'e': 'ع', 'E': 'ے', 'f': 'ف', 'F': 'غ',
            'g': 'گ', 'G': 'غ', 'h': 'ح', 'H': 'ھ', 'i': 'ی', 'I': 'ی',
            'j': 'ج', 'J': 'ض', 'k': 'ک', 'K': 'خ', 'l': 'ل', 'L': 'ل',
            'm': 'م', 'M': 'م', 'n': 'ن', 'N': 'ں', 'o': 'ہ', 'O': 'ہ',
            'p': 'پ', 'P': 'پ', 'q': 'ق', 'Q': 'ق', 'r': 'ر', 'R': 'ڑ',
            's': 'س', 'S': 'ص', 't': 'ت', 'T': 'ٹ', 'u': 'ء', 'U': 'ئ',
            'v': 'ط', 'V': 'ظ', 'w': 'و', 'W': 'و', 'x': 'ش', 'X': 'ژ',
            'y': 'ے', 'Y': 'ے', 'z': 'ز', 'Z': 'ذ',
            ' ': ' ', '.': '۔', ',': '،', '?': '؟'
        }
        self.current_language = 'UR'  # Track current language

    def set_language(self, lang):
        """Set current input language"""
        self.current_language = lang
        print(f"DEBUG: Language set to {lang}")  # Debug output

    def process_key(self, event):
        if self.current_language == 'EN':
            return None  # Let default English input through
            
        text = event.text()
        if not text:
            return None
            
        # Debug output
        print(f"DEBUG: Processing key '{text}', language={self.current_language}")
            
        # Return mapped Urdu character
        mapped_char = self.phonetic_map.get(text, text)
        print(f"DEBUG: Mapped '{text}' to '{mapped_char}'")
        return mapped_char