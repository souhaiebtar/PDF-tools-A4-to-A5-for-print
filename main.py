#!/usr/bin/env python3
"""
PDF Tools - A modern GUI application using CustomTk
Reorder PDF pages and apply 2-up imposition using qpdf and pdfcpu.
"""

import os
import shutil
import subprocess
import sys
import threading
from tkinter import PhotoImage, filedialog, messagebox

import customtkinter as ctk


def _candidate_base_dirs():
    """Where to look for bundled dependencies (dev + PyInstaller)."""
    dirs = []

    # PyInstaller: prefer folder next to the exe (where users can ship dependencies/)
    if getattr(sys, "frozen", False):
        dirs.append(os.path.dirname(sys.executable))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            dirs.append(meipass)

    # Dev: folder containing main.py
    dirs.append(os.path.dirname(os.path.abspath(__file__)))

    # De-duplicate while preserving order
    unique_dirs = []
    for d in dirs:
        if d and d not in unique_dirs:
            unique_dirs.append(d)
    return unique_dirs


def resolve_pdfcpu_path():
    env = os.environ.get("PDFCPU_PATH")
    if env and os.path.exists(env):
        return env

    exe_name = "pdfcpu.exe" if os.name == "nt" else "pdfcpu"
    for base in _candidate_base_dirs():
        candidate = os.path.join(base, "dependencies", exe_name)
        if os.path.exists(candidate):
            return candidate

    return shutil.which("pdfcpu")


def resolve_qpdf_path():
    env = os.environ.get("QPDF_PATH")
    if env and os.path.exists(env):
        return env

    exe_name = "qpdf.exe" if os.name == "nt" else "qpdf"
    for base in _candidate_base_dirs():
        candidate = os.path.join(base, "dependencies", "qpdf", exe_name)
        if os.path.exists(candidate):
            return candidate

    return shutil.which("qpdf")


def _subprocess_no_window_kwargs():
    """Suppress console windows for subprocesses on Windows GUI builds."""
    if os.name != "nt":
        return {}

    kwargs = {}

    # Prevent a console window from being created (most reliable).
    kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    # Extra safety: explicitly hide any window that might be shown.
    if hasattr(subprocess, "STARTUPINFO") and hasattr(subprocess, "STARTF_USESHOWWINDOW"):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = getattr(subprocess, "SW_HIDE", 0)
        kwargs["startupinfo"] = startupinfo

    return kwargs


def resolve_app_icon_path():
    """Return path to an app icon file (prefers .ico, falls back to .png)."""
    rel_candidates = [
        os.path.join("dependencies", "app.ico"),
        os.path.join("dependencies", "app.png"),
        "app.ico",
        "app.png",
    ]

    for base in _candidate_base_dirs():
        for rel in rel_candidates:
            candidate = os.path.join(base, rel)
            if os.path.exists(candidate):
                return candidate

    return None


# Resolved tool paths (may be None if not found)
PDFCPU_PATH = resolve_pdfcpu_path()
QPDF_PATH = resolve_qpdf_path()


