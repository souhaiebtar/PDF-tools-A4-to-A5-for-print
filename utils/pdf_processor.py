"""
PDF processing operations.
Handles page reordering and 2-up imposition using qpdf and pdfcpu.
"""

import os
from typing import List, Optional, Tuple

from utils.path_resolver import resolve_pdfcpu_path, resolve_qpdf_path
from utils.subprocess_utils import run_command, check_command


class PDFProcessor:
    """Handles PDF processing operations."""

    def __init__(self):
        self.pdfcpu_path = resolve_pdfcpu_path()
        self.qpdf_path = resolve_qpdf_path()

    def verify_tools(self) -> Tuple[bool, Optional[str]]:
        """Verify that both tools are available and working."""
        if not self.qpdf_path:
            return False, "qpdf not found"

        if not self.pdfcpu_path:
            return False, "pdfcpu not found"

        # Test qpdf
        try:
            check_command([self.qpdf_path, "--version"])
        except Exception as e:
            return False, f"qpdf failed to run: {e}"

        return True, None

    def get_page_count(self, pdf_file: str) -> int:
        """Get the number of pages in a PDF file."""
        output = check_command([self.qpdf_path, "--show-npages", pdf_file])
        return int(output.strip())

    def create_swapped_pages(self, input_file: str, output_file: str) -> None:
        """Create a PDF with swapped page pairs (2,1,4,3,6,5,...)."""
        n = self.get_page_count(input_file)

        # Create swapped page order: 2,1,4,3,6,5,...
        swapped_pages = []
        for i in range(1, n + 1, 2):
            if i + 1 <= n:
                swapped_pages.extend([i + 1, i])
            else:
                swapped_pages.append(i)

        page_arg = ",".join(map(str, swapped_pages))

        run_command(
            [
                self.qpdf_path,
                input_file,
                "--pages",
                ".",
                page_arg,
                "--",
                output_file,
            ],
            check=True,
        )

    def create_reordered_pages(
        self, input_file: str, output_file: str, start_page: int = 1
    ) -> None:
        """Create a PDF with reordered pages using 1,3,2,4 pattern."""
        n = self.get_page_count(input_file)

        pages = list(range(1, n + 1))
        prefix = pages[: start_page - 1]
        tail = pages[start_page - 1 :]

        reordered = []
        i = 0
        while i < len(tail):
            chunk = tail[i : i + 4]
            if len(chunk) == 4:
                a, b, c, d = chunk
                reordered += [a, c, b, d]  # 1,3,2,4 pattern
            else:
                reordered += chunk
            i += 4

        final = prefix + reordered
        page_arg = ",".join(map(str, final))

        run_command(
            [
                self.qpdf_path,
                input_file,
                "--pages",
                ".",
                page_arg,
                "--",
                output_file,
            ],
            check=True,
        )

    def apply_nup_imposition(self, input_file: str, output_file: str) -> None:
        """Apply 2-up imposition using pdfcpu."""
        result = run_command(
            [
                self.pdfcpu_path,
                "nup",
                "--",
                output_file,
                "2",
                input_file,
            ],
            check=False,
        )

        if result.returncode != 0:
            error_msg = f"pdfcpu failed with exit code {result.returncode}\\n\\nOutput: {result.stdout}\\n\\nError: {result.stderr}"
            raise RuntimeError(error_msg)

    def apply_nup_with_swapping(self, input_file: str, output_file: str) -> None:
        """Apply 2-up imposition with page swapping."""
        # First create swapped pages
        temp_file = output_file + ".temp.pdf"
        try:
            self.create_swapped_pages(input_file, temp_file)
            self.apply_nup_imposition(temp_file, output_file)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def apply_combined_operation(
        self,
        input_file: str,
        output_file: str,
        start_page: int = 1,
        swap_on_nup: bool = True,
    ) -> None:
        """Apply reorder + 2-up imposition in one operation."""
        temp_file = output_file + ".temp.pdf"
        swapped_nup_file = output_file + ".swapped.pdf"

        try:
            # Step 1: Reorder pages
            self.create_reordered_pages(input_file, temp_file, start_page)

            # Step 2: Apply 2-up imposition with optional swapping
            if swap_on_nup:
                self.create_swapped_pages(temp_file, swapped_nup_file)
                self.apply_nup_imposition(swapped_nup_file, output_file)
            else:
                self.apply_nup_imposition(temp_file, output_file)

        finally:
            # Clean up temporary files
            for temp in [temp_file, swapped_nup_file]:
                if os.path.exists(temp):
                    os.remove(temp)
