# CtrlSTube 📺⬇️

![App Screenshot](docs/images/screenshot.png)

**CtrlSTube** is a professional-grade YouTube downloader application built with Python and PySide6. It combines a sleek, modern interface with powerful backend processing to deliver high-quality video and audio downloads.

Designed for both casual users and power users, CtrlSTube supports 4K video downloads, batch processing, and automatic metadata tagging, all wrapped in a responsive, dark-themed UI.

---

## ✨ Key Features

*   **🎥 High-Fidelity Downloads**: Support for 4K (2160p), 2K (1440p), 1080p, and 60fps videos.
*   **🎵 Smart Audio Extraction**: Convert videos to crystal-clear MP3s with automatic metadata (ID3 tags) and thumbnail embedding.
*   **📦 Batch & Playlist Support**: Queue multiple videos or download entire playlists with a single click.
*   **🚀 Intelligent Auto-Fetch**: Automatically detects clipboard URLs and fetches metadata instantly.
*   **⚡ Optimized Performance**: Multi-threaded downloading engine powered by `yt-dlp` and `FFmpeg`.
*   **🎨 Modern UX/UI**: A polished, responsive interface built with PySide6.
*   **🛠️ Portable**: Available as a standalone `.exe` requiring no installation.

## 🛠️ Tech Stack

*   **Core**: [Python 3.8+](https://www.python.org/)
*   **GUI**: [PySide6](https://pypi.org/project/PySide6/) (Qt for Python)
*   **Engine**: [yt-dlp](https://github.com/yt-dlp/yt-dlp)
*   **Processing**: [FFmpeg](https://ffmpeg.org/)
*   **Metadata**: [mutagen](https://pypi.org/project/mutagen/)

## 🚀 Installation

### Option 1: Standalone Executable (Windows)
Download the latest release from the [Releases](https://github.com/mushfiqk47/ctrl-s-tube/releases) page and run `CtrlSTube.exe`. No Python installation required.

### Option 2: Run from Source

#### Prerequisites
- Python 3.8 or higher
- [FFmpeg](https://ffmpeg.org/download.html) (Added to system PATH)

#### Steps

1.  **Clone the repository**
    ```bash
    git clone https://github.com/mushfiqk47/ctrl-s-tube.git
    cd ctrl-s-tube
    ```

2.  **Run the setup script** (Automates venv creation and dependency installation)
    *   **Windows**: Double-click `setup.bat`
    *   **macOS/Linux**: Run `./setup.sh`

3.  **Start the Application**
    *   **Windows**: Double-click `run.bat`
    *   **macOS/Linux**: Run `./run.sh`

## ⚙️ Configuration

CtrlSTube works out of the box, but you can customize it using environment variables.

1.  Copy `.env.example` to `.env`:
    ```bash
    cp .env.example .env
    ```
2.  Edit `.env` to configure default download paths or API keys if needed.

## 📂 Project Structure

```text
ctrl-s-tube/
├── core/               # Application logic & controllers
├── services/           # Business logic (YouTube, Download, FFmpeg)
├── ui/                 # PySide6 GUI components
├── utils/              # Helpers & configuration
├── app_utils/          # Application-specific utilities
├── docs/               # Documentation & assets
├── tests/              # Unit tests
├── main.py             # Entry point
└── requirements.txt    # Dependencies
```

## 🤝 Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

1.  Fork the repo
2.  Create your feature branch (`git checkout -b feature/amazing-feature`)
3.  Commit your changes (`git commit -m 'Add amazing feature'`)
4.  Push to the branch (`git push origin feature/amazing-feature`)
5.  Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

Made with ❤️ by [Md. Mushfiq Kabir](https://github.com/mushfiqk47)
