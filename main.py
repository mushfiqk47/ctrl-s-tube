"""Application entry point."""

import sys

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def main() -> int:
    """Run the application."""
    try:
        app = QApplication(sys.argv)
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