class PDFToolsApp:
    def __init__(self):
        # Set CustomTk appearance and color theme
        ctk.set_appearance_mode("dark")  # Modes: "system", "dark", "light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("PDF Tools - Modern GUI with CustomTk")
        self.root.geometry("650x750")
        self.root.minsize(550, 600)

        # Window icon (separate from the EXE icon)
        self._app_icon_image = None
        self._apply_window_icon()
        
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Initialize variables
        self.pdf_file = ""
        self.pdf_dest_folder = ""
        self.reordered_file = ""
        
        # Create scrollable frame for content
        self.create_scrollable_frame()
        
        # Create the UI components inside scrollable frame
        self.create_header()
        self.create_pdf_selection()
        self.create_nup_section()
        self.create_combined_section()
        self.create_status_section()

    def _apply_window_icon(self):
        """Best-effort: set the window/taskbar icon."""
        icon_path = resolve_app_icon_path()
        if not icon_path:
            return

        # On Windows, .ico works best; otherwise use PNG via iconphoto.
        if os.name == "nt" and icon_path.lower().endswith(".ico"):
            try:
                self.root.iconbitmap(icon_path)
                return
            except Exception:
                pass

        try:
            img = PhotoImage(file=icon_path)
            self.root.iconphoto(True, img)
            # Keep a reference so Tk doesn't garbage-collect it
            self._app_icon_image = img
        except Exception:
            pass
    
    def create_scrollable_frame(self):
        """Create a scrollable frame for the main content"""
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.root,
            label_text="PDF Tools",
            label_font=ctk.CTkFont(size=20, weight="bold")
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
    def create_header(self):
        """Create the header section"""
        self.header_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 5))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="📄 PDF Tools",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(15, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Apply 2-up imposition with page swapping",
            font=ctk.CTkFont(size=13)
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 10))
        
    def create_pdf_selection(self):
        """Create PDF file selection section"""
        self.selection_frame = ctk.CTkFrame(self.scrollable_frame)
        self.selection_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.selection_frame.grid_columnconfigure(1, weight=1)
        
        # PDF File Selection
        self.pdf_file_label = ctk.CTkLabel(
            self.selection_frame, 
            text="📄 Select PDF File:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.pdf_file_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 2), sticky="w")
        
        self.pdf_file_entry = ctk.CTkEntry(
            self.selection_frame, 
            placeholder_text="Click Browse to select a PDF file...",
            height=40
        )
        self.pdf_file_entry.grid(row=1, column=0, columnspan=2, padx=15, pady=2, sticky="ew")
        
        self.pdf_browse_button = ctk.CTkButton(
            self.selection_frame,
            text="Browse",
            width=100,
            height=40,
            command=self.browse_pdf_file
        )
        self.pdf_browse_button.grid(row=1, column=2, padx=15, pady=2)
        
        # Destination Folder Selection
        self.dest_folder_label = ctk.CTkLabel(
            self.selection_frame, 
            text="📁 Select Destination Folder:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.dest_folder_label.grid(row=2, column=0, columnspan=2, padx=15, pady=(10, 2), sticky="w")
        
        self.dest_folder_entry = ctk.CTkEntry(
            self.selection_frame, 
            placeholder_text="Click Browse to select destination folder...",
            height=40
        )
        self.dest_folder_entry.grid(row=3, column=0, columnspan=2, padx=15, pady=2, sticky="ew")
        
        self.dest_browse_button = ctk.CTkButton(
            self.selection_frame,
            text="Browse",
            width=100,
            height=40,
            command=self.browse_dest_folder
        )
        self.dest_browse_button.grid(row=3, column=2, padx=15, pady=2)
        
    def create_nup_section(self):
        """Create the 2-up imposition section"""
        self.nup_frame = ctk.CTkFrame(self.scrollable_frame)
        self.nup_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.nup_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        self.nup_header = ctk.CTkLabel(
            self.nup_frame,
            text="📑 Apply 2-Up Imposition",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.nup_header.grid(row=0, column=0, columnspan=3, padx=15, pady=(8, 8))
        
        # Page swapping options
        self.swap_frame = ctk.CTkFrame(self.nup_frame)
        self.swap_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=15, pady=2)
        self.swap_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.swap_var = ctk.BooleanVar(value=False)
        self.swap_checkbox = ctk.CTkCheckBox(
            self.swap_frame,
            text="Swap left/right pages",
            variable=self.swap_var,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.swap_checkbox.grid(row=0, column=0, padx=15, pady=5)
        
        self.swap_label = ctk.CTkLabel(
            self.swap_frame,
            text="Swaps pages within each pair (2,1,4,3,...)",
            font=ctk.CTkFont(size=11)
        )
        self.swap_label.grid(row=0, column=1, columnspan=2, padx=15, pady=5)
        
        # Output filename
        self.nup_output_label = ctk.CTkLabel(
            self.nup_frame, 
            text="📝 Output Filename:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.nup_output_label.grid(row=2, column=0, columnspan=2, padx=15, pady=(8, 2), sticky="w")
        
        self.nup_output_entry = ctk.CTkEntry(
            self.nup_frame,
            placeholder_text="Enter output filename...",
            height=40
        )
        self.nup_output_entry.grid(row=3, column=0, columnspan=2, padx=15, pady=2, sticky="ew")
        
        # 2-up info
        self.nup_info = ctk.CTkLabel(
            self.nup_frame,
            text="Creates 2-up imposition using pdfcpu",
            font=ctk.CTkFont(size=11)
        )
        self.nup_info.grid(row=4, column=0, columnspan=3, padx=15, pady=2)
        
        # N-up button
        self.nup_button = ctk.CTkButton(
            self.nup_frame,
            text="📑 Apply 2-Up Imposition",
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.apply_nup
        )
        self.nup_button.grid(row=5, column=0, columnspan=3, padx=15, pady=10, sticky="ew")
        
        self.nup_status = ctk.CTkLabel(
            self.nup_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.nup_status.grid(row=6, column=0, columnspan=3, padx=15, pady=(0, 8))
        
    def create_combined_section(self):
        """Create the combined section with page swap pattern and nup"""
        self.combined_frame = ctk.CTkFrame(self.scrollable_frame)
        self.combined_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=(0, 5))
        self.combined_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        self.combined_header = ctk.CTkLabel(
            self.combined_frame,
            text="🔄 Reorder + 2-Up (Combined)",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.combined_header.grid(row=0, column=0, columnspan=3, padx=15, pady=(8, 8))
        
        # Starting Page Number
        self.start_page_label = ctk.CTkLabel(
            self.combined_frame, 
            text="🔢 Starting Page (1-based):",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.start_page_label.grid(row=1, column=0, padx=15, pady=5, sticky="w")
        
        self.start_page_entry = ctk.CTkEntry(
            self.combined_frame,
            placeholder_text="1",
            height=35,
            width=100
        )
        self.start_page_entry.insert(0, "1")
        self.start_page_entry.grid(row=1, column=1, padx=15, pady=5, sticky="w")
        
        self.start_page_info = ctk.CTkLabel(
            self.combined_frame,
            text="Pages from here use 1,3,2,4 pattern",
            font=ctk.CTkFont(size=11)
        )
        self.start_page_info.grid(row=1, column=2, padx=15, pady=5, sticky="w")
        
        # Page swap on imposition checkbox
        self.combined_swap_var = ctk.BooleanVar(value=True)
        self.combined_swap_checkbox = ctk.CTkCheckBox(
            self.combined_frame,
            text="Also swap left/right on 2-up",
            variable=self.combined_swap_var,
            font=ctk.CTkFont(size=13)
        )
        self.combined_swap_checkbox.grid(row=2, column=0, columnspan=3, padx=15, pady=5, sticky="w")
        
        # Output filename
        self.combined_output_label = ctk.CTkLabel(
            self.combined_frame, 
            text="📝 Output Filename:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.combined_output_label.grid(row=3, column=0, columnspan=2, padx=15, pady=(8, 2), sticky="w")
        
        self.combined_output_entry = ctk.CTkEntry(
            self.combined_frame,
            placeholder_text="Enter output filename...",
            height=35
        )
        self.combined_output_entry.grid(row=4, column=0, columnspan=2, padx=15, pady=2, sticky="ew")
        
        self.combined_info = ctk.CTkLabel(
            self.combined_frame,
            text="Swaps pages + applies 2-up imposition in one step",
            font=ctk.CTkFont(size=11)
        )
        self.combined_info.grid(row=5, column=0, columnspan=3, padx=15, pady=2)
        
        # Combined button
        self.combined_button = ctk.CTkButton(
            self.combined_frame,
            text="⚡ Reorder + Apply 2-Up",
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.apply_combined
        )
        self.combined_button.grid(row=6, column=0, columnspan=3, padx=15, pady=10, sticky="ew")
        
        self.combined_status = ctk.CTkLabel(
            self.combined_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.combined_status.grid(row=7, column=0, columnspan=3, padx=15, pady=(0, 8))
        
    def create_status_section(self):
        """Create the status bar section"""
        self.status_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=0)
        self.status_frame.grid(row=4, column=0, sticky="ew", padx=0, pady=(5, 0))
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready - Requires qpdf and pdfcpu",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=8)
        
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
            
            # Auto-suggest destination folder
            pdf_folder = os.path.dirname(filename)
            self.dest_folder_entry.delete(0, "end")
            self.dest_folder_entry.insert(0, pdf_folder)
            
            # Auto-suggest output filename
            base_name = os.path.splitext(os.path.basename(filename))[0]
            self.nup_output_entry.delete(0, "end")
            self.nup_output_entry.insert(0, f"{base_name}_2up.pdf")
            self.combined_output_entry.delete(0, "end")
            self.combined_output_entry.insert(0, f"{base_name}_reordered_2up.pdf")
            
            # Update status
            self.status_label.configure(text=f"Selected: {os.path.basename(filename)}")
            
    def browse_dest_folder(self):
        """Browse and select destination folder"""
        directory = filedialog.askdirectory(title="Select Destination Folder")
        if directory:
            self.dest_folder_entry.delete(0, "end")
            self.dest_folder_entry.insert(0, directory)
            
    def apply_nup(self):
        """Apply 2-up imposition using pdfcpu with optional page swapping"""
        # Validate input
        pdf_file = self.pdf_file_entry.get().strip()
        output_file = self.nup_output_entry.get().strip()
        dest_folder = self.dest_folder_entry.get().strip()
        swap_pages = self.swap_var.get()
        
        if not pdf_file:
            messagebox.showwarning("Warning", "Please select a PDF file.")
            return
            
        if not os.path.exists(pdf_file):
            messagebox.showerror("Error", "PDF file not found.")
            return
            
        # Build output file path
        if output_file:
            if dest_folder and not os.path.isabs(output_file):
                output_file = os.path.join(dest_folder, output_file)
            elif not dest_folder:
                pdf_folder = os.path.dirname(pdf_file)
                output_file = os.path.join(pdf_folder, output_file)
        else:
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_filename = f"{base_name}_2up.pdf"
            if dest_folder:
                output_file = os.path.join(dest_folder, output_filename)
            else:
                pdf_folder = os.path.dirname(pdf_file)
                output_file = os.path.join(pdf_folder, output_filename)
            self.nup_output_entry.insert(0, output_file)
            
        # Resolve tools (bundled dependencies/ first, then PATH)
        pdfcpu_path = resolve_pdfcpu_path()
        if not pdfcpu_path:
            exe_name = "pdfcpu.exe" if os.name == "nt" else "pdfcpu"
            searched = "\n".join(
                f"  - {os.path.join(base, 'dependencies', exe_name)}" for base in _candidate_base_dirs()
            )
            messagebox.showerror(
                "Error",
                "pdfcpu was not found.\n\n"
                "Looked for a bundled copy at:\n"
                f"{searched}\n\n"
                "Also searched in PATH.\n\n"
                "Fix: place pdfcpu in the dependencies folder."
            )
            return

        qpdf_path = resolve_qpdf_path()
        if not qpdf_path:
            exe_name = "qpdf.exe" if os.name == "nt" else "qpdf"
            searched = "\n".join(
                f"  - {os.path.join(base, 'dependencies', 'qpdf', exe_name)}" for base in _candidate_base_dirs()
            )
            messagebox.showerror(
                "Error",
                "qpdf was not found.\n\n"
                "Looked for a bundled copy at:\n"
                f"{searched}\n\n"
                "Also searched in PATH.\n\n"
                "Install options:\n"
                "  Windows: scoop install qpdf\n"
                "  macOS: brew install qpdf\n"
                "  Linux: apt install qpdf"
            )
            return

        # Sanity check that qpdf starts (fixes false negatives from invalid args)
        version = subprocess.run(
            [qpdf_path, "--version"],
            capture_output=True,
            text=True,
            check=False,
            **_subprocess_no_window_kwargs(),
        )
        if version.returncode != 0:
            messagebox.showerror(
                "Error",
                "qpdf was found but failed to run.\n\n"
                f"Command: {qpdf_path} --version\n\n"
                f"Output:\n{version.stdout}\n\nError:\n{version.stderr}"
            )
            return
            
        # Update status
        self.nup_status.configure(text="Processing... Please wait.", text_color="yellow")
        self.root.update()
        
        # Run in a separate thread
        threading.Thread(
            target=self._nup_thread,
            args=(pdf_file, output_file, swap_pages, pdfcpu_path, qpdf_path),
            daemon=True
        ).start()
        
    def _nup_thread(self, pdf_file, output_file, swap_pages, pdfcpu_path, qpdf_path):
        """Background thread for 2-up imposition with optional page swapping"""
        try:
            temp_file = None
            
            # If swapping pages, first reorder with swapped pairs
            if swap_pages:
                temp_file = output_file + ".temp.pdf"
                
                # Get total number of pages
                n_output = subprocess.check_output(
                    [qpdf_path, "--show-npages", pdf_file],
                    **_subprocess_no_window_kwargs(),
                ).decode().strip()
                n = int(n_output)
                
                # Create swapped page order: 2,1,4,3,6,5,...
                swapped_pages = []
                for i in range(1, n + 1, 2):
                    if i + 1 <= n:
                        swapped_pages.extend([i + 1, i])
                    else:
                        swapped_pages.append(i)
                
                page_arg = ",".join(map(str, swapped_pages))
                
                # Execute qpdf command to create swapped PDF
                subprocess.check_call(
                    [
                        qpdf_path,
                        pdf_file,
                        "--pages",
                        ".",
                        page_arg,
                        "--",
                        temp_file,
                    ],
                    **_subprocess_no_window_kwargs(),
                )
                
                input_for_nup = temp_file
            else:
                input_for_nup = pdf_file
            
            # Apply 2-up imposition with pdfcpu
            result = subprocess.run(
                [
                    pdfcpu_path,
                    "nup",
                    "--",
                    output_file,
                    "2",
                    input_for_nup,
                ],
                capture_output=True,
                text=True,
                check=False,
                **_subprocess_no_window_kwargs(),
            )
            
            # Clean up temporary file
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)
            
            if result.returncode != 0:
                error_msg = f"pdfcpu failed with exit code {result.returncode}\n\nOutput: {result.stdout}\n\nError: {result.stderr}"
                self.root.after(0, lambda: self._nup_failed(error_msg))
            else:
                self.root.after(0, lambda: self._nup_completed(output_file))
            
        except subprocess.CalledProcessError as e:
            # Clean up temp file if it exists
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            error_msg = f"Operation failed with exit code {e.returncode}"
            self.root.after(0, lambda: self._nup_failed(error_msg))
        except Exception as e:
            # Clean up temp file if it exists
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            self.root.after(0, lambda: self._nup_failed(str(e)))
            
    def _nup_completed(self, output_file):
        """Called when 2-up imposition is completed"""
        self.nup_status.configure(text=f"✓ Saved: {os.path.basename(output_file)}", text_color="green")
        self.status_label.configure(text=f"2-up: {os.path.basename(output_file)}")
        
        result = messagebox.askyesno(
            "Success", 
            f"2-up imposition applied successfully!\n\nOutput: {output_file}\n\nWould you like to open the file?"
        )
        
        if result:
            try:
                os.startfile(output_file) if os.name == 'nt' else os.system(f'open "{output_file}"')
            except Exception as e:
                print(f"Could not open file: {e}")
                
    def _nup_failed(self, error_msg):
        """Called when 2-up imposition fails"""
        self.nup_status.configure(text="✗ Failed", text_color="red")
        messagebox.showerror("Error", f"2-up imposition failed:\n\n{error_msg}")
        
    def apply_combined(self):
        """Apply reorder (1,3,2,4 pattern) + 2-up imposition with optional left/right swap"""
        # Validate input
        pdf_file = self.pdf_file_entry.get().strip()
        start_page_str = self.start_page_entry.get().strip()
        output_file = self.combined_output_entry.get().strip()
        dest_folder = self.dest_folder_entry.get().strip()
        swap_on_nup = self.combined_swap_var.get()
        
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
            
        # Build output file path
        base_name = os.path.splitext(os.path.basename(pdf_file))[0]
        if dest_folder:
            temp_file = os.path.join(dest_folder, f"{base_name}_temp.pdf")
            if output_file:
                final_output = os.path.join(dest_folder, output_file)
            else:
                final_output = os.path.join(dest_folder, f"{base_name}_reordered_2up.pdf")
        else:
            pdf_folder = os.path.dirname(pdf_file)
            temp_file = os.path.join(pdf_folder, f"{base_name}_temp.pdf")
            if output_file:
                final_output = os.path.join(pdf_folder, output_file)
            else:
                final_output = os.path.join(pdf_folder, f"{base_name}_reordered_2up.pdf")

        # Resolve tools (bundled dependencies/ first, then PATH)
        pdfcpu_path = resolve_pdfcpu_path()
        if not pdfcpu_path:
            exe_name = "pdfcpu.exe" if os.name == "nt" else "pdfcpu"
            searched = "\n".join(
                f"  - {os.path.join(base, 'dependencies', exe_name)}" for base in _candidate_base_dirs()
            )
            messagebox.showerror(
                "Error",
                "pdfcpu was not found.\n\n"
                "Looked for a bundled copy at:\n"
                f"{searched}\n\n"
                "Also searched in PATH.\n\n"
                "Fix: place pdfcpu in the dependencies folder."
            )
            return

        qpdf_path = resolve_qpdf_path()
        if not qpdf_path:
            exe_name = "qpdf.exe" if os.name == "nt" else "qpdf"
            searched = "\n".join(
                f"  - {os.path.join(base, 'dependencies', 'qpdf', exe_name)}" for base in _candidate_base_dirs()
            )
            messagebox.showerror(
                "Error",
                "qpdf was not found.\n\n"
                "Looked for a bundled copy at:\n"
                f"{searched}\n\n"
                "Also searched in PATH.\n\n"
                "Install options:\n"
                "  Windows: scoop install qpdf\n"
                "  macOS: brew install qpdf\n"
                "  Linux: apt install qpdf"
            )
            return

        version = subprocess.run(
            [qpdf_path, "--version"],
            capture_output=True,
            text=True,
            check=False,
            **_subprocess_no_window_kwargs(),
        )
        if version.returncode != 0:
            messagebox.showerror(
                "Error",
                "qpdf was found but failed to run.\n\n"
                f"Command: {qpdf_path} --version\n\n"
                f"Output:\n{version.stdout}\n\nError:\n{version.stderr}"
            )
            return
                
        # Update status
        self.combined_status.configure(text="Processing... Please wait.", text_color="yellow")
        self.root.update()
        
        # Run combined operation in a separate thread
        threading.Thread(
            target=self._combined_thread,
            args=(pdf_file, start_page, temp_file, final_output, swap_on_nup, pdfcpu_path, qpdf_path),
            daemon=True
        ).start()
        
    def _combined_thread(self, pdf_file, start_page, temp_file, final_output, swap_on_nup, pdfcpu_path, qpdf_path):
        """Background thread for combined reorder + nup with optional left/right swap"""
        try:
            # Step 1: Reorder pages with 1,3,2,4 pattern from starting page
            n_output = subprocess.check_output(
                [qpdf_path, "--show-npages", pdf_file],
                **_subprocess_no_window_kwargs(),
            ).decode().strip()
            n = int(n_output)
            
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
                    reordered += chunk
                i += 4
            
            final = prefix + reordered
            page_arg = ",".join(map(str, final))
            
            # Execute qpdf command to create reordered PDF
            subprocess.check_call(
                [
                    qpdf_path,
                    pdf_file,
                    "--pages",
                    ".",
                    page_arg,
                    "--",
                    temp_file,
                ],
                **_subprocess_no_window_kwargs(),
            )
            
            # Step 2: Apply 2-up imposition
            input_for_nup = temp_file
            
            # If swapping left/right on 2-up, create another temp file with swapped pairs
            if swap_on_nup:
                swapped_nup_file = final_output + ".swapped.pdf"
                
                # Get page count of reordered PDF
                n2_output = subprocess.check_output(
                    [qpdf_path, "--show-npages", temp_file],
                    **_subprocess_no_window_kwargs(),
                ).decode().strip()
                n2 = int(n2_output)
                
                # Create swapped page order for 2-up: 2,1,4,3,6,5,...
                swapped_pages = []
                for i in range(1, n2 + 1, 2):
                    if i + 1 <= n2:
                        swapped_pages.extend([i + 1, i])
                    else:
                        swapped_pages.append(i)
                
                page_arg2 = ",".join(map(str, swapped_pages))
                
                # Execute qpdf command
                subprocess.check_call(
                    [
                        qpdf_path,
                        temp_file,
                        "--pages",
                        ".",
                        page_arg2,
                        "--",
                        swapped_nup_file,
                    ],
                    **_subprocess_no_window_kwargs(),
                )
                
                input_for_nup = swapped_nup_file
            
            # Step 3: Apply pdfcpu nup
            result = subprocess.run(
                [
                    pdfcpu_path,
                    "nup",
                    "--",
                    final_output,
                    "2",
                    input_for_nup,
                ],
                capture_output=True,
                text=True,
                check=False,
                **_subprocess_no_window_kwargs(),
            )
            
            # Clean up temporary files
            if os.path.exists(temp_file):
                os.remove(temp_file)
            if swap_on_nup:
                swapped_file = final_output + ".swapped.pdf"
                if os.path.exists(swapped_file):
                    os.remove(swapped_file)
            
            if result.returncode != 0:
                error_msg = f"pdfcpu failed with exit code {result.returncode}\n\nOutput: {result.stdout}\n\nError: {result.stderr}"
                self.root.after(0, lambda: self._combined_failed(error_msg))
            else:
                self.root.after(0, lambda: self._combined_completed(final_output))
            
        except subprocess.CalledProcessError as e:
            # Clean up temp files
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            error_msg = f"Operation failed with exit code {e.returncode}"
            self.root.after(0, lambda: self._combined_failed(error_msg))
        except Exception as e:
            error_msg = str(e)
            # Clean up temp files
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            self.root.after(0, lambda msg=error_msg: self._combined_failed(msg))
            
    def _combined_completed(self, output_file):
        """Called when combined operation is completed"""
        self.combined_status.configure(text=f"✓ Saved: {os.path.basename(output_file)}", text_color="green")
        self.status_label.configure(text=f"Combined: {os.path.basename(output_file)}")
        
        result = messagebox.askyesno(
            "Success", 
            f"Reorder + 2-up completed successfully!\n\nOutput: {output_file}\n\nWould you like to open the file?"
        )
        
        if result:
            try:
                os.startfile(output_file) if os.name == 'nt' else os.system(f'open "{output_file}"')
            except Exception as e:
                print(f"Could not open file: {e}")
                
    def _combined_failed(self, error_msg):
        """Called when combined operation fails"""
        self.combined_status.configure(text="✗ Failed", text_color="red")
        messagebox.showerror("Error", f"Combined operation failed:\n\n{error_msg}")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main function"""
    app = PDFToolsApp()
    app.run()


if __name__ == "__main__":
    main()
