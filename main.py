#!/usr/bin/env python3
"""
PDF Tools - A modern GUI application using CustomTk
Reorder PDF pages and apply 2-up imposition using qpdf and pdfcpu.
"""

import os
import sys
import threading
from tkinter import PhotoImage, filedialog, messagebox

import customtkinter as ctk

from utils.path_resolver import resolve_app_icon_path
from utils.pdf_processor import PDFProcessor


class PDFToolsApp:
    def __init__(self):
        # Set CustomTk appearance and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create the main window
        self.root = ctk.CTk()
        self.root.title("PDF Tools - Modern GUI with CustomTk")
        self.root.geometry("650x750")
        self.root.minsize(550, 600)

        # Initialize PDF processor
        self.pdf_processor = PDFProcessor()

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

        # Create UI components
        self.create_ui()

    def create_ui(self):
        """Create all UI components."""
        self.create_scrollable_frame()
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
            label_font=ctk.CTkFont(size=20, weight="bold"),
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
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        self.header_label.grid(row=0, column=0, padx=20, pady=(15, 5))

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Apply 2-up imposition with page swapping",
            font=ctk.CTkFont(size=13),
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
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.pdf_file_label.grid(
            row=0, column=0, columnspan=2, padx=15, pady=(10, 2), sticky="w"
        )

        self.pdf_file_entry = ctk.CTkEntry(
            self.selection_frame,
            placeholder_text="Click Browse to select a PDF file...",
            height=40,
        )
        self.pdf_file_entry.grid(
            row=1, column=0, columnspan=2, padx=15, pady=2, sticky="ew"
        )

        self.pdf_browse_button = ctk.CTkButton(
            self.selection_frame,
            text="Browse",
            width=100,
            height=40,
            command=self.browse_pdf_file,
        )
        self.pdf_browse_button.grid(row=1, column=2, padx=15, pady=2)

        # Destination Folder Selection
        self.dest_folder_label = ctk.CTkLabel(
            self.selection_frame,
            text="📁 Select Destination Folder:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.dest_folder_label.grid(
            row=2, column=0, columnspan=2, padx=15, pady=(10, 2), sticky="w"
        )

        self.dest_folder_entry = ctk.CTkEntry(
            self.selection_frame,
            placeholder_text="Click Browse to select destination folder...",
            height=40,
        )
        self.dest_folder_entry.grid(
            row=3, column=0, columnspan=2, padx=15, pady=2, sticky="ew"
        )

        self.dest_browse_button = ctk.CTkButton(
            self.selection_frame,
            text="Browse",
            width=100,
            height=40,
            command=self.browse_dest_folder,
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
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.nup_header.grid(row=0, column=0, columnspan=3, padx=15, pady=(8, 8))

        # Page swapping options
        self.swap_frame = ctk.CTkFrame(self.nup_frame)
        self.swap_frame.grid(
            row=1, column=0, columnspan=3, sticky="ew", padx=15, pady=2
        )
        self.swap_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.swap_var = ctk.BooleanVar(value=False)
        self.swap_checkbox = ctk.CTkCheckBox(
            self.swap_frame,
            text="Swap left/right pages",
            variable=self.swap_var,
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.swap_checkbox.grid(row=0, column=0, padx=15, pady=5)

        self.swap_label = ctk.CTkLabel(
            self.swap_frame,
            text="Swaps pages within each pair (2,1,4,3,...)",
            font=ctk.CTkFont(size=11),
        )
        self.swap_label.grid(row=0, column=1, columnspan=2, padx=15, pady=5)

        # Output filename
        self.nup_output_label = ctk.CTkLabel(
            self.nup_frame,
            text="📝 Output Filename:",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.nup_output_label.grid(
            row=2, column=0, columnspan=2, padx=15, pady=(8, 2), sticky="w"
        )

        self.nup_output_entry = ctk.CTkEntry(
            self.nup_frame, placeholder_text="Enter output filename...", height=40
        )
        self.nup_output_entry.grid(
            row=3, column=0, columnspan=2, padx=15, pady=2, sticky="ew"
        )

        # 2-up info
        self.nup_info = ctk.CTkLabel(
            self.nup_frame,
            text="Creates 2-up imposition using pdfcpu",
            font=ctk.CTkFont(size=11),
        )
        self.nup_info.grid(row=4, column=0, columnspan=3, padx=15, pady=2)

        # N-up button
        self.nup_button = ctk.CTkButton(
            self.nup_frame,
            text="📑 Apply 2-Up Imposition",
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.apply_nup,
        )
        self.nup_button.grid(
            row=5, column=0, columnspan=3, padx=15, pady=10, sticky="ew"
        )

        self.nup_status = ctk.CTkLabel(
            self.nup_frame, text="", font=ctk.CTkFont(size=11)
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
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self.combined_header.grid(row=0, column=0, columnspan=3, padx=15, pady=(8, 8))

        # Starting Page Number
        self.start_page_label = ctk.CTkLabel(
            self.combined_frame,
            text="🔢 Starting Page (1-based):",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.start_page_label.grid(row=1, column=0, padx=15, pady=5, sticky="w")

        self.start_page_entry = ctk.CTkEntry(
            self.combined_frame, placeholder_text="1", height=35, width=100
        )
        self.start_page_entry.insert(0, "1")
        self.start_page_entry.grid(row=1, column=1, padx=15, pady=5, sticky="w")

        self.start_page_info = ctk.CTkLabel(
            self.combined_frame,
            text="Pages from here use 1,3,2,4 pattern",
            font=ctk.CTkFont(size=11),
        )
        self.start_page_info.grid(row=1, column=2, padx=15, pady=5, sticky="w")

        # Page swap on imposition checkbox
        self.combined_swap_var = ctk.BooleanVar(value=True)
        self.combined_swap_checkbox = ctk.CTkCheckBox(
            self.combined_frame,
            text="Also swap left/right on 2-up",
            variable=self.combined_swap_var,
            font=ctk.CTkFont(size=13),
        )
        self.combined_swap_checkbox.grid(
            row=2, column=0, columnspan=3, padx=15, pady=5, sticky="w"
        )

        # Output filename
        self.combined_output_label = ctk.CTkLabel(
            self.combined_frame,
            text="📝 Output Filename:",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.combined_output_label.grid(
            row=3, column=0, columnspan=2, padx=15, pady=(8, 2), sticky="w"
        )

        self.combined_output_entry = ctk.CTkEntry(
            self.combined_frame, placeholder_text="Enter output filename...", height=35
        )
        self.combined_output_entry.grid(
            row=4, column=0, columnspan=2, padx=15, pady=2, sticky="ew"
        )

        self.combined_info = ctk.CTkLabel(
            self.combined_frame,
            text="Swaps pages + applies 2-up imposition in one step",
            font=ctk.CTkFont(size=11),
        )
        self.combined_info.grid(row=5, column=0, columnspan=3, padx=15, pady=2)

        # Combined button
        self.combined_button = ctk.CTkButton(
            self.combined_frame,
            text="⚡ Reorder + Apply 2-Up",
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.apply_combined,
        )
        self.combined_button.grid(
            row=6, column=0, columnspan=3, padx=15, pady=10, sticky="ew"
        )

        self.combined_status = ctk.CTkLabel(
            self.combined_frame, text="", font=ctk.CTkFont(size=11)
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
            font=ctk.CTkFont(size=12),
        )
        self.status_label.grid(row=0, column=0, padx=15, pady=8)

    def browse_pdf_file(self):
        """Browse and select PDF file"""
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        if filename:
            self._set_pdf_file(filename)

    def browse_dest_folder(self):
        """Browse and select destination folder"""
        directory = filedialog.askdirectory(title="Select Destination Folder")
        if directory:
            self.dest_folder_entry.delete(0, "end")
            self.dest_folder_entry.insert(0, directory)

    def _set_pdf_file(self, filename: str):
        """Set PDF file and update related fields."""
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

    def apply_nup(self):
        """Apply 2-up imposition using pdfcpu with optional page swapping"""
        # Validate input and get parameters
        params = self._validate_and_get_params("nup")
        if not params:
            return

        pdf_file, output_file, swap_pages = params

        # Verify tools
        success, error = self.pdf_processor.verify_tools()
        if not success:
            self._show_tool_error(error)
            return

        # Update status and run in background
        self.nup_status.configure(
            text="Processing... Please wait.", text_color="yellow"
        )
        self.root.update()

        threading.Thread(
            target=self._nup_thread,
            args=(pdf_file, output_file, swap_pages),
            daemon=True,
        ).start()

    def _validate_and_get_params(self, operation: str):
        """Validate input and return parameters for the specified operation."""
        pdf_file = self.pdf_file_entry.get().strip()
        if not pdf_file:
            messagebox.showwarning("Warning", "Please select a PDF file.")
            return None

        if not os.path.exists(pdf_file):
            messagebox.showerror("Error", "PDF file not found.")
            return None

        dest_folder = self.dest_folder_entry.get().strip()

        if operation == "nup":
            output_file = self.nup_output_entry.get().strip()
            swap_pages = self.swap_var.get()
        else:  # combined
            output_file = self.combined_output_entry.get().strip()
            swap_pages = self.combined_swap_var.get()

        # Build output file path
        if not output_file:
            base_name = os.path.splitext(os.path.basename(pdf_file))[0]
            suffix = "_2up.pdf" if operation == "nup" else "_reordered_2up.pdf"
            output_file = f"{base_name}{suffix}"

        if dest_folder and not os.path.isabs(output_file):
            output_file = os.path.join(dest_folder, output_file)
        elif not dest_folder:
            pdf_folder = os.path.dirname(pdf_file)
            output_file = os.path.join(pdf_folder, output_file)

        return pdf_file, output_file, swap_pages

    def _show_tool_error(self, error: str):
        """Show tool-related error message."""
        messagebox.showerror("Error", f"Tool verification failed:\n\n{error}")

    def _nup_thread(self, pdf_file, output_file, swap_pages):
        """Background thread for 2-up imposition with optional page swapping"""
        try:
            if swap_pages:
                self.pdf_processor.apply_nup_with_swapping(pdf_file, output_file)
            else:
                self.pdf_processor.apply_nup_imposition(pdf_file, output_file)

            self.root.after(0, lambda: self._nup_completed(output_file))

        except Exception as e:
            self.root.after(0, lambda: self._nup_failed(str(e)))

    def _nup_completed(self, output_file):
        """Called when 2-up imposition is completed"""
        self.nup_status.configure(
            text=f"✓ Saved: {os.path.basename(output_file)}", text_color="green"
        )
        self.status_label.configure(text=f"2-up: {os.path.basename(output_file)}")

        result = messagebox.askyesno(
            "Success",
            f"2-up imposition applied successfully!\n\nOutput: {output_file}\n\nWould you like to open the file?",
        )

        if result:
            try:
                os.startfile(output_file) if os.name == "nt" else os.system(
                    f'open "{output_file}"'
                )
            except Exception as e:
                print(f"Could not open file: {e}")

    def _nup_failed(self, error_msg):
        """Called when 2-up imposition fails"""
        self.nup_status.configure(text="✗ Failed", text_color="red")
        messagebox.showerror("Error", f"2-up imposition failed:\n\n{error_msg}")

    def apply_combined(self):
        """Apply reorder (1,3,2,4 pattern) + 2-up imposition with optional left/right swap"""
        # Validate input and get parameters
        params = self._validate_and_get_params("combined")
        if not params:
            return

        pdf_file, output_file, swap_on_nup = params

        # Validate starting page
        try:
            start_page = int(self.start_page_entry.get().strip())
            if start_page < 1:
                raise ValueError("Starting page must be 1 or greater")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid starting page: {str(e)}")
            return

        # Verify tools
        success, error = self.pdf_processor.verify_tools()
        if not success:
            self._show_tool_error(error)
            return

        # Update status and run in background
        self.combined_status.configure(
            text="Processing... Please wait.", text_color="yellow"
        )
        self.root.update()

        threading.Thread(
            target=self._combined_thread,
            args=(pdf_file, start_page, output_file, swap_on_nup),
            daemon=True,
        ).start()

    def _combined_thread(self, pdf_file, start_page, output_file, swap_on_nup):
        """Background thread for combined reorder + nup with optional left/right swap"""
        try:
            self.pdf_processor.apply_combined_operation(
                pdf_file, output_file, start_page, swap_on_nup
            )

            self.root.after(0, lambda: self._combined_completed(output_file))

        except Exception as e:
            self.root.after(0, lambda: self._combined_failed(str(e)))

    def _combined_completed(self, output_file):
        """Called when combined operation is completed"""
        self.combined_status.configure(
            text=f"✓ Saved: {os.path.basename(output_file)}", text_color="green"
        )
        self.status_label.configure(text=f"Combined: {os.path.basename(output_file)}")

        result = messagebox.askyesno(
            "Success",
            f"Reorder + 2-up completed successfully!\n\nOutput: {output_file}\n\nWould you like to open the file?",
        )

        if result:
            try:
                os.startfile(output_file) if os.name == "nt" else os.system(
                    f'open "{output_file}"'
                )
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
