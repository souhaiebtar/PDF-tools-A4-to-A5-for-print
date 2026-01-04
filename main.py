#!/usr/bin/env python3
"""
PDF Tools - A modern GUI application using CustomTk
Reorder PDF pages and apply 2-up imposition using qpdf and pdfcpu.
"""

import os
import subprocess
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk


class PDFToolsApp:
    def __init__(self):
        # Set CustomTk appearance and color theme
        ctk.set_appearance_mode("dark")  # Modes: "system", "dark", "light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("PDF Tools - Modern GUI with CustomTk")
        self.root.geometry("650x750")
        self.root.minsize(550, 650)
        
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(4, weight=1)
        
        # Initialize variables
        self.pdf_file = ""
        self.pdf_dest_folder = ""
        self.reordered_file = ""
        
        # Create the UI components
        self.create_header()
        self.create_pdf_selection()
        self.create_reorder_section()
        self.create_nup_section()
        self.create_combined_section()
        self.create_status_section()
        
    def create_header(self):
        """Create the header section"""
        self.header_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="📄 PDF Tools",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.header_label.grid(row=0, column=0, padx=30, pady=(30, 10))
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Reorder pages and apply 2-up imposition",
            font=ctk.CTkFont(size=13)
        )
        self.subtitle_label.grid(row=1, column=0, padx=30, pady=(0, 20))
        
    def create_pdf_selection(self):
        """Create PDF file selection section"""
        self.selection_frame = ctk.CTkFrame(self.root)
        self.selection_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.selection_frame.grid_columnconfigure(1, weight=1)
        
        # PDF File Selection
        self.pdf_file_label = ctk.CTkLabel(
            self.selection_frame, 
            text="📄 Select PDF File:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.pdf_file_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")
        
        self.pdf_file_entry = ctk.CTkEntry(
            self.selection_frame, 
            placeholder_text="Click Browse to select a PDF file...",
            height=40
        )
        self.pdf_file_entry.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.pdf_browse_button = ctk.CTkButton(
            self.selection_frame,
            text="Browse",
            width=100,
            height=40,
            command=self.browse_pdf_file
        )
        self.pdf_browse_button.grid(row=1, column=2, padx=20, pady=5)
        
        # Destination Folder Selection
        self.dest_folder_label = ctk.CTkLabel(
            self.selection_frame, 
            text="📁 Select Destination Folder:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.dest_folder_label.grid(row=2, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")
        
        self.dest_folder_entry = ctk.CTkEntry(
            self.selection_frame, 
            placeholder_text="Click Browse to select destination folder...",
            height=40
        )
        self.dest_folder_entry.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.dest_browse_button = ctk.CTkButton(
            self.selection_frame,
            text="Browse",
            width=100,
            height=40,
            command=self.browse_dest_folder
        )
        self.dest_browse_button.grid(row=3, column=2, padx=20, pady=5)
        
    def create_reorder_section(self):
        """Create the page reordering section"""
        self.reorder_frame = ctk.CTkFrame(self.root)
        self.reorder_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.reorder_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        self.reorder_header = ctk.CTkLabel(
            self.reorder_frame,
            text="🔄 Step 1: Reorder Pages (Optional)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.reorder_header.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10))
        
        # Starting Page Number
        self.start_page_label = ctk.CTkLabel(
            self.reorder_frame, 
            text="🔢 Starting Page (1-based):",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.start_page_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.start_page_entry = ctk.CTkEntry(
            self.reorder_frame,
            placeholder_text="10",
            height=35,
            width=100
        )
        self.start_page_entry.insert(0, "10")
        self.start_page_entry.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        self.start_page_info = ctk.CTkLabel(
            self.reorder_frame,
            text="Pages from here use 1,3,2,4 pattern",
            font=ctk.CTkFont(size=11)
        )
        self.start_page_info.grid(row=1, column=2, padx=20, pady=5, sticky="w")
        
        # Reorder button
        self.reorder_button = ctk.CTkButton(
            self.reorder_frame,
            text="🔄 Reorder Pages",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.reorder_pdf
        )
        self.reorder_button.grid(row=2, column=0, columnspan=3, padx=20, pady=15, sticky="ew")
        
        self.reorder_status = ctk.CTkLabel(
            self.reorder_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.reorder_status.grid(row=3, column=0, columnspan=3, padx=20, pady=(0, 15))
        
    def create_nup_section(self):
        """Create the 2-up imposition section"""
        self.nup_frame = ctk.CTkFrame(self.root)
        self.nup_frame.grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        self.nup_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        self.nup_header = ctk.CTkLabel(
            self.nup_frame,
            text="📑 Step 2: 2-Up Imposition (Optional)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.nup_header.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10))
        
        # Input file for nup
        self.nup_input_label = ctk.CTkLabel(
            self.nup_frame, 
            text="📄 Input File for 2-up:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.nup_input_label.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        
        self.nup_input_entry = ctk.CTkEntry(
            self.nup_frame,
            placeholder_text="Auto-filled after reorder or select manually...",
            height=35
        )
        self.nup_input_entry.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.nup_browse_button = ctk.CTkButton(
            self.nup_frame,
            text="Browse",
            width=80,
            height=35,
            command=self.browse_nup_input
        )
        self.nup_browse_button.grid(row=2, column=2, padx=20, pady=5)
        
        # Output filename for nup
        self.nup_output_label = ctk.CTkLabel(
            self.nup_frame, 
            text="📝 Output Filename:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.nup_output_label.grid(row=3, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")
        
        self.nup_output_entry = ctk.CTkEntry(
            self.nup_frame,
            placeholder_text="Enter output filename...",
            height=35
        )
        self.nup_output_entry.grid(row=4, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        # 2-up info
        self.nup_info = ctk.CTkLabel(
            self.nup_frame,
            text="Creates 2-up imposition using pdfcpu",
            font=ctk.CTkFont(size=11)
        )
        self.nup_info.grid(row=5, column=0, columnspan=3, padx=20, pady=5)
        
        # N-up button
        self.nup_button = ctk.CTkButton(
            self.nup_frame,
            text="📑 Apply 2-Up Imposition",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.apply_nup
        )
        self.nup_button.grid(row=6, column=0, columnspan=3, padx=20, pady=15, sticky="ew")
        
        self.nup_status = ctk.CTkLabel(
            self.nup_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.nup_status.grid(row=7, column=0, columnspan=3, padx=20, pady=(0, 15))
        
    def create_combined_section(self):
        """Create the combined reorder + nup section"""
        self.combined_frame = ctk.CTkFrame(self.root)
        self.combined_frame.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 10))
        self.combined_frame.grid_columnconfigure(1, weight=1)
        
        # Section header
        self.combined_header = ctk.CTkLabel(
            self.combined_frame,
            text="⚡ Step 3: Reorder + 2-Up (Combined)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.combined_header.grid(row=0, column=0, columnspan=3, padx=20, pady=(15, 10))
        
        # Starting Page Number
        self.combined_start_page_label = ctk.CTkLabel(
            self.combined_frame, 
            text="🔢 Starting Page (1-based):",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.combined_start_page_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        
        self.combined_start_page_entry = ctk.CTkEntry(
            self.combined_frame,
            placeholder_text="10",
            height=35,
            width=100
        )
        self.combined_start_page_entry.insert(0, "10")
        self.combined_start_page_entry.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        self.combined_info = ctk.CTkLabel(
            self.combined_frame,
            text="Swap pages + apply 2-up imposition in one step",
            font=ctk.CTkFont(size=11)
        )
        self.combined_info.grid(row=1, column=2, padx=20, pady=5, sticky="w")
        
        # Output filename for combined
        self.combined_output_label = ctk.CTkLabel(
            self.combined_frame, 
            text="📝 Output Filename:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.combined_output_label.grid(row=2, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")
        
        self.combined_output_entry = ctk.CTkEntry(
            self.combined_frame,
            placeholder_text="Enter output filename...",
            height=35
        )
        self.combined_output_entry.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        # Combined button
        self.combined_button = ctk.CTkButton(
            self.combined_frame,
            text="⚡ Reorder + Apply 2-Up",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.apply_combined
        )
        self.combined_button.grid(row=4, column=0, columnspan=3, padx=20, pady=15, sticky="ew")
        
        self.combined_status = ctk.CTkLabel(
            self.combined_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.combined_status.grid(row=5, column=0, columnspan=3, padx=20, pady=(0, 15))
        
    def create_status_section(self):
        """Create the status bar section"""
        self.status_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.status_frame.grid(row=5, column=0, sticky="ew", padx=0, pady=0)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready - Requires qpdf and pdfcpu",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=15)
        
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
            
            # Auto-suggest nup input
            self.nup_input_entry.delete(0, "end")
            self.nup_input_entry.insert(0, filename)
            
            # Auto-suggest combined output filename
            base_name = os.path.splitext(os.path.basename(filename))[0]
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
            
    def browse_nup_input(self):
        """Browse and select input file for nup"""
        filename = filedialog.askopenfilename(
            title="Select Input PDF for 2-up",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.nup_input_entry.delete(0, "end")
            self.nup_input_entry.insert(0, filename)
            
    def reorder_pdf(self):
        """Reorder PDF pages using qpdf"""
        # Validate input
        pdf_file = self.pdf_file_entry.get().strip()
        start_page_str = self.start_page_entry.get().strip()
        dest_folder = self.dest_folder_entry.get().strip()
        
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
        output_filename = f"{base_name}_reordered.pdf"
        if dest_folder:
            output_file = os.path.join(dest_folder, output_filename)
        else:
            pdf_folder = os.path.dirname(pdf_file)
            output_file = os.path.join(pdf_folder, output_filename)
            
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
        self.reorder_status.configure(text="Processing... Please wait.", text_color="yellow")
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
            self.reordered_file = output_file
            self.root.after(0, lambda: self._reorder_completed(output_file))
            
        except subprocess.CalledProcessError as e:
            error_msg = f"qpdf failed with exit code {e.returncode}"
            self.root.after(0, lambda: self._reorder_failed(error_msg))
        except Exception as e:
            self.root.after(0, lambda: self._reorder_failed(str(e)))
            
    def _reorder_completed(self, output_file):
        """Called when PDF reordering is completed"""
        self.reorder_status.configure(text=f"✓ Saved: {os.path.basename(output_file)}", text_color="green")
        self.status_label.configure(text=f"Reordered: {os.path.basename(output_file)}")
        
        # Auto-fill nup input with reordered file
        self.nup_input_entry.delete(0, "end")
        self.nup_input_entry.insert(0, output_file)
        
        # Suggest nup output filename
        base_name = os.path.splitext(os.path.basename(output_file))[0]
        self.nup_output_entry.delete(0, "end")
        self.nup_output_entry.insert(0, f"{base_name}_2up.pdf")
        
        result = messagebox.askyesno(
            "Success", 
            f"PDF reordered successfully!\n\nOutput: {output_file}\n\nWould you like to open the file?"
        )
        
        if result:
            try:
                os.startfile(output_file) if os.name == 'nt' else os.system(f'open "{output_file}"')
            except Exception as e:
                print(f"Could not open file: {e}")
                
    def _reorder_failed(self, error_msg):
        """Called when PDF reordering fails"""
        self.reorder_status.configure(text="✗ Failed", text_color="red")
        messagebox.showerror("Error", f"PDF reordering failed:\n\n{error_msg}")
        
    def apply_nup(self):
        """Apply 2-up imposition using pdfcpu"""
        # Validate input
        input_file = self.nup_input_entry.get().strip()
        output_file = self.nup_output_entry.get().strip()
        dest_folder = self.dest_folder_entry.get().strip()
        
        if not input_file:
            messagebox.showwarning("Warning", "Please select an input PDF file.")
            return
            
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Input PDF file not found.")
            return
            
        # Build output file path
        if output_file:
            if dest_folder and not os.path.isabs(output_file):
                output_file = os.path.join(dest_folder, output_file)
            elif not dest_folder:
                pdf_folder = os.path.dirname(input_file)
                output_file = os.path.join(pdf_folder, output_file)
        else:
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_filename = f"{base_name}_2up.pdf"
            if dest_folder:
                output_file = os.path.join(dest_folder, output_filename)
            else:
                pdf_folder = os.path.dirname(input_file)
                output_file = os.path.join(pdf_folder, output_filename)
            self.nup_output_entry.insert(0, output_file)
            
        # Check if pdfcpu is available
        try:
            subprocess.check_output(["pdfcpu", "version"], stderr=subprocess.STDOUT)
        except (subprocess.CalledProcessError, FileNotFoundError):
            messagebox.showerror(
                "Error", 
                "pdfcpu is not installed or not found in PATH.\n\n"
                "Please install pdfcpu first:\n"
                "  Windows: scoop install pdfcpu\n"
                "  macOS: brew install pdfcpu\n"
                "  Linux: apt install pdfcpu"
            )
            return
            
        # Update status
        self.nup_status.configure(text="Processing... Please wait.", text_color="yellow")
        self.root.update()
        
        # Run pdfcpu in a separate thread
        threading.Thread(target=self._nup_thread, args=(input_file, output_file), daemon=True).start()
        
    def _nup_thread(self, input_file, output_file):
        """Background thread for 2-up imposition"""
        try:
            # Execute pdfcpu nup command (correct syntax: pdfcpu nup -- outFile n inFile)
            result = subprocess.run([
                "pdfcpu", 
                "nup", 
                "--", 
                output_file,
                "2", 
                input_file
            ], capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                error_msg = f"pdfcpu failed with exit code {result.returncode}\n\nOutput: {result.stdout}\n\nError: {result.stderr}"
                self.root.after(0, lambda: self._nup_failed(error_msg))
            else:
                self.root.after(0, lambda: self._nup_completed(output_file))
            
        except subprocess.CalledProcessError as e:
            error_msg = f"pdfcpu failed with exit code {e.returncode}\n\nOutput: {e.stdout}\n\nError: {e.stderr}"
            self.root.after(0, lambda: self._nup_failed(error_msg))
        except Exception as e:
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
        """Apply reorder + 2-up imposition in one combined step"""
        # Validate input
        pdf_file = self.pdf_file_entry.get().strip()
        start_page_str = self.combined_start_page_entry.get().strip()
        output_file = self.combined_output_entry.get().strip()
        dest_folder = self.dest_folder_entry.get().strip()
        
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
            
        # Build intermediate and output file paths
        base_name = os.path.splitext(os.path.basename(pdf_file))[0]
        if dest_folder:
            temp_file = os.path.join(dest_folder, f"{base_name}_temp_reordered.pdf")
            if output_file:
                final_output = os.path.join(dest_folder, output_file)
            else:
                final_output = os.path.join(dest_folder, f"{base_name}_reordered_2up.pdf")
        else:
            pdf_folder = os.path.dirname(pdf_file)
            temp_file = os.path.join(pdf_folder, f"{base_name}_temp_reordered.pdf")
            if output_file:
                final_output = os.path.join(pdf_folder, output_file)
            else:
                final_output = os.path.join(pdf_folder, f"{base_name}_reordered_2up.pdf")
                
        # Update status
        self.combined_status.configure(text="Processing... Please wait.", text_color="yellow")
        self.root.update()
        
        # Run combined operation in a separate thread
        threading.Thread(target=self._combined_thread, args=(pdf_file, start_page, temp_file, final_output), daemon=True).start()
        
    def _combined_thread(self, pdf_file, start_page, temp_file, final_output):
        """Background thread for combined reorder + nup"""
        try:
            # Step 1: Reorder pages with qpdf
            n_output = subprocess.check_output(["qpdf", "--show-npages", pdf_file]).decode().strip()
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
            subprocess.check_call([
                "qpdf", 
                pdf_file, 
                "--pages", 
                ".", 
                page_arg, 
                "--", 
                temp_file
            ])
            
            # Step 2: Apply 2-up imposition with pdfcpu
            result = subprocess.run([
                "pdfcpu", 
                "nup", 
                "--", 
                final_output,
                "2", 
                temp_file
            ], capture_output=True, text=True, check=False)
            
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)
            
            if result.returncode != 0:
                error_msg = f"pdfcpu failed with exit code {result.returncode}\n\nOutput: {result.stdout}\n\nError: {result.stderr}"
                self.root.after(0, lambda: self._combined_failed(error_msg))
            else:
                self.root.after(0, lambda: self._combined_completed(final_output))
            
        except subprocess.CalledProcessError as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            error_msg = f"Operation failed with exit code {e.returncode}"
            self.root.after(0, lambda: self._combined_failed(error_msg))
        except Exception as e:
            # Clean up temp file if it exists
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            self.root.after(0, lambda: self._combined_failed(str(e)))
            
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
