#!/usr/bin/env python3
"""
PDF Reorder - A modern GUI application using CustomTk
Reorder PDF pages using qpdf with the 1,3,2,4 pattern.
"""

import os
import subprocess
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk


class PDFReorderApp:
    def __init__(self):
        # Set CustomTk appearance and color theme
        ctk.set_appearance_mode("dark")  # Modes: "system", "dark", "light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
        
        # Create the main window
        self.root = ctk.CTk()
        self.root.title("PDF Reorder - Modern GUI with CustomTk")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)
        
        # Configure grid layout
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)
        
        # Initialize variables
        self.pdf_file = ""
        self.pdf_dest_folder = ""
        self.pdf_output_file = ""
        
        # Create the UI components
        self.create_header()
        self.create_input_section()
        self.create_action_section()
        self.create_status_bar()
        
    def create_header(self):
        """Create the header section"""
        self.header_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text="📄 PDF Page Reorder",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.header_label.grid(row=0, column=0, padx=30, pady=(30, 10))
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Reorder pages starting from a specific page using 1,3,2,4 pattern",
            font=ctk.CTkFont(size=13)
        )
        self.subtitle_label.grid(row=1, column=0, padx=30, pady=(0, 30))
        
    def create_input_section(self):
        """Create the input section with all fields"""
        self.input_frame = ctk.CTkFrame(self.root)
        self.input_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.input_frame.grid_columnconfigure(1, weight=1)
        
        # PDF File Selection
        self.pdf_file_label = ctk.CTkLabel(
            self.input_frame, 
            text="📄 Select PDF File:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.pdf_file_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")
        
        self.pdf_file_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Click Browse to select a PDF file...",
            height=40
        )
        self.pdf_file_entry.grid(row=1, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.pdf_browse_button = ctk.CTkButton(
            self.input_frame,
            text="Browse",
            width=100,
            height=40,
            command=self.browse_pdf_file
        )
        self.pdf_browse_button.grid(row=1, column=2, padx=20, pady=5)
        
        # Destination Folder Selection
        self.dest_folder_label = ctk.CTkLabel(
            self.input_frame, 
            text="📁 Select Destination Folder:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.dest_folder_label.grid(row=2, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")
        
        self.dest_folder_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Click Browse to select destination folder...",
            height=40
        )
        self.dest_folder_entry.grid(row=3, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.dest_browse_button = ctk.CTkButton(
            self.input_frame,
            text="Browse",
            width=100,
            height=40,
            command=self.browse_dest_folder
        )
        self.dest_browse_button.grid(row=3, column=2, padx=20, pady=5)
        
        # Starting Page Number
        self.start_page_label = ctk.CTkLabel(
            self.input_frame, 
            text="🔢 Starting Page Number:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_page_label.grid(row=4, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")
        
        self.start_page_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter starting page (1-based)",
            height=40,
            width=150
        )
        self.start_page_entry.insert(0, "10")  # Default value
        self.start_page_entry.grid(row=5, column=0, padx=20, pady=5, sticky="w")
        
        self.start_page_info = ctk.CTkLabel(
            self.input_frame,
            text="Pages will be reordered from this point using 1,3,2,4 pattern",
            font=ctk.CTkFont(size=11)
        )
        self.start_page_info.grid(row=5, column=1, columnspan=2, padx=10, pady=5, sticky="w")
        
        # Output Filename
        self.output_file_label = ctk.CTkLabel(
            self.input_frame, 
            text="📝 Output Filename:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.output_file_label.grid(row=6, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="w")
        
        self.output_file_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Enter output filename...",
            height=40
        )
        self.output_file_entry.grid(row=7, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
    def create_action_section(self):
        """Create the action button section"""
        self.action_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.action_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.action_frame.grid_columnconfigure(0, weight=1)
        
        self.reorder_button = ctk.CTkButton(
            self.action_frame,
            text="🔄 Reorder PDF Pages",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.reorder_pdf
        )
        self.reorder_button.grid(row=0, column=0, padx=30, pady=20, sticky="ew")
        
        self.status_label = ctk.CTkLabel(
            self.action_frame,
            text="Ready to reorder PDF pages",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.grid(row=1, column=0, padx=30, pady=(0, 15))
        
    def create_status_bar(self):
        """Create the status bar at the bottom"""
        self.status_frame = ctk.CTkFrame(self.root, height=25)
        self.status_frame.grid(row=3, column=0, sticky="ew")
        self.status_frame.grid_propagate(False)
        
        self.footer_label = ctk.CTkLabel(
            self.status_frame,
            text="Requires qpdf to be installed",
            anchor="w"
        )
        self.footer_label.pack(side="left", padx=10, pady=3)
        
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
            self.dest_folder_entry.delete(0, "end")
            self.dest_folder_entry.insert(0, pdf_folder)
            
            # Auto-suggest output filename
            base_name = os.path.splitext(os.path.basename(filename))[0]
            suggested_output = f"{base_name}_reordered.pdf"
            self.output_file_entry.delete(0, "end")
            self.output_file_entry.insert(0, suggested_output)
            
            # Update status
            self.status_label.configure(text=f"Selected: {os.path.basename(filename)}")
            
    def browse_dest_folder(self):
        """Browse and select destination folder"""
        directory = filedialog.askdirectory(title="Select Destination Folder")
        if directory:
            self.dest_folder_entry.delete(0, "end")
            self.dest_folder_entry.insert(0, directory)
            
    def reorder_pdf(self):
        """Reorder PDF pages using qpdf"""
        # Validate input
        pdf_file = self.pdf_file_entry.get().strip()
        start_page_str = self.start_page_entry.get().strip()
        output_file = self.output_file_entry.get().strip()
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
        if output_file:
            if dest_folder and not os.path.isabs(output_file):
                output_file = os.path.join(dest_folder, output_file)
            elif not dest_folder:
                # Use same folder as input PDF
                pdf_folder = os.path.dirname(pdf_file)
                output_file = os.path.join(pdf_folder, output_file)
        else:
            # Auto-generate output filename
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            output_filename = f"{base_name}_reordered.pdf"
            if dest_folder:
                output_file = os.path.join(dest_folder, output_filename)
            else:
                pdf_folder = os.path.dirname(pdf_file)
                output_file = os.path.join(pdf_folder, output_filename)
            self.output_file_entry.insert(0, output_file)
            
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
        self.status_label.configure(text="Processing PDF... Please wait.")
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
        self.status_label.configure(text=f"✓ Successfully saved: {os.path.basename(output_file)}")
        
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
        self.status_label.configure(text="✗ Reordering failed")
        messagebox.showerror("Error", f"PDF reordering failed:\n\n{error_msg}")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()


def main():
    """Main function"""
    app = PDFReorderApp()
    app.run()


if __name__ == "__main__":
    main()
