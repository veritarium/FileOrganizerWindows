# File Organizer for Windows

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)]()

A **simple, portable Windows application** for organizing your files using virtual views. No installation required - just download and run the `.exe` file!

## Key Features

- **Zero Installation** - Single executable file, runs immediately
- **Simple GUI** - Easy-to-use graphical interface
- **Virtual Organization** - Creates symbolic links without moving files
- **Multiple Views** - Organize by category, date, size, or find duplicates
- **Safe** - Original files are never modified or moved
- **Real-time Progress** - Status bar and detailed logs show what's happening

## Quick Start

### Option 1: Download Pre-built Executable (Recommended)

1. Download `FileOrganizer.exe` from the [Releases page](https://github.com/yourusername/FileOrganizerWindows/releases)
2. Double-click to run - no installation needed!
3. Select your folder and start organizing

### Option 2: Build from Source

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/FileOrganizerWindows.git
cd FileOrganizerWindows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run directly
python file_organizer_gui.py

# OR build your own .exe
python build_exe.py
# Your .exe will be in the dist/ folder
```

## How to Use

### Step 1: Select Directory

1. Click **"Browse..."** button
2. Choose your top-level folder (e.g., `C:\Users\YourName\Documents`)
3. All operations will work within this folder

### Step 2: Scan Files

1. Click **"Scan Files"** button
2. Wait for the scan to complete (progress shown in status bar)
3. Files are cataloged in a hidden database (`.file_organizer.db`)

### Step 3: Organize

Choose one or more organization methods:

#### Organize by Category
Creates folders organized by file type:
```
_Views/
  ByCategory/
    Documents/
      PDF/
        invoice.pdf -> C:\...\original_invoice.pdf
      Word/
        report.docx -> C:\...\original_report.docx
    Images/
      Photos/
        vacation.jpg -> C:\...\original_vacation.jpg
    CAD/
      AutoCAD/
        drawing.dwg -> C:\...\original_drawing.dwg
```

#### Organize by Date
Creates folders by modification date:
```
_Views/
  ByDate/
    2025/
      01-January/
        document.pdf -> C:\...\original_document.pdf
      02-February/
        photo.jpg -> C:\...\original_photo.jpg
```

#### Organize by Size
Groups files by size ranges:
```
_Views/
  BySize/
    Small (1 KB - 1 MB)/
      tiny_file.txt -> C:\...\original_tiny_file.txt
    Large (10-100 MB)/
      video.mp4 -> C:\...\original_video.mp4
```

#### Find Duplicates
Detects duplicate files and groups them:
```
_Views/
  Duplicates/
    document_duplicates/
      document.pdf -> C:\...\location1\document.pdf
      document.pdf -> C:\...\location2\document.pdf
```

## Features in Detail

### Supported File Types

The application recognizes **70+ file types** including:

- **Documents**: PDF, Word, Excel, PowerPoint, Text files
- **Images**: JPG, PNG, GIF, BMP, SVG, AI
- **CAD Files**: DWG, DXF, SKP
- **Videos**: MP4, AVI, MKV, MOV
- **Audio**: MP3, WAV, FLAC
- **Archives**: ZIP, RAR, 7Z, TAR
- **Code**: Python, JavaScript, Java, C++, HTML, CSS

### Safety Features

- **Read-only operations** - Original files are never touched
- **Symbolic links** - Virtual organization with zero storage overhead
- **Hidden database** - All metadata stored in `.file_organizer.db`
- **Skip _Views folder** - The tool ignores its own virtual views during scans

### Status Bar

The status bar shows:
- Current operation (Scanning, Organizing, etc.)
- Progress indication
- Completion messages
- Error notifications

### Output Log

The main text area displays:
- Detailed operation logs
- File counts and statistics
- Errors and warnings
- View locations

## System Requirements

- **OS**: Windows 10 or later (Windows 11 recommended)
- **Python**: 3.11+ (only if building from source)
- **Permissions**: Administrator privileges may be required for symbolic links
  - **Tip**: Enable Developer Mode in Windows Settings to avoid admin prompts

### Enabling Developer Mode (Recommended)

1. Open **Settings** → **Privacy & Security** → **For developers**
2. Turn on **Developer Mode**
3. Restart if prompted
4. Now you can create symbolic links without admin rights!

## Building from Source

### Prerequisites

```bash
# Install Python 3.11 or later
# Download from https://www.python.org/downloads/

# Install dependencies
pip install -r requirements.txt
```

### Build Executable

```bash
# Run the build script
python build_exe.py

# Your executable will be in:
dist/FileOrganizer.exe

# Test it
cd dist
FileOrganizer.exe
```

### Build Options

The build script uses PyInstaller with these options:
- `--onefile` - Single executable file
- `--windowed` - No console window (GUI only)
- `--clean` - Clean build directory first
- Hidden imports for tkinter and sqlite3

## Troubleshooting

### "Permission Denied" when creating symbolic links

**Solution**: Enable Developer Mode (see above) or run as Administrator

### "Module not found" error when building

**Solution**:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Application won't start

**Solution**:
- Ensure you're on Windows 10 or later
- Try running from command prompt to see error messages
- Check antivirus didn't block the .exe

### Scan is slow

**Solution**:
- This is normal for folders with many files
- Close other applications during scan
- Consider scanning smaller folders first

### Links don't work

**Solution**:
- Ensure Developer Mode is enabled
- Run as Administrator
- Check that original files still exist

## FAQ

**Q: Does this move my files?**
A: No! It only creates symbolic links (shortcuts) to organize views.

**Q: Can I delete the _Views folder?**
A: Yes! It only contains links. Deleting it won't affect your original files.

**Q: What is the .file_organizer.db file?**
A: It's a hidden SQLite database containing file metadata. Safe to delete if you want to rescan.

**Q: Can I organize multiple folders?**
A: Yes! Just select a different folder and scan again. Each folder gets its own database.

**Q: What happens if I move the original files?**
A: The symbolic links will break. You'll need to rescan and reorganize.

**Q: Is this safe for production files?**
A: Yes! The tool only reads files, never modifies them. However, always keep backups of important data.

## Known Limitations

- Requires Windows 10 or later
- Symbolic links need Developer Mode or admin rights
- Large scans (60,000+ files) may take several minutes
- Duplicate detection requires computing file hashes (slower for large files)

## Project Structure

```
FileOrganizerWindows/
├── file_organizer_gui.py    # Main GUI application
├── build_exe.py              # Build script for .exe
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── dist/                     # Build output (after running build_exe.py)
    └── FileOrganizer.exe     # Standalone executable
```

## Technical Details

### Architecture

- **GUI Framework**: tkinter (built into Python)
- **Database**: SQLite3 (built into Python)
- **Hashing**: SHA-256 via hashlib (built into Python)
- **Threading**: Background threads for non-blocking UI
- **Build Tool**: PyInstaller for standalone .exe

### File Categorization

Files are categorized using:
1. Extension-based mapping (70+ types)
2. Filename pattern matching (e.g., "screenshot" → Images/Screenshots)
3. Fallback to "Miscellaneous/Unknown"

### Duplicate Detection

1. Computes SHA-256 hash for each file
2. Groups files with identical hashes
3. Calculates wasted space
4. Creates organized view in _Views/Duplicates/

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/FileOrganizerWindows/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/FileOrganizerWindows/discussions)

## Related Projects

This is a simplified Windows GUI version of the full-featured [Virtual File Organizer](https://github.com/veritarium/Metafileorg) project.

For advanced features like:
- Custom view definitions (YAML rules)
- Web-based search interface
- Advanced metadata extraction
- Project detection
- Command-line interface

Check out the full version!

## Disclaimer

This tool creates symbolic links to organize files virtually. While it does not modify original files:

- Always have **backups** of important data
- Test with a **small dataset** first
- Understand that symbolic links are **pointers** to original files
- The authors are not responsible for any data loss

**Use at your own risk.**

---

**Made with love for file organization on Windows** ❤️

*Star this repo if you find it useful!* ⭐
