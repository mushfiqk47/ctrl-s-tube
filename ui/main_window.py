"""Main window UI implementation using PySide6."""

from __future__ import annotations

import os
import re
import threading
from typing import Optional, Dict, Any

from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from core.controller import Controller
from utils.config import Colors, Config, Fonts, Spacing


class FetchWorker(QObject):
    """Worker object to fetch metadata in a background thread."""

    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, controller: Controller, url: str):
        super().__init__()
        self.controller = controller
        self.url = url

    def run(self) -> None:
        """Execute the fetch request."""
        try:
            metadata = self.controller.fetch_metadata(self.url)
            self.finished.emit(metadata)
        except Exception as exc:  # noqa: BLE001 - bubbling up to UI layer
            self.error.emit(str(exc))


class DownloadWorker(QObject):
    """Worker object to perform downloads without blocking the UI."""

    progress = Signal(float, str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(
        self,
        controller: Controller,
        url: str,
        output_path: str,
        quality: Optional[str],
    ):
        super().__init__()
        self.controller = controller
        self.url = url
        self.output_path = output_path
        self.quality = quality

    def run(self) -> None:
        """Execute the download request."""
        try:
            def progress_callback(percent: float, status: str) -> None:
                self.progress.emit(percent, status)

            file_path = self.controller.download(
                self.url,
                self.output_path,
                self.quality,
                progress_callback,
            )
            self.finished.emit(file_path)
        except Exception as exc:  # noqa: BLE001 - bubbling up to UI layer
            self.error.emit(str(exc))


class MainWindow(QMainWindow):
    """Main application window rendered with Qt widgets."""

    def __init__(self) -> None:
        super().__init__()

        # Set window icon FIRST, before other settings
        self._set_window_icon()
        
        self.setWindowTitle(Config.WINDOW_TITLE)
        self.resize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)

        # Backend controller
        self.controller = Controller()

        # State
        self.youtube_metadata: Optional[Dict[str, Any]] = None
        self.download_type = "video"
        self.is_downloading = False
        self.download_lock = threading.Lock()
        self.fetch_thread: Optional[QThread] = None
        self.download_thread: Optional[QThread] = None
        self.fetch_worker: Optional[FetchWorker] = None
        self.download_worker: Optional[DownloadWorker] = None

        # UI setup
        self._load_icons()
        self._init_fonts()
        self._build_central_widget()
        self._apply_styles()

    # ------------------------------------------------------------------
    # UI Construction helpers
    # ------------------------------------------------------------------
    def _init_fonts(self) -> None:
        """Create reusable QFont instances."""
        self.font_h1 = QFont(Fonts.FAMILY, 22, QFont.Weight.Bold)
        self.font_h3 = QFont(Fonts.FAMILY, 16, QFont.Weight.Bold)
        self.font_body = QFont(Fonts.FAMILY, 13)
        self.font_body_bold = QFont(Fonts.FAMILY, 13, QFont.Weight.Bold)
        self.font_small = QFont(Fonts.FAMILY, 11)

    def _load_icons(self) -> None:
        """Load button icons if available."""
        self.icon_video_red = self._create_icon(Config.ICON_VIDEO_RED)
        self.icon_video_dark = self._create_icon(Config.ICON_VIDEO_DARK)
        self.icon_audio_red = self._create_icon(Config.ICON_AUDIO_RED)
        self.icon_audio_dark = self._create_icon(Config.ICON_AUDIO_DARK)

    def _set_window_icon(self) -> None:
        """Set the window icon from icon128.ico file."""
        # Try multiple possible locations
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon128.ico"),
            os.path.join(os.getcwd(), "icon128.ico"),
            os.path.join(os.path.dirname(__file__), "..", "icon128.ico"),
        ]
        
        for icon_path in possible_paths:
            if os.path.exists(icon_path):
                icon = QIcon(icon_path)
                self.setWindowIcon(icon)
                return

    @staticmethod
    def _create_icon(path: str) -> Optional[QIcon]:
        if not path or not os.path.exists(path):
            return None
        pixmap = QPixmap(path)
        if pixmap.isNull():
            return None
        return QIcon(pixmap)

    def _build_central_widget(self) -> None:
        """Assemble widgets and layouts for the main interface."""
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout - removed the inner "Card" to save space and look cleaner
        layout = QVBoxLayout(central)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        # Header
        header = QHBoxLayout()
        header.setSpacing(Spacing.MD)
        layout.addLayout(header)

        icon_label = QLabel("▶")
        icon_label.setFixedSize(40, 40) # Smaller icon
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFont(QFont(Fonts.FAMILY, 20, QFont.Weight.Bold))
        icon_label.setObjectName("IconLabel")
        header.addWidget(icon_label)

        title_label = QLabel("YouTube Downloader")
        title_label.setFont(self.font_h1)
        header.addWidget(title_label, stretch=1)

        layout.addSpacing(Spacing.SM)

        # URL input
        input_label = QLabel("Video URL")
        input_label.setFont(self.font_h3)
        layout.addWidget(input_label)

        input_row = QHBoxLayout()
        input_row.setSpacing(Spacing.SM)
        layout.addLayout(input_row)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste link here...")
        self.url_input.setFont(self.font_body)
        self.url_input.setFixedHeight(Spacing.INPUT_HEIGHT)
        input_row.addWidget(self.url_input, stretch=1)

        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.setFont(self.font_body_bold)
        self.fetch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.fetch_btn.setFixedHeight(Spacing.BUTTON_HEIGHT)
        self.fetch_btn.setFixedWidth(100)
        self.fetch_btn.setObjectName("PrimaryButton")
        self.fetch_btn.clicked.connect(self._on_fetch)
        input_row.addWidget(self.fetch_btn)

        layout.addSpacing(Spacing.SM)

        # Download type toggle
        type_label = QLabel("Format")
        type_label.setFont(self.font_h3)
        layout.addWidget(type_label)

        toggle_row = QHBoxLayout()
        toggle_row.setSpacing(Spacing.SM)
        layout.addLayout(toggle_row)

        self.video_btn = QPushButton("Video")
        self.video_btn.setFont(self.font_body_bold)
        self.video_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.video_btn.setFixedHeight(Spacing.BUTTON_HEIGHT)
        self.video_btn.setCheckable(True)
        self.video_btn.clicked.connect(lambda: self._set_download_type("video"))
        toggle_row.addWidget(self.video_btn)

        self.audio_btn = QPushButton("Audio")
        self.audio_btn.setFont(self.font_body_bold)
        self.audio_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.audio_btn.setFixedHeight(Spacing.BUTTON_HEIGHT)
        self.audio_btn.setCheckable(True)
        self.audio_btn.clicked.connect(lambda: self._set_download_type("audio"))
        toggle_row.addWidget(self.audio_btn)

        layout.addSpacing(Spacing.SM)

        # Quality selector
        quality_label = QLabel("Quality")
        quality_label.setFont(self.font_h3)
        layout.addWidget(quality_label)

        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Select quality...")
        self.quality_combo.setEnabled(False)
        self.quality_combo.setFont(self.font_body)
        self.quality_combo.setFixedHeight(Spacing.INPUT_HEIGHT)
        self.quality_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.quality_combo)

        layout.addStretch() # Push everything up

        # Progress section
        self.progress_label = QLabel("")
        self.progress_label.setFont(self.font_small)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6) # Thinner progress bar
        layout.addWidget(self.progress_bar)

        layout.addSpacing(Spacing.SM)

        # Download button
        self.download_btn = QPushButton("Download Now")
        self.download_btn.setFont(self.font_body_bold)
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.setFixedHeight(50) # Slightly taller for emphasis
        self.download_btn.setObjectName("ActionButton")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self._on_download)
        layout.addWidget(self.download_btn)

        self._apply_toggle_styles()

    def _apply_styles(self) -> None:
        """Set global stylesheet for consistent theming."""
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {Colors.BG_MAIN};
                color: {Colors.TEXT_PRIMARY};
            }}
            QWidget {{
                color: {Colors.TEXT_PRIMARY};
            }}
            QLabel#IconLabel {{
                background-color: {Colors.ACTIVE_RED};
                color: white;
                border-radius: {Spacing.RADIUS_MD}px;
            }}
            QLineEdit {{
                background-color: {Colors.BG_INPUT};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: 0 12px;
                selection-background-color: {Colors.PRIMARY};
            }}
            QLineEdit:focus {{
                border: 1px solid {Colors.BORDER_FOCUS};
                background-color: {Colors.BG_HOVER};
            }}
            QPushButton {{
                border-radius: {Spacing.RADIUS_MD}px;
                border: none;
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_PRIMARY};
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
            }}
            QPushButton#PrimaryButton {{
                background-color: {Colors.ACTIVE_RED};
                color: white;
            }}
            QPushButton#PrimaryButton:hover {{
                background-color: {Colors.PRIMARY_HOVER};
            }}
            QPushButton#PrimaryButton:pressed {{
                background-color: {Colors.PRIMARY};
            }}
            QPushButton#ActionButton {{
                background-color: {Colors.ACTIVE_RED};
                color: white;
                border-radius: {Spacing.RADIUS_LG}px;
                font-size: 15px;
            }}
            QPushButton#ActionButton:hover {{
                background-color: {Colors.PRIMARY_HOVER};
            }}
            QPushButton#ActionButton:disabled {{
                background-color: {Colors.BG_INPUT};
                color: {Colors.TEXT_DISABLED};
            }}
            QComboBox {{
                background-color: {Colors.BG_INPUT};
                border: 1px solid {Colors.BORDER_LIGHT};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: 0 12px;
            }}
            QComboBox:hover {{
                background-color: {Colors.BG_HOVER};
                border: 1px solid {Colors.BORDER_LIGHT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none; 
            }}
            /* Custom arrow indicator could be added here if needed */
            
            QComboBox QAbstractItemView {{
                background-color: {Colors.BG_CARD};
                color: {Colors.TEXT_PRIMARY};
                selection-background-color: {Colors.BG_HOVER};
                border: 1px solid {Colors.BORDER_LIGHT};
                outline: none;
            }}
            QProgressBar {{
                background-color: {Colors.BG_INPUT};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {Colors.ACTIVE_RED};
                border-radius: 3px;
            }}
            """
        )

    def _apply_toggle_styles(self) -> None:
        """Update styles/icons for download type toggle buttons."""
        if self.download_type == "video":
            self._set_button_active(self.video_btn)
            self._set_button_inactive(self.audio_btn)
        else:
            self._set_button_active(self.audio_btn)
            self._set_button_inactive(self.video_btn)

    def _set_button_active(self, button: QPushButton) -> None:
        button.setStyleSheet(
            f"background-color: {Colors.ACTIVE_RED}; color: {Colors.TEXT_PRIMARY};"
            f"border: none;"
        )

    def _set_button_inactive(self, button: QPushButton) -> None:
        button.setStyleSheet(
            f"background-color: {Colors.INACTIVE_DARK}; color: {Colors.TEXT_PRIMARY};"
            f"border: none;"
        )

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def _on_fetch(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube URL")
            return

        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Fetching...")
        self.progress_label.setText("Fetching video information...")

        self.fetch_thread = QThread()
        self.fetch_worker = FetchWorker(self.controller, url)
        worker = self.fetch_worker
        worker.moveToThread(self.fetch_thread)

        self.fetch_thread.started.connect(worker.run)
        worker.finished.connect(self._on_fetch_success)
        worker.error.connect(self._on_fetch_error)
        worker.finished.connect(self.fetch_thread.quit)
        worker.error.connect(self.fetch_thread.quit)
        self.fetch_thread.finished.connect(worker.deleteLater)
        self.fetch_thread.finished.connect(self._clear_fetch_thread)

        self.fetch_thread.start()

    def _clear_fetch_thread(self) -> None:
        self.fetch_thread = None
        self.fetch_worker = None

    def _on_fetch_success(self, metadata: Dict[str, Any]) -> None:
        self.youtube_metadata = metadata
        self._update_quality_options()
        self.download_btn.setEnabled(True)

        if metadata.get("type") == "playlist":
            count = metadata.get("count", 0)
            title = metadata.get("title", "Playlist")
            self.progress_label.setText(f"Playlist found: {title} ({count} videos)")
            self.download_btn.setText("Download Playlist")
        else:
            self.progress_label.setText("Ready to download")
            self.download_btn.setText("Download Video")

        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch")

    def _on_fetch_error(self, error: str) -> None:
        QMessageBox.critical(self, "Fetch Error", f"Failed to fetch video information:\n{error}")
        self.progress_label.setText("")
        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("Fetch")

    def _on_download(self) -> None:
        with self.download_lock:
            if self.is_downloading:
                QMessageBox.information(
                    self,
                    "Download in Progress",
                    "A download is already running. Please wait for it to finish.",
                )
                return
            self.is_downloading = True

        if not self.youtube_metadata:
            QMessageBox.warning(self, "Download Error", "Please fetch video details first.")
            with self.download_lock:
                self.is_downloading = False
            return

        selected_quality = self.quality_combo.currentText()
        if selected_quality == "Select quality...":
            QMessageBox.warning(self, "Selection Error", "Please select a quality option.")
            with self.download_lock:
                self.is_downloading = False
            return

        output_path = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if not output_path:
            with self.download_lock:
                self.is_downloading = False
            return

        url = self.url_input.text().strip()
        download_quality = self._determine_download_quality(selected_quality)

        self.fetch_btn.setEnabled(False)
        self.download_btn.setEnabled(False)

        self.download_thread = QThread()
        self.download_worker = DownloadWorker(self.controller, url, output_path, download_quality)
        worker = self.download_worker
        worker.moveToThread(self.download_thread)

        self.download_thread.started.connect(worker.run)
        worker.progress.connect(self._update_progress)
        worker.finished.connect(self._on_download_success)
        worker.error.connect(self._on_download_error)
        worker.finished.connect(self.download_thread.quit)
        worker.error.connect(self.download_thread.quit)
        self.download_thread.finished.connect(worker.deleteLater)
        self.download_thread.finished.connect(self._clear_download_thread)

        self.download_thread.start()

    def _clear_download_thread(self) -> None:
        self.download_thread = None
        self.download_worker = None

    def _on_download_success(self, file_path: str) -> None:
        self.progress_bar.setValue(100)
        self.progress_label.setText("Download complete!")
        QMessageBox.information(self, "Success", f"Download complete!\n\nSaved to:\n{file_path}")

        self.fetch_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        with self.download_lock:
            self.is_downloading = False

    def _on_download_error(self, error: str) -> None:
        self.progress_bar.setValue(0)
        self.progress_label.setText("Download failed")
        QMessageBox.critical(self, "Download Error", f"Download failed:\n{error}")

        self.fetch_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        with self.download_lock:
            self.is_downloading = False

    def _update_progress(self, percent: float, status: str) -> None:
        self.progress_bar.setValue(int(percent))
        self.progress_label.setText(f"{status} {int(percent)}%")

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _set_download_type(self, download_type: str) -> None:
        self.download_type = download_type
        self._apply_toggle_styles()
        if self.youtube_metadata:
            self._update_quality_options()

    def _update_quality_options(self) -> None:
        if not self.youtube_metadata:
            return

        is_playlist = self.youtube_metadata.get("type") == "playlist"

        if self.download_type == "audio":
            self.quality_combo.clear()
            self.quality_combo.addItem("MP3 320kbps")
            self.quality_combo.setEnabled(True)
            self.quality_combo.setCurrentIndex(0)
            return

        if is_playlist:
            quality_labels = [
                "Best Available",
                "4K (2160p)",
                "2K (1440p)",
                "1080p",
                "720p",
                "480p",
                "360p",
            ]
        else:
            formats = self.youtube_metadata.get("formats", [])
            quality_labels = []
            for fmt in formats:
                label = fmt.get("label", fmt.get("quality", "Unknown"))
                quality_labels.append(f"{label}.mkv")

        self.quality_combo.clear()
        if quality_labels:
            self.quality_combo.addItems(quality_labels)
            self.quality_combo.setEnabled(True)
            self.quality_combo.setCurrentIndex(0)
        else:
            self.quality_combo.addItem("No qualities available")
            self.quality_combo.setEnabled(False)

    def _determine_download_quality(self, quality: str) -> Optional[str]:
        if self.download_type == "audio":
            return "Audio Only"

        is_playlist = self.youtube_metadata and self.youtube_metadata.get("type") == "playlist"

        if is_playlist:
            if quality == "Best Available":
                return None
            if "(" in quality:
                match = re.search(r"\((\d+p)\)", quality)
                if match:
                    return match.group(1)
            return quality.split(" ")[0]

        quality_clean = quality.replace(".mkv", "")
        if "(" in quality_clean and "p)" in quality_clean:
            match = re.search(r"\((\d+p\d*)\)", quality_clean)
            if match:
                return match.group(1)
        return quality_clean
