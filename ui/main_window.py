"""Main window UI implementation using PySide6."""

from __future__ import annotations

import os
import re
import threading
from typing import Optional, Dict, Any, List

from PySide6.QtCore import QObject, Qt, QThread, Signal, QSize, QUrl, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap, QTextCursor
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
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
    QTabWidget,
    QTextEdit,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
)

from core.controller import Controller
from app_utils.config import Colors, Config, Fonts, Spacing
from app_utils.batch_processor import extract_urls, validate_url_list, VideoItem, BatchProgress


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
        format: str = "mkv",
    ):
        super().__init__()
        self.controller = controller
        self.url = url
        self.output_path = output_path
        self.quality = quality
        self.format = format

    def run(self) -> None:
        """Execute the download request."""
        try:
            def progress_callback(percent: float, status: str) -> None:
                self.progress.emit(percent, status)

            file_path = self.controller.download(
                self.url,
                self.output_path,
                self.quality,
                self.format,
                progress_callback,
            )
            self.finished.emit(file_path)
        except Exception as exc:  # noqa: BLE001 - bubbling up to UI layer
            self.error.emit(str(exc))


class BatchFetchWorker(QObject):
    """Worker to fetch metadata for multiple URLs concurrently."""
    
    item_fetched = Signal(int, dict)  # index, metadata
    item_error = Signal(int, str)  # index, error
    all_finished = Signal()
    
    def __init__(self, controller: Controller, urls: List[str]):
        super().__init__()
        self.controller = controller
        self.urls = urls
        self.stopped = False
    
    def run(self) -> None:
        """Fetch metadata for all URLs."""
        for i, url in enumerate(self.urls):
            if self.stopped:
                break
            try:
                metadata = self.controller.fetch_metadata(url)
                self.item_fetched.emit(i, metadata)
            except Exception as exc:  # noqa: BLE001
                self.item_error.emit(i, str(exc))
        
        self.all_finished.emit()
    
    def stop(self) -> None:
        """Stop the worker."""
        self.stopped = True


