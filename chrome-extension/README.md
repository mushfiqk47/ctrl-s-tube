# Ctrl+S Tube - Chrome Extension

A modern Chrome extension for downloading YouTube videos and audio, directly integrated into your browser.

![Chrome Extension](https://img.shields.io/badge/Chrome-Extension-green.svg)
![Manifest V3](https://img.shields.io/badge/Manifest-V3-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Features

- **🚀 One-Click Access** - Click the extension icon or use the download button on YouTube pages
- **🎨 Modern UI** - Beautiful dark mode interface with smooth animations
- **📊 Video Preview** - See video thumbnail, title, and author before downloading
- **🎥 Video & Audio** - Toggle between video and audio download modes
- **⚙️ Quality Selection** - Choose from multiple quality options (4K, 1080p, 720p, etc.)
- **🔄 Auto-Detection** - Automatically detects YouTube videos on current tab
- **💾 Chrome Integration** - Uses Chrome's native download manager

## 📦 Installation

### Option 1: Load as Unpacked Extension (Development)

1. **Open Chrome Extensions Page**
   - Navigate to `chrome://extensions/`
   - Or click Menu → More Tools → Extensions

2. **Enable Developer Mode**
   - Toggle the "Developer mode" switch in the top-right corner

3. **Load the Extension**
   - Click "Load unpacked"
   - Navigate to the `chrome-extension` folder
   - Select the folder

4. **Pin the Extension** (Optional)
   - Click the puzzle icon in Chrome toolbar
   - Find "Ctrl+S Tube" and click the pin icon

### Option 2: Install from Chrome Web Store

*Coming soon - This extension is currently in development*

## 🎮 Usage

### Method 1: Extension Popup

1. Click the Ctrl+S Tube icon in your Chrome toolbar
2. The extension will auto-detect if you're on a YouTube video page
3. Or paste any YouTube URL into the input field
4. Click "Fetch" to load video information
5. Select download type (Video or Audio)
6. Choose your desired quality
7. Click "Download"

### Method 2: YouTube Page Integration

1. Navigate to any YouTube video page
2. Look for the red "Download" button next to the Like/Dislike buttons
3. Click the button to open the extension popup
4. Follow steps 5-7 from Method 1

### Method 3: Context Menu

1. Right-click anywhere on a YouTube video page
2. Select "Download with Ctrl+S Tube"
3. The extension popup will open

## ⚠️ Important Limitations

### Current Version

**This Chrome extension provides the UI and basic functionality**, but has limitations due to browser security restrictions:

- **No Direct Downloads**: Chrome extensions cannot run Python code (yt-dlp, FFmpeg)
- **Backend Required**: Full download functionality requires one of the following:
  - A backend server running yt-dlp
  - Chrome Native Messaging to communicate with the desktop app
  - A third-party API service

### Recommended Setup Options

#### Option A: Use the Desktop App
For full functionality, use the **desktop Python application** included in this repository:
```bash
cd ..
python main.py
```
The desktop app has no restrictions and can download any video/audio quality.

#### Option B: Backend Service (Advanced)
Set up a local or remote server running yt-dlp:

1. Create a simple Flask/FastAPI server
2. Endpoint: `POST /download` with `{ videoId, quality, type }`
3. Server uses yt-dlp to process the download
4. Update `popup.js` to call your backend API

Example backend structure:
```
backend/
├── server.py          # Flask/FastAPI server
├── requirements.txt   # yt-dlp, ffmpeg-python
└── README.md         # Backend setup instructions
```

#### Option C: Native Messaging (Advanced)
Connect the Chrome extension to the Python desktop app:

1. Configure Chrome Native Messaging host
2. Extension sends download requests to Python app
3. Python app processes downloads using existing codebase

See [Chrome Native Messaging Documentation](https://developer.chrome.com/docs/apps/nativeMessaging/)

## 📁 Extension Structure

```
chrome-extension/
├── manifest.json          # Extension configuration
├── popup.html            # Extension popup UI
├── popup.css             # Popup styles (dark mode)
├── popup.js              # Popup logic
├── content.js            # YouTube page integration
├── content.css           # YouTube button styles
├── background.js         # Service worker
├── icons/                # Extension icons
│   ├── icon16.png
│   ├── icon32.png
│   ├── icon48.png
│   └── icon128.png
└── README.md            # This file
```

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| **Manifest** | V3 (Latest Chrome Extension standard) |
| **UI** | HTML5, CSS3 (OKLCH colors) |
| **Logic** | Vanilla JavaScript (ES6+) |
| **APIs** | Chrome Extensions API, YouTube oEmbed API |
| **Styling** | Custom CSS with design tokens |
| **Font** | Poppins (Google Fonts) |

## 🎨 Design System

The extension uses the same design system as the desktop app:

- **Colors**: OKLCH color space for modern, vibrant colors
- **Typography**: Poppins font family
- **Dark Mode**: Premium dark theme with subtle gradients
- **Animations**: Smooth transitions and micro-interactions
- **Responsiveness**: Optimized for 420px popup width

## 🔧 Development

### Prerequisites
- Google Chrome (latest version)
- Text editor (VS Code recommended)
- Basic knowledge of HTML, CSS, JavaScript

### Making Changes

1. Edit the files in the `chrome-extension` folder
2. Go to `chrome://extensions/`
3. Click the refresh icon on the Ctrl+S Tube extension card
4. Test your changes

### Debugging

- **Popup**: Right-click the popup → Inspect
- **Background**: Click "Service Worker" link in extension card
- **Content Script**: Use Chrome DevTools on any YouTube page

### Adding Backend Support

To add full download functionality:

1. Create or deploy a backend service
2. Update `popup.js`:
   ```javascript
   async getVideoDownloadUrl(videoId, quality) {
       const response = await fetch('YOUR_API_ENDPOINT', {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ videoId, quality, type: this.downloadType })
       });
       const data = await response.json();
       return data.downloadUrl;
   }
   ```
3. Handle CORS properly on your backend
4. Test thoroughly

## 📝 Known Issues

- ✅ UI and video metadata fetching works perfectly
- ⚠️ Direct downloads require backend implementation
- ⚠️ Some YouTube videos may not provide full metadata via oEmbed API
- ⚠️ Thumbnails may not load for some videos

## 🚀 Roadmap

- [ ] Implement backend service for downloads
- [ ] Add native messaging for desktop app integration
- [ ] Support for YouTube playlists
- [ ] Download history tracking
- [ ] Settings page with preferences
- [ ] Keyboard shortcuts
- [ ] Chrome Web Store publication
- [ ] Multi-language support

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](../LICENSE) file for details.

## ⚖️ Legal & Ethical Use

**Important**: This tool is for educational purposes only.

- ✅ Download your own content
- ✅ Download Creative Commons content
- ✅ Download with creator permission
- ❌ Don't download copyrighted content without permission
- ❌ Don't redistribute downloaded content
- ❌ Don't violate YouTube's Terms of Service

**Users are responsible for complying with:**
- YouTube's Terms of Service
- Copyright laws in their jurisdiction
- Fair use guidelines
- Content creators' rights

## 🙏 Acknowledgments

- **[Chrome Extensions API](https://developer.chrome.com/docs/extensions/)** - Extension platform
- **[YouTube oEmbed API](https://oembed.com/)** - Video metadata
- **Desktop App** - Full-featured Python application (parent directory)

## 📧 Support

- **Issues**: [GitHub Issues](../../issues)
- **Desktop App**: See main [README.md](../README.md)
- **Chrome Extension Docs**: [developer.chrome.com](https://developer.chrome.com/docs/extensions/)

---

**Note**: For full download functionality, use the desktop application or implement a backend service. This extension provides a great UI and YouTube integration, but requires additional setup for actual downloads.
