"""
Build script to create a standalone Windows executable.
Run this script to create FileOrganizer.exe - no installation needed!
"""
import subprocess
import sys
import shutil
from pathlib import Path

def build():
    print("🏗️  Building File Organizer for Windows...")
    print()

    # Clean previous builds
    for dir_name in ['build', 'dist']:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"🧹 Cleaning {dir_name}/...")
            shutil.rmtree(dir_path)

    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=FileOrganizer",
        "--onefile",
        "--windowed",  # No console window
        "--icon=NONE",  # You can add an icon later
        "--clean",
        # Add hidden imports
        "--hidden-import=tkinter",
        "--hidden-import=sqlite3",
        # Main file
        "file_organizer_gui.py"
    ]

    print("📦 Running PyInstaller...")
    print()

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)

        print()
        print("✅ Build successful!")
        print()
        print("📁 Your executable is ready:")
        print(f"   dist/FileOrganizer.exe")
        print()
        print("🚀 You can now:")
        print("   1. Copy FileOrganizer.exe to any folder")
        print("   2. Run it - no installation needed!")
        print("   3. Share it with others")
        print()
        print("💡 The .exe is completely portable and self-contained")

    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print()
        print("Error output:")
        print(e.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    build()