class BatchDownloadWorker(QObject):
    """Worker to download multiple videos concurrently."""
    
    item_progress = Signal(int, float, str)  # index, percent, status
    item_finished = Signal(int, str)  # index, file_path
    item_error = Signal(int, str)  # index, error
    all_finished = Signal()
    
    def __init__(
        self,
        controller: Controller,
        video_items: List[VideoItem],
        output_path: str,
        quality: Optional[str],
        format: str = "mkv",
    ):
        super().__init__()
        self.controller = controller
        self.video_items = video_items
        self.output_path = output_path
        self.quality = quality
        self.format = format
        self.stopped = False
    
    def run(self) -> None:
        """Download all videos sequentially (can be enhanced with threading)."""
        for i, item in enumerate(self.video_items):
            if self.stopped:
                break
            
            if item.status != "ready":
                continue
            
            try:
                def progress_callback(percent: float, status: str) -> None:
                    self.item_progress.emit(i, percent, status)
                
                file_path = self.controller.download(
                    item.url,
                    self.output_path,
                    self.quality,
                    self.format,
                    progress_callback,
                )
                self.item_finished.emit(i, file_path)
            except Exception as exc:  # noqa: BLE001
                self.item_error.emit(i, str(exc))
        
        self.all_finished.emit()
    
    def stop(self) -> None:
        """Stop the worker."""
        self.stopped = True



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
        
        # Batch download state
        self.video_items: List[VideoItem] = []
        self.batch_fetch_thread: Optional[QThread] = None
        self.batch_fetch_worker: Optional[BatchFetchWorker] = None
        self.batch_download_thread: Optional[QThread] = None
        self.batch_download_worker: Optional[BatchDownloadWorker] = None
        self.batch_progress: Optional[BatchProgress] = None

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
        """Set the window icon from icon.ico or icon.png file."""
        # Try multiple possible locations and formats
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon.ico"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "icon.png"),
            os.path.join(os.getcwd(), "icon.ico"),
            os.path.join(os.getcwd(), "icon.png"),
            os.path.join(os.path.dirname(__file__), "..", "icon.ico"),
            os.path.join(os.path.dirname(__file__), "..", "icon.png"),
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

        # Main layout
        layout = QVBoxLayout(central)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        # Header
        header = QHBoxLayout()
        header.setSpacing(Spacing.MD)
        layout.addLayout(header)

        icon_label = QLabel("▶")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFont(QFont(Fonts.FAMILY, 20, QFont.Weight.Bold))
        icon_label.setObjectName("IconLabel")
        header.addWidget(icon_label)

        title_label = QLabel("CtrlSTube")
        title_label.setFont(self.font_h1)
        header.addWidget(title_label, stretch=1)

        layout.addSpacing(Spacing.SM)

        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setFont(self.font_body)
        layout.addWidget(self.tab_widget)

        # Build tabs
        self._build_single_download_tab()
        self._build_multiple_download_tab()

    def _build_single_download_tab(self) -> None:
        """Build the single video download tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.MD)

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
        self.url_input.textChanged.connect(self._on_url_input_changed)  # Auto-fetch
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
        self.quality_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.quality_combo)

        layout.addSpacing(Spacing.SM)

        # Format selector (MP4/MKV)
        format_label = QLabel("Video Format")
        format_label.setFont(self.font_h3)
        layout.addWidget(format_label)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["mkv", "mp4"])
        self.format_combo.setFont(self.font_body)
        self.format_combo.setFixedHeight(Spacing.INPUT_HEIGHT)
        self.format_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.format_combo)

        layout.addStretch()

        # Progress section
        self.progress_label = QLabel("")
        self.progress_label.setFont(self.font_small)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(self.progress_label)
        
        # File location label
        self.file_location_label = QLabel("")
        self.file_location_label.setFont(self.font_small)
        self.file_location_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_location_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        self.file_location_label.setVisible(False)
        layout.addWidget(self.file_location_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)

        layout.addSpacing(Spacing.SM)

        # Download button
        self.download_btn = QPushButton("Download Now")
        self.download_btn.setFont(self.font_body_bold)
        self.download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_btn.setFixedHeight(50)
        self.download_btn.setObjectName("ActionButton")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self._on_download)
        layout.addWidget(self.download_btn)

        self._apply_toggle_styles()
        
        self.tab_widget.addTab(tab, "Single Download")
    
    def _build_multiple_download_tab(self) -> None:
        """Build the multiple video download tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.MD)

        # URL input (single line like single download tab)
        input_label = QLabel("Video URL")
        input_label.setFont(self.font_h3)
        layout.addWidget(input_label)

        input_row = QHBoxLayout()
        input_row.setSpacing(Spacing.SM)
        layout.addLayout(input_row)

        self.batch_url_input = QLineEdit()
        self.batch_url_input.setPlaceholderText("Paste YouTube URL here...")
        self.batch_url_input.setFont(self.font_body)
        self.batch_url_input.setFixedHeight(Spacing.INPUT_HEIGHT)
        input_row.addWidget(self.batch_url_input, stretch=1)

        self.add_to_queue_btn = QPushButton("Add to Queue")
        self.add_to_queue_btn.setFont(self.font_body_bold)
        self.add_to_queue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_to_queue_btn.setFixedHeight(Spacing.BUTTON_HEIGHT)
        self.add_to_queue_btn.setFixedWidth(120)
        self.add_to_queue_btn.setObjectName("PrimaryButton")
        self.add_to_queue_btn.clicked.connect(self._on_add_to_queue)
        input_row.addWidget(self.add_to_queue_btn)

        layout.addSpacing(Spacing.SM)

        # Video list preview
        preview_label = QLabel("Download Queue")
        preview_label.setFont(self.font_h3)
        layout.addWidget(preview_label)

        self.batch_video_list = QListWidget()
        self.batch_video_list.setFont(self.font_body)
        layout.addWidget(self.batch_video_list)

        layout.addSpacing(Spacing.SM)

        # Batch quality selector
        batch_quality_label = QLabel("Quality (for all videos)")
        batch_quality_label.setFont(self.font_h3)
        layout.addWidget(batch_quality_label)

        self.batch_quality_combo = QComboBox()
        self.batch_quality_combo.addItems([
            "Best Available",
            "Audio Only (MP3)",
            "4K (2160p)",
            "2K (1440p)",
            "1080p",
            "720p",
            "480p",
            "360p",
        ])
        self.batch_quality_combo.setCurrentIndex(0)  # Best Available as default
        self.batch_quality_combo.setFont(self.font_body)
        self.batch_quality_combo.setFixedHeight(Spacing.INPUT_HEIGHT)
        self.batch_quality_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.batch_quality_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.batch_quality_combo)

        layout.addSpacing(Spacing.SM)

        # Batch Format selector
        batch_format_label = QLabel("Video Format (for all videos)")
        batch_format_label.setFont(self.font_h3)
        layout.addWidget(batch_format_label)

        self.batch_format_combo = QComboBox()
        self.batch_format_combo.addItems(["mkv", "mp4"])
        self.batch_format_combo.setFont(self.font_body)
        self.batch_format_combo.setFixedHeight(Spacing.INPUT_HEIGHT)
        self.batch_format_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.batch_format_combo)

        layout.addSpacing(Spacing.SM)

        # Batch progress
        self.batch_progress_label = QLabel("")
        self.batch_progress_label.setFont(self.font_small)
        self.batch_progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.batch_progress_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(self.batch_progress_label)

        self.batch_progress_bar = QProgressBar()
        self.batch_progress_bar.setRange(0, 100)
        self.batch_progress_bar.setValue(0)
        self.batch_progress_bar.setTextVisible(False)
        self.batch_progress_bar.setFixedHeight(6)
        layout.addWidget(self.batch_progress_bar)

        layout.addSpacing(Spacing.SM)

        # Download All button
        self.batch_download_btn = QPushButton("Download All")
        self.batch_download_btn.setFont(self.font_body_bold)
        self.batch_download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.batch_download_btn.setFixedHeight(50)
        self.batch_download_btn.setObjectName("ActionButton")
        self.batch_download_btn.setEnabled(False)
        self.batch_download_btn.clicked.connect(self._on_batch_download)
        layout.addWidget(self.batch_download_btn)

        self.tab_widget.addTab(tab, "Multiple Download")

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
            self.format_combo.setEnabled(True)
        else:
            self._set_button_active(self.audio_btn)
            self._set_button_inactive(self.video_btn)
            self.format_combo.setEnabled(False)

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
    def _on_url_input_changed(self, text: str) -> None:
        """Auto-fetch when a valid YouTube URL is pasted."""
        # Don't auto-fetch if already fetching or downloading
        if self.fetch_thread or self.is_downloading:
            return
        
        url = text.strip()
        if not url:
            return
        
        # Validate URL
        valid_urls, invalid_urls = validate_url_list([url])
        
        # If valid and looks complete (has video ID pattern), auto-fetch
        if valid_urls and not invalid_urls:
            # Use a short delay to ensure user finished pasting
            if hasattr(self, '_auto_fetch_timer'):
                self._auto_fetch_timer.stop()
            
            self._auto_fetch_timer = QTimer()
            self._auto_fetch_timer.setSingleShot(True)
            self._auto_fetch_timer.timeout.connect(lambda: self._auto_fetch_url(url))
            self._auto_fetch_timer.start(500)  # 500ms delay after last character
    
    def _auto_fetch_url(self, url: str) -> None:
        """Trigger automatic fetch for the given URL."""
        # Verify URL is still in the input field
        if self.url_input.text().strip() == url and not self.fetch_thread:
            self._on_fetch()
    
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
        selected_format = self.format_combo.currentText()
        
        # Show download location
        self.file_location_label.setText(f"Downloading to: {output_path}")
        self.file_location_label.setVisible(True)

        self.fetch_btn.setEnabled(False)
        self.download_btn.setEnabled(False)

        self.download_thread = QThread()
        self.download_worker = DownloadWorker(self.controller, url, output_path, download_quality, selected_format)
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
        self.file_location_label.setVisible(False)
        QMessageBox.information(self, "Success", f"Download complete!\n\nSaved to:\n{file_path}")

        self.fetch_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        with self.download_lock:
            self.is_downloading = False

    def _on_download_error(self, error: str) -> None:
        self.progress_bar.setValue(0)
        self.progress_label.setText("Download failed")
        self.file_location_label.setVisible(False)
        QMessageBox.critical(self, "Download Error", f"Download failed:\n{error}")

        self.fetch_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        with self.download_lock:
            self.is_downloading = False

    def _update_progress(self, percent: float, status: str) -> None:
        self.progress_bar.setValue(int(percent))
        # Status may include speed info from progress handler
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
                quality_labels.append(f"{label}")

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

    # ------------------------------------------------------------------
    # Batch download event handlers
    # ------------------------------------------------------------------
    def _on_add_to_queue(self) -> None:
        """Add a single URL to the download queue."""
        url = self.batch_url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a YouTube URL first.")
            return
        
        # Validate URL
        valid_urls, invalid_urls = validate_url_list([url])
        
        if invalid_urls or not valid_urls:
            QMessageBox.warning(
                self,
                "Invalid URL",
                "The URL you entered is not a valid YouTube URL.\n\n"
                "Supported formats:\n"
                "• https://www.youtube.com/watch?v=VIDEO_ID\n"
                "• https://youtu.be/VIDEO_ID\n"
                "• https://www.youtube.com/shorts/VIDEO_ID"
            )
            return
        
        validated_url = valid_urls[0]
        
        # Check for duplicates
        for existing_item in self.video_items:
            if existing_item.url == validated_url:
                QMessageBox.information(
                    self,
                    "Duplicate URL",
                    "This URL is already in the queue."
                )
                return
        
        # Create video item
        item = VideoItem(url=validated_url)
        self.video_items.append(item)
        
        # Add to list widget
        list_item = QListWidgetItem(f"⏳ Fetching: {validated_url}")
        self.batch_video_list.addItem(list_item)
        
        # Clear input
        self.batch_url_input.clear()
        
        # Fetch metadata in background
        self.add_to_queue_btn.setEnabled(False)
        self.add_to_queue_btn.setText("Adding...")
        
        index = len(self.video_items) - 1
        
        # Use single fetch worker
        self.batch_fetch_thread = QThread()
        self.batch_fetch_worker = BatchFetchWorker(self.controller, [validated_url])
        worker = self.batch_fetch_worker
        worker.moveToThread(self.batch_fetch_thread)
        
        # Connect with index offset
        def on_fetched(i: int, metadata: Dict[str, Any]) -> None:
            self._on_batch_item_fetched(index, metadata)
        
        def on_error(i: int, error: str) -> None:
            self._on_batch_item_error(index, error)
        
        self.batch_fetch_thread.started.connect(worker.run)
        worker.item_fetched.connect(on_fetched)
        worker.item_error.connect(on_error)
        worker.all_finished.connect(self._on_single_fetch_finished)
        worker.all_finished.connect(self.batch_fetch_thread.quit)
        self.batch_fetch_thread.finished.connect(worker.deleteLater)
        self.batch_fetch_thread.finished.connect(self._clear_batch_fetch_thread)
        
        self.batch_fetch_thread.start()
    
    def _on_single_fetch_finished(self) -> None:
        """Handle completion of single URL fetch."""
        self.add_to_queue_btn.setEnabled(True)
        self.add_to_queue_btn.setText("Add to Queue")
        
        # Update ready count
        ready_count = sum(1 for item in self.video_items if item.status == "ready")
        if ready_count > 0:
            self.batch_download_btn.setEnabled(True)
            self.batch_progress_label.setText(f"{ready_count} video(s) ready to download")
    
    def _on_batch_item_fetched(self, index: int, metadata: Dict[str, Any]) -> None:
        """Handle successful metadata fetch for a batch item."""
        if index < len(self.video_items):
            item = self.video_items[index]
            item.title = metadata.get("title", "Unknown Title")
            item.status = "ready"
            item.metadata = metadata
            
            # Update list widget
            list_item = self.batch_video_list.item(index)
            if list_item:
                list_item.setText(f"✓ {item.title}")
    
    def _on_batch_item_error(self, index: int, error: str) -> None:
        """Handle metadata fetch error for a batch item."""
        if index < len(self.video_items):
            item = self.video_items[index]
            item.status = "error"
            item.error_message = error
            
            # Update list widget
            list_item = self.batch_video_list.item(index)
            if list_item:
                list_item.setText(f"✗ Error: {item.url} - {error}")
    
    
    def _clear_batch_fetch_thread(self) -> None:
        """Clear batch fetch thread references."""
        self.batch_fetch_thread = None
        self.batch_fetch_worker = None
    
    def _on_batch_download(self) -> None:
        """Start batch download of all ready videos (concurrent like playlist)."""
        ready_items = [item for item in self.video_items if item.status == "ready"]
        
        if not ready_items:
            QMessageBox.warning(
                self,
                "No Videos Ready",
                "No videos are ready for download. Please add videos to the queue first."
            )
            return
        
        output_path = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if not output_path:
            return
        
        # Get selected quality (with fallback to best available)
        selected_quality = self.batch_quality_combo.currentText()
        download_quality = self._determine_batch_quality(selected_quality)
        
        # Initialize progress tracking
        self.batch_progress = BatchProgress(len(ready_items))
        
        # Disable buttons
        self.add_to_queue_btn.setEnabled(False)
        quality = self.batch_quality_combo.currentText()
        download_quality = self._determine_download_quality(quality)
        selected_format = self.batch_format_combo.currentText()
        
        self.batch_download_thread = QThread()
        self.batch_download_worker = BatchDownloadWorker(
            self.controller,
            self.video_items,
            output_path,
            download_quality,
            selected_format
        )
        worker = self.batch_download_worker
        worker.moveToThread(self.batch_download_thread)
        
        self.batch_download_thread.started.connect(worker.run)
        worker.item_progress.connect(self._on_batch_item_progress)
        worker.item_finished.connect(self._on_batch_item_finished)
        worker.item_error.connect(self._on_batch_item_download_error)
        worker.all_finished.connect(self._on_batch_download_finished)
        worker.all_finished.connect(self.batch_download_thread.quit)
        self.batch_download_thread.finished.connect(worker.deleteLater)
        self.batch_download_thread.finished.connect(self._clear_batch_download_thread)
        
        self.batch_download_thread.start()
    
    def _on_batch_item_progress(self, index: int, percent: float, status: str) -> None:
        """Handle progress update for a batch download item."""
        if self.batch_progress:
            self.batch_progress.update_item_progress(str(index), percent)
            overall = self.batch_progress.get_overall_progress()
            self.batch_progress_bar.setValue(int(overall))
            self.batch_progress_label.setText(
                f"{self.batch_progress.get_status_summary()} - {status}"
            )
    
    def _on_batch_item_finished(self, index: int, file_path: str) -> None:
        """Handle successful download of a batch item."""
        if index < len(self.video_items):
            item = self.video_items[index]
            item.status = "complete"
            
            list_item = self.batch_video_list.item(index)
            if list_item:
                list_item.setText(f"✓ Downloaded: {item.title}")
        
        if self.batch_progress:
            self.batch_progress.mark_completed(str(index))
            overall = self.batch_progress.get_overall_progress()
            self.batch_progress_bar.setValue(int(overall))
            self.batch_progress_label.setText(self.batch_progress.get_status_summary())
    
    def _on_batch_item_download_error(self, index: int, error: str) -> None:
        """Handle download error for a batch item."""
        if index < len(self.video_items):
            item = self.video_items[index]
            item.status = "error"
            item.error_message = error
            
            list_item = self.batch_video_list.item(index)
            if list_item:
                list_item.setText(f"✗ Failed: {item.title} - {error}")
        
        if self.batch_progress:
            self.batch_progress.mark_failed(str(index))
    
    def _on_batch_download_finished(self) -> None:
        """Handle completion of batch download."""
        if self.batch_progress:
            completed = self.batch_progress.completed_items
            failed = self.batch_progress.failed_items
            total = self.batch_progress.total_items
            
            self.batch_progress_bar.setValue(100)
            self.batch_progress_label.setText(
                f"Batch complete: {completed} succeeded, {failed} failed out of {total}"
            )
            
            QMessageBox.information(
                self,
                "Batch Download Complete",
                f"Downloaded {completed} of {total} videos.\n"
                f"{failed} videos failed."
            )
        
        self.add_to_queue_btn.setEnabled(True)
        self.batch_download_btn.setEnabled(True)
    
    def _clear_batch_download_thread(self) -> None:
        """Clear batch download thread references."""
        self.batch_download_thread = None
        self.batch_download_worker = None
    
    def _determine_batch_quality(self, quality: str) -> Optional[str]:
        """
        Determine quality string for batch downloads.
        
        Note: If a video doesn't have the selected quality, the download
        service will automatically fallback to best available quality.
        """
        if quality.startswith("Audio Only"):
            return "Audio Only"  # Triggers audio-only download
        if quality == "Best Available":
            return None  # None triggers best quality in download service
        if "(" in quality:
            match = re.search(r"\((\d+p)\)", quality)
            if match:
                return match.group(1)
        return quality.split(" ")[0]
