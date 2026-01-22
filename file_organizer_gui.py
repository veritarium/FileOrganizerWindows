"""
File Organizer - Windows GUI Version
A simple, portable file organization tool with graphical interface.
No installation required - just run the .exe!
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
import threading
import yaml
import json

class FileOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer - Windows Edition")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Variables
        self.base_directory = tk.StringVar()
        self.db_path = None
        self.is_scanning = False
        self.categories = self.load_default_categories()

        # Create GUI
        self.create_widgets()

    def create_widgets(self):
        """Create all GUI widgets"""

        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="📁 File Organizer",
                               font=("Segoe UI", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)

        # Directory Selection Frame
        dir_frame = ttk.LabelFrame(main_frame, text="Step 1: Select Directory", padding="10")
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        dir_frame.columnconfigure(1, weight=1)

        ttk.Label(dir_frame, text="Top-level folder:").grid(row=0, column=0, sticky=tk.W, padx=5)

        dir_entry = ttk.Entry(dir_frame, textvariable=self.base_directory, width=50)
        dir_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)

        browse_btn = ttk.Button(dir_frame, text="Browse...", command=self.browse_directory)
        browse_btn.grid(row=0, column=2, padx=5)

        # Info label
        info_label = ttk.Label(dir_frame, text="ℹ️ All operations will work on files within this directory",
                              foreground="blue", font=("Segoe UI", 8))
        info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        # Actions Frame
        actions_frame = ttk.LabelFrame(main_frame, text="Step 2: Choose Action", padding="10")
        actions_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        actions_frame.columnconfigure(2, weight=1)

        self.scan_btn = ttk.Button(actions_frame, text="📊 Scan Files",
                                    command=self.scan_files, width=20)
        self.scan_btn.grid(row=0, column=0, padx=5, pady=5)

        self.organize_btn = ttk.Button(actions_frame, text="📁 Organize by Category",
                                       command=self.organize_by_category, width=20, state=tk.DISABLED)
        self.organize_btn.grid(row=0, column=1, padx=5, pady=5)

        self.duplicates_btn = ttk.Button(actions_frame, text="🔍 Find Duplicates",
                                         command=self.find_duplicates, width=20, state=tk.DISABLED)
        self.duplicates_btn.grid(row=0, column=2, padx=5, pady=5)

        self.date_btn = ttk.Button(actions_frame, text="📅 Organize by Date",
                                    command=self.organize_by_date, width=20, state=tk.DISABLED)
        self.date_btn.grid(row=1, column=0, padx=5, pady=5)

        self.size_btn = ttk.Button(actions_frame, text="📏 Organize by Size",
                                    command=self.organize_by_size, width=20, state=tk.DISABLED)
        self.size_btn.grid(row=1, column=1, padx=5, pady=5)

        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        self.status_label = ttk.Label(progress_frame, text="Ready. Select a directory to begin.",
                                      font=("Segoe UI", 9))
        self.status_label.grid(row=1, column=0, sticky=tk.W)

        # Output/Log Frame
        output_frame = ttk.LabelFrame(main_frame, text="Results & Status", padding="10")
        output_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)

        self.output_text = scrolledtext.ScrolledText(output_frame, height=15,
                                                     font=("Consolas", 9), wrap=tk.WORD)
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Bottom status bar
        status_bar = ttk.Frame(main_frame)
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        self.bottom_status = ttk.Label(status_bar, text="Version 1.0 | Ready",
                                       relief=tk.SUNKEN, anchor=tk.W)
        self.bottom_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Initial message
        self.log("👋 Welcome to File Organizer!")
        self.log("📝 Instructions:")
        self.log("   1. Click 'Browse' to select your top-level directory")
        self.log("   2. Click 'Scan Files' to analyze your files")
        self.log("   3. Choose an organization method")
        self.log("")
        self.log("💡 All virtual views will be created in a '_Views' subfolder")
        self.log("💡 Original files are NEVER moved or modified - only links are created")
        self.log("")

    def browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(title="Select Top-Level Directory")
        if directory:
            self.base_directory.set(directory)
            self.db_path = os.path.join(directory, ".file_organizer.db")
            self.log(f"📂 Selected directory: {directory}")
            self.log(f"💾 Database will be stored at: {self.db_path}")
            self.update_status("Directory selected. Ready to scan.")

    def scan_files(self):
        """Scan files in the selected directory"""
        if not self.base_directory.get():
            messagebox.showwarning("No Directory", "Please select a directory first!")
            return

        # Run scan in background thread
        self.is_scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.progress_bar.start()

        thread = threading.Thread(target=self._scan_files_thread, daemon=True)
        thread.start()

    def _scan_files_thread(self):
        """Background thread for scanning"""
        try:
            base_dir = self.base_directory.get()
            self.log(f"\n🔍 Starting scan of: {base_dir}")
            self.update_status("Scanning files...")

            # Create/connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    extension TEXT,
                    size INTEGER,
                    created REAL,
                    modified REAL,
                    category TEXT,
                    subcategory TEXT,
                    hash TEXT
                )
            """)
            conn.commit()

            # Scan files
            file_count = 0
            for root, dirs, files in os.walk(base_dir):
                # Skip _Views directory
                if '_Views' in root:
                    continue

                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        stat = os.stat(file_path)

                        # Get extension
                        ext = Path(file).suffix[1:].lower() if Path(file).suffix else ''

                        # Categorize
                        category, subcategory = self.categorize_file(ext, file)

                        # Insert into database
                        cursor.execute("""
                            INSERT OR REPLACE INTO files
                            (path, name, extension, size, created, modified, category, subcategory)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (file_path, file, ext, stat.st_size, stat.st_ctime,
                              stat.st_mtime, category, subcategory))

                        file_count += 1

                        if file_count % 100 == 0:
                            self.log(f"   Scanned {file_count} files...")

                    except Exception as e:
                        self.log(f"   ⚠️ Error scanning {file}: {str(e)}")

            conn.commit()
            conn.close()

            self.log(f"\n✅ Scan complete! Found {file_count} files")
            self.log(f"💾 Database saved to: {self.db_path}")
            self.update_status(f"Scan complete: {file_count} files indexed")

            # Enable organize buttons
            self.root.after(0, lambda: self.organize_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.duplicates_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.date_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.size_btn.config(state=tk.NORMAL))

        except Exception as e:
            self.log(f"\n❌ Error during scan: {str(e)}")
            self.update_status("Scan failed")

        finally:
            self.is_scanning = False
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress_bar.stop())

    def organize_by_category(self):
        """Organize files by category"""
        if not self.db_path or not os.path.exists(self.db_path):
            messagebox.showwarning("No Data", "Please scan files first!")
            return

        thread = threading.Thread(target=self._organize_by_category_thread, daemon=True)
        thread.start()

    def _organize_by_category_thread(self):
        """Background thread for organizing by category"""
        try:
            self.progress_bar.start()
            self.log("\n📁 Organizing by category...")
            self.update_status("Creating category views...")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all files
            cursor.execute("SELECT path, name, category, subcategory FROM files")
            files = cursor.fetchall()

            base_dir = self.base_directory.get()
            views_dir = os.path.join(base_dir, "_Views", "ByCategory")

            # Create directory structure
            os.makedirs(views_dir, exist_ok=True)

            created = 0
            for file_path, name, category, subcategory in files:
                try:
                    # Create category structure
                    category_dir = os.path.join(views_dir, category or "Unknown",
                                               subcategory or "General")
                    os.makedirs(category_dir, exist_ok=True)

                    # Create symbolic link
                    link_path = os.path.join(category_dir, name)

                    # Remove existing link if present
                    if os.path.exists(link_path):
                        os.remove(link_path)

                    # Create link (Windows: mklink)
                    try:
                        os.symlink(file_path, link_path)
                        created += 1
                    except OSError:
                        # Fallback: try creating shortcut or just skip
                        pass

                except Exception as e:
                    self.log(f"   ⚠️ Error creating link for {name}: {str(e)}")

            conn.close()

            self.log(f"\n✅ Category organization complete!")
            self.log(f"   Created {created} links")
            self.log(f"   📂 View at: {views_dir}")
            self.update_status(f"Category view created: {created} links")

        except Exception as e:
            self.log(f"\n❌ Error organizing by category: {str(e)}")
            self.update_status("Organization failed")

        finally:
            self.root.after(0, lambda: self.progress_bar.stop())

    def _organize_by_date_thread(self):
        """Background thread for organizing by date"""
        try:
            self.progress_bar.start()
            self.log("\n📅 Organizing by date...")
            self.update_status("Creating date views...")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all files
            cursor.execute("SELECT path, name, modified FROM files")
            files = cursor.fetchall()

            base_dir = self.base_directory.get()
            views_dir = os.path.join(base_dir, "_Views", "ByDate")

            # Create directory structure
            os.makedirs(views_dir, exist_ok=True)

            created = 0
            for file_path, name, modified_time in files:
                try:
                    # Convert timestamp to date
                    date = datetime.fromtimestamp(modified_time)
                    year = date.strftime("%Y")
                    month = date.strftime("%m-%B")  # e.g., "01-January"

                    # Create date structure
                    date_dir = os.path.join(views_dir, year, month)
                    os.makedirs(date_dir, exist_ok=True)

                    # Create symbolic link
                    link_path = os.path.join(date_dir, name)

                    # Remove existing link if present
                    if os.path.exists(link_path):
                        os.remove(link_path)

                    # Create link
                    try:
                        os.symlink(file_path, link_path)
                        created += 1
                    except OSError:
                        # Fallback: skip if symlink fails
                        pass

                except Exception as e:
                    self.log(f"   ⚠️ Error creating link for {name}: {str(e)}")

            conn.close()

            self.log(f"\n✅ Date organization complete!")
            self.log(f"   Created {created} links")
            self.log(f"   📂 View at: {views_dir}")
            self.update_status(f"Date view created: {created} links")

        except Exception as e:
            self.log(f"\n❌ Error organizing by date: {str(e)}")
            self.update_status("Organization failed")

        finally:
            self.root.after(0, lambda: self.progress_bar.stop())

    def organize_by_date(self):
        """Organize files by date"""
        if not self.db_path or not os.path.exists(self.db_path):
            messagebox.showwarning("No Data", "Please scan files first!")
            return

        thread = threading.Thread(target=self._organize_by_date_thread, daemon=True)
        thread.start()

    def _organize_by_size_thread(self):
        """Background thread for organizing by size"""
        try:
            self.progress_bar.start()
            self.log("\n📏 Organizing by size...")
            self.update_status("Creating size views...")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all files
            cursor.execute("SELECT path, name, size FROM files")
            files = cursor.fetchall()

            base_dir = self.base_directory.get()
            views_dir = os.path.join(base_dir, "_Views", "BySize")

            # Create directory structure
            os.makedirs(views_dir, exist_ok=True)

            created = 0
            for file_path, name, size in files:
                try:
                    # Categorize by size
                    if size < 1024:  # < 1 KB
                        size_category = "Tiny (< 1 KB)"
                    elif size < 1024 * 1024:  # < 1 MB
                        size_category = "Small (1 KB - 1 MB)"
                    elif size < 10 * 1024 * 1024:  # < 10 MB
                        size_category = "Medium (1-10 MB)"
                    elif size < 100 * 1024 * 1024:  # < 100 MB
                        size_category = "Large (10-100 MB)"
                    else:
                        size_category = "Very Large (> 100 MB)"

                    # Create size structure
                    size_dir = os.path.join(views_dir, size_category)
                    os.makedirs(size_dir, exist_ok=True)

                    # Create symbolic link
                    link_path = os.path.join(size_dir, name)

                    # Remove existing link if present
                    if os.path.exists(link_path):
                        os.remove(link_path)

                    # Create link
                    try:
                        os.symlink(file_path, link_path)
                        created += 1
                    except OSError:
                        # Fallback: skip if symlink fails
                        pass

                except Exception as e:
                    self.log(f"   ⚠️ Error creating link for {name}: {str(e)}")

            conn.close()

            self.log(f"\n✅ Size organization complete!")
            self.log(f"   Created {created} links")
            self.log(f"   📂 View at: {views_dir}")
            self.update_status(f"Size view created: {created} links")

        except Exception as e:
            self.log(f"\n❌ Error organizing by size: {str(e)}")
            self.update_status("Organization failed")

        finally:
            self.root.after(0, lambda: self.progress_bar.stop())

    def organize_by_size(self):
        """Organize files by size"""
        if not self.db_path or not os.path.exists(self.db_path):
            messagebox.showwarning("No Data", "Please scan files first!")
            return

        thread = threading.Thread(target=self._organize_by_size_thread, daemon=True)
        thread.start()

    def find_duplicates(self):
        """Find duplicate files"""
        if not self.db_path or not os.path.exists(self.db_path):
            messagebox.showwarning("No Data", "Please scan files first!")
            return

        thread = threading.Thread(target=self._find_duplicates_thread, daemon=True)
        thread.start()

    def _find_duplicates_thread(self):
        """Background thread for finding duplicates"""
        try:
            self.progress_bar.start()
            self.log("\n🔍 Finding duplicate files...")
            self.update_status("Computing file hashes...")

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all files that don't have hashes yet
            cursor.execute("SELECT id, path, size FROM files WHERE hash IS NULL")
            files_to_hash = cursor.fetchall()

            self.log(f"   Computing hashes for {len(files_to_hash)} files...")

            # Compute hashes
            for file_id, file_path, size in files_to_hash:
                try:
                    if not os.path.exists(file_path):
                        continue

                    # Compute SHA-256 hash
                    hash_obj = hashlib.sha256()
                    with open(file_path, 'rb') as f:
                        # Read in chunks for large files
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_obj.update(chunk)

                    file_hash = hash_obj.hexdigest()

                    # Update database
                    cursor.execute("UPDATE files SET hash = ? WHERE id = ?", (file_hash, file_id))

                except Exception as e:
                    self.log(f"   ⚠️ Error hashing {file_path}: {str(e)}")

            conn.commit()

            # Find duplicates
            cursor.execute("""
                SELECT hash, COUNT(*) as count
                FROM files
                WHERE hash IS NOT NULL
                GROUP BY hash
                HAVING count > 1
                ORDER BY count DESC
            """)
            duplicate_hashes = cursor.fetchall()

            self.log(f"\n📊 Found {len(duplicate_hashes)} sets of duplicate files:")

            total_duplicates = 0
            total_wasted_space = 0

            for file_hash, count in duplicate_hashes:
                # Get all files with this hash
                cursor.execute("""
                    SELECT path, name, size
                    FROM files
                    WHERE hash = ?
                """, (file_hash,))
                duplicate_files = cursor.fetchall()

                if duplicate_files:
                    size = duplicate_files[0][2]
                    wasted = size * (count - 1)
                    total_wasted_space += wasted

                    self.log(f"\n   📄 {count} copies of '{duplicate_files[0][1]}' ({size:,} bytes each)")
                    self.log(f"      Wasted space: {wasted:,} bytes")

                    for path, name, _ in duplicate_files[:5]:  # Show first 5
                        self.log(f"      - {path}")

                    if count > 5:
                        self.log(f"      ... and {count - 5} more")

                    total_duplicates += count - 1

            # Create duplicate view
            views_dir = os.path.join(self.base_directory.get(), "_Views", "Duplicates")
            os.makedirs(views_dir, exist_ok=True)

            created = 0
            for file_hash, count in duplicate_hashes:
                cursor.execute("SELECT path, name FROM files WHERE hash = ?", (file_hash,))
                duplicate_files = cursor.fetchall()

                # Create folder for this duplicate set
                if duplicate_files:
                    safe_name = duplicate_files[0][1][:50]  # Limit folder name length
                    dup_folder = os.path.join(views_dir, f"{safe_name}_duplicates")
                    os.makedirs(dup_folder, exist_ok=True)

                    for file_path, name in duplicate_files:
                        try:
                            link_path = os.path.join(dup_folder, name)

                            # Remove existing link
                            if os.path.exists(link_path):
                                os.remove(link_path)

                            # Create link
                            try:
                                os.symlink(file_path, link_path)
                                created += 1
                            except OSError:
                                pass

                        except Exception as e:
                            self.log(f"   ⚠️ Error creating link for {name}: {str(e)}")

            conn.close()

            self.log(f"\n✅ Duplicate detection complete!")
            self.log(f"   Total duplicate files: {total_duplicates}")
            self.log(f"   Total wasted space: {total_wasted_space:,} bytes ({total_wasted_space / (1024*1024):.2f} MB)")
            self.log(f"   Created {created} links in duplicate view")
            self.log(f"   📂 View at: {views_dir}")
            self.update_status(f"Found {total_duplicates} duplicates")

        except Exception as e:
            self.log(f"\n❌ Error finding duplicates: {str(e)}")
            self.update_status("Duplicate detection failed")

        finally:
            self.root.after(0, lambda: self.progress_bar.stop())

    def categorize_file(self, extension, filename):
        """Categorize a file based on extension and filename"""
        ext = extension.lower()

        # Check categories dictionary
        if ext in self.categories:
            return self.categories[ext]

        # Filename patterns
        filename_lower = filename.lower()
        if 'invoice' in filename_lower:
            return ('Documents', 'Invoices')
        elif 'report' in filename_lower:
            return ('Documents', 'Reports')
        elif 'screenshot' in filename_lower:
            return ('Images', 'Screenshots')

        return ('Miscellaneous', 'Unknown')

    def load_default_categories(self):
        """Load default file extension to category mapping"""
        return {
            # Documents
            'pdf': ('Documents', 'PDF'),
            'doc': ('Documents', 'Word'),
            'docx': ('Documents', 'Word'),
            'txt': ('Documents', 'Text'),
            'rtf': ('Documents', 'Text'),
            'odt': ('Documents', 'OpenDocument'),

            # Spreadsheets
            'xls': ('Documents', 'Excel'),
            'xlsx': ('Documents', 'Excel'),
            'csv': ('Documents', 'Spreadsheet'),

            # Presentations
            'ppt': ('Documents', 'PowerPoint'),
            'pptx': ('Documents', 'PowerPoint'),

            # Images
            'jpg': ('Images', 'Photos'),
            'jpeg': ('Images', 'Photos'),
            'png': ('Images', 'Graphics'),
            'gif': ('Images', 'Graphics'),
            'bmp': ('Images', 'Bitmap'),
            'svg': ('Images', 'Vector'),
            'ai': ('Images', 'Vector'),

            # Videos
            'mp4': ('Media', 'Video'),
            'avi': ('Media', 'Video'),
            'mkv': ('Media', 'Video'),
            'mov': ('Media', 'Video'),

            # Audio
            'mp3': ('Media', 'Audio'),
            'wav': ('Media', 'Audio'),
            'flac': ('Media', 'Audio'),

            # Archives
            'zip': ('Archives', 'ZIP'),
            'rar': ('Archives', 'RAR'),
            '7z': ('Archives', '7Zip'),
            'tar': ('Archives', 'TAR'),
            'gz': ('Archives', 'GZip'),

            # Code
            'py': ('Code', 'Python'),
            'js': ('Code', 'JavaScript'),
            'java': ('Code', 'Java'),
            'cpp': ('Code', 'C++'),
            'c': ('Code', 'C'),
            'html': ('Code', 'Web'),
            'css': ('Code', 'Web'),

            # CAD
            'dwg': ('CAD', 'AutoCAD'),
            'dxf': ('CAD', 'AutoCAD'),
            'skp': ('CAD', 'SketchUp'),
        }

    def log(self, message):
        """Add message to output log"""
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)

    def update_status(self, message):
        """Update status bar"""
        self.status_label.config(text=message)
        self.bottom_status.config(text=f"Status: {message}")

def main():
    root = tk.Tk()
    app = FileOrganizerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
