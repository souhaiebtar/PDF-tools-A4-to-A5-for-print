#!/usr/bin/env python3
"""
File Organizer - A modern GUI application using CustomTk
A utility app for organizing and managing files with a clean, modern interface.
"""

import os
import shutil
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk


class FileOrganizerApp:
    def __init__(self):
        # Set CustomTk appearance and color theme
        ctk.set_appearance_mode("dark")  # Modes: "system", "dark", "light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("File Organizer - Modern GUI with CustomTk")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure grid layout
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Initialize variables
        self.source_dir = ""
        self.dest_dir = ""
        self.file_list = []
        self.organizing_thread = None
        
        # Create the UI components
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        
    def create_sidebar(self):
        """Create the left sidebar with controls"""
        # Sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # Logo and title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="File Organizer", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Theme selection
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Appearance Mode:", 
            anchor="w"
        )
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        
        # UI scaling
        self.scaling_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="UI Scaling:", 
            anchor="w"
        )
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        
        self.scaling_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self.change_scaling_event
        )
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        
    def create_main_content(self):
        """Create the main content area"""
        # Main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(3, weight=1)
        
        # Header
        self.header_label = ctk.CTkLabel(
            self.main_frame,
            text="Organize Your Files Efficiently",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Directory selection frame
        self.dir_frame = ctk.CTkFrame(self.main_frame)
        self.dir_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 5))
        self.dir_frame.grid_columnconfigure(1, weight=1)
        
        # Source directory
        self.source_label = ctk.CTkLabel(self.dir_frame, text="Source Directory:")
        self.source_label.grid(row=0, column=0, padx=(20, 10), pady=(20, 5), sticky="w")
        
        self.source_entry = ctk.CTkEntry(self.dir_frame, placeholder_text="Select source directory...")
        self.source_entry.grid(row=0, column=1, padx=(0, 10), pady=(20, 5), sticky="ew")
        
        self.source_button = ctk.CTkButton(
            self.dir_frame,
            text="Browse",
            width=100,
            command=self.browse_source_directory
        )
        self.source_button.grid(row=0, column=2, padx=(0, 20), pady=(20, 5))
        
        # Destination directory
        self.dest_label = ctk.CTkLabel(self.dir_frame, text="Destination Directory:")
        self.dest_label.grid(row=1, column=0, padx=(20, 10), pady=(5, 20), sticky="w")
        
        self.dest_entry = ctk.CTkEntry(self.dir_frame, placeholder_text="Select destination directory...")
        self.dest_entry.grid(row=1, column=1, padx=(0, 10), pady=(5, 20), sticky="ew")
        
        self.dest_button = ctk.CTkButton(
            self.dir_frame,
            text="Browse",
            width=100,
            command=self.browse_destination_directory
        )
        self.dest_button.grid(row=1, column=2, padx=(0, 20), pady=(5, 20))
        
        # Organization options frame
        self.options_frame = ctk.CTkFrame(self.main_frame)
        self.options_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        self.options_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.options_label = ctk.CTkLabel(
            self.options_frame,
            text="Organization Options:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.options_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10))
        
        # Checkboxes for organization options
        self.organize_by_type_var = ctk.BooleanVar(value=True)
        self.organize_by_type_checkbox = ctk.CTkCheckBox(
            self.options_frame,
            text="Organize by File Type",
            variable=self.organize_by_type_var
        )
        self.organize_by_type_checkbox.grid(row=1, column=0, padx=20, pady=5)
        
        self.create_folders_var = ctk.BooleanVar(value=True)
        self.create_folders_checkbox = ctk.CTkCheckBox(
            self.options_frame,
            text="Create Folders",
            variable=self.create_folders_var
        )
        self.create_folders_checkbox.grid(row=1, column=1, padx=20, pady=5)
        
        self.copy_files_var = ctk.BooleanVar(value=False)
        self.copy_files_checkbox = ctk.CTkCheckBox(
            self.options_frame,
            text="Copy Files (don't move)",
            variable=self.copy_files_var
        )
        self.copy_files_checkbox.grid(row=1, column=2, padx=20, pady=5)
        
        # Action buttons
        self.action_frame = ctk.CTkFrame(self.main_frame)
        self.action_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        self.action_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.preview_button = ctk.CTkButton(
            self.action_frame,
            text="Preview Organization",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.preview_organization
        )
        self.preview_button.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="ew")
        
        self.organize_button = ctk.CTkButton(
            self.action_frame,
            text="Organize Files",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.organize_files
        )
        self.organize_button.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="ew")
        
        # Progress bar (initially hidden)
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(5, 20))
        self.progress_frame.grid_columnconfigure(0, weight=1)
        self.progress_frame.grid_remove()  # Hide initially
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Progress:")
        self.progress_label.grid(row=0, column=0, padx=20, pady=(20, 5), sticky="w")
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_frame = ctk.CTkFrame(self.root, height=30)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status_frame.grid_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready to organize files",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
    def change_appearance_mode_event(self, new_appearance_mode: str):
        """Callback for appearance mode changes"""
        ctk.set_appearance_mode(new_appearance_mode.lower())
        
    def change_scaling_event(self, new_scaling: str):
        """Callback for UI scaling changes"""
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
        
    def browse_source_directory(self):
        """Browse and select source directory"""
        directory = filedialog.askdirectory(title="Select Source Directory")
        if directory:
            self.source_dir = directory
            self.source_entry.delete(0, "end")
            self.source_entry.insert(0, directory)
            self.status_label.configure(text=f"Source directory: {directory}")
            
    def browse_destination_directory(self):
        """Browse and select destination directory"""
        directory = filedialog.askdirectory(title="Select Destination Directory")
        if directory:
            self.dest_dir = directory
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, directory)
            self.status_label.configure(text=f"Destination directory: {directory}")
            
    def preview_organization(self):
        """Preview how files will be organized"""
        if not self.source_dir or not self.dest_dir:
            messagebox.showwarning("Warning", "Please select both source and destination directories.")
            return
            
        # Scan files in source directory
        try:
            source_path = Path(self.source_dir)
            files = [f for f in source_path.iterdir() if f.is_file()]
            
            if not files:
                messagebox.showinfo("Info", "No files found in the source directory.")
                return
                
            # Show preview in a new window
            self.show_preview_window(files)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error reading directory: {str(e)}")
            
    def show_preview_window(self, files):
        """Show organization preview in a new window"""
        preview_window = ctk.CTkToplevel(self.root)
        preview_window.title("Organization Preview")
        preview_window.geometry("600x400")
        
        # Header
        header = ctk.CTkLabel(
            preview_window,
            text=f"Preview - {len(files)} files found",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.pack(pady=10)
        
        # Scrollable frame for file list
        scrollable_frame = ctk.CTkScrollableFrame(preview_window)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Show file organization plan
        organized_files = self.organize_files_by_type(files)
        
        for file_type, type_files in organized_files.items():
            # File type header
            type_frame = ctk.CTkFrame(scrollable_frame)
            type_frame.pack(fill="x", pady=5)
            
            type_label = ctk.CTkLabel(
                type_frame,
                text=f"📁 {file_type} ({len(type_files)} files)",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            type_label.pack(anchor="w", padx=10, pady=5)
            
            # List files of this type
            for file in type_files[:5]:  # Show first 5 files
                file_label = ctk.CTkLabel(
                    type_frame,
                    text=f"  • {file.name}",
                    anchor="w"
                )
                file_label.pack(anchor="w", padx=20, pady=1)
                
            if len(type_files) > 5:
                more_label = ctk.CTkLabel(
                    type_frame,
                    text=f"  ... and {len(type_files) - 5} more files",
                    anchor="w"
                )
                more_label.pack(anchor="w", padx=20, pady=1)
                
        # Close button
        close_button = ctk.CTkButton(
            preview_window,
            text="Close",
            command=preview_window.destroy
        )
        close_button.pack(pady=10)
        
    def organize_files(self):
        """Start the file organization process"""
        if not self.source_dir or not self.dest_dir:
            messagebox.showwarning("Warning", "Please select both source and destination directories.")
            return
            
        # Show progress frame
        self.progress_frame.grid()
        self.progress_bar.start()
        self.status_label.configure(text="Organizing files...")
        
        # Start organization in a separate thread
        self.organizing_thread = threading.Thread(target=self._organize_files_thread, daemon=True)
        self.organizing_thread.start()
        
    def _organize_files_thread(self):
        """Background thread for file organization"""
        try:
            source_path = Path(self.source_dir)
            files = [f for f in source_path.iterdir() if f.is_file()]
            
            if not files:
                self.root.after(0, lambda: messagebox.showinfo("Info", "No files found to organize."))
                return
                
            organized_files = self.organize_files_by_type(files)
            total_files = len(files)
            processed = 0
            
            # Create destination directory structure and move/copy files
            for file_type, type_files in organized_files.items():
                dest_type_dir = Path(self.dest_dir) / file_type
                
                if self.create_folders_var.get():
                    dest_type_dir.mkdir(exist_ok=True)
                    
                for file in type_files:
                    try:
                        dest_file = dest_type_dir / file.name
                        
                        # Handle duplicate names
                        counter = 1
                        while dest_file.exists():
                            stem = file.stem
                            suffix = file.suffix
                            dest_file = dest_type_dir / f"{stem}_{counter}{suffix}"
                            counter += 1
                            
                        # Copy or move file
                        if self.copy_files_var.get():
                            shutil.copy2(file, dest_file)
                        else:
                            shutil.move(str(file), str(dest_file))
                            
                        processed += 1
                        progress = (processed / total_files) * 100
                        
                        # Update progress (thread-safe)
                        self.root.after(0, lambda p=progress: self.progress_label.configure(text=f"Progress: {p:.1f}%"))
                        
                    except Exception as e:
                        print(f"Error processing {file.name}: {e}")
                        
            # Show completion message
            self.root.after(0, self._organization_completed)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Organization failed: {str(e)}"))
            
    def _organization_completed(self):
        """Called when organization is completed"""
        self.progress_bar.stop()
        self.progress_frame.grid_remove()
        self.status_label.configure(text="File organization completed!")
        
        result = messagebox.askyesno(
            "Success", 
            "File organization completed successfully!\n\nWould you like to open the destination folder?"
        )
        
        if result:
            os.startfile(self.dest_dir) if os.name == 'nt' else os.system(f'open "{self.dest_dir}"')
            
    def organize_files_by_type(self, files):
        """Organize files by their extension/type"""
        organized = {}
        
        # File type mapping
        type_mapping = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'Spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'Presentations': ['.ppt', '.pptx', '.odp'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php'],
            'Executables': ['.exe', '.msi', '.app', '.deb', '.dmg']
        }
        
        # Initialize categories
        for category in type_mapping.keys():
            organized[category] = []
        organized['Other'] = []
        
        # Categorize files
        for file in files:
            file_ext = file.suffix.lower()
            categorized = False
            
            for category, extensions in type_mapping.items():
                if file_ext in extensions:
                    organized[category].append(file)
                    categorized = True
                    break
                    
            if not categorized:
                organized['Other'].append(file)
                
        return organized
        
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main function"""
    app = FileOrganizerApp()
    app.run()


if __name__ == "__main__":
    main()
