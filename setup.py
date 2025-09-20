# setup.py - Automated setup script for PDF Organizer
import os
from pathlib import Path

def create_project_structure():
    """Create the complete project structure"""
    
    # Create directories
    directories = [
        "src",
        "src/core", 
        "src/ui"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/core/__init__.py", 
        "src/ui/__init__.py"
    ]
    
    for init_file in init_files:
        Path(init_file).touch()
        print(f"✅ Created: {init_file}")

def create_requirements_file():
    """Create requirements.txt file"""
    requirements = """streamlit>=1.28.0
PyPDF2>=3.0.0
pathlib
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    print("✅ Created requirements.txt")

def create_run_script():
    """Create easy run script"""
    run_script = """#!/bin/bash
# run.sh - Easy run script

echo "🚀 Starting PDF Organizer..."
echo "📝 Installing dependencies..."
pip install -r requirements.txt

echo "🌐 Launching Streamlit app..."
streamlit run main.py
"""
    
    with open("run.sh", "w") as f:
        f.write(run_script)
    
    # Make executable on Unix systems
    try:
        os.chmod("run.sh", 0o755)
    except:
        pass
    
    print("✅ Created run.sh")

def create_readme():
    """Create comprehensive README"""
    readme = """# 📚 PDF Page Organizer

A powerful tool to organize PDF books into structured folder hierarchies with individual page extraction.

## 🚀 Quick Start

### Option 1: One-Command Start (Unix/Mac)
```bash
chmod +x run.sh
./run.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run main.py
```

## ✨ Features

- 📤 **PDF Upload & Validation**: Upload and validate PDF files
- 🏗️ **Project Structure**: Create organized folder hierarchies
- 📂 **Chapter Management**: Configure chapters within book parts
- 📄 **Page Extraction**: Extract individual pages to specific folders
- 🎯 **Flexible Ranges**: Support for "1-5, 10, 15-20" page range formats
- 📊 **Progress Tracking**: Visual feedback throughout the process
- 🔄 **History Management**: Track all completed extractions

## 📖 How to Use

1. **Upload PDF**: Select your book PDF file
2. **Configure Project**: Enter project code and book name
3. **Set Parts**: Specify number of main parts
4. **Create Structure**: Generate basic folder structure
5. **Setup Chapters**: Configure chapters within parts (optional)
6. **Extract Pages**: Assign page ranges to specific folders

## 📁 Generated Structure Example

```
CS101_DataStructures/
├── CS101_DataStructures_prologue/
│   ├── CS101_DataStructures_prologue_page_1.pdf
│   └── CS101_DataStructures_prologue_page_2.pdf
├── CS101_DataStructures_part_1/
│   ├── CS101_DataStructures_part_1_1_Introduction/
│   │   ├── CS101_DataStructures_part_1_1_Introduction_page_10.pdf
│   │   └── CS101_DataStructures_part_1_1_Introduction_page_11.pdf
│   └── CS101_DataStructures_part_1_page_25.pdf
└── CS101_DataStructures_index/
    └── CS101_DataStructures_index_page_300.pdf
```

## 🔧 System Requirements

- Python 3.7 or higher
- Web browser (for Streamlit interface)
- Write permissions in the working directory

## 🐛 Troubleshooting

### Common Issues:

1. **Import Errors**: Ensure all dependencies are installed
2. **PDF Reading Issues**: Try a different PDF file
3. **Permission Errors**: Run from a writable directory
4. **Port Issues**: If port 8501 is busy, Streamlit will suggest alternatives

### Need Help?

- Check the Progress tracker in the app
- Review error messages carefully
- Ensure PDF file is not corrupted or password-protected

## 📝 File Naming Convention

- **Default folders**: `{code}_{bookname}_{foldername}_page_{number}.pdf`
- **Part folders**: `{code}_{bookname}_part_{num}_page_{number}.pdf`
- **Chapter folders**: `{code}_{bookname}_part_{num}_{chapter_num}_{chapter_name}_page_{number}.pdf`

## 🎯 Tips for Best Results

1. Use descriptive project codes and book names
2. Test with smaller PDFs first
3. Use clear chapter naming conventions
4. Preview assignments before extracting
5. Keep page ranges reasonable (avoid extracting entire books at once)

## 📊 Performance Notes

- Processing time depends on PDF size and page count
- Large extractions (50+ pages) may take a few minutes
- Individual page PDFs are saved immediately as they're processed

---

**Developed with ❤️ using Streamlit and PyPDF2**
"""
    
    with open("README.md", "w") as f:
        f.write(readme)
    print("✅ Created README.md")

def main():
    """Run the complete setup"""
    print("🔧 Setting up PDF Organizer...")
    print("=" * 50)
    
    create_project_structure()
    create_requirements_file()
    create_run_script()
    create_readme()
    
    print("=" * 50)
    print("✅ Setup complete!")
    print()
    print("📝 Next steps:")
    print("1. Copy the code files from the main artifact into their respective locations")
    print("2. Run: pip install -r requirements.txt")
    print("3. Run: streamlit run main.py")
    print()
    print("🚀 Or simply run: ./run.sh (on Unix/Mac)")

if __name__ == "__main__":
    main()