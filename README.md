# 📝 PDF Translator 🌍

> Turn Chinese PDFs into English with AI-powered translation! Perfect for presentations, documents, and research papers. Come and try it!

## ✨ Features

- 🔄 Convert PDF documents to high-quality images
- 🔍 Detect and extract text from images using AI vision models
- 🇨🇳 ➡️ 🇬🇧 Translate Chinese text to English automatically
- 📊 Maintain the original layout and formatting
- 📱 User-friendly web interface with progress tracking
- 🖼️ Preview translated pages before downloading
- 📄 Generate new PDFs with the translated content
- 🔧 Both command line and web interfaces available

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- pip package manager
- ModelScope API key (get it from [ModelScope](https://modelscope.cn/))

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ppt_translator.git
cd ppt_translator
```

### Step 2: Set Up a Virtual Environment (Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate on macOS/Linux
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Your API Key 🔑

This application requires a ModelScope API key to access translation services. You need to set it as an environment variable:

**On macOS/Linux:**
```bash
export MODELSCOPE_API_KEY="your-api-key-here"
```

**On Windows:**
```bash
set MODELSCOPE_API_KEY=your-api-key-here
```

**Permanently add to your profile (optional):**
- For bash (add to ~/.bashrc or ~/.bash_profile):
  ```bash
  echo 'export MODELSCOPE_API_KEY="your-api-key-here"' >> ~/.bashrc
  source ~/.bashrc
  ```
- For zsh (add to ~/.zshrc):
  ```bash
  echo 'export MODELSCOPE_API_KEY="your-api-key-here"' >> ~/.zshrc
  source ~/.zshrc
  ```
- For Windows, add a System Environment Variable through Control Panel.

## 🚀 Quick Start

### Web Interface

The easiest way to use PDF Translator is through the web interface:

```bash
python main.py --web
```

This will launch a browser interface where you can:
1. 📂 Upload PDF files
2. ⏳ Watch real-time translation progress
3. 👁️ Preview translated pages
4. 💾 Download the translated PDF

### Command Line Interface

For batch processing or integration with other tools:

```bash
python main.py path/to/your/file.pdf -o output_directory
```

## 📋 Detailed Usage Guide

### Web Interface Instructions

1. **Upload PDF** 📤
   - Click on the "Upload a PDF file" area
   - Select any PDF containing Chinese text
   - Wait for the upload to complete

2. **Translation Process** ⚙️
   - Click the "Translate PDF" button
   - The system will show progress through each stage:
     - Converting PDF to images
     - Identifying text regions
     - Translating content
     - Generating the final PDF

3. **View Results** 👓
   - Switch to the "Page Preview" tab to see each translated page
   - Check the translation quality and layout

4. **Download** 📥
   - Go to the "Translated PDF" tab
   - Click "Download Translated PDF" to save the translated document

### Command Line Options

```
python main.py [-h] [-o OUTPUT] [--web] [pdf_path]

Arguments:
  pdf_path              Path to the PDF file
  
Options:
  -h, --help            Show this help message
  -o OUTPUT, --output OUTPUT
                        Output directory for the translated PDF (default: outputs)
  --web                 Launch the web interface
```

## 🧩 How It Works

PDF Translator uses a multi-step process to deliver high-quality translations:

1. **PDF Conversion** 📄➡️🖼️
   - The PDF is converted to high-resolution images using PyMuPDF
   - Each page becomes a separate image file

2. **Text Detection** 🔍
   - Qwen Vision-Language model analyzes each image
   - Detects text regions and their positions on the page
   - Extracts Chinese text while preserving layout information

3. **Translation** 🔄
   - Each detected text segment is sent to the translation API
   - Chinese text is translated to English

4. **Rendering** 🎨
   - The translated text is overlaid on the original images
   - Layout and positioning are preserved

5. **PDF Generation** 🔄➡️📑
   - Translated images are compiled back into a PDF document
   - Pages are sorted in the correct order using natural sorting

## 🔧 Troubleshooting

### API Key Issues

If you see a warning about missing API key:

1. Make sure you've set the MODELSCOPE_API_KEY environment variable
2. Verify the key is correct and has necessary permissions
3. Try closing and reopening your terminal after setting the variable
4. For web applications, you may need to restart the server

### PyMuPDF Installation Issues

If you encounter `ModuleNotFoundError: No module named 'frontend'` when importing PyMuPDF:

```bash
# Reinstall PyMuPDF correctly
pip uninstall PyMuPDF fitz
pip install PyMuPDF
```

### Image Sorting Issues

If pages appear in the wrong order in your output PDF:

- Check the file naming system for your intermediate images
- The program uses natural sorting (so page10 comes after page2, not page1)

### Translation Quality

For the best translation results:

- Ensure the original PDF has clear, readable text
- Use scanned PDFs with at least 300 DPI resolution
- For complex layouts, check the page previews before downloading

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

- Report bugs and issues
- Suggest new features
- Submit pull requests with improvements
- Help with documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Qwen Vision-Language model for text detection and layout analysis
- ModelScope for API services
- ReportLab and PyMuPDF for PDF handling
- Gradio for the web interface
