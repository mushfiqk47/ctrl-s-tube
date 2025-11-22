"""Application entry point."""

import sys
import os
import ctypes
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow
from utils.config import Config

def main() -> int:
    """Run the application."""
    try:
        # Fix for Windows taskbar icon
        if sys.platform == 'win32':
            myappid = f'ctrlstube.downloader.app.{Config.VERSION}'  # Arbitrary unique ID
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        app = QApplication(sys.argv)
        
        # Set application icon
        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if not os.path.exists(icon_path):
             icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
             
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))

        window = MainWindow()
        window.show()
        return app.exec()
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        return 0
    except Exception as exc:  # noqa: BLE001 - surface fatal startup issues
        print(f"Fatal error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
