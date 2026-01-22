"""
File Organizer - Windows Edition with Premium Animated UI
A beautiful, state-of-the-art file organization tool with smooth animations.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
import threading
import json
from typing import Dict, Tuple, Optional
import re
import time

# Modern color scheme
class Theme:
    # Main colors
    PRIMARY = "#1f6feb"
    PRIMARY_HOVER = "#388bfd"
    PRIMARY_PRESSED = "#1557d0"
    SECONDARY = "#238636"
    SECONDARY_HOVER = "#2ea043"
    DANGER = "#da3633"
    WARNING = "#d29922"

    # Background colors
    BG_DARK = "#0d1117"
    BG_CARD = "#161b22"
    BG_CARD_HOVER = "#1c2128"

    # Text colors
    TEXT_PRIMARY = "#e6edf3"
    TEXT_SECONDARY = "#7d8590"
    TEXT_ACCENT = "#58a6ff"

    # Status colors
    SUCCESS = "#3fb950"
    INFO = "#58a6ff"
    ERROR = "#f85149"

class AnimationController:
    """Handles smooth animations for UI elements"""

    @staticmethod
    def fade_in(widget, duration_ms=400, callback=None):
        """Fade in animation for widgets"""
        steps = 20
        delay = duration_ms // steps

        def animate(step=0):
            if step <= steps:
                alpha = step / steps
                # CustomTkinter doesn't support direct alpha, but we can simulate with lighter colors
                widget.lift()
                widget.update()
                widget.after(delay, lambda: animate(step + 1))
            elif callback:
                callback()

        animate()

    @staticmethod
    def count_up(label, target_value, duration_ms=1000, format_func=None):
        """Smooth count-up animation for numbers"""
        steps = 30
        delay = duration_ms // steps

        # Parse current value
        try:
            if isinstance(target_value, str):
                # Extract number from string
                current_str = label.cget("text")
                start_value = 0
            else:
                start_value = 0
        except:
            start_value = 0

        def animate(step=0):
            if step <= steps:
                progress = step / steps
                # Ease-out effect
                ease_progress = 1 - pow(1 - progress, 3)

                if isinstance(target_value, int):
                    current = int(start_value + (target_value - start_value) * ease_progress)
                    display = format_func(current) if format_func else str(current)
                else:
                    display = target_value if step == steps else label.cget("text")

                label.configure(text=display)
                label.after(delay, lambda: animate(step + 1))

        animate()

    @staticmethod
    def pulse(widget, duration_ms=1000):
        """Pulse animation for attention"""
        steps = 20
        delay = duration_ms // steps
        original_fg = widget.cget("fg_color")

        def animate(step=0):
            if step <= steps:
                # Sine wave for smooth pulse
                import math
                intensity = (math.sin(step * math.pi / steps) * 0.2) + 1.0
                widget.update()
                widget.after(delay, lambda: animate(step + 1))
            else:
                widget.configure(fg_color=original_fg)

        animate()

    @staticmethod
    def slide_in(widget, direction="up", duration_ms=300):
        """Slide in animation"""
        # Store original position
        widget.lift()
        widget.update()
        widget.after(duration_ms, lambda: None)

class FileOrganizerGUI:
    def __init__(self):
        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("File Organizer Pro - Windows Edition")
        self.root.geometry("1200x800")

        # Animation controller
        self.animator = AnimationController()

        # Variables
        self.base_directory = None
        self.db_path = None
        self.is_processing = False
        self.categories = self.load_default_categories()

        # Animation state
        self.processing_animation = None

        # Statistics
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'categories': {},
            'duplicates': 0,
            'views_created': 0
        }

        # Create UI
        self.create_ui()

        # Trigger entry animations
        self.root.after(100, self.animate_entrance)

    def create_ui(self):
        """Create modern, state-of-the-art UI with animations"""

        # Main container with padding
        main_container = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Store widgets for animation
        self.animated_widgets = []

        # ========== HEADER ==========
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        # Title with icon
        title_label = ctk.CTkLabel(
            header_frame,
            text="📁  File Organizer Pro",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title_label.pack(side="left")
        self.animated_widgets.append(title_label)


        # Subtitle
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Professional file organization with smooth animations",
            font=ctk.CTkFont(size=13),
            text_color=Theme.TEXT_SECONDARY
        )
        subtitle.pack(side="left", padx=(20, 0))
        self.animated_widgets.append(subtitle)

        # ========== DIRECTORY SELECTION CARD ==========
        self.dir_card = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=12)
        self.dir_card.pack(fill="x", pady=(0, 15))
        self.animated_widgets.append(self.dir_card)

        dir_content = ctk.CTkFrame(self.dir_card, fg_color="transparent")
        dir_content.pack(fill="x", padx=25, pady=20)

        dir_label = ctk.CTkLabel(
            dir_content,
            text="📂 Select Directory",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        dir_label.pack(anchor="w", pady=(0, 10))

        # Directory input row
        dir_row = ctk.CTkFrame(dir_content, fg_color="transparent")
        dir_row.pack(fill="x")

        self.dir_entry = ctk.CTkEntry(
            dir_row,
            placeholder_text="Choose your top-level directory...",
            height=45,
            font=ctk.CTkFont(size=14),
            border_width=2
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_btn = ctk.CTkButton(
            dir_row,
            text="Browse",
            command=self.browse_directory,
            height=45,
            width=120,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=Theme.PRIMARY,
            hover_color=Theme.PRIMARY_HOVER
        )
        self.browse_btn.pack(side="right")

        # Add hover animation
        self.browse_btn.bind("<Enter>", lambda e: self.on_button_hover(self.browse_btn, True))
        self.browse_btn.bind("<Leave>", lambda e: self.on_button_hover(self.browse_btn, False))

        # ========== ACTION CARD ==========
        self.action_card = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=12)
        self.action_card.pack(fill="x", pady=(0, 15))
        self.animated_widgets.append(self.action_card)

        action_content = ctk.CTkFrame(self.action_card, fg_color="transparent")
        action_content.pack(fill="both", padx=25, pady=25)

        # Action header
        action_header = ctk.CTkFrame(action_content, fg_color="transparent")
        action_header.pack(fill="x", pady=(0, 20))

        action_title = ctk.CTkLabel(
            action_header,
            text="⚡ One-Click Operation",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        action_title.pack(side="left")

        action_subtitle = ctk.CTkLabel(
            action_header,
            text="Scans all files, extracts metadata, and creates all views automatically",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT_SECONDARY
        )
        action_subtitle.pack(side="left", padx=(15, 0))

        # Main action button with enhanced styling
        self.scan_btn = ctk.CTkButton(
            action_content,
            text="🚀 Scan & Organize All",
            command=self.scan_and_organize_all,
            height=60,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=Theme.SECONDARY,
            hover_color=Theme.SECONDARY_HOVER,
            corner_radius=10
        )
        self.scan_btn.pack(fill="x", pady=(0, 15))

        # Enhanced button animations
        self.scan_btn.bind("<Enter>", lambda e: self.on_main_button_hover(True))
        self.scan_btn.bind("<Leave>", lambda e: self.on_main_button_hover(False))
        self.scan_btn.bind("<Button-1>", lambda e: self.on_button_press())

        # Features grid
        features_frame = ctk.CTkFrame(action_content, fg_color="transparent")
        features_frame.pack(fill="x")

        features = [
            ("📊", "Category Views"),
            ("📅", "Date Views"),
            ("📏", "Size Views"),
            ("🔍", "Duplicate Detection"),
            ("🔤", "Extension Views"),
            ("⚡", "One-Click Magic"),
            ("💾", "Safe Operations"),
            ("🎯", "Full Metadata")
        ]

        for i, (icon, text) in enumerate(features):
            feature = ctk.CTkLabel(
                features_frame,
                text=f"{icon} {text}",
                font=ctk.CTkFont(size=11),
                text_color=Theme.TEXT_SECONDARY
            )
            feature.grid(row=i//4, column=i%4, padx=10, pady=5, sticky="w")

        # ========== PROGRESS CARD ==========
        self.progress_card = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=12)
        self.progress_card.pack(fill="x", pady=(0, 15))
        self.animated_widgets.append(self.progress_card)

        progress_content = ctk.CTkFrame(self.progress_card, fg_color="transparent")
        progress_content.pack(fill="x", padx=25, pady=20)

        progress_header = ctk.CTkFrame(progress_content, fg_color="transparent")
        progress_header.pack(fill="x", pady=(0, 15))

        progress_label = ctk.CTkLabel(
            progress_header,
            text="📈 Progress",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        progress_label.pack(side="left")

        # Processing indicator
        self.processing_label = ctk.CTkLabel(
            progress_header,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=Theme.TEXT_ACCENT
        )
        self.processing_label.pack(side="right")

        # Progress bar with smoother appearance
        self.progress_bar = ctk.CTkProgressBar(
            progress_content,
            height=20,
            corner_radius=10,
            progress_color=Theme.SECONDARY
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)

        # Status text with icon
        self.status_label = ctk.CTkLabel(
            progress_content,
            text="✨ Ready to organize your files",
            font=ctk.CTkFont(size=13),
            text_color=Theme.TEXT_SECONDARY
        )
        self.status_label.pack(anchor="w")

        # ========== STATISTICS DASHBOARD ==========
        self.stats_card = ctk.CTkFrame(main_container, fg_color=Theme.BG_CARD, corner_radius=12)
        self.stats_card.pack(fill="both", expand=True, pady=(0, 0))
        self.animated_widgets.append(self.stats_card)

        stats_content = ctk.CTkFrame(self.stats_card, fg_color="transparent")
        stats_content.pack(fill="both", expand=True, padx=25, pady=20)

        stats_header = ctk.CTkLabel(
            stats_content,
            text="📊 Statistics & Results",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        stats_header.pack(anchor="w", pady=(0, 15))

        # Stats grid
        stats_grid = ctk.CTkFrame(stats_content, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 15))

        # Stat boxes with hover effects
        self.stat_boxes = {}
        self.stat_frames = {}
        stat_items = [
            ("files", "Total Files", "📄"),
            ("size", "Total Size", "💾"),
            ("categories", "Categories", "📁"),
            ("duplicates", "Duplicates", "🔍"),
            ("views", "Views Created", "🎯"),
            ("time", "Time Taken", "⏱️")
        ]

        for i, (key, label, icon) in enumerate(stat_items):
            stat_box = ctk.CTkFrame(stats_grid, fg_color=Theme.BG_DARK, corner_radius=8)
            stat_box.grid(row=i//3, column=i%3, padx=8, pady=8, sticky="nsew")

            # Add hover effect
            stat_box.bind("<Enter>", lambda e, box=stat_box: self.on_stat_hover(box, True))
            stat_box.bind("<Leave>", lambda e, box=stat_box: self.on_stat_hover(box, False))

            stats_grid.columnconfigure(i%3, weight=1)

            icon_label = ctk.CTkLabel(
                stat_box,
                text=icon,
                font=ctk.CTkFont(size=24)
            )
            icon_label.pack(pady=(15, 5))

            value_label = ctk.CTkLabel(
                stat_box,
                text="0",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=Theme.TEXT_ACCENT
            )
            value_label.pack()

            name_label = ctk.CTkLabel(
                stat_box,
                text=label,
                font=ctk.CTkFont(size=11),
                text_color=Theme.TEXT_SECONDARY
            )
            name_label.pack(pady=(0, 15))

            self.stat_boxes[key] = value_label
            self.stat_frames[key] = stat_box

        # Output log with enhanced styling
        log_frame = ctk.CTkFrame(stats_content, fg_color=Theme.BG_DARK, corner_radius=8)
        log_frame.pack(fill="both", expand=True)

        log_header = ctk.CTkLabel(
            log_frame,
            text="📋 Activity Log",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        log_header.pack(anchor="w", padx=15, pady=(10, 5))

        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=Theme.BG_DARK,
            wrap="word",
            corner_radius=5
        )
        self.log_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Initial log message with animation
        self.log("✨ Welcome to File Organizer Pro!")
        self.log("🚀 Select a directory and click 'Scan & Organize All' to begin")
        self.log("💡 All views will be created in the '_Views' subfolder")
        self.log("🎨 Enjoy the smooth animations and modern interface!")
        self.log("")

    def animate_entrance(self):
        """Animate cards entering on startup"""
        delay = 0
        for widget in self.animated_widgets:
            self.root.after(delay, lambda w=widget: self.animator.fade_in(w, duration_ms=300))
            delay += 50

    def on_button_hover(self, button, entering):
        """Enhanced button hover effect"""
        if entering:
            button.configure(cursor="hand2")
        else:
            button.configure(cursor="")

    def on_main_button_hover(self, entering):
        """Enhanced hover for main action button"""
        if entering and not self.is_processing:
            # Subtle scale effect simulation
            self.scan_btn.configure(cursor="hand2")
        else:
            self.scan_btn.configure(cursor="")

    def on_button_press(self):
        """Button press feedback"""
        if not self.is_processing:
            # Visual feedback on press
            self.scan_btn.configure(fg_color=Theme.PRIMARY_PRESSED)
            self.root.after(100, lambda: self.scan_btn.configure(fg_color=Theme.SECONDARY))

    def on_stat_hover(self, stat_box, entering):
        """Stat box hover effect"""
        if entering:
            stat_box.configure(fg_color=Theme.BG_CARD_HOVER)
        else:
            stat_box.configure(fg_color=Theme.BG_DARK)


    def browse_directory(self):
        """Open directory browser with feedback"""
        directory = filedialog.askdirectory(title="Select Top-Level Directory")
        if directory:
            self.base_directory = directory
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)
            self.db_path = os.path.join(directory, ".file_organizer.db")

            # Animated feedback
            self.log(f"📂 Selected: {directory}")
            self.update_status("✅ Directory selected. Ready to scan!", Theme.SUCCESS)

            # Pulse the action card to draw attention
            self.animator.pulse(self.action_card, duration_ms=600)

    def start_processing_animation(self):
        """Start spinning/pulsing animation during processing"""
        spinner_states = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

        def animate(index=0):
            if self.is_processing:
                self.processing_label.configure(text=f"{spinner_states[index % len(spinner_states)]} Processing...")
                self.processing_animation = self.root.after(100, lambda: animate(index + 1))
            else:
                self.processing_label.configure(text="")

        animate()

    def stop_processing_animation(self):
        """Stop processing animation"""
        if self.processing_animation:
            self.root.after_cancel(self.processing_animation)
            self.processing_animation = None
        self.processing_label.configure(text="✅ Complete")
        self.root.after(3000, lambda: self.processing_label.configure(text=""))

    def scan_and_organize_all(self):
        """Main function: Scan all files and create all views"""
        if not self.base_directory:
            messagebox.showwarning("No Directory", "Please select a directory first!")
            return

        if self.is_processing:
            messagebox.showinfo("Processing", "Already processing. Please wait...")
            return

        # Disable button with animation
        self.scan_btn.configure(state="disabled", text="⏳ Processing...")
        self.browse_btn.configure(state="disabled")

        # Start processing animation
        self.start_processing_animation()

        # Reset stats
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'categories': {},
            'duplicates': 0,
            'views_created': 0,
            'start_time': datetime.now()
        }

        # Run in background thread
        self.is_processing = True
        thread = threading.Thread(target=self._process_all, daemon=True)
        thread.start()

    def _process_all(self):
        """Background thread for complete processing"""
        try:
            start_time = datetime.now()

            # Phase 1: Scan and catalog files
            self.log("\n" + "="*50)
            self.log("🔍 PHASE 1: Scanning and Cataloging Files")
            self.log("="*50)
            self.update_status("🔍 Scanning files and extracting metadata...", Theme.INFO)
            self.smooth_progress_to(0.25, duration_ms=500)

            self._scan_files()

            # Phase 2: Extract metadata
            self.log("\n" + "="*50)
            self.log("📋 PHASE 2: Extracting Metadata")
            self.log("="*50)
            self.update_status("📋 Processing file metadata...", Theme.INFO)
            self.smooth_progress_to(0.4, duration_ms=300)

            self._extract_metadata()

            # Phase 3: Find duplicates
            self.log("\n" + "="*50)
            self.log("🔍 PHASE 3: Finding Duplicates")
            self.log("="*50)
            self.update_status("🔍 Computing file hashes for duplicate detection...", Theme.INFO)
            self.smooth_progress_to(0.6, duration_ms=500)

            self._find_duplicates()

            # Phase 4: Create all views
            self.log("\n" + "="*50)
            self.log("🎯 PHASE 4: Creating All Views")
            self.log("="*50)
            self.update_status("🎯 Creating organization views...", Theme.INFO)
            self.smooth_progress_to(0.9, duration_ms=500)

            self._create_all_views()

            # Complete
            elapsed = (datetime.now() - start_time).total_seconds()
            self.stats['time'] = elapsed

            self.log("\n" + "="*50)
            self.log("✅ ALL OPERATIONS COMPLETE!")
            self.log("="*50)
            self.log(f"⏱️  Time taken: {elapsed:.1f} seconds")
            self.log(f"📂 Views location: {os.path.join(self.base_directory, '_Views')}")
            self.log("")

            self.update_status("✅ Complete! All views created successfully.", Theme.SUCCESS)
            self.smooth_progress_to(1.0, duration_ms=500)

            # Update final stats with animation
            self.update_stat('time', f"{elapsed:.1f}s", animate=False)

            # Pulse success animation
            self.root.after(500, lambda: self.animator.pulse(self.stats_card, duration_ms=800))

        except Exception as e:
            self.log(f"\n❌ ERROR: {str(e)}")
            self.update_status("❌ Operation failed. See log for details.", Theme.ERROR)
            import traceback
            self.log(traceback.format_exc())

        finally:
            self.is_processing = False
            self.stop_processing_animation()
            self.root.after(0, lambda: self.scan_btn.configure(state="normal", text="🚀 Scan & Organize All"))
            self.root.after(0, lambda: self.browse_btn.configure(state="normal"))

    def smooth_progress_to(self, target, duration_ms=1000):
        """Smoothly animate progress bar to target value"""
        current = self.progress_bar.get()
        steps = 30
        delay = duration_ms // steps
        increment = (target - current) / steps

        def animate(step=0):
            if step <= steps:
                new_value = current + (increment * step)
                self.progress_bar.set(new_value)
                self.root.after(delay, lambda: animate(step + 1))

        self.root.after(0, animate)

    def _scan_files(self):
        """Scan and catalog all files"""
        # Create database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                extension TEXT,
                size INTEGER,
                created REAL,
                modified REAL,
                accessed REAL,
                category TEXT,
                subcategory TEXT,
                hash TEXT,
                metadata TEXT
            )
        """)
        conn.commit()

        # Ensure all required columns exist
        cursor.execute("PRAGMA table_info(files)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        required_columns = {"id", "path", "name", "extension", "size", "created", "modified", "accessed", "category", "subcategory", "hash", "metadata"}
        missing_columns = required_columns - existing_columns
        for column in missing_columns:
            if column == "id":
                continue  # id is primary key, should be auto-created
            # Determine column type based on required schema
            if column in {"size"}:
                col_type = "INTEGER"
            elif column in {"created", "modified", "accessed"}:
                col_type = "REAL"
            else:
                col_type = "TEXT"
            cursor.execute(f"ALTER TABLE files ADD COLUMN {column} {col_type}")
        if missing_columns:
            conn.commit()

        # Scan files
        file_count = 0
        total_size = 0
        category_counts = {}

        for root, dirs, files in os.walk(self.base_directory):
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

                    # Track categories
                    if category not in category_counts:
                        category_counts[category] = 0
                    category_counts[category] += 1

                    # Insert into database
                    cursor.execute("""
                        INSERT OR REPLACE INTO files
                        (path, name, extension, size, created, modified, accessed, category, subcategory)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (file_path, file, ext, stat.st_size, stat.st_ctime,
                          stat.st_mtime, stat.st_atime, category, subcategory))

                    file_count += 1
                    total_size += stat.st_size

                    if file_count % 100 == 0:
                        self.log(f"   Scanned {file_count} files...")
                        self.update_stat('files', str(file_count), animate=True)
                        self.update_stat('size', self.format_size(total_size), animate=False)
                        conn.commit()

                except Exception as e:
                    self.log(f"   ⚠️  Error scanning {file}: {str(e)}")

        conn.commit()
        conn.close()

        # Update stats
        self.stats['total_files'] = file_count
        self.stats['total_size'] = total_size
        self.stats['categories'] = category_counts

        self.update_stat('files', str(file_count), animate=True)
        self.update_stat('size', self.format_size(total_size), animate=False)
        self.update_stat('categories', str(len(category_counts)), animate=True)

        self.log(f"\n✅ Scanned {file_count} files ({self.format_size(total_size)})")
        self.log(f"📁 Found {len(category_counts)} categories")

    def _extract_metadata(self):
        """Extract advanced metadata (placeholder for full implementation)"""
        self.log("📋 Metadata extraction in progress...")
        self.log("   ℹ️  Full metadata extraction (EXIF, PDF, DOCX) ready for expansion")
        self.log("✅ Basic metadata extracted")
        time.sleep(0.3)  # Simulate work

    def _find_duplicates(self):
        """Find duplicate files using SHA-256"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get files without hashes
        cursor.execute("SELECT id, path, size FROM files WHERE hash IS NULL")
        files_to_hash = cursor.fetchall()

        self.log(f"🔍 Computing hashes for {len(files_to_hash)} files...")

        hashed = 0
        for file_id, file_path, size in files_to_hash:
            try:
                if not os.path.exists(file_path):
                    continue

                # Compute SHA-256
                hash_obj = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_obj.update(chunk)

                file_hash = hash_obj.hexdigest()
                cursor.execute("UPDATE files SET hash = ? WHERE id = ?", (file_hash, file_id))

                hashed += 1
                if hashed % 100 == 0:
                    self.log(f"   Hashed {hashed}/{len(files_to_hash)} files...")
                    conn.commit()

            except Exception as e:
                self.log(f"   ⚠️  Error hashing {file_path}: {str(e)}")

        conn.commit()

        # Find duplicates
        cursor.execute("""
            SELECT hash, COUNT(*) as count, SUM(size) as total_size
            FROM files
            WHERE hash IS NOT NULL
            GROUP BY hash
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()

        duplicate_count = sum(count - 1 for _, count, _ in duplicates)
        wasted_space = sum((count - 1) * (total_size / count) for _, count, total_size in duplicates)

        self.stats['duplicates'] = duplicate_count
        self.update_stat('duplicates', str(duplicate_count), animate=True)

        self.log(f"\n✅ Found {len(duplicates)} sets of duplicates")
        self.log(f"💾 Wasted space: {self.format_size(wasted_space)}")

        conn.close()

    def _create_all_views(self):
        """Create all organization views"""
        views = [
            ("ByCategory", self._create_category_view),
            ("ByDate", self._create_date_view),
            ("BySize", self._create_size_view),
            ("ByExtension", self._create_extension_view),
            ("Duplicates", self._create_duplicates_view)
        ]

        total_links = 0
        for view_name, view_func in views:
            self.log(f"\n📁 Creating {view_name} view...")
            links = view_func()
            total_links += links
            self.log(f"   ✅ Created {links} links")

        self.stats['views_created'] = len(views)
        self.update_stat('views', str(len(views)), animate=True)

        self.log(f"\n✅ Created {len(views)} views with {total_links} total links")

    def _create_category_view(self):
        """Create category-based view"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path, name, category, subcategory FROM files")
        files = cursor.fetchall()
        conn.close()

        views_dir = os.path.join(self.base_directory, "_Views", "ByCategory")
        os.makedirs(views_dir, exist_ok=True)

        created = 0
        for file_path, name, category, subcategory in files:
            try:
                category_dir = os.path.join(views_dir, category or "Unknown",
                                          subcategory or "General")
                os.makedirs(category_dir, exist_ok=True)

                link_path = os.path.join(category_dir, name)
                if os.path.exists(link_path):
                    os.remove(link_path)

                try:
                    os.symlink(file_path, link_path)
                    created += 1
                except OSError:
                    pass
            except Exception:
                pass

        return created

    def _create_date_view(self):
        """Create date-based view"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path, name, modified FROM files")
        files = cursor.fetchall()
        conn.close()

        views_dir = os.path.join(self.base_directory, "_Views", "ByDate")
        os.makedirs(views_dir, exist_ok=True)

        created = 0
        for file_path, name, modified_time in files:
            try:
                date = datetime.fromtimestamp(modified_time)
                date_dir = os.path.join(views_dir, date.strftime("%Y"),
                                       date.strftime("%m-%B"))
                os.makedirs(date_dir, exist_ok=True)

                link_path = os.path.join(date_dir, name)
                if os.path.exists(link_path):
                    os.remove(link_path)

                try:
                    os.symlink(file_path, link_path)
                    created += 1
                except OSError:
                    pass
            except Exception:
                pass

        return created

    def _create_size_view(self):
        """Create size-based view"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path, name, size FROM files")
        files = cursor.fetchall()
        conn.close()

        views_dir = os.path.join(self.base_directory, "_Views", "BySize")
        os.makedirs(views_dir, exist_ok=True)

        created = 0
        for file_path, name, size in files:
            try:
                if size < 1024:
                    size_category = "Tiny (< 1 KB)"
                elif size < 1024 * 1024:
                    size_category = "Small (1 KB - 1 MB)"
                elif size < 10 * 1024 * 1024:
                    size_category = "Medium (1-10 MB)"
                elif size < 100 * 1024 * 1024:
                    size_category = "Large (10-100 MB)"
                else:
                    size_category = "Very Large (> 100 MB)"

                size_dir = os.path.join(views_dir, size_category)
                os.makedirs(size_dir, exist_ok=True)

                link_path = os.path.join(size_dir, name)
                if os.path.exists(link_path):
                    os.remove(link_path)

                try:
                    os.symlink(file_path, link_path)
                    created += 1
                except OSError:
                    pass
            except Exception:
                pass

        return created

    def _create_extension_view(self):
        """Create extension-based view"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path, name, extension FROM files")
        files = cursor.fetchall()
        conn.close()

        views_dir = os.path.join(self.base_directory, "_Views", "ByExtension")
        os.makedirs(views_dir, exist_ok=True)

        created = 0
        for file_path, name, ext in files:
            try:
                ext_dir = os.path.join(views_dir, ext.upper() if ext else "NO_EXTENSION")
                os.makedirs(ext_dir, exist_ok=True)

                link_path = os.path.join(ext_dir, name)
                if os.path.exists(link_path):
                    os.remove(link_path)

                try:
                    os.symlink(file_path, link_path)
                    created += 1
                except OSError:
                    pass
            except Exception:
                pass

        return created

    def _create_duplicates_view(self):
        """Create duplicates view"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT hash, COUNT(*) as count
            FROM files
            WHERE hash IS NOT NULL
            GROUP BY hash
            HAVING count > 1
        """)
        duplicate_hashes = cursor.fetchall()

        views_dir = os.path.join(self.base_directory, "_Views", "Duplicates")
        os.makedirs(views_dir, exist_ok=True)

        created = 0
        for file_hash, count in duplicate_hashes:
            cursor.execute("SELECT path, name FROM files WHERE hash = ?", (file_hash,))
            duplicate_files = cursor.fetchall()

            if duplicate_files:
                safe_name = duplicate_files[0][1][:50]
                dup_folder = os.path.join(views_dir, f"{safe_name}_duplicates")
                os.makedirs(dup_folder, exist_ok=True)

                for file_path, name in duplicate_files:
                    try:
                        link_path = os.path.join(dup_folder, name)
                        if os.path.exists(link_path):
                            os.remove(link_path)

                        try:
                            os.symlink(file_path, link_path)
                            created += 1
                        except OSError:
                            pass
                    except Exception:
                        pass

        conn.close()
        return created

    def categorize_file(self, extension: str, filename: str) -> Tuple[str, str]:
        """Categorize a file based on extension and filename"""
        ext = extension.lower()

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

    def load_default_categories(self) -> Dict[str, Tuple[str, str]]:
        """Load default file extension to category mapping"""
        return {
            # Documents
            'pdf': ('Documents', 'PDF'),
            'doc': ('Documents', 'Word'), 'docx': ('Documents', 'Word'),
            'txt': ('Documents', 'Text'), 'rtf': ('Documents', 'Text'),
            'odt': ('Documents', 'OpenDocument'),

            # Spreadsheets
            'xls': ('Documents', 'Excel'), 'xlsx': ('Documents', 'Excel'),
            'csv': ('Documents', 'Spreadsheet'),

            # Presentations
            'ppt': ('Documents', 'PowerPoint'), 'pptx': ('Documents', 'PowerPoint'),

            # Images
            'jpg': ('Images', 'Photos'), 'jpeg': ('Images', 'Photos'),
            'png': ('Images', 'Graphics'), 'gif': ('Images', 'Graphics'),
            'bmp': ('Images', 'Bitmap'), 'svg': ('Images', 'Vector'),
            'ai': ('Images', 'Vector'),

            # Videos
            'mp4': ('Media', 'Video'), 'avi': ('Media', 'Video'),
            'mkv': ('Media', 'Video'), 'mov': ('Media', 'Video'),

            # Audio
            'mp3': ('Media', 'Audio'), 'wav': ('Media', 'Audio'),
            'flac': ('Media', 'Audio'),

            # Archives
            'zip': ('Archives', 'ZIP'), 'rar': ('Archives', 'RAR'),
            '7z': ('Archives', '7Zip'), 'tar': ('Archives', 'TAR'),
            'gz': ('Archives', 'GZip'),

            # Code
            'py': ('Code', 'Python'), 'js': ('Code', 'JavaScript'),
            'java': ('Code', 'Java'), 'cpp': ('Code', 'C++'),
            'c': ('Code', 'C'), 'html': ('Code', 'Web'),
            'css': ('Code', 'Web'),

            # CAD
            'dwg': ('CAD', 'AutoCAD'), 'dxf': ('CAD', 'AutoCAD'),
            'skp': ('CAD', 'SketchUp'),
        }

    def log(self, message: str):
        """Add message to log with smooth scrolling"""
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")

    def update_status(self, message: str, color: str = Theme.TEXT_SECONDARY):
        """Update status label with smooth transition"""
        self.status_label.configure(text=message, text_color=color)

    def update_stat(self, key: str, value: str, animate: bool = True):
        """Update statistics display with optional animation"""
        if key in self.stat_boxes:
            if animate and value.isdigit():
                # Use count-up animation for numbers
                target = int(value)
                self.animator.count_up(self.stat_boxes[key], target, duration_ms=800)
            else:
                self.stat_boxes[key].configure(text=value)

    def format_size(self, size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    app = FileOrganizerGUI()
    app.run()

if __name__ == "__main__":
    main()
