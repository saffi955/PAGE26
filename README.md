# page26

**page26** is an advanced Urdu desktop publishing application that represents an upgraded version of InPage with modern AI integration. Similar to how Adobe software like Photoshop and Illustrator have integrated AI capabilities, page26 combines traditional desktop publishing features with intelligent AI assistance for writing, editing, and formatting.

## 📝 Description

page26 is an advanced Urdu desktop publishing application that upgrades InPage with modern AI integration. It features built-in templates and an AI assistant to help with writing, editing, and formatting, bringing Adobe-style AI capabilities to Urdu DTP.

## 🚀 Features

### Core Desktop Publishing Features
- **Multi-document Interface (MDI)**: Work with multiple documents simultaneously
- **Rich Text Editing**: Full-featured text box editor with Urdu font support
- **Document Management**: Create, open, save, and export documents
- **Page Management**: Flexible page settings and layout options
- **Print Support**: Print documents with printer setup options

### Built-in Templates
- Pre-designed templates to jumpstart your projects
- Professional layouts for various document types
- Easy template customization

### AI Assistant Integration
- **AI Writing Assistant**: Get help with content creation and writing
- **AI Editing Support**: Intelligent text editing and refinement
- **AI Formatting**: Automated formatting suggestions and improvements
- **Smart Content Generation**: Generate content with AI assistance

### Advanced Text Features
- **Character Formatting**: Comprehensive character dialog for font, size, style, and color
- **Paragraph Formatting**: Advanced paragraph dialog for alignment, spacing, and indentation
- **Find & Replace**: Powerful search and replace functionality
- **Hyphenation**: Automatic text hyphenation support
- **Word Count**: Real-time word count tracking

### Layout & Design Tools
- **Text Boxes**: Flexible text box creation and manipulation
- **Shape Tools**: Create and edit various shapes
- **Table Support**: Insert and format tables
- **Border Dialog**: Customize borders and frames
- **Ruler**: Visual rulers for precise layout

### Urdu Language Support
- **Urdu Fonts**: Built-in support for popular Urdu fonts including:
  - Jameel Noori Nastaleeq
  - AlQalam Taj Nastaleeq
  - Gandhara Suls
- **Bidirectional Text**: Full support for right-to-left text rendering
- **Language Switching**: Toggle between Urdu and other languages

## 📋 Prerequisites

- **Python 3.8+**
- **PyQt6**: GUI framework
- **qtawesome**: Icon library

## 🔧 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "Inpage 2026/UrduPage"
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install PyQt6 qtawesome
```

## 🎯 Usage

### Running the Application

```bash
python main.py
```

### Creating a New Document

1. Go to **File → New** (or press `Ctrl+N`)
2. Configure your document settings in the dialog:
   - Page size
   - Margins
   - Orientation
   - Other layout options
3. Click **OK** to create the document

### Working with Text

1. Select the text tool from the toolbox
2. Click and drag to create a text box
3. Start typing or paste your content
4. Use the formatting toolbar or dialogs to style your text:
   - **Character Dialog**: Format individual characters
   - **Paragraph Dialog**: Format paragraphs
   - **Find & Replace**: Search and replace text

### Using AI Assistant

- Access AI features through the menu or toolbar
- Get writing suggestions and improvements
- Use AI for content generation and formatting

### Saving Your Work

- **Save**: `Ctrl+S` to save the current document
- **Save As**: `Ctrl+Shift+S` to save with a new name
- Documents are saved in `.upg` format (page26 format)

## 📁 Project Structure

```
UrduPage/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── assets/
│   └── fonts/
│       ├── urdu/          # Urdu font files
│       └── latin/          # Latin font files
├── src/
│   ├── engine/            # Core engine components
│   │   ├── text_box.py    # Text box implementation
│   │   ├── page_manager.py
│   │   └── shape_items.py
│   └── ui/                # User interface components
│       ├── main_window.py  # Main application window
│       ├── document_window.py
│       ├── document_view.py
│       └── dialogs/       # Various dialog windows
│           ├── character_dialog.py
│           ├── paragraph_dialog.py
│           ├── find_replace_dialog.py
│           ├── table_dialog.py
│           └── ...
└── tests/                 # Test files
```

## 🛠️ Development

### Running Tests

```bash
python run_tests.py
```

### Testing Startup

```bash
python test_startup.py
```

## 🎨 Key Features in Detail

### Text Box System
- Locked and unlocked text boxes
- Resizable and movable text containers
- Rich text editing capabilities
- Font family support

### Document Management
- Recent files tracking
- Import/Export functionality
- Document reversion
- Multiple document windows

### UI Components
- Modern toolbar with icons
- Status bar with word count
- Property ribbon for quick formatting
- Toolbox for drawing tools

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

[Specify your license here]

## 🙏 Acknowledgments

- Built on PyQt6 framework
- Inspired by InPage desktop publishing software
- Enhanced with modern AI capabilities

## 📞 Support

For issues, questions, or contributions, please open an issue on the repository.

---

**page26** - Modern Urdu Desktop Publishing with AI Integration

