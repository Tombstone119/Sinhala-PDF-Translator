"""
PDF to Sinhala Translator — PyQt6 desktop application entry point.

Provides a GUI for selecting English PDF files, choosing an output folder,
and running the translation pipeline in a background thread so the UI remains
responsive throughout processing.
"""

import sys
from typing import List, Optional

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.pipeline import process_files


# ---------------------------------------------------------------------------
# Background worker
# ---------------------------------------------------------------------------

class TranslationWorker(QThread):
    """
    Runs the translation pipeline in a background thread.

    Signals:
        progress(current, total, error_or_empty): Emitted after each file
            completes. ``error_or_empty`` is an empty string on success or a
            human-readable error message on failure.
        finished(): Emitted once all files have been processed.
    """

    progress = pyqtSignal(int, int, str)   # current, total, error_or_empty
    chunk_progress = pyqtSignal(int, int)  # chunks_done, chunks_total
    all_done = pyqtSignal()

    def __init__(self, files: List[str], output_dir: str, parent=None) -> None:
        super().__init__(parent)
        self._files = files
        self._output_dir = output_dir

    # ------------------------------------------------------------------
    # QThread interface
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Entry point executed in the worker thread."""
        try:
            process_files(
                self._files,
                self._output_dir,
                progress_callback=self._on_file_done,
                chunk_callback=lambda done, total: self.chunk_progress.emit(done, total),
            )
        except Exception as exc:
            # Treat a top-level failure as a single error for the first item
            self.progress.emit(1, max(len(self._files), 1), str(exc))
        finally:
            self.all_done.emit()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _on_file_done(
        self,
        current: int,
        total: int,
        error: Optional[str],
    ) -> None:
        """Translate the pipeline callback into a Qt signal."""
        self.progress.emit(current, total, error or "")


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """Main application window for the PDF-to-Sinhala translator."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("PDF → Sinhala Translator")
        self.setMinimumWidth(640)

        self._selected_files: List[str] = []
        self._output_dir: str = ""
        self._worker: Optional[TranslationWorker] = None
        self._error_count: int = 0

        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Create and lay out all widgets."""
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(16, 16, 16, 16)

        # --- File selection ---
        btn_row_files = QHBoxLayout()
        self._btn_select_files = QPushButton("Select PDFs")
        self._btn_select_files.clicked.connect(self._on_select_files)
        btn_row_files.addWidget(self._btn_select_files)
        btn_row_files.addStretch()
        root.addLayout(btn_row_files)

        self._file_list = QListWidget()
        self._file_list.setMinimumHeight(120)
        self._file_list.setToolTip("Selected PDF files")
        root.addWidget(self._file_list)

        # --- Output folder selection ---
        btn_row_out = QHBoxLayout()
        self._btn_select_output = QPushButton("Select Output Folder")
        self._btn_select_output.clicked.connect(self._on_select_output)
        btn_row_out.addWidget(self._btn_select_output)
        btn_row_out.addStretch()
        root.addLayout(btn_row_out)

        self._lbl_output = QLabel("No output folder selected")
        self._lbl_output.setWordWrap(True)
        root.addWidget(self._lbl_output)

        # --- Start button ---
        self._btn_start = QPushButton("Start Translation")
        self._btn_start.setEnabled(False)
        self._btn_start.clicked.connect(self._on_start)
        root.addWidget(self._btn_start)

        # --- Progress bar ---
        self._progress_bar = QProgressBar()
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        root.addWidget(self._progress_bar)

        # --- Status label ---
        self._lbl_status = QLabel("Ready")
        self._lbl_status.setWordWrap(True)
        root.addWidget(self._lbl_status)

    # ------------------------------------------------------------------
    # Slots — user interactions
    # ------------------------------------------------------------------

    def _on_select_files(self) -> None:
        """Open a multi-file dialog and populate the file list."""
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select PDF Files",
            "",
            "PDF Files (*.pdf);;All Files (*)",
        )
        if not paths:
            return

        self._selected_files = paths
        self._file_list.clear()
        for path in paths:
            self._file_list.addItem(path)

        self._lbl_status.setText(f"{len(paths)} file(s) selected.")
        self._update_start_button()

    def _on_select_output(self) -> None:
        """Open a folder picker and display the chosen directory."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Folder",
            "",
        )
        if not folder:
            return

        self._output_dir = folder
        self._lbl_output.setText(folder)
        self._update_start_button()

    def _on_start(self) -> None:
        """Start the translation pipeline in a background thread."""
        if not self._selected_files or not self._output_dir:
            return

        # Reset UI state
        self._error_count = 0
        total = len(self._selected_files)
        self._progress_bar.setRange(0, total)
        self._progress_bar.setValue(0)
        self._lbl_status.setText("Starting translation…")
        self._set_controls_enabled(False)

        # Create and start the worker
        self._worker = TranslationWorker(
            files=self._selected_files,
            output_dir=self._output_dir,
            parent=self,
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.chunk_progress.connect(self._on_chunk_progress)
        self._worker.all_done.connect(self._on_finished)
        self._worker.start()

    # ------------------------------------------------------------------
    # Slots — worker signals
    # ------------------------------------------------------------------

    def _on_progress(self, current: int, total: int, error: str) -> None:
        """Update the progress bar and status label after each file."""
        self._progress_bar.setValue(current)

        if error:
            self._error_count += 1
            file_name = (
                self._selected_files[current - 1]
                if 0 < current <= len(self._selected_files)
                else "unknown file"
            )
            self._lbl_status.setText(
                f"Warning ({current}/{total}): {file_name}\n{error}"
            )
        else:
            file_name = (
                self._selected_files[current - 1]
                if 0 < current <= len(self._selected_files)
                else ""
            )
            self._lbl_status.setText(
                f"Translated {current}/{total}: {file_name}"
            )

    def _on_chunk_progress(self, done: int, total: int) -> None:
        """Update status label with per-chunk progress within the current file."""
        file_idx = self._progress_bar.value() + 1
        file_total = self._progress_bar.maximum()
        self._lbl_status.setText(
            f"Translating file {file_idx}/{file_total} — chunk {done}/{total}"
        )

    def _on_finished(self) -> None:
        """Re-enable controls and notify the user that processing is done."""
        self._set_controls_enabled(True)
        if not self._error_count:
            self._lbl_status.setText("Translation complete.")
        # else: leave the last error message visible so the user can read it

        success = len(self._selected_files) - self._error_count
        msg = f"{success}/{len(self._selected_files)} file(s) translated successfully."
        if self._error_count:
            msg += f"\n{self._error_count} file(s) failed — check status messages above."
        QMessageBox.information(self, "Translation Complete", msg)

        # Clean up the worker reference
        self._worker = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _update_start_button(self) -> None:
        """Enable the Start button only when both inputs are provided."""
        self._btn_start.setEnabled(
            bool(self._selected_files) and bool(self._output_dir)
        )

    def _set_controls_enabled(self, enabled: bool) -> None:
        """Toggle interactive controls during processing."""
        self._btn_select_files.setEnabled(enabled)
        self._btn_select_output.setEnabled(enabled)
        self._btn_start.setEnabled(enabled and bool(self._selected_files) and bool(self._output_dir))

    # ------------------------------------------------------------------
    # Window lifecycle
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:
        if self._worker is not None and self._worker.isRunning():
            reply = QMessageBox.question(
                self, "Translation in progress",
                "Translation is still running. Quit anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            self._worker.quit()
            self._worker.wait(3000)
        event.accept()


# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
