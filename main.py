#!/usr/bin/env python3
"""
File Organizer - A modern GUI application using CustomTk
A utility app for organizing and managing files with a clean, modern interface.
Includes PDF reordering functionality using qpdf.
"""

import os
import shutil
import subprocess
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
        self.root.title("File Organizer & PDF Tools - Modern GUI with CustomTk")
        self.root.geometry("1000x750")
        self.root.minsize(800, 600)
        
        # Configure grid layout
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Initialize variables for file organizer
        self.source_dir = ""
        self.dest_dir = ""
        self.file_list = []
        self.organizing_thread = None
        
        # Initialize variables for PDF reordering
        self.pdf_file = ""
        self.pdf_start_page = 10
        self.pdf_output_file = ""
        
        # Create the UI components
        self.create_sidebar()
        self.create_status_bar()
        self.create_main_content()
        
    def create_sidebar(self):
        """Create the left sidebar with controls"""
        # Sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        
        # Logo and title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="File Organizer\n& PDF Tools", 
            font=ctk.CTkFont(size=20, weight="bold"),
            justify="center"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Tab buttons
        self.tab_frame = ctk.CTkFrame(self.sidebar_frame)
        self.tab_frame.grid(row=1, column=0, padx=20, pady=10)
        
        self.organize_tab_button = ctk.CTkButton(
            self.tab_frame,
            text="📁 File Organizer",
            command=self.show_organize_tab,
            width=160,
            height=35
        )
        self.organize_tab_button.pack(pady=5)
        
        self.pdf_tab_button = ctk.CTkButton(
            self.tab_frame,
            text="📄 PDF Reorder",
            command=self.show_pdf_tab,
            width=160,
            height=35
        )
        self.pdf_tab_button.pack(pady=5)
        
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
        
        # Create both tabs (they'll be shown/hidden based on selection)
        self.create_organize_tab()
        self.create_pdf_tab()
        
        # Show organize tab by default
        self.show_organize_tab()
        
    def create_organize_tab(self):
        """Create the file organizer tab content"""
        # Header
        self.organize_header = ctk.CTkLabel(
            self.main_frame,
            text="Organize Your Files Efficiently",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.organize_header.grid(row=0, column=0, padx=20, pady=(20, 10))
        
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
        
    def create_pdf_tab(self):
        """Create the PDF reordering tab content"""
        # Store references to PDF widgets so we can show/hide them
        self.pdf_widgets = []
        
        # Header
        self.pdf_header = ctk.CTkLabel(
            self.main_frame,
            text="Reorder PDF Pages with QPDF",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.pdf_widgets.append(self.pdf_header)
        
        # PDF File Selection Section
        self.pdf_section_frame = ctk.CTkFrame(self.main_frame)
        self.pdf_widgets.append(self.pdf_section_frame)
        
        self.pdf_file_label = ctk.CTkLabel(
            self.pdf_section_frame, 
            text="📄 Select PDF File:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.pdf_widgets.append(self.pdf_file_label)
        
        self.pdf_file_entry = ctk.CTkEntry(
            self.pdf_section_frame, 
            placeholder_text="Click Browse to select a PDF file...",
            height=35
        )
        self.pdf_widgets.append(self.pdf_file_entry)
        
        self.pdf_browse_button = ctk.CTkButton(
            self.pdf_section_frame,
            text="Browse",
            width=100,
            height=35,
            command=self.browse_pdf_file
        )
        self.pdf_widgets.append(self.pdf_browse_button)
        
        # Destination Folder Selection Section
        self.pdf_dest_frame = ctk.CTkFrame(self.main_frame)
        self.pdf_widgets.append(self.pdf_dest_frame)
        
        self.pdf_dest_label = ctk.CTkLabel(
            self.pdf_dest_frame, 
            text="📁 Select Destination Folder:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.pdf_widgets.append(self.pdf_dest_label)
        
        self.pdf_dest_entry = ctk.CTkEntry(
            self.pdf_dest_frame, 
            placeholder_text="Click Browse to select output folder...",
            height=35
        )
        self.pdf_widgets.append(self.pdf_dest_entry)
        
        self.pdf_dest_browse_button = ctk.CTkButton(
            self.pdf_dest_frame,
            text="Browse",
            width=100,
            height=35,
            command=self.browse_pdf_destination
        )
        self.pdf_widgets.append(self.pdf_dest_browse_button)
        
        # Starting Page Number Section
        self.pdf_page_frame = ctk.CTkFrame(self.main_frame)
        self.pdf_widgets.append(self.pdf_page_frame)
        
        self.pdf_page_label = ctk.CTkLabel(
            self.pdf_page_frame, 
            text="🔢 Starting Page Number:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.pdf_widgets.append(self.pdf_page_label)
        
        self.pdf_page_entry = ctk.CTkEntry(
            self.pdf_page_frame,
            placeholder_text="Enter starting page (1-based)",
            height=35,
            width=150
        )
        self.pdf_page_entry.insert(0, "10")  # Default value
        self.pdf_widgets.append(self.pdf_page_entry)
        
        self.pdf_page_info = ctk.CTkLabel(
            self.pdf_page_frame,
            text="Pages will be reordered from this point using 1,3,2,4 pattern",
            font=ctk.CTkFont(size=11)
        )
        self.pdf_widgets.append(self.pdf_page_info)
        
        # Output Filename Section
        self.pdf_output_frame = ctk.CTkFrame(self.main_frame)
        self.pdf_widgets.append(self.pdf_output_frame)
        
        self.pdf_output_label = ctk.CTkLabel(
            self.pdf_output_frame, 
            text="📝 Output Filename:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.pdf_widgets.append(self.pdf_output_label)
        
        self.pdf_output_entry = ctk.CTkEntry(
            self.pdf_output_frame,
            placeholder_text="Enter output filename...",
            height=35
        )
        self.pdf_widgets.append(self.pdf_output_entry)
        
        # Action button
        self.reorder_button = ctk.CTkButton(
            self.main_frame,
            text="🔄 Reorder PDF Pages",
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.reorder_pdf
        )
        self.pdf_widgets.append(self.reorder_button)
        
        # Status message for PDF
        self.pdf_status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.pdf_widgets.append(self.pdf_status_label)
        
        # Grid layout for PDF widgets
        self.pdf_header.grid(row=0, column=0, padx=20, pady=(20, 15))
        
        # PDF File Section
        self.pdf_section_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        self.pdf_section_frame.grid_columnconfigure(1, weight=1)
        self.pdf_file_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 5), sticky="w")
        self.pdf_file_entry.grid(row=1, column=0, columnspan=2, padx=(20, 10), pady=5, sticky="ew")
        self.pdf_browse_button.grid(row=1, column=2, padx=(0, 20), pady=5)
        
        # Destination Section
        self.pdf_dest_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        self.pdf_dest_frame.grid_columnconfigure(1, weight=1)
        self.pdf_dest_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 5), sticky="w")
        self.pdf_dest_entry.grid(row=1, column=0, columnspan=2, padx=(20, 10), pady=5, sticky="ew")
        self.pdf_dest_browse_button.grid(row=1, column=2, padx=(0, 20), pady=5)
        
        # Starting Page Section
        self.pdf_page_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        self.pdf_page_frame.grid_columnconfigure(1, weight=1)
        self.pdf_page_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        self.pdf_page_entry.grid(row=1, column=0, padx=(20, 10), pady=5, sticky="w")
        self.pdf_page_info.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Output Filename Section
        self.pdf_output_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=5)
        self.pdf_output_frame.grid_columnconfigure(1, weight=1)
        self.pdf_output_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 5), sticky="w")
        self.pdf_output_entry.grid(row=1, column=0, columnspan=2, padx=(20, 10), pady=5, sticky="ew")
        
        # Reorder Button
        self.reorder_button.grid(row=5, column=0, padx=20, pady=20, sticky="ew")
        
        # Status Label
        self.pdf_status_label.grid(row=6, column=0, padx=20, pady=10)
        
        # Initially hide PDF widgets
        for widget in self.pdf_widgets:
            widget.grid_remove()
            
    def show_organize_tab(self):
        """Show the file organizer tab"""
        # Hide PDF widgets
        for widget in self.pdf_widgets:
            widget.grid_remove()
            
        # Show organize widgets
        self.organize_header.grid()
        self.dir_frame.grid()
        self.options_frame.grid()
        self.action_frame.grid()
        
        # Update sidebar button states
        self.organize_tab_button.configure(fg_color="#3B8ED0")
        self.pdf_tab_button.configure(fg_color="transparent")
        
        self.status_label.configure(text="Ready to organize files")
        
    def show_pdf_tab(self):
        """Show the PDF reordering tab"""
        # Hide organize widgets
        self.organize_header.grid_remove()
        self.dir_frame.grid_remove()
        self.options_frame.grid_remove()
        self.action_frame.grid_remove()
        if self.progress_frame.winfo_ismapped():
            self.progress_frame.grid_remove()
            
        # Show PDF widgets
        for widget in self.pdf_widgets:
            widget.grid()
            
        # Update sidebar button states
        self.organize_tab_button.configure(fg_color="transparent")
        self.pdf_tab_button.configure(fg_color="#3B8ED0")
        
        self.status_label.configure(text="Ready to reorder PDF files")
        
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
            
    def browse_pdf_file(self):
        """Browse and select PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_file = filename
            self.pdf_file_entry.delete(0, "end")
            self.pdf_file_entry.insert(0, filename)
            
            # Auto-suggest destination folder (same as source PDF folder)
            pdf_folder = os.path.dirname(filename)
            self.pdf_dest_entry.delete(0, "end")
            self.pdf_dest_entry.insert(0, pdf_folder)
            
            # Auto-suggest output filename
            base_name = os.path.splitext(os.path.basename(filename))[0]
            suggested_output = f"{base_name}_reordered.pdf"
            self.pdf_output_entry.delete(0, "end")
            self.pdf_output_entry.insert(0, suggested_output)
            
            # Update status
            self.pdf_status_label.configure(text=f"Selected: {os.path.basename(filename)}")
            
    def browse_pdf_output_file(self):
        """Browse and select output file location"""
        filename = filedialog.asksaveasfilename(
            title="Save Output PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_output_entry.delete(0, "end")
            self.pdf_output_entry.insert(0, filename)
            
    def browse_pdf_destination(self):
        """Browse and select destination folder for PDF output"""
        directory = filedialog.askdirectory(title="Select Destination Folder")
        if directory:
            self.pdf_dest_entry.delete(0, "end")
            self.pdf_dest_entry.insert(0, directory)
            
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
        
    def reorder_pdf(self):
        """Reorder PDF pages using qpdf"""
        # Validate input
        pdf_file = self.pdf_file_entry.get().strip()
        start_page_str = self.pdf_page_entry.get().strip()
        output_file = self.pdf_output_entry.get().strip()
        dest_folder = self.pdf_dest_entry.get().strip()
        
        if not pdf_file:
            messagebox.showwarning("Warning", "Please select a PDF file.")
            return
            
        if not os.path.exists(pdf_file):
            messagebox.showerror("Error", "PDF file not found.")
            return
            
        try:
            start_page = int(start_page_str)
            if start_page < 1:
                raise ValueError("Starting page must be 1 or greater")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid starting page: {str(e)}")
            return
            
        # If output filename is provided without full path, combine with destination folder
        if output_file and not os.path.isabs(output_file):
            if dest_folder:
                output_file = os.path.join(dest_folder, output_file)
        elif not output_file:
            # Auto-generate output filename
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_filename = f"{base_name}_reordered.pdf"
            if dest_folder:
                output_file = os.path.join(dest_folder, output_filename)
            else:
                output_file = output_filename
            self.pdf_output_entry.insert(0, output_file)
            
        # Check if qpdf is available
        try:
            subprocess.check_output(["qpdf", "--version"], stderr=subprocess.STDOUT)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror(
                "Error", 
                "qpdf is not installed or not found in PATH.\n\n"
                "Please install qpdf first:\n"
                "  Windows: scoop install qpdf\n"
                "  macOS: brew install qpdf\n"
                "  Linux: apt install qpdf"
            )
            return
            
        # Update status
        self.pdf_status_label.configure(text="Processing PDF... Please wait.")
        self.root.update()
        
        # Run qpdf in a separate thread
        threading.Thread(target=self._reorder_pdf_thread, args=(pdf_file, start_page, output_file), daemon=True).start()
        
    def _reorder_pdf_thread(self, pdf_file, start_page, output_file):
        """Background thread for PDF reordering"""
        try:
            # Get total number of pages
            n_output = subprocess.check_output(["qpdf", "--show-npages", pdf_file]).decode().strip()
            n = int(n_output)
            
            # Build page order
            pages = list(range(1, n + 1))
            prefix = pages[:start_page - 1]
            tail = pages[start_page - 1:]
            
            reordered = []
            i = 0
            while i < len(tail):
                chunk = tail[i:i + 4]
                if len(chunk) == 4:
                    a, b, c, d = chunk
                    reordered += [a, c, b, d]  # 1,3,2,4 pattern
                else:
                    reordered += chunk  # leftover pages keep normal order
                i += 4
            
            final = prefix + reordered
            page_arg = ",".join(map(str, final))
            
            # Execute qpdf command
            subprocess.check_call([
                "qpdf", 
                pdf_file, 
                "--pages", 
                ".", 
                page_arg, 
                "--", 
                output_file
            ])
            
            # Success
            self.root.after(0, lambda: self._pdf_reorder_completed(output_file))
            
        except subprocess.CalledProcessError as e:
            error_msg = f"qpdf failed with exit code {e.returncode}"
            self.root.after(0, lambda: self._pdf_reorder_failed(error_msg))
        except Exception as e:
            self.root.after(0, lambda: self._pdf_reorder_failed(str(e)))
            
    def _pdf_reorder_completed(self, output_file):
        """Called when PDF reordering is completed"""
        self.pdf_status_label.configure(text=f"✓ Successfully saved: {os.path.basename(output_file)}")
        
        result = messagebox.askyesno(
            "Success", 
            f"PDF reordered successfully!\n\nOutput: {output_file}\n\nWould you like to open the output file?"
        )
        
        if result:
            try:
                os.startfile(output_file) if os.name == 'nt' else os.system(f'open "{output_file}"')
            except Exception as e:
                print(f"Could not open file: {e}")
                
    def _pdf_reorder_failed(self, error_msg):
        """Called when PDF reordering fails"""
        self.pdf_status_label.configure(text="✗ Reordering failed")
        messagebox.showerror("Error", f"PDF reordering failed:\n\n{error_msg}")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main function"""
    app = FileOrganizerApp()
    app.run()


if __name__ == "__main__":
    main()
